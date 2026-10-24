"""Check that the customized SuperUI scripts ship with their complete component."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def verify(directory):
    component = json.loads((ROOT / 'localization/superui-manifest.json').read_text('utf8'))
    problems = []
    sources = []
    for item in component['files']:
        path = directory / item['path']
        if not path.is_file():
            problems.append('Missing: ' + item['path'])
            continue
        data = path.read_bytes()
        if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            problems.append('Different bytes: ' + item['path'])
        if path.suffix == '.lua':
            sources.append(data.decode('utf8'))
    if problems:
        raise ValueError('\n'.join(problems))
    # SuperUI's shared functions are Lua functions, not native game APIs.
    # Check the full component, including the two customized scripts already shipped.
    text = '\n'.join(sources)
    definitions = set(re.findall(r'function\s+(sui_\w+)\s*\(', text))
    calls = set(re.findall(r'\b(sui_\w+)\s*\(', text))
    unresolved = sorted(calls - definitions)
    if unresolved:
        raise ValueError('Unresolved SuperUI functions: ' + ', '.join(unresolved))
    library = (directory / 'Mods/vint_lib.lua').read_text('utf8')
    if not re.search(r'^SUI_VERSION\s*=\s*2\.9\b', library, re.M):
        raise ValueError('Expected the matching SuperUI 2.9 library')
    for function in ['sui_compare_string', 'sui_is_zombie', 'sui_get_human_readable_time_float']:
        if not re.search(r'function\s+' + function + r'\s*\(', library):
            raise ValueError('Missing shared-library function: ' + function)
    return {'files': len(component['files']), 'sharedFunctions': len(definitions)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=ROOT / 'localization/payload')
    args = parser.parse_args()
    try:
        result = verify(args.directory)
    except ValueError as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps({'passed': True, **result}, indent=2))
