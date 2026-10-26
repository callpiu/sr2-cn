"""Check menu CXT structure and glyph coverage against the shipped SR2 charlist."""
import json
from pathlib import Path
import re
from cxt import parse

ROOT = Path(__file__).resolve().parents[1]
RELATIVE = Path('Mods/JUICED - Strings/juiced_CH.cxt')


def verify(payload=None):
    payload = payload or ROOT / 'localization/payload'
    data = (payload / RELATIVE).read_bytes()
    assert not data.startswith(b'\xef\xbb\xbf'), 'CXT must not have a BOM'
    assert data.endswith(b'\r\n'), 'CXT must end with CRLF'
    assert data.count(b'\n') == data.count(b'\r\n'), 'CXT requires CRLF'
    parsed = parse(data.decode('utf8'))
    entries = {r['tag']: r['text'] for r in parsed}
    assert len(entries) == len(parsed), 'duplicate CXT tag'
    characters = set(json.loads((ROOT / 'localization/text/charlist_CH.json').read_text('utf8')))
    missing = {k: ''.join(sorted({c for c in v if ord(c) >= 256 and ord(c) not in characters}))
               for k, v in entries.items()}
    missing = {k: v for k, v in missing.items() if v}
    assert not missing, ('unsupported menu glyphs', missing)
    assert entries['MP_SERVER_IP'] == '', 'keep original empty server IP value'
    for key in ['Profile', 'Settings', 'Credits', 'SuperUI',
                'Display & Audio Options', 'Control Options', 'Uncap FPS',
                'DynamicRenderDistance', 'Mouse Weapon Wheel',
                'J_FOVMULT', 'J_MOUSEFOV', 'J_FINEAIMONLY']:
        assert entries.get(key), ('missing menu translation', key)
    assert entries['J_UNCFPS'] == entries['Uncap FPS']
    assert entries['J_UNCFPS'] != entries['J_VFXPLUS'], 'FPS and lighting are different options'
    help_source = json.loads((ROOT / 'localization/text/superui-help.json').read_text('utf8'))
    help_keys = set(re.findall(r'SUI_[A-Z0-9_]+',
                    (payload / 'Mods/help_screens.xtbl').read_text('utf8')))
    assert help_keys == {r['tag'] for r in help_source['records']}
    command_count = 0
    for record in help_source['records']:
        tag, source, text = record['tag'], record['source'], record['text']
        assert entries.get(tag) == text, ('help export differs from CXT', tag)
        codes = re.findall(r'^\d{3} - ', source, re.M)
        assert codes == re.findall(r'^\d{3} - ', text, re.M), ('command code drift', tag)
        assert re.findall(r'\{[^{}]+\}', source) == re.findall(r'\{[^{}]+\}', text), tag
        assert re.findall(r'https?://\S+', source) == re.findall(r'https?://\S+', text), tag
        command_count += len(codes)
    return {'passed': True, 'entries': len(entries), 'unsupportedCharacters': missing,
            'superuiHelpEntries': len(help_keys), 'sandboxCommandCodes': command_count}


if __name__ == '__main__':
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
