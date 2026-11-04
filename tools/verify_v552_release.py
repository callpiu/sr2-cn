"""Verify a built v552 archive against the committed manifests."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

import cxt
from build_subtitle_places import build as build_subtitle_places

ROOT = Path(__file__).resolve().parents[1]
FILELIST_LINE = re.compile(r'^([0-9a-f]{64})\s+(\d+)\s{2}(.+)$')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--rebuilt', type=Path)
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()

    archive_data = args.archive.read_bytes()
    archive_hash = sha256(archive_data)
    with zipfile.ZipFile(args.archive) as zipped:
        names = zipped.namelist()
        assert len(names) == len(set(names))
        assert zipped.testzip() is None
        forbidden = [
            name for name in names
            if name.lower().endswith(
                ('sr2_pc.exe', '.bbsave', '.dmp', '.log', '.pdb'))
        ]
        assert not forbidden, forbidden

        payload_manifest = json.loads(
            (ROOT / 'localization/manifest.json').read_text('utf8'))
        payload_checked = 0
        for item in payload_manifest['payload']:
            data = zipped.read(item['path'])
            assert len(data) == item['bytes'], item['path']
            assert sha256(data) == item['sha256'], item['path']
            payload_checked += 1

        package_manifest = json.loads(
            zipped.read('patch/package-manifest.json').decode('utf8'))
        package_checked = 0
        for item in package_manifest['files']:
            data = zipped.read(item['relative'])
            assert len(data) == item['size'], item['relative']
            assert sha256(data) == item['sha256'], item['relative']
            package_checked += 1

        filelist_lines = zipped.read('FILELIST.txt').decode('utf8').splitlines()
        listed = {}
        for line in filelist_lines[3:]:
            match = FILELIST_LINE.fullmatch(line)
            assert match, line
            digest, size, relative = match.groups()
            listed[relative] = (int(size), digest)
        expected = {name for name in names if name != 'FILELIST.txt'}
        assert set(listed) == expected, {
            'missing': sorted(expected - set(listed)),
            'extra': sorted(set(listed) - expected),
        }
        for relative, (size, digest) in listed.items():
            data = zipped.read(relative)
            assert len(data) == size, relative
            assert sha256(data) == digest, relative

        cxt_data = zipped.read('Mods/JUICED - Strings/juiced_CH.cxt')
        assert not cxt_data.startswith(b'\xef\xbb\xbf')
        assert cxt_data.count(b'\r\n') == cxt_data.count(b'\n')
        assert b'\n' not in cxt_data.replace(b'\r\n', b'')
        entries = cxt.parse(cxt_data.decode('utf8'))
        assert len(entries) == 412
        additions = json.loads(
            (ROOT / 'localization/text/juiced-932-additions.json').read_text('utf8'))
        by_tag = {entry['tag'].lower(): entry['text'] for entry in entries}
        for item in additions['additions']:
            assert by_tag[item['tag'].lower()] == item['text'], item['tag']

        subtitle_places = build_subtitle_places()
        subtitle_entries = 0
        for relative, expected in subtitle_places.items():
            data = zipped.read(relative)
            assert data == expected, relative
            subtitle_entries += len(cxt.parse(data.decode('utf8')))

        assert zipped.read('README.md') == zipped.read('_先读我.txt')
        for required in (
                'DFEngine.dll',
                'juiced.ini',
                'Mods/JUICED - Lua Libraries/mouse_ui.lua',
                'Mods/JUICED - Strings/sr2cn_court_vcCH.cxt',
                'Mods/JUICED - Strings/sr2cn_garage_CH.cxt',
                'Mods/JUICED - Strings/sr2cn_subtitle_places_vcCH.cxt',
                'Mods/JUICED - Strings/sr2cn_subtitle_places_CH.cxt'):
            assert required in names, required

    rebuilt_hash = None
    if args.rebuilt:
        rebuilt_hash = sha256(args.rebuilt.read_bytes())
        assert rebuilt_hash == archive_hash

    report = {
        'schema': 'sr2-cn/v552-release-verification/v1',
        'archive': args.archive.name,
        'bytes': len(archive_data),
        'sha256': archive_hash,
        'rebuiltSha256': rebuilt_hash,
        'reproducible': rebuilt_hash == archive_hash,
        'zipMembers': len(names),
        'payloadFiles': payload_checked,
        'packageManifestFiles': package_checked,
        'filelistEntries': len(listed),
        'juicedCxtEntries': len(entries),
        'hardcodedFixEntries': len(additions['additions']),
        'subtitlePlaceFiles': len(subtitle_places),
        'subtitlePlaceEntries': subtitle_entries,
        'readmeMatchesQuickStart': True,
        'forbiddenFiles': forbidden,
        'passed': True,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.json:
        args.json.write_text(text, encoding='utf8')
    print(text, end='')


if __name__ == '__main__':
    main()
