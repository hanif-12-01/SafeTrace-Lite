"""Pemeriksaan repositori dokumentasi/model dengan pustaka standar.

Memeriksa tautan/anchor Markdown, bagian/skenario/modul wajib, DOI, file berisi,
chunk/CRC/data piksel PNG, dan rahasia yang tidak sengaja disertakan.
Tidak melakukan verifikasi perangkat keras atau resolusi DOI melalui jaringan.
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
    require(data[:8] == b'\x89PNG\r\n\x1a\n', 'Signature PNG tidak sesuai')
    offset, compressed, dimensions, ended = 8, bytearray(), None, False
    while offset < len(data):
        require(offset + 12 <= len(data), 'Chunk PNG terpotong')
        length = struct.unpack('>I', data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        require(offset + length + 12 <= len(data), 'Data PNG terpotong')
        crc = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
        require((binascii.crc32(kind + body) & 0xffffffff) == crc, 'CRC PNG tidak sesuai')
        if kind == b'IHDR':
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', body)
            require((depth, color, compression, filtering, interlace) == (8, 2, 0, 0, 0),
                    'PNG harus berupa RGB 8 bit tanpa interlace')
            require(width >= 1600 and height >= 1000, 'Resolusi diagram terlalu kecil')
            dimensions = (width, height)
        elif kind == b'IDAT':
            compressed.extend(body)
        elif kind == b'IEND':
            ended = True
            break
        offset += length + 12
    require(ended and dimensions, 'Chunk wajib PNG tidak lengkap')
    pixels = zlib.decompress(compressed)
    width, height = dimensions
    require(len(pixels) == height * (1 + width * 3), 'Ukuran data piksel PNG tidak sesuai')
    require(all(pixels[y * (1 + width * 3)] <= 4 for y in range(height)), 'Filter baris PNG tidak valid')
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
        require(path.is_file() and path.stat().st_size > 0, f'File hilang/kosong: {relative}')

    markdown = sorted(p for p in ROOT.rglob('*.md') if '.git' not in p.parts)
    link_count = 0
    for path in markdown:
        text = path.read_text(encoding='utf-8')
        require(text.endswith('\n'), f'Baris akhir belum lengkap: {path.name}')
        require(not re.search(r'[ \t]+$', text, re.M), f'Spasi di akhir baris: {path.name}')
        require(len(re.findall(r'^```', text, re.M)) % 2 == 0, f'Blok kode tidak berpasangan: {path.name}')
        # Lewati blok kode agar contoh struktur/perintah tidak dianggap tautan.
        prose = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', prose):
            if re.match(r'[a-zA-Z][\w+.-]*:', target):
                continue
            local, _, anchor = unquote(target.strip('<>')).partition('#')
            destination = (path.parent / local).resolve() if local else path
            require(destination.is_relative_to(ROOT), f'Tautan keluar repositori: {target}')
            require(destination.is_file(), f'Tautan rusak di {path.name}: {target}')
            if anchor:
                require(destination.suffix == '.md' and anchor in headings(destination.read_text(encoding='utf-8')),
                        f'Anchor rusak di {path.name}: {target}')
            link_count += 1
        table_width = None
        for line in prose.splitlines():
            if line.startswith('|'):
                columns = len(re.split(r'(?<!\\)\|', line)) - 2
                if table_width is None:
                    table_width = columns
                require(columns == table_width, f'Tabel tidak konsisten di {path.name}: {line}')
            else:
                table_width = None

    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    for section in ['Gambaran Proyek', 'Latar Belakang dan Rumusan Masalah', 'Solusi yang Diusulkan',
                    'Tiga Lapisan Keamanan', 'Diagram Arsitektur Sistem', 'Target Perangkat Keras dan Teknologi',
                    'Keamanan Sejak Tahap Perancangan', 'Model Ancaman dan Batasan', 'Struktur Repositori',
                    'Strategi Verifikasi', 'Peta Jalan Pengembangan', 'Referensi Ilmiah', 'Status Proyek']:
        require(f'## {section}\n' in readme, f'Bagian README belum ada: {section}')
    require('Usulan Arsitektur / Praimplementasi' in readme, 'Status proyek yang jujur belum ada')
    verification = (ROOT / 'docs/verification-plan.md').read_text(encoding='utf-8')
    scenarios = re.split(r'^### T\d+.*\n', verification, flags=re.M)[1:]
    require(len(scenarios) == 12, 'Skenario harus tepat T1-T12')
    for i, scenario in enumerate(scenarios, 1):
        for field in ['Tujuan', 'Prasyarat', 'Stimulus masukan', 'Perilaku yang diharapkan',
                      'Sinyal keluaran yang diharapkan', 'Kriteria lulus/gagal', 'Metode verifikasi yang direncanakan']:
            require(f'| {field} |' in scenario, f'T{i} belum memuat {field}')
    architecture = (ROOT / 'docs/architecture.md').read_text(encoding='utf-8')
    modules = re.split(r'^### `\w+`\n', architecture, flags=re.M)[1:]
    require(len(modules) == 10, 'Harus ada sepuluh spesifikasi modul RTL')
    for module in modules:
        for field in ['Tujuan', 'Masukan', 'Keluaran', 'Keadaan internal', 'Ketergantungan',
                      'Perilaku yang diharapkan', 'Rencana verifikasi']:
            require(f'| {field} |' in module, f'Modul RTL belum memuat {field}')
    references = (ROOT / 'docs/references.md').read_text(encoding='utf-8')
    entries = re.split(r'^### \[\d+\].*\n', references, flags=re.M)[1:]
    require(len(entries) == 16, 'Harus ada 16 referensi dari proposal')
    for i, entry in enumerate(entries, 1):
        require(re.search(r'\*\*DOI:\*\* \[10\.\d{4,9}/[^\]]+\]\(https://doi.org/', entry),
                f'Referensi {i} belum memuat tautan DOI')
        for field in ['**Judul:**', '**Publikasi / tahun:**', '**Relevansi:**']:
            require(field in entry, f'Referensi {i} belum memuat {field}')
        require('**Penulis:**' in entry, f'Referensi {i} belum memuat penulis')

    # Pindai teks tanpa menampilkan credential yang mungkin ditemukan.
    secret_patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}',
                       r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                       r'\bAKIA[A-Z0-9]{16}\b', r'\bsk-[A-Za-z0-9]{24,}']
    for relative in required:
        path = ROOT / relative
        if path.suffix in ('.py', '.md', '.mmd') or path.name == '.gitignore':
            text = path.read_text(encoding='utf-8')
            require(not any(re.search(pattern, text) for pattern in secret_patterns),
                    f'Kemungkinan credential di {relative}; periksa secara lokal')
    dimensions = validate_png(ROOT / 'docs/block-diagram.png')
    print(f'LULUS: {len(required)} file wajib berisi, {len(markdown)} dokumen Markdown, '
          f'{link_count} tautan lokal, T1-T12, 10 modul, 16 DOI, PNG {dimensions[0]}x{dimensions[1]}, pemeriksaan rahasia')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, zlib.error) as exc:
        print(f'GAGAL: {exc}', file=sys.stderr)
        sys.exit(1)
