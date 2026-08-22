#!/usr/bin/env python3
"""Erzeugt die Link-Vorschaubilder (Open Graph) fuer host.clero.de.

  og-host.png     -> eintragen.html
  og-creator.png  -> creator.html

1200x630, Clero-Farben, Rubik. Fonts liegen unter FONT_DIR (nur zum Bauen
noetig, nicht im Repo).
"""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = '/tmp/fonts'
W, H = 1200, 630

NEON       = (130, 255, 65)
NEON_LIGHT = (218, 255, 234)
NEON_SOFT  = (238, 255, 244)
GREEN      = (33, 59, 44)
GREEN_DARK = (22, 41, 30)
MUTED      = (94, 107, 99)
WHITE      = (255, 255, 255)


def font(weight, size):
    return ImageFont.truetype(f'{FONT_DIR}/Rubik-{weight}.ttf', size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def heart(d, cx, cy, size, color):
    """Kleines Herz, zentriert auf (cx, cy)."""
    r = size * 0.28
    top = cy - size * 0.22
    d.ellipse([cx - r * 2, top - r, cx, top + r], fill=color)
    d.ellipse([cx, top - r, cx + r * 2, top + r], fill=color)
    d.polygon([(cx - r * 2, top), (cx + r * 2, top), (cx, cy + size * 0.42)], fill=color)


def rounded(im, r):
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    out = im.convert('RGBA')
    out.putalpha(mask)
    return out


def shadow(base, im, xy, blur=26, alpha=64, r=34):
    from PIL import ImageFilter
    sh = Image.new('RGBA', base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.rounded_rectangle([xy[0] + 6, xy[1] + 14, xy[0] + im.width + 6, xy[1] + im.height + 14],
                        r, fill=(20, 51, 43, alpha))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def build(out_name, pill, headline, sub, chips, mock_path, mock_crop):
    base = Image.new('RGBA', (W, H), NEON_LIGHT + (255,))
    d = ImageDraw.Draw(base)

    # weiches Farbfeld rechts, damit das Mockup nicht im Nichts steht
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W - 620, -240, W + 200, H + 200], fill=NEON_SOFT + (255,))
    base.alpha_composite(glow)

    # Neon-Kante oben
    d.rectangle([0, 0, W, 10], fill=NEON)

    PAD = 68
    TEXT_W = 620
    y = 92

    # Logo
    logo = Image.open('logo.png').convert('RGBA')
    lh = 74
    logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    base.alpha_composite(logo, (PAD, y - 18))
    y += lh + 26

    # Pill (Herz als Form, Rubik hat keine Emoji-Glyphen)
    f_pill = font('700', 22)
    tw = d.textlength(pill, font=f_pill)
    d.rounded_rectangle([PAD, y, PAD + tw + 66, y + 46], 23, fill=WHITE)
    heart(d, PAD + 22, y + 23, 20, NEON)
    d.text((PAD + 46, y + 23), pill, font=f_pill, fill=GREEN_DARK, anchor='lm')
    y += 76

    # Headline: Groesse automatisch so waehlen, dass sie in zwei Zeilen passt
    for size in (58, 54, 50, 46, 42, 38):
        f_h = font('800', size)
        h_lines = wrap(d, headline, f_h, TEXT_W)
        if len(h_lines) <= 2:
            break
    for line in h_lines:
        d.text((PAD, y), line, font=f_h, fill=GREEN)
        y += int(size * 1.14)
    y += 12

    # Subline
    f_s = font('400', 27)
    for line in wrap(d, sub, f_s, TEXT_W):
        d.text((PAD, y), line, font=f_s, fill=MUTED)
        y += 38
    y += 20

    # Chips
    f_c = font('500', 22)
    x = PAD
    for chip in chips:
        cw = d.textlength(chip, font=f_c)
        if x + cw + 36 > PAD + TEXT_W:
            x = PAD
            y += 52
        d.rounded_rectangle([x, y, x + cw + 36, y + 44], 22, fill=WHITE, outline=(228, 233, 228), width=2)
        d.text((x + 18, y + 22), chip, font=f_c, fill=GREEN, anchor='lm')
        x += cw + 50

    # Mockup rechts
    mock = Image.open(mock_path).convert('RGBA')
    mw, mh = mock.size
    l, t, r, b = mock_crop
    mock = mock.crop((int(mw * l), int(mh * t), int(mw * r), int(mh * b)))
    target_h = 585
    mock = mock.resize((int(mock.width * target_h / mock.height), target_h), Image.LANCZOS)
    mock = rounded(mock, 34)
    pos = (W - mock.width - 62, 74)
    shadow(base, mock, pos)
    base.alpha_composite(mock, pos)

    base.convert('RGB').save(out_name, quality=92)
    print(out_name, Image.open(out_name).size)


build('og-host.png',
      pill='München · Founding 20',
      headline='Trag deine Community ein',
      sub='20 Founding-Plätze für die ersten Münchner Communities. Kostenlos und unverbindlich.',
      chips=['Sichtbar zum Launch', 'Priorisierte Platzierung', 'Direkter Support'],
      mock_path='mock-map.webp', mock_crop=(0.0, 0.02, 1.0, 0.86))

build('og-creator.png',
      pill='München · Creator',
      headline='Werde Clero Creator in München',
      sub='Bau deine Community in deiner Nische auf. 20 Founding-Plätze, kostenlos und unverbindlich.',
      chips=['Sichtbar zum Launch', 'Priorisierte Platzierung', 'Direkter Support'],
      mock_path='mock-feed.webp', mock_crop=(0.0, 0.02, 1.0, 0.86))
