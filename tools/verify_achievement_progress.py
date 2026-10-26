"""Run the actual SuperUI progress callback in Lua 5.1 against native formats.

Pass --lua-path with a directory containing lupa when it is not installed.
Only the engine text conversion is mocked; the callback and comparisons are real.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def function_text(source, name):
    start = source.index('function ' + name + '(')
    following = re.search(r'^function ', source[start + 1:], re.M)
    return source[start:start + 1 + following.start()] if following else source[start:]


def verify(lua_path=None):
    if lua_path:
        sys.path.insert(0, str(lua_path))
    from lupa.lua51 import LuaRuntime
    from cxt import parse, tag_hash

    payload = ROOT / 'localization/payload'
    menu = (payload / 'Mods/pause_menu.lua').read_bytes().decode('ascii')
    vint = (payload / 'Mods/vint_lib.lua').read_bytes().decode('ascii')
    native = {r['id']: r['text'] for r in json.loads(
        (ROOT / 'localization/text/static_CH.json').read_text('utf8'))['records']}
    entries = {r['tag']: r['text'] for r in parse(
        (payload / 'Mods/JUICED - Strings/juiced_CH.cxt').read_bytes().decode('utf8'))}
    def native_text(tag):
        return native[f'0x{tag_hash(tag):08X}']
    native_format = native_text('STATS_BLANK_OF_BLANK')
    menu_format = native_text('PAUSE_MENU_OF')
    assert native_format == '%d / %d' and menu_format == '{0}/{1}'
    entries['PAUSE_MENU_OF'] = menu_format
    lua = LuaRuntime(encoding=None)
    g = lua.globals()
    lua.execute(b'local f,e=loadstring(...); assert(f,e)', menu.encode('ascii'))

    def wide(text):
        return b'\xffU' + text.encode('utf-16-le')

    def resolve(value):
        if isinstance(value, (int, float)):
            return str(int(value))
        if value.startswith(b'\xffU'):
            return value[2:].decode('utf-16-le')
        value = value.decode('utf8')
        return entries.get(value, value)

    def insert(template, arguments):
        result = resolve(template)
        for key, value in arguments.items():
            result = result.replace('{' + str(key) + '}', resolve(value))
        return wide(result)

    g[b'vint_insert_values_in_string'] = insert
    g[b'format_int_to_string'] = lambda n: str(int(n)).encode()
    lua.execute((function_text(vint, 'sui_create_string') +
                 function_text(vint, 'sui_compare_string') +
                 function_text(menu, 'pause_menu_achievements_stats')).encode('ascii'))
    g[b'Pause_info_achievements_menu'] = lua.table_from({b'num_items': 0})
    captured = []
    g[b'pause_menu_achievements_add'] = lambda *args: captured.append(args)
    # Use actual tag translations for the predicates as well as the real native
    # percent-format template. The former fixture incorrectly used compact 3/11.
    callback = function_text(menu, 'pause_menu_achievements_stats')
    branches = re.findall(
        r'if sui_compare_string\(stat_text, "([^"]+)"\) then(.*?)\n\tend',
        callback, re.S)
    bounded = []
    for tag, body in branches:
        name = re.search(r'achieve_name = "([^"]+)"', body)
        maximum = re.search(r'stat_max = (\d+)', body)
        if name and maximum and int(maximum[1]) > 0:
            if tag not in entries:
                entries[tag] = native_text(tag)
            # Independent native fixture: index 163/type 53 formats its total
            # from 0x2527B2C. This PC installation has 27 race definitions
            # (Race_Number 0..26), unlike SuperUI's old hardcoded 28.
            expected_maximum = 27 if tag == 'STAT_RACES_COMPLETED' else int(maximum[1])
            bounded.append((tag, name[1], expected_maximum))
    assert len(bounded) == 27, len(bounded)
    failures = []
    cases = 0
    for tag, name, maximum in bounded:
        for template in (native_format, '%d/%d'):
            sample = {0, maximum // 2, maximum}
            if tag == 'STAT_RACES_COMPLETED':
                sample |= {1, 26}
            for current in sorted(sample):
                captured.clear()
                g[b'Pause_menu_achievements_blue_collar_count'] = 0
                g[b'pause_menu_achievements_stats'](
                    wide(entries[tag]), 1, wide(template % (current, maximum)))
                if name == 'internal_blue_collar':
                    actual = g[b'Pause_menu_achievements_blue_collar_count']
                    expected = int(current == maximum)
                else:
                    actual = captured[0][2] if len(captured) == 1 else None
                    expected = current
                    if captured[0][3] != maximum:
                        failures.append([tag, 'achievement total', captured[0][3], maximum])
                cases += 1
                if actual != expected:
                    failures.append([tag, template % (current, maximum), actual, expected])
    # Existing unbounded and cash paths must retain their behavior.
    for tag, value, expected in [('STAT_MP_NUTSHOTS', '58', 58),
                                 ('STAT_TAUNT_GANG', '1', 1),
                                 ('SUI_STAT_TOTAL_MONEY_GAMBLED', '$0.00', 0)]:
        if tag not in entries:
            entries[tag] = native_text(tag)
        captured.clear()
        g[b'pause_menu_achievements_stats'](wide(entries[tag]), 1, wide(value))
        assert captured[0][2] == expected, tag
    # Do not invent zero/completion for corrupt or unrecognized bounded values.
    captured.clear()
    g[b'pause_menu_achievements_stats'](wide(entries['STAT_CDS_FOUND']), 1, wide('invalid'))
    assert captured[0][2] == -1
    # Run the real add/display function too: 26/27 is incomplete, while 27/27
    # receives exactly one completion star and increments the menu count once.
    lua.execute(('local sr2cn_achievement_descriptions = {}\n' +
                 function_text(menu, 'pause_menu_achievements_add')).encode('ascii'))
    for current in (0, 1, 26, 27):
        g[b'Pause_info_achievements_menu'] = lua.table_from({b'num_items': 0})
        g[b'Pause_menu_achievements_unlock_count'] = 0
        g[b'pause_menu_achievements_stats'](
            wide(entries['STAT_RACES_COMPLETED']), 1, wide(native_format % (current, 27)))
        item = g[b'Pause_info_achievements_menu'][0]
        expected_complete = int(current == 27)
        assert item[b'progress_now'] == current and item[b'progress_max'] == 27
        assert g[b'Pause_menu_achievements_unlock_count'] == expected_complete
        assert resolve(item[b'label']).count('ui_hud_diversion_star_gold') == expected_complete
    report = dict(passed=not failures, luaVersion='5.1', boundedStatBranches=len(bounded),
                  boundedCases=cases, racingCompletionDisplayCases=4,
                  unaffectedPaths=3, malformedValueNotFalselyCompleted=True,
                  nativeTemplate=native_format, menuTemplate=menu_format,
                  luaSha256=hashlib.sha256(menu.encode('ascii')).hexdigest(),
                  failures=failures,
                  limitation='Engine text conversion is mocked; in-game verification is separate.')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lua-path', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = verify(args.lua_path)
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print(json.dumps({**report, 'failures': report['failures'][:5]}))
    raise SystemExit(0 if report['passed'] else 1)
