"""Standard-library checks for this documentation/model repository.

Checks local Markdown links/anchors, required sections/scenarios/modules, DOI
entries, nonempty files, PNG chunks/CRCs/pixel data, and accidental secrets.
It does not perform hardware verification or network DOI resolution.
"""

from pathlib import Path
import binascii
import re
import struct
import sys
from urllib.parse import unquote
import zlib

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def headings(text):
    anchors, counts = set(), {}
    for title in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        title = re.sub(r'[`*_]', '', title.strip()).lower()
        slug = re.sub(r'[^\w\- ]', '', title).replace(' ', '-')
        duplicate = counts.get(slug, 0)
        counts[slug] = duplicate + 1
        anchors.add(slug if not duplicate else f'{slug}-{duplicate}')
    return anchors


def validate_png(path):
    data = path.read_bytes()
    require(data[:8] == b'\x89PNG\r\n\x1a\n', 'Not a PNG signature')
    offset, compressed, dimensions, ended = 8, bytearray(), None, False
    while offset < len(data):
        require(offset + 12 <= len(data), 'Truncated PNG chunk')
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        require(offset + length + 12 <= len(data), 'Truncated PNG data')
        crc = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
        require((binascii.crc32(kind + body) & 0xffffffff) == crc, 'PNG CRC mismatch')
        if kind == b'IHDR':
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', body)
            require((depth, color, compression, filtering, interlace) == (8, 2, 0, 0, 0),
                    'Expected non-interlaced 8-bit RGB PNG')
            require(width >= 1600 and height >= 1000, 'Diagram resolution is too small')
            dimensions = (width, height)
        elif kind == b'IDAT':
            compressed.extend(body)
        elif kind == b'IEND':
            ended = True
            break
        offset += length + 12
    require(ended and dimensions, 'PNG missing required chunks')
    pixels = zlib.decompress(compressed)
    width, height = dimensions
    require(len(pixels) == height * (1 + width * 3), 'PNG pixel data size mismatch')
    require(all(pixels[y * (1 + width * 3)] <= 4 for y in range(height)), 'Invalid PNG row filter')
    return dimensions


def main():
    required = [
        'README.md', '.gitignore', 'docs/architecture.md', 'docs/block-diagram.mmd',
        'docs/block-diagram.png', 'docs/verification-plan.md', 'docs/references.md',
        'docs/source-notes.md', 'simulation/README.md', 'simulation/__init__.py',
        'simulation/reference_model.py', 'simulation/demo.py', 'tests/README.md',
        'tests/test_reference_model.py', 'tools/render_diagram.py', 'tools/validate_repository.py',
    ]
    for relative in required:
        path = ROOT / relative
        require(path.is_file() and path.stat().st_size > 0, f'Missing/empty file: {relative}')

    markdown = sorted(p for p in ROOT.rglob('*.md') if '.git' not in p.parts)
    link_count = 0
    for path in markdown:
        text = path.read_text(encoding='utf-8')
        require(text.endswith('\n'), f'Missing final newline: {path.name}')
        require(not re.search(r'[ \t]+$', text, re.M), f'Trailing whitespace: {path.name}')
        require(len(re.findall(r'^```', text, re.M)) % 2 == 0, f'Unbalanced fence: {path.name}')
        # Exclude fenced code so example tree/commands are not interpreted as links.
        prose = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', prose):
            if re.match(r'[a-zA-Z][\w+.-]*:', target):
                continue
            local, _, anchor = unquote(target.strip('<>')).partition('#')
            destination = (path.parent / local).resolve() if local else path
            require(destination.is_relative_to(ROOT), f'Link escapes repository: {target}')
            require(destination.is_file(), f'Broken link in {path.name}: {target}')
            if anchor:
                require(destination.suffix == '.md' and anchor in headings(destination.read_text(encoding='utf-8')),
                        f'Broken anchor in {path.name}: {target}')
            link_count += 1
        table_width = None
        for line in prose.splitlines():
            if line.startswith('|'):
                columns = len(re.split(r'(?<!\\)\|', line)) - 2
                if table_width is None:
                    table_width = columns
                require(columns == table_width, f'Inconsistent table in {path.name}: {line}')
            else:
                table_width = None

    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    for section in ['Project Overview', 'Problem Statement', 'Proposed Solution', 'Three Security Layers',
                    'System Architecture Diagram', 'Hardware Target & Technology', 'Security-by-Design',
                    'Threat Model & Limitations', 'Project Structure', 'Verification Strategy',
                    'Development Roadmap', 'Research References', 'Project Status']:
        require(f'## {section}\n' in readme, f'Missing README section: {section}')
    require('Proposed Architecture / Pre-Implementation' in readme, 'Missing honest project status')
    verification = (ROOT / 'docs/verification-plan.md').read_text(encoding='utf-8')
    scenarios = re.split(r'^### T\d+.*\n', verification, flags=re.M)[1:]
    require(len(scenarios) == 12, 'Expected exactly T1-T12')
    for i, scenario in enumerate(scenarios, 1):
        for field in ['Objective', 'Preconditions', 'Input stimulus', 'Expected behavior',
                      'Expected output signals', 'Pass/fail criteria', 'Planned verification method']:
            require(f'| {field} |' in scenario, f'T{i} missing {field}')
    architecture = (ROOT / 'docs/architecture.md').read_text(encoding='utf-8')
    modules = re.split(r'^### `\w+`\n', architecture, flags=re.M)[1:]
    require(len(modules) == 10, 'Expected ten RTL module specifications')
    for module in modules:
        for field in ['Purpose', 'Input', 'Output', 'Internal state', 'Dependencies',
                      'Expected behavior', 'Planned verification']:
            require(f'| {field} |' in module, f'RTL module missing {field}')
    references = (ROOT / 'docs/references.md').read_text(encoding='utf-8')
    entries = re.split(r'^### \[\d+\].*\n', references, flags=re.M)[1:]
    require(len(entries) == 16, 'Expected 16 proposal bibliography entries')
    for i, entry in enumerate(entries, 1):
        require(re.search(r'\*\*DOI:\*\* \[10\.\d{4,9}/[^\]]+\]\(https://doi.org/', entry),
                f'Reference {i} lacks DOI link')
        for field in ['**Title:**', '**Publication / year:**', '**Relevance:**']:
            require(field in entry, f'Reference {i} missing {field}')
        require('**Author' in entry, f'Reference {i} missing author')

    # Scan text files without displaying matched credential material.
    secret_patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}',
                       r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                       r'\bAKIA[A-Z0-9]{16}\b', r'\bsk-[A-Za-z0-9]{24,}']
    for relative in required:
        path = ROOT / relative
        if path.suffix in ('.py', '.md', '.mmd') or path.name == '.gitignore':
            text = path.read_text(encoding='utf-8')
            require(not any(re.search(pattern, text) for pattern in secret_patterns),
                    f'Possible credential in {relative}; inspect locally')
    dimensions = validate_png(ROOT / 'docs/block-diagram.png')
    print(f'PASS: {len(required)} nonempty required files, {len(markdown)} Markdown documents, '
          f'{link_count} local links, T1-T12, 10 modules, 16 DOI entries, PNG {dimensions[0]}x{dimensions[1]}, secret scan')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, zlib.error) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
