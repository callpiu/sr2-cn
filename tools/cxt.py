"""The subset of Juiced MStrings.cpp CXT syntax used by this project.

Quoted entries use `"TAG" value`, without quotes around the value. Unlike
section bodies, their values unescape backslash sequences and can therefore
preserve consecutive newlines in native dossiers.
"""
import re
import zlib

HEADER = re.compile(r'^\[([^\[\]]+)\]$')
QUOTED = re.compile(r'^"((?:[^"\\]|\\.)+)"[ \t]+(.+)$')
ESCAPES = {'n': '\n', 'r': '\r', 't': '\t', '\\': '\\', '"': '"'}


def unescape(text):
    return re.sub(r'\\(.)', lambda m: ESCAPES.get(m[1], '\\' + m[1]), text)


def escape(text):
    return text.replace('\\', '\\\\').replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t').replace('"', '\\"')


def tag_hash(tag):
    if re.fullmatch(r'0[xX][0-9a-fA-F]{1,8}', tag):
        return int(tag, 16)
    return zlib.crc32(tag.lower().encode('utf8'), 0xffffffff) ^ 0xffffffff


def parse(text):
    """Return entries and their character spans, including trailing blank lines."""
    result = []
    current = None
    offset = 0
    for line in text.splitlines(keepends=True):
        trimmed = line.strip()
        section = HEADER.fullmatch(trimmed)
        if section and section[1].lower() in ('format', '/format'):
            section = None
        inline = QUOTED.fullmatch(trimmed)
        if section or inline:
            if current is not None:
                current['end'] = offset
            if section:
                # MStrings::ParseTagHeader treats comma-separated suffixes as
                # controller flags, not part of the tag. Quoted tags bypass it.
                parts = [part.strip() for part in section[1].split(',')]
                current = {'tag': parts[0], 'pad': any(p.lower() in ('pad', 'gamepad', 'controller') for p in parts[1:]),
                           'lines': [], 'start': offset, 'kind': 'section'}
            else:
                current = {'tag': unescape(inline[1]).strip(), 'lines': [unescape(inline[2])], 'start': offset, 'kind': 'quoted'}
            result.append(current)
        elif trimmed:
            assert current is not None and current['kind'] == 'section', 'CXT text without a section'
            current['lines'].append(line.rstrip('\r\n'))
        offset += len(line)
    if current is not None:
        current['end'] = len(text)
    for item in result:
        item['text'] = '\n'.join(item.pop('lines'))
    return result


def render(tag, text):
    if '\n' in text or '\r' in text or ',' in tag:
        return '"' + escape(tag) + '" ' + escape(text) + '\r\n\r\n'
    return '[' + tag + ']\r\n' + text + '\r\n\r\n'
