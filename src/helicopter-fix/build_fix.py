"""Build the tested SR2 Chinese Helicopter Escort lookup fix. Python 3 stdlib only.

Usage: python build_fix.py ORIGINAL_EXE NEW_OUTPUT_EXE
Never overwrites either input or an existing output. This is a builder, not an installer.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

ORIGINAL_SHA256 = '7d119931c7356a534f7a1b903dd6f920e417249d128438e939edb35b0dc2f244'
PATCHES = (
    (0x3F4C38, bytes.fromhex('5fb8d05ee2005ec3'), bytes.fromhex('e9abffffff909090')),
    (0x3F4C48, bytes.fromhex('5fb8785ee2005ec3'), bytes.fromhex('e99bffffff909090')),
)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def build(original):
    if sha(original) != ORIGINAL_SHA256:
        raise ValueError('Unsupported executable SHA-256. No output written.')
    result = bytearray(original)
    for offset, before, after in PATCHES:
        assert result[offset:offset+len(before)] == before
        result[offset:offset+len(before)] = after
    assert len(result) == len(original)
    changed = [i for i, (a, b) in enumerate(zip(original, result)) if a != b]
    assert changed == [i for offset, _, new in PATCHES for i in range(offset, offset+len(new))]
    return bytes(result)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    source, output = map(Path, sys.argv[1:])
    data = source.read_bytes()
    patched = build(data)
    with output.open('xb') as file:
        file.write(patched)
    print(json.dumps({'source_sha256': sha(data), 'output_sha256': sha(patched),
                      'output_bytes': len(patched), 'changed_bytes': 16,
                      'output': str(output.resolve())}, indent=2))
