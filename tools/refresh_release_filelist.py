"""Prepare a release tree and refresh its complete SHA-256 file list."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile

from build_release import copy_tree, digest


ROOT = Path(__file__).resolve().parents[1]


def header():
    manifest = json.loads(
        (ROOT / 'localization/manifest.json').read_text('utf8'))
    return (
        f'SR2 整合包 {manifest["version"]} / {manifest["date"]} '
        'Juiced 9.3.2 中文合并版\r\n'
        'SHA-256  bytes  relative-path（不含 FILELIST.txt 自身）\r\n\r\n')


def extract_base(base, target):
    with zipfile.ZipFile(base) as zipped:
        seen = set()
        for info in zipped.infolist():
            member = PurePosixPath(info.filename.replace('\\', '/'))
            if (member.is_absolute() or '..' in member.parts or
                    ':' in str(member) or
                    stat.S_ISLNK(info.external_attr >> 16) or
                    str(member).lower() in seen):
                raise ValueError(f'Unsafe or duplicate ZIP member: {member}')
            seen.add(str(member).lower())
            if not info.is_dir():
                output = target.joinpath(*member.parts)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(zipped.read(info))


def render_filelist(folder):
    lines = [header()]
    for path in sorted(folder.rglob('*')):
        if not path.is_file() or path.name == 'FILELIST.txt':
            continue
        relative = path.relative_to(folder).as_posix()
        lines.append(
            f'{digest(path)}  {path.stat().st_size:>12}  {relative}\r\n')
    return ''.join(lines).encode('utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; choose a new directory')
    args.output.mkdir(parents=True)
    extract_base(args.base, args.output)
    copy_tree(ROOT / 'localization/payload', args.output)
    copy_tree(ROOT / 'packaging/integration-overlay', args.output)
    filelist = render_filelist(args.output)
    (args.output / 'FILELIST.txt').write_bytes(filelist)
    overlay_filelist = ROOT / 'packaging/integration-overlay/FILELIST.txt'
    overlay_filelist.write_bytes(filelist)
    print(f'{len(filelist.splitlines()) - 3} files; {hashlib.sha256(filelist).hexdigest()}')


if __name__ == '__main__':
    main()
