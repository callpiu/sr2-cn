"""Verify frozen localization bytes, readable text exports and CXT controls."""
import hashlib
import json
from pathlib import Path
import re
import struct

import cxt as cxt_tool
from vpp import LightVpp
from verify_superui import verify as verify_superui
from verify_menu_strings import verify as verify_menu_strings
from verify_list_tips import verify as verify_list_tips
from verify_store_places import verify as verify_store_places
from court_garage_strings import verify as verify_court_garage
from build_subtitle_places import build as build_subtitle_places

ROOT = Path(__file__).resolve().parents[1]


def check_juiced_932(payload):
    metadata = json.loads(
        (ROOT / 'localization/text/juiced-932-additions.json').read_text('utf8'))
    assert metadata['upstreamVersion'] == '9.3.2'
    assert metadata['upstreamSha256'] == (
        'd5b3436122cf7fd602be7719ddc79bcd24655a0e4f0e2ad630b196b31d1bc7f')

    path = payload / 'Mods/JUICED - Strings/juiced_CH.cxt'
    data = path.read_bytes()
    assert not data.startswith(b'\xef\xbb\xbf')
    assert data.count(b'\r\n') == data.count(b'\n')
    assert data.endswith(b'\r\n')
    assert b'\n' not in data.replace(b'\r\n', b'')
    entries = cxt_tool.parse(data.decode('utf8'))
    assert len(entries) == metadata['mergedEntryCount'] == 412
    by_tag = {entry['tag'].lower(): entry['text'] for entry in entries}
    for addition in metadata['additions']:
        tag = addition['tag'].lower()
        assert by_tag[tag] == addition['text'], tag
        assert cxt_tool.tag_hash(addition['tag']) == int(
            addition['runtimeId'], 16), tag

    additions = [entry['text'] for entry in metadata['additions']]
    assert sum('[format]' in text for text in additions) == 2
    assert sum('[/format]' in text for text in additions) == 2
    assert sum('{ATTACK_SECONDARY_IMG}' in text for text in additions) == 1
    assert sum('{ATTACK_PRIMARY_IMG}' in text for text in additions) == 1
    assert not (payload / 'DFEngine.pdb').exists()
    return len(entries)


def check_table(data, name, characters):
    exported = json.loads((ROOT / 'localization/text' / (name + '.json')).read_text('utf8'))
    assert hashlib.sha256(data).hexdigest() == exported['sourceSha256'], name
    magic, version, buckets, count = struct.unpack_from('<IHHI', data)
    assert magic == 0xA84C7F73 and version == 1, name
    assert len(exported['records']) == count, name
    ptr_start = 12 + buckets * 8
    pointers = struct.unpack_from(f'<{count}I', data, ptr_start)
    assert sum(struct.unpack_from('<I', data, 12 + i * 8)[0]
               for i in range(buckets)) == count, name
    for index, offset in enumerate(pointers):
        assert ptr_start + count * 4 <= offset < len(data) - 4, (name, index)
        identifier = struct.unpack_from('>I', data, offset)[0]
        units = []
        position = offset + 4
        while True:
            unit = struct.unpack_from('>H', data, position)[0]
            position += 2
            if unit == 0:
                break
            units.append(unit)
        assert all(u < len(characters) + 32 for u in units), (name, index)
        text = ''.join(chr(u) if u < 32 else chr(characters[u - 32]) for u in units)
        assert exported['records'][index] == {
            'index': index, 'id': f'0x{identifier:08X}', 'text': text}, (name, index)
    return count


def main():
    payload = ROOT / 'localization/payload'
    manifest = json.loads((ROOT / 'localization/manifest.json').read_text('utf8'))
    assert manifest['version'] == 'v553'
    assert manifest['combinedArchiveName'] == (
        'sr2-cn-v553-juiced-9.3.2-dlc-1.0.1-superui-2.9.zip')
    for item in manifest['payload']:
        data = (payload / item['path']).read_bytes()
        assert len(data) == item['bytes'], item['path']
        assert hashlib.sha256(data).hexdigest() == item['sha256'], item['path']
    juiced_932 = check_juiced_932(payload)
    characters = json.loads((ROOT / 'localization/text/charlist_CH.json').read_text('utf8'))
    totals = {}
    with LightVpp(str(payload / 'patch.vpp_pc')) as vpp:
        for entry in vpp.entries():
            name = vpp.name(entry)
            if name.lower().endswith('_ch') and vpp.ext(entry).lower() == 'le_strings':
                totals[name] = check_table(vpp.read(entry), name, characters)
        char_entry = next(e for e in vpp.entries() if vpp.name(e).lower() == 'charlist_ch')
        actual_characters = [int(line) for line in vpp.read(char_entry).decode('utf8').splitlines()
                             if line.strip().isdigit()]
        assert actual_characters == characters
    for name, relative in [('dlc_ch', 'DLC/Text/dlc_ch.le_strings'),
                           ('juiced_CH', 'Mods/JUICED - Strings/juiced_CH.le_strings')]:
        totals[name] = check_table((payload / relative).read_bytes(), name, characters)
    cxt = (ROOT / 'upstream/juiced_CH.hardcoded-fixes.cxt').read_bytes()
    assert not cxt.startswith(b'\xef\xbb\xbf')
    assert cxt.count(b'\r\n') == cxt.count(b'\n') and cxt.endswith(b'\r\n')
    text = cxt.decode('utf8')
    ids = re.findall(r'^\[(0x[0-9A-F]{8})\]\r?$', text, re.M)
    assert ids == ['0xFF6299D9', '0x2370E5A4', '0xAF10621E',
                   '0xF284ED87', '0xAB55CE3B', '0x42363FC7']
    assert text.count('[format]') == text.count('[/format]') == 2
    assert text.count('{ATTACK_SECONDARY_IMG}') == text.count('{ATTACK_PRIMARY_IMG}') == 1
    blocks = re.split(r'^\[0x[0-9A-F]{8}\]\r?\n', text, flags=re.M)[1:]
    assert len(blocks[0].strip().splitlines()) == len(blocks[1].strip().splitlines()) == 2
    indexes = json.loads((ROOT / 'localization/text/index.json').read_text('utf8'))
    assert totals == indexes
    superui = verify_superui(payload)
    menu_strings = verify_menu_strings(payload)
    list_tips = verify_list_tips(payload)
    store_places = verify_store_places(payload)
    court_garage = verify_court_garage(payload)
    subtitle_places = build_subtitle_places()
    for relative, expected in subtitle_places.items():
        assert (payload / relative).read_bytes() == expected, relative
    print(json.dumps({'passed': True, 'payload_files': len(manifest['payload']),
                      'text_tables': totals, 'total_records': sum(totals.values()),
                      'hardcoded_fix_entries': len(ids),
                      'juiced_932_cxt_entries': juiced_932, 'superui': superui,
                      'menu_strings': menu_strings,
                      'list_tips': list_tips,
                      'store_places': store_places,
                      'court_garage': court_garage,
                      'subtitle_place_files': len(subtitle_places)},
                     ensure_ascii=True, indent=2))


if __name__ == '__main__':
    main()
