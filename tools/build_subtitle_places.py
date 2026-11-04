"""Build the place-name overlays for Juiced's voice and general tables."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

from cxt import parse, render, tag_hash
from verify_store_places import CONTROL

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / 'localization/payload'
MODS = Path('Mods/JUICED - Strings')
RULES = ROOT / 'localization/text/subtitle-places.json'


def build():
    spec = json.loads(RULES.read_text('utf8'))
    charlist = set(json.loads((ROOT / 'localization/text/charlist_CH.json').read_text('utf8')))
    paths = {'voice_script_CH': 'sr2cn_subtitle_places_vcCH.cxt',
             'static_CH': 'sr2cn_subtitle_places_CH.cxt'}
    existing = {}
    generated_names = set(paths.values())
    for path in (PAYLOAD / MODS).glob('*CH.cxt'):
        if path.name in generated_names:
            continue
        for entry in parse(path.read_bytes().decode('utf8')):
            existing[tag_hash(entry['tag'])] = path.name
    result = {}
    for table, file in paths.items():
        raw = (ROOT / 'localization/text' / (table + '.json')).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == spec[table]['exportSha256']
        rules = spec[table]['replacements']
        pattern = re.compile(r'(?<![A-Za-z])(?:' + '|'.join(
            re.escape(s) for s in sorted(rules, key=len, reverse=True)) + r')(?![A-Za-z])')
        entries = {}
        for row in json.loads(raw)['records']:
            before = row['text']
            after = pattern.sub(lambda match: rules[match[0]], before)
            if before == after:
                continue
            tag = row['id']
            identifier = int(tag, 16)
            assert identifier not in existing and tag not in entries, (table, tag)
            assert CONTROL.findall(before) == CONTROL.findall(after), tag
            assert re.search(r'(?:\n\d+)?\Z', before)[0] == re.search(r'(?:\n\d+)?\Z', after)[0]
            assert all(ord(ch) < 256 or ord(ch) in charlist for ch in after), tag
            entries[tag] = after
        assert list(entries) == spec[table]['ids'], table
        # Use literal body lines so the timed subtitles keep the engine's
        # original newline and trailing duration exactly.
        content = ''.join(
            f'[{tag}]\r\n' + value.replace('\n', '\r\n') + '\r\n\r\n'
            if table == 'voice_script_CH' else render(tag, value)
            for tag, value in entries.items()).encode('utf8')
        assert [(r['tag'], r['text']) for r in parse(content.decode('utf8'))] == list(entries.items())
        result[(MODS / file).as_posix()] = content
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--archive', type=Path)
    args = parser.parse_args()
    outputs = build()
    for relative, content in outputs.items():
        path = PAYLOAD / relative
        if args.build:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        assert path.read_bytes() == content, relative
    if args.build:
        manifest_path = ROOT / 'localization/manifest.json'
        manifest = json.loads(manifest_path.read_text('utf8'))
        for relative, content in outputs.items():
            info = dict(path=relative, bytes=len(content),
                        sha256=hashlib.sha256(content).hexdigest())
            existing = next(
                (item for item in manifest['payload'] if item['path'] == info['path']),
                None)
            if existing is None:
                manifest['payload'].append(info)
            else:
                existing.update(info)
        manifest['payload'].sort(key=lambda item: item['path'])
        manifest['localRevision'] = '2026-11-04-juiced-932-subtitle-places'
        manifest_path.write_bytes(
            (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    if args.archive:
        with zipfile.ZipFile(args.archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
            for relative in sorted(outputs):
                info = zipfile.ZipInfo(relative, (2026, 11, 4, 0, 0, 0))
                z.writestr(info, outputs[relative], compress_type=zipfile.ZIP_DEFLATED)
        with zipfile.ZipFile(args.archive) as z:
            assert z.testzip() is None and set(z.namelist()) == set(outputs)
            assert all(z.read(p) == b for p, b in outputs.items())
    print(json.dumps({p: dict(entries=len(parse(b.decode('utf8'))),
                             sha256=hashlib.sha256(b).hexdigest()) for p, b in outputs.items()}))


if __name__ == '__main__':
    main()
