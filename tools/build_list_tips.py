"""Rebuild only the managed list/tips CXT records; retain all other CXT bytes."""
import hashlib
import json
from pathlib import Path
import sys
import re

from cxt import parse, render, tag_hash

ROOT = Path(__file__).resolve().parents[1]
RELATIVE = 'Mods/JUICED - Strings/juiced_CH.cxt'
LUA_RELATIVE = 'Mods/pause_menu.lua'
BEGIN = '-- BEGIN SR2CN DISPLAY LOCALIZATION\r\n'
END = '-- END SR2CN DISPLAY LOCALIZATION\r\n\r\n'
STAT_ALIASES = {
    'Ronin missions completed': 'SUI_STAT_RN_MISSIONS_COMPLETED',
    'Brotherhood missions completed': 'SUI_STAT_BH_MISSIONS_COMPLETED',
    'Sons of Samedi missions completed': 'SUI_STAT_SS_MISSIONS_COMPLETED',
    'Total money gambled': 'SUI_STAT_TOTAL_MONEY_GAMBLED',
}
CALLS = {
    'function pause_menu_populate_hitman_target(name, dead, dossier, peg, image, location, current)':
        '\tname = sr2cn_localize_display_name(name, sr2cn_hitman_names)',
    'function pause_menu_populate_chop_shop_vehicle(name, retrieved, dossier, peg, image, cash, respect, current)':
        '\tname = sr2cn_localize_display_name(name, sr2cn_vehicle_names)',
    'function pause_menu_achievements_add(achieve_name, description, progress_now, progress_max, format_type)':
        '\tdescription = sr2cn_achievement_descriptions[achieve_name] or description',
}
BOUNDED_STAT_OLD = (
    '\t\t\t\tlocal s = vint_insert_values_in_string("PAUSE_MENU_OF", {[0] = i, [1] = stat_max})\r\n'
    '\t\t\t\tif sui_compare_string(value, s) then\r\n')
BOUNDED_STAT_NEW = (
    '\t\t\t\tlocal s = vint_insert_values_in_string("PAUSE_MENU_OF", {[0] = i, [1] = stat_max})\r\n'
    '\t\t\t\t-- Native Chinese STATS_BLANK_OF_BLANK is "%d / %d", not the menu template.\r\n'
    '\t\t\t\tlocal native_s = vint_insert_values_in_string("{0} / {1}", {[0] = i, [1] = stat_max})\r\n'
    '\t\t\t\tif sui_compare_string(value, s) or sui_compare_string(value, native_s) then\r\n')
RACING_OLD = (
    '\t\tprogress_max = 28\r\n'
    '\t\tstat_max = 28\r\n')
RACING_NEW = (
    '\t\t-- PC racing_sr2_city.xtbl has Race_Number 0..26; native total is 27.\r\n'
    '\t\tprogress_max = 27\r\n'
    '\t\tstat_max = 27\r\n')


def strip_lua(text):
    text = text.replace(RACING_NEW, RACING_OLD)
    text = text.replace(BOUNDED_STAT_NEW, BOUNDED_STAT_OLD)
    if BEGIN in text:
        assert text.count(BEGIN) == text.count(END) == 1
        start = text.index(BEGIN)
        end = text.index(END, start) + len(END)
        text = text[:start] + text[end:]
    for signature, call in CALLS.items():
        text = text.replace(signature + '\r\n' + call + '\r\n', signature + '\r\n')
    for original, tag in STAT_ALIASES.items():
        text = text.replace('sui_compare_string(stat_text, "' + tag + '")',
                            'sui_compare_string(stat_text, "' + original + '")')
    return text


def lua_display_block(records, info):
    lines = [BEGIN.rstrip('\r\n'), '-- ASCII tags only; native Unicode stays in the engine text layer.']
    for group, variable in [('hitman-name', 'sr2cn_hitman_names'), ('vehicle-name', 'sr2cn_vehicle_names')]:
        lines.append('local ' + variable + ' = {')
        for r in records:
            if r['group'] == group:
                # The engine's ASCII literal for Bezier also compares against
                # the native accented alias where applicable; escape UTF-8 bytes.
                name = ''.join(chr(b) if 32 <= b < 127 else '\\%03d' % b for b in r['source'].encode('utf8'))
                lines.append('\t{"' + name + '", "' + r['tag'] + '"},')
        lines.append('}')
    lines.extend(['local function sr2cn_localize_display_name(name, aliases)',
                  '\tfor _, pair in ipairs(aliases) do',
                  '\t\tif sui_compare_string(name, pair[1]) then return pair[2] end',
                  '\tend', '\treturn name', 'end',
                  'local sr2cn_achievement_descriptions = {'])
    for r in info['records']:
        if r['group'] == 'achievement-description':
            lines.append('\t["' + r['achievement'] + '"] = "' + r['tag'] + '",')
    lines.extend(['}', END.rstrip('\r\n'), '', ''])
    return '\r\n'.join(lines)


def rebuild_lua(records, info):
    path = ROOT / 'localization/payload' / LUA_RELATIVE
    baseline = strip_lua(path.read_bytes().decode('ascii'))
    assert hashlib.sha256(baseline.encode('ascii')).hexdigest() == info['pauseMenuBaselineSha256'], 'unexpected Lua baseline'
    output = baseline
    anchor = next(iter(CALLS))
    assert output.count(anchor) == 1
    output = output.replace(anchor, lua_display_block(records, info) + anchor, 1)
    for signature, call in CALLS.items():
        assert output.count(signature) == 1
        output = output.replace(signature + '\r\n', signature + '\r\n' + call + '\r\n', 1)
    for original, tag in STAT_ALIASES.items():
        old = 'sui_compare_string(stat_text, "' + original + '")'
        assert output.count(old) == 1
        output = output.replace(old, 'sui_compare_string(stat_text, "' + tag + '")')
    assert output.count(BOUNDED_STAT_OLD) == 1
    output = output.replace(BOUNDED_STAT_OLD, BOUNDED_STAT_NEW, 1)
    assert output.count(RACING_OLD) == 1
    output = output.replace(RACING_OLD, RACING_NEW, 1)
    assert strip_lua(output) == baseline, 'unmanaged Lua changed'
    path.write_bytes(output.encode('ascii'))
    return path.read_bytes()


def main():
    source = json.loads((ROOT / 'localization/text/list-tips.json').read_text('utf8'))
    records = source['records']
    info = json.loads((ROOT / 'localization/text/info-pages.json').read_text('utf8'))
    all_records = records + info['records']
    tags = {r['tag'] for r in all_records}
    assert len(tags) == len(all_records)
    remove = tags | set(source.get('retiredTags', []))
    # Old section headers containing commas were parsed under truncated IDs.
    remove |= {t.split(',')[0].strip() for t in tags if ',' in t}
    path = ROOT / 'localization/payload' / RELATIVE
    data = path.read_bytes()
    text = data.decode('utf8')
    entries = parse(text)
    for item in reversed(entries):
        if item['tag'] in remove:
            text = text[:item['start']] + text[item['end']:]
    baseline = parse(text)
    assert not ({tag_hash(r['tag']) for r in baseline} & {tag_hash(t) for t in tags}), 'CXT ID collision'
    generated = ''.join(render(r['tag'], r['text']) for r in all_records)
    output = (text.rstrip('\r\n') + '\r\n\r\n' + generated.rstrip('\r\n') + '\r\n').encode('utf8')
    rebuilt = parse(output.decode('utf8'))
    assert {r['tag']: r['text'] for r in baseline} == {
        r['tag']: r['text'] for r in rebuilt if r['tag'] not in tags}, 'unmanaged CXT entries changed'
    assert len({tag_hash(r['tag']) for r in rebuilt}) == len(rebuilt), 'duplicate CXT ID'
    path.write_bytes(output)
    lua = rebuild_lua(records, info)
    manifest_path = ROOT / 'localization/manifest.json'
    manifest = json.loads(manifest_path.read_text('utf8'))
    item = next(r for r in manifest['payload'] if r['path'] == RELATIVE)
    item.update(bytes=len(output), sha256=hashlib.sha256(output).hexdigest())
    lua_item = next(r for r in manifest['payload'] if r['path'] == LUA_RELATIVE)
    lua_item.update(bytes=len(lua), sha256=hashlib.sha256(lua).hexdigest())
    manifest['localRevision'] = '2026-10-26-achievement-racing-progress'
    manifest_path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    super_path = ROOT / 'localization/superui-manifest.json'
    superui = json.loads(super_path.read_text('utf8'))
    super_item = next(r for r in superui['files'] if r['path'] == LUA_RELATIVE)
    super_item.update(bytes=len(lua), sha256=hashlib.sha256(lua).hexdigest(), matchesOriginalSuperUI=False,
                      modification='ASCII-only display-name mapping, Chinese achievement descriptions, localized statistics comparison tags, native spaced-ratio matching, and PC race total corrected from 28 to 27; save data unchanged.')
    super_path.write_bytes((json.dumps(superui, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'managed': len(all_records), 'retained': len(baseline), **item, 'luaSha256':lua_item['sha256']}))


if __name__ == '__main__':
    main()
