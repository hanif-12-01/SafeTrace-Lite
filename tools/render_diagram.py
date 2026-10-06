"""Render the repository's Mermaid topology to a real PNG using Pillow.

Fallback for environments without Mermaid CLI. Labels/edges come from .mmd;
presentation coordinates below are deliberately fixed for this architecture.
Run: python tools/render_diagram.py. Pillow is needed only to regenerate PNG.
"""

from pathlib import Path
import math
import re

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/block-diagram.mmd'
OUTPUT = ROOT / 'docs/block-diagram.png'

BOXES = {
    'SENDER': (60, 180, 520, 330), 'HPS': (800, 180, 1320, 330),
    'SENSOR': (1960, 180, 2490, 330), 'CONFIG': (460, 490, 850, 660),
    'BOOT': (1000, 490, 1620, 630), 'HMAC': (1000, 790, 1230, 915),
    'REPLAY': (1390, 790, 1620, 915), 'POLICY': (1000, 980, 1620, 1105),
    'GATE': (1000, 1250, 1620, 1390), 'SCHED': (475, 945, 855, 1085),
    'SHA': (475, 1200, 855, 1340), 'LOG': (1740, 1190, 2040, 1380),
    'ACTUATOR': (1000, 1490, 1620, 1630), 'STORE': (1650, 1490, 2050, 1630),
    'BACKEND': (2140, 1490, 2510, 1630),
}

# (polyline, label center, label wrap width); endpoints stop at node boundaries.
ROUTES = {
    ('SENDER', 'HPS'): ([(520, 255), (800, 255)], (660, 225), 255),
    ('HPS', 'BOOT'): ([(1060, 330), (1060, 490)], (1210, 385), 270),
    ('HPS', 'HMAC'): ([(1320, 255), (1680, 255), (1680, 700), (1115, 700), (1115, 790)], (1820, 650), 245),
    ('CONFIG', 'BOOT'): ([(850, 550), (1000, 550)], (925, 505), 145),
    ('CONFIG', 'HMAC'): ([(850, 580), (915, 580), (915, 850), (1000, 850)], (905, 765), 175),
    ('CONFIG', 'POLICY'): ([(850, 620), (935, 620), (935, 1030), (1000, 1030)], (915, 900), 175),
    ('BOOT', 'GATE'): ([(1620, 555), (1710, 555), (1710, 1320), (1620, 1320)], (1830, 900), 230),
    ('HMAC', 'REPLAY'): ([(1230, 850), (1390, 850)], (1310, 820), 155),
    ('REPLAY', 'POLICY'): ([(1505, 915), (1505, 980)], (1505, 948), 230),
    ('SENSOR', 'POLICY'): ([(2225, 330), (2225, 1040), (1620, 1040)], (2300, 680), 250),
    ('POLICY', 'GATE'): ([(1310, 1105), (1310, 1250)], (1390, 1190), 370),
    ('GATE', 'ACTUATOR'): ([(1310, 1390), (1310, 1490)], (1305, 1442), 360),
    ('GATE', 'LOG'): ([(1620, 1355), (1740, 1355)], (1730, 1404), 240),
    ('LOG', 'STORE'): ([(1890, 1380), (1890, 1490)], (1890, 1450), 280),
    ('STORE', 'BACKEND'): ([(2050, 1560), (2095, 1560), (2095, 1435), (2325, 1435), (2325, 1490)], (2340, 1400), 350),
    ('BOOT', 'SCHED'): ([(1000, 600), (880, 600), (880, 980), (855, 980)], (775, 735), 195),
    ('HMAC', 'SCHED'): ([(1000, 880), (895, 880), (895, 1015), (855, 1015)], (750, 880), 195),
    ('LOG', 'SCHED'): ([(1740, 1220), (1695, 1220), (1695, 1150), (910, 1150), (910, 1050), (855, 1050)], (1060, 1150), 185),
    ('SCHED', 'SHA'): ([(665, 1085), (665, 1200)], (660, 1142), 370),
}


def read_topology():
    source = SOURCE.read_text(encoding='utf-8')
    nodes = dict(re.findall(r'^\s*(\w+)\["([^"]+)"\]', source, re.M))
    edges = re.findall(r'^\s*(\w+)\s+(-->|<-\.->)\|([^|]+)\|\s+(\w+)\s*$', source, re.M)
    if set(nodes) != set(BOXES) or {(a, b) for a, _, _, b in edges} != set(ROUTES):
        raise ValueError('Mermaid topology changed: update BOXES/ROUTES before rendering')
    return nodes, edges


def font(size, bold=False):
    candidates = ([Path('C:/Windows/Fonts/arialbd.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]
                  if bold else [Path('C:/Windows/Fonts/arial.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def main():
    nodes, edges = read_topology()
    canvas = Image.new('RGB', (2560, 1780), '#ffffff')
    draw = ImageDraw.Draw(canvas)
    ink = '#15324d'
    draw.text((60, 40), 'SafeTrace Lite', font=font(56, True), fill=ink)
    draw.text((60, 110), 'Boot integrity  /  authenticated safe action  /  verifiable evidence', font=font(30), fill='#5b7085')
    draw.text((1730, 65), 'PROPOSED ARCHITECTURE', font=font(28, True), fill='#5b7085')
    draw.rounded_rectangle((420, 410, 2090, 1420), radius=24, fill='#f8fbfe', outline='#2c5c85', width=4)
    draw.text((450, 435), 'FPGA FABRIC - SafeTrace Lite', font=font(30, True), fill=ink)
    draw.rounded_rectangle((960, 740, 1660, 1130), radius=18, fill='#fffcf5', outline='#d1a04b', width=3)
    draw.text((985, 750), 'Runtime Command Guard', font=font(25, True), fill='#73521c')

    def arrowhead(tip, previous, color):
        angle = math.atan2(tip[1] - previous[1], tip[0] - previous[0])
        back = (tip[0] - 16 * math.cos(angle), tip[1] - 16 * math.sin(angle))
        perpendicular = (-7 * math.sin(angle), 7 * math.cos(angle))
        draw.polygon([tip, (back[0] + perpendicular[0], back[1] + perpendicular[1]),
                      (back[0] - perpendicular[0], back[1] - perpendicular[1])], fill=color)

    def segment(a, b, color, dashed):
        if not dashed:
            draw.line([a, b], fill=color, width=4)
            return
        distance = math.dist(a, b)
        for offset in range(0, int(distance), 25):
            end = min(offset + 15, distance)
            start_point = tuple(a[i] + (b[i] - a[i]) * offset / distance for i in range(2))
            end_point = tuple(a[i] + (b[i] - a[i]) * end / distance for i in range(2))
            draw.line([start_point, end_point], fill=color, width=3)

    for a, style, label, b in edges:
        points, _, _ = ROUTES[a, b]
        dashed = style != '-->'
        color = '#9274bd' if dashed else '#476b8c'
        for start, end in zip(points, points[1:]):
            segment(start, end, color, dashed)
        arrowhead(points[-1], points[-2], color)
        if dashed:
            arrowhead(points[0], points[1], color)

    def wrapped(text, typeface, width):
        lines, line = [], ''
        for word in text.split():
            trial = (line + ' ' + word).strip()
            if line and draw.textlength(trial, font=typeface) > width:
                lines.append(line)
                line = word
            else:
                line = trial
        return lines + ([line] if line else [])

    palette = {
        'BOOT': ('#e7f1ff', '#2563eb'), 'CONFIG': ('#f0f4f8', '#748aa0'),
        **{x: ('#fff2d9', '#d49b24') for x in ['HMAC', 'REPLAY', 'POLICY', 'GATE']},
        **{x: ('#f0eaff', '#8262bd') for x in ['SCHED', 'SHA']},
        **{x: ('#e6f6f3', '#1b927e') for x in ['LOG', 'STORE', 'BACKEND']},
    }
    for node, label in nodes.items():
        box = BOXES[node]
        fill, stroke = palette.get(node, ('#eff5fc', '#64748b'))
        draw.rounded_rectangle(box, radius=18, fill=fill, outline=stroke, width=3)
        width = box[2] - box[0] - 24
        titles = label.split('<br/>')
        size = 27
        while draw.textlength(titles[0], font=font(size, True)) > width and size > 19:
            size -= 1
        lines = [(titles[0], font(size, True))]
        for body in titles[1:]:
            lines += [(line, font(23)) for line in wrapped(body, font(23), width)]
        height = sum(f.size + 8 for _, f in lines)
        y = (box[1] + box[3] - height) / 2
        for line, typeface in lines:
            x = (box[0] + box[2] - draw.textlength(line, font=typeface)) / 2
            draw.text((x, y), line, font=typeface, fill=ink)
            y += typeface.size + 8

    for a, style, label, b in edges:
        _, center, width = ROUTES[a, b]
        size = 21
        while max(draw.textlength(word, font=font(size)) for word in label.split()) > width and size > 17:
            size -= 1
        typeface = font(size)
        lines = wrapped(label, typeface, width)
        line_height = size + 5
        actual_width = max(draw.textlength(line, font=typeface) for line in lines)
        height = len(lines) * line_height
        x, y = center[0] - actual_width / 2, center[1] - height / 2
        draw.rounded_rectangle((x - 4, y - 2, x + actual_width + 4, y + height + 2), radius=5, fill='#ffffff')
        for i, line in enumerate(lines):
            draw.text((center[0] - draw.textlength(line, font=typeface) / 2, y + i * line_height),
                      line, font=typeface, fill='#5c417e' if style != '-->' else '#34546f')

    draw.line((65, 1685, 145, 1685), fill='#476b8c', width=4)
    arrowhead((145, 1685), (65, 1685), '#476b8c')
    draw.text((165, 1668), 'Data / decision / configuration', font=font(24), fill=ink)
    segment((650, 1685), (730, 1685), '#9274bd', True)
    arrowhead((730, 1685), (650, 1685), '#9274bd')
    arrowhead((650, 1685), (730, 1685), '#9274bd')
    draw.text((750, 1668), 'Shared SHA request + result', font=font(24), fill=ink)
    draw.text((1420, 1668), 'Default/reset: BLOCK. Every runtime decision is logged.', font=font(24), fill=ink)
    draw.text((65, 1720), 'MVP: test-image gate, not native board secure boot. Tamper evidence requires a trusted checkpoint.',
              font=font(23), fill='#5b7085')
    canvas.save(OUTPUT, format='PNG', optimize=True, dpi=(150, 150))
    with Image.open(OUTPUT) as check:
        check.verify()
    print(f'Rendered {OUTPUT.name}: 2560 x 1780 RGB PNG; {len(nodes)} nodes, {len(edges)} source edges')


if __name__ == '__main__':
    main()
