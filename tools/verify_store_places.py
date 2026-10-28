"""Verify exact native lookup IDs, unchanged prior overlays, controls and glyphs."""
import hashlib
import json
from pathlib import Path
import re

from cxt import parse, tag_hash
from build_store_places import RELATIVE

ROOT = Path(__file__).resolve().parents[1]
CONTROL = re.compile(r'\{[^{}]+\}|\[[^\]]+\]|%%|%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?(?:l[sd]|[sdfiu])|\n')


def verify(payload=None):
    payload = payload or ROOT / 'localization/payload'
    source = json.loads((ROOT / 'localization/text/store-places.json').read_text('utf8'))
    records = source['records']
    native_bytes = (ROOT / source['sourceAsset']).read_bytes()
    assert hashlib.sha256(native_bytes).hexdigest() == source['sourceSha256']
    native = json.loads(native_bytes)['records']
    data = (payload / RELATIVE).read_bytes()
    assert not data.startswith(b'\xef\xbb\xbf')
    assert data.count(b'\n') == data.count(b'\r\n') and data.endswith(b'\r\n')
    entries = parse(data.decode('utf8'))
    actual = {tag_hash(r['tag']):r['text'] for r in entries}
    assert len(actual) == len(entries), 'duplicate CXT ID'
    ids = {int(r['id'],16) for r in records}
    assert len(ids) == len(records) == 61
    chars = set(json.loads((ROOT / 'localization/text/charlist_CH.json').read_text('utf8')))
    for r in records:
        original = native[r['sourceIndex']]
        assert original['id'] == r['id'] and original['text'] == r['source'], r['id']
        assert tag_hash(r['tag']) == int(r['id'],16), r['tag']
        assert actual.get(int(r['id'],16)) == r['text'], ('missing or stale place/store entry', r['id'])
        assert CONTROL.findall(r['source']) == CONTROL.findall(r['text']), ('control drift',r['id'])
        assert not {c for c in r['text'] if ord(c)>=256 and ord(c) not in chars}, r['id']
    # The entire v550 CXT prefix remains byte-identical.
    first = next(e for e in entries if tag_hash(e['tag']) in ids)
    prior = (data.decode('utf8')[:first['start']].rstrip('\r\n')+'\r\n').encode('utf8')
    assert hashlib.sha256(prior).hexdigest() == source['priorCxtSha256'], 'earlier translations changed'
    assert len(parse(prior.decode('utf8'))) == 345
    assert actual[0x46E5FEA4] == '在[format][color:teal]捡破鞋[/format]买几件新衣服'
    assert actual[0xDFECAF1E] == '前往[format][color:teal]蒂妮酒吧[/format]'
    assert actual[0x09694999] == '蒂妮酒吧'
    return dict(passed=True, records=len(records), unchangedPriorEntries=345,
                entries=len(entries), glyphCoverage=True, controlsPreserved=True)


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2))
