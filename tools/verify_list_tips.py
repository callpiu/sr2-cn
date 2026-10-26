"""Check list/tip coverage, glyphs, CXT IDs, paragraph breaks and game controls."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from cxt import parse, render, tag_hash
from build_list_tips import strip_lua, lua_display_block, STAT_ALIASES, CALLS, BOUNDED_STAT_NEW, RACING_NEW

ROOT = Path(__file__).resolve().parents[1]
CONTROL = re.compile(r'\{[^{}]+\}|\[(?:/?format|color:[^\]]+)\]|%%|\n|555-[A-Z]+')


def verify(payload=None):
    payload = payload or ROOT / 'localization/payload'
    source = json.loads((ROOT / 'localization/text/list-tips.json').read_text('utf8'))
    records = source['records']
    assert len(records) == 188
    assert len({r['tag'] for r in records}) == len(records)
    assert len({r['id'] for r in records}) == len(records)
    counts = Counter(r['group'] for r in records)
    assert counts == {'hitman-name': 28, 'vehicle-name': 42, 'shop-name': 3,
                      'hitman-dossier': 30, 'chop-shop-dossier': 40, 'loading-tip': 45}
    entries = parse((payload / 'Mods/JUICED - Strings/juiced_CH.cxt').read_bytes().decode('utf8'))
    assert len({tag_hash(r['tag']) for r in entries}) == len(entries), 'CXT hash collision'
    actual = {r['tag']: r['text'] for r in entries}
    chars = set(json.loads((ROOT / 'localization/text/charlist_CH.json').read_text('utf8')))
    for r in records:
        assert r['id'] == f"0x{tag_hash(r['tag']):08X}", r['tag']
        assert actual.get(r['tag']) == r['text'], ('CXT differs', r['tag'])
        assert not {c for c in r['text'] if ord(c) >= 256 and ord(c) not in chars}, r['tag']
        if r['group'].endswith('dossier'):
            assert CONTROL.findall(r['source']) == CONTROL.findall(r['text']), ('control drift', r['tag'])
        visible = re.sub(r'555-(?:FIRE|OOPS)|V8', '', r['text'])
        assert not re.search(r'[A-Za-z]', visible), ('remaining English', r['tag'])
    for group, prefix, size in [('hitman-dossier', 'HITMAN_TARGET', 6),
                                ('chop-shop-dossier', 'CHOP_SHOP_TARGET', 8)]:
        assert {r['tag'] for r in records if r['group'] == group} == {
            f'{prefix}_{i}_{j}' for i in range(1, 6) for j in range(1, size + 1)}
    # Source Chinese dossiers are immutable. This revision adds overlays only.
    static_bytes = (ROOT / 'localization/text/static_CH.json').read_bytes()
    static_source = next(s for s in source['sources'] if s['asset'] == 'localization/text/static_CH.json')
    assert hashlib.sha256(static_bytes).hexdigest() == static_source['sha256']
    native = {r['id']: r['text'] for r in json.loads(static_bytes)['records']}
    for r in records:
        if r['group'].endswith('dossier'):
            assert native[r['id']] == r['source'], r['tag']
    lua = (payload / 'Mods/city_load.lua').read_bytes()
    lua_source = next(s for s in source['sources'] if s['asset'] == 'Mods/city_load.lua')
    assert hashlib.sha256(lua).hexdigest() == lua_source['sha256'], 'loading Lua was modified'
    block = re.search(r'LOADING_SCREEN_TIPS\s*=\s*\{(.*?)\}', lua.decode('utf8'), re.S)[1]
    tips = re.findall(r'"([^"\r\n]+)"', block)
    assert len(tips) == 46
    assert set(tips) == {r['tag'] for r in records if r['group'] == 'loading-tip'}
    assert max(len(r['text']) for r in records if r['group'] == 'loading-tip') <= 30
    # Native parser regression: commas in section headers are flags, whereas
    # quoted entries preserve the complete loading-tip lookup key.
    money = 'Money buys gear, weapons and property'
    assert parse('[' + money + ']\r\nx\r\n')[0]['tag'] == 'Money buys gear'
    assert parse(render(money, 'x'))[0]['tag'] == money
    assert parse('[TEST, gamepad]\r\nx\r\n')[0]['pad'] is True
    assert all(r['tag'].startswith('SR2CN_') for r in records if r['group'] in ('hitman-name', 'vehicle-name'))
    assert not set(source['retiredTags']) & actual.keys(), 'raw-name aliases would break native name comparisons'
    info = json.loads((ROOT / 'localization/text/info-pages.json').read_text('utf8'))
    assert Counter(r['group'] for r in info['records']) == {'statistics': 16, 'achievement-name': 6, 'achievement-description': 37}
    stat_keys = set(re.findall(r'<DisplayName>(SUI_STAT_[A-Z0-9_]+)</DisplayName>', (payload / 'Mods/stats.xtbl').read_text('utf8')))
    assert stat_keys == {r['tag'] for r in info['records'] if r['group'] == 'statistics'}
    for r in info['records']:
        assert actual.get(r['tag']) == r['text'], r['tag']
        assert r['id'] == f"0x{tag_hash(r['tag']):08X}", r['tag']
        assert not {c for c in r['text'] if ord(c) >= 256 and ord(c) not in chars}, r['tag']
    assert actual['SUI_STAT_PERCENT_COMPLETE'].count('%%') == 1
    menu = (payload / 'Mods/pause_menu.lua').read_bytes().decode('ascii')
    assert hashlib.sha256(strip_lua(menu).encode('ascii')).hexdigest() == info['pauseMenuBaselineSha256'], 'unmanaged Lua changes'
    assert menu.count(BOUNDED_STAT_NEW) == 1
    assert menu.count(RACING_NEW) == 1
    race_description = next(r for r in info['records'] if r.get('achievement') == 'ACHIEVE_SR2_QUICK_AND_PISSED')
    assert '27' in race_description['text'] and '28' not in race_description['text']
    assert native[f'0x{tag_hash("STATS_BLANK_OF_BLANK"):08X}'] == '%d / %d'
    assert lua_display_block(records, info) in menu
    for signature, call in CALLS.items():
        assert menu.count(signature + '\r\n' + call + '\r\n') == 1
    for old, new in STAT_ALIASES.items():
        assert 'sui_compare_string(stat_text, "' + new + '")' in menu
    names = set(re.findall(r'achieve_name = "(ACHIEVE_SR2_[A-Z0-9_]+)"', menu))
    names |= set(re.findall(r'pause_menu_achievements_add\("([^"]+)"', menu))
    assert names == {r['achievement'] for r in info['records'] if r['group'] == 'achievement-description'}
    return {'passed': True, 'managedRecords': len(records), 'groups': dict(counts),
            'loadingTipOccurrences': len(tips), 'unsupportedCharacters': [],
            'dossierControlsAndParagraphsPreserved': True, 'loadingLuaUnchanged': True,
            'statistics':len(stat_keys), 'achievementDescriptions':len(names),
            'pauseMenuChangesRestrictedToManagedEdits':True, 'nativeProgressFormatMatched':True,
            'commaHeaderRegressionPassed':True,
            'runtime': 'tracked separately in the installation/runtime evidence'}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
