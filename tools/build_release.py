"""Rebuild the frozen release without reading or modifying a game install."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as file:
        for block in iter(lambda: file.read(4 * 1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def copy_tree(source, target):
    for file in sorted(source.rglob('*')):
        if file.is_file():
            output = target / file.relative_to(source)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, output)


def archive(folder, output):
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as zipped:
        for file in sorted(folder.rglob('*')):
            if not file.is_file():
                continue
            info = zipfile.ZipInfo(file.relative_to(folder).as_posix(),
                                   (2026, 10, 23, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with file.open('rb') as source, zipped.open(
                    info, 'w', force_zip64=True) as target:
                shutil.copyfileobj(source, target, 4 * 1024 * 1024)
    with zipfile.ZipFile(output) as zipped:
        assert zipped.testzip() is None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path,
                        help='Frozen 2026-10-21 v546 integration ZIP')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist',
                        help='New, nonexistent output directory')
    parser.add_argument('--accept-new-asset', action='store_true',
                        help='Allow an archive name absent from release-assets.json')
    args = parser.parse_args()
    config = json.loads((ROOT / 'localization/manifest.json').read_text('utf8'))
    if args.base and digest(args.base) != config['baseArchiveSha256']:
        parser.error('Unsupported base ZIP SHA-256; nothing written')
    if args.output.exists():
        parser.error('Output already exists; choose a new directory')
    args.output.mkdir(parents=True)
    standalone = args.output / 'standalone'
    standalone.mkdir()
    copy_tree(ROOT / 'installer', standalone)
    name = 'sr2-cn-helicopter-fix-v1.0.0.zip'
    archive(standalone, args.output / name)
    results = {name: digest(args.output / name)}
    if args.base:
        combined = args.output / 'combined'
        combined.mkdir()
        with zipfile.ZipFile(args.base) as zipped:
            seen = set()
            for info in zipped.infolist():
                member = PurePosixPath(info.filename.replace('\\', '/'))
                if (member.is_absolute() or '..' in member.parts or
                    ':' in str(member) or stat.S_ISLNK(info.external_attr >> 16) or
                    str(member).lower() in seen):
                    raise ValueError('Unsafe or duplicate ZIP member: ' + str(member))
                seen.add(str(member).lower())
                if not info.is_dir():
                    output = combined.joinpath(*member.parts)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(zipped.read(info))
        copy_tree(ROOT / 'localization/payload', combined)
        copy_tree(ROOT / 'packaging/integration-overlay', combined)
        name = config['combinedArchiveName']
        archive(combined, args.output / name)
        results[name] = digest(args.output / name)
    expected = {a['name']: a['sha256'] for a in json.loads(
        (ROOT / 'packaging/release-assets.json').read_text('utf8'))}
    for name, actual in results.items():
        if name not in expected:
            if not args.accept_new_asset:
                raise ValueError('Archive not in release-assets.json: ' + name)
            continue
        if actual != expected[name]:
            raise ValueError('Rebuilt ZIP differs from frozen release: ' + name)
    (args.output / 'build-result.json').write_text(
        json.dumps(results, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'verified': True, 'sha256': results}, indent=2))


if __name__ == '__main__':
    main()
