"""Build and verify the three scoped garage/court CXT corrections."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

from cxt import parse, render, tag_hash
from vpp import LightVpp

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / 'localization/payload'
SOURCE = ROOT / 'localization/text/court-garage.json'


def records():
    return json.loads(SOURCE.read_text('utf8'))['records']


def read_table(data):
    magic, version, buckets, count = struct.unpack_from('<IHHI', data)
    assert magic == 0xA84C7F73 and version == 1
    result = {}
    for offset in struct.unpack_from(f'<{count}I', data, 12 + buckets * 8):
        identifier = struct.unpack_from('>I', data, offset)[0]
        end = offset + 4
        while data[end:end+2] != b'\0\0':
            assert end < len(data), 'unterminated source string'
            end += 2
        result[identifier] = data[offset+4:end].decode('utf-16-be')
    return result


def verify(payload=None):
    payload = payload or PAYLOAD
    rows = records()
    assert len(rows) == len({r['id'] for r in rows}) == 3
    chars = set(json.loads((ROOT / 'localization/text/charlist_CH.json').read_text('utf8')))
    tables = {'Mods/static_US.le_strings': read_table((PAYLOAD / 'Mods/static_US.le_strings').read_bytes())}
    with LightVpp(str(PAYLOAD / 'patch.vpp_pc')) as archive:
        entry = next(e for e in archive.entries() if archive.name(e) == 'voice_script_US')
        english = archive.read(entry)
        assert hashlib.sha256(english).hexdigest() == '90e7481a53721a0edfbf12aaa8fa01f1b5fe3d19f25e5f2a5711662c308cf479'
        tables['patch.vpp_pc/voice_script_US.le_strings'] = read_table(english)
    for output in {r['output'] for r in rows}:
        data = (payload / output).read_bytes()
        assert not data.startswith(b'\xef\xbb\xbf')
        assert data.count(b'\r\n') == data.count(b'\n') and data.endswith(b'\r\n')
        actual = parse(data.decode('utf8'))
        expected = [r for r in rows if r['output'] == output]
        assert [(r['tag'], r['text']) for r in actual] == [(r['tag'], r['text']) for r in expected]
    for row in rows:
        identifier = int(row['id'], 16)
        assert tag_hash(row['tag']) == identifier
        assert tables[row['asset']][identifier] == row['source'], row['tag']
        assert row['source'].count('\n') == row['text'].count('\n'), row['tag']
        assert not {c for c in row['text'] if ord(c) >= 256 and ord(c) not in chars}, row['tag']
    # The warning is needed only by the special reward-vehicle branch.
    garage = (payload / 'Mods/garage.lua').read_text('utf8')
    assert '"SUI_DELETE_REWARD_VEHICLE_WARNING", "garage_remove_confirm"' in garage
    base = json.loads((ROOT / 'localization/text/static_CH.json').read_text('utf8'))
    known = {int(r['id'], 16) for r in base['records']}
    for path in (payload / 'Mods/JUICED - Strings').glob('*CH.cxt'):
        if not path.name.lower().endswith('_vcch.cxt'):
            known.update(tag_hash(r['tag']) for r in parse(path.read_bytes().decode('utf8')))
    required = set(re.findall(r'"(SUI_[A-Z0-9_]+)"', garage))
    assert all(tag_hash(tag) in known for tag in required), 'missing garage SUI strings'
    return dict(passed=True, records=3, garageSuiTagsChecked=len(required), glyphCoverage=True,
                originalEnglishMatched=True, warningLineBreaksPreserved=True)


def build():
    rows = records()
    manifest_path = ROOT / 'localization/manifest.json'
    manifest = json.loads(manifest_path.read_text('utf8'))
    for output in sorted({r['output'] for r in rows}):
        data = ''.join(render(r['tag'], r['text']) for r in rows if r['output'] == output).encode('utf8')
        (PAYLOAD / output).write_bytes(data)
        info = dict(path=output, bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        existing = next((r for r in manifest['payload'] if r['path'] == output), None)
        if existing is None:
            manifest['payload'].append(info)
        else:
            existing.update(info)
    manifest['payload'].sort(key=lambda r:r['path'])
    manifest['localRevision'] = '2026-10-26-store-places-court-garage'
    manifest_path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    if args.build:
        build()
    print(json.dumps(verify(), indent=2))
