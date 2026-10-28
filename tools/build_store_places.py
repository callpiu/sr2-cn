"""Append native-ID place/store overlays without changing earlier CXT entries."""
import hashlib
import json
from pathlib import Path

from cxt import parse, render, tag_hash

ROOT = Path(__file__).resolve().parents[1]
RELATIVE = 'Mods/JUICED - Strings/juiced_CH.cxt'


def main():
    source = json.loads((ROOT / 'localization/text/store-places.json').read_text('utf8'))
    records = source['records']
    ids = {int(r['id'], 16) for r in records}
    assert len(ids) == len(records)
    path = ROOT / 'localization/payload' / RELATIVE
    text = path.read_bytes().decode('utf8')
    for entry in reversed(parse(text)):
        if tag_hash(entry['tag']) in ids:
            assert entry['tag'] in {r['tag'] for r in records}, 'unmanaged ID collision'
            text = text[:entry['start']] + text[entry['end']:]
    baseline = (text.rstrip('\r\n') + '\r\n').encode('utf8')
    assert hashlib.sha256(baseline).hexdigest() == source['priorCxtSha256'], 'prior CXT changed'
    generated = ''.join(render(r['tag'], r['text']) for r in records)
    output = baseline + b'\r\n' + generated.rstrip('\r\n').encode('utf8') + b'\r\n'
    path.write_bytes(output)
    manifest_path = ROOT / 'localization/manifest.json'
    manifest = json.loads(manifest_path.read_text('utf8'))
    item = next(r for r in manifest['payload'] if r['path'] == RELATIVE)
    item.update(bytes=len(output), sha256=hashlib.sha256(output).hexdigest())
    manifest['localRevision'] = '2026-10-26-store-place-prompts'
    manifest_path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps(dict(managed=len(records), retained=len(parse(baseline.decode('utf8'))), **item)))


if __name__ == '__main__':
    main()
