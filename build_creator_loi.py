#!/usr/bin/env python3
"""Erzeugt clero-creator-loi.pdf (DE) und clero-creator-loi-en.pdf (EN) - das
LOI fuer die Founding-Creator-Bewerbung (creator.html).

Ueberarbeitung 2026-09: gleiches visuelles Design/Layout-Prinzip wie das neue
Host-LOI (build_host_loi.py) - dynamischer y-Cursor mit automatischem
Seitenumbruch, Tabellen-Zeilen fuer Angaben, Seitenzahlen im Footer. Der
rechtliche Inhalt (Abschnitte 1-7) bleibt inhaltlich der bisherige
Creator-LOI-Text; nur der Clero-Rechtstraeger-Block (Name/Sitz/Handelsregister/
Vertretung) wurde an den inzwischen aktuellen Stand (Clero GmbH statt Clero UG
i.G.) angeglichen, damit beide LOI-Typen (Host & Creator) den gleichen,
aktuellen Rechtstraeger nennen.

Gleiches Prinzip wie build_host_loi.py: die Seiten werden so gebaut, dass die
Stempel-Koordinaten fuer pdf-lib (Client-seitiges Befuellen im Browser) exakt
bekannt sind. Das Skript gibt am Ende ein JS-Objekt aus, das 1:1 als
LOI_FIELDS in creator.html kann. Die Feld-Keys (cName, cTheme, cChannels,
cReach, sName, sHandle, sContact, sOrtDatum, sSign, tjard) sind unveraendert -
die bestehende buildFilledLoi()-Logik in creator.html muss dafuer nicht
angefasst werden, nur die LOI_FIELDS-Koordinaten werden ersetzt.
"""
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

W, H = A4
INK = HexColor('#14332B')
GREEN = HexColor('#213B2C')
ACCENT = HexColor('#82FF41')
GREY = HexColor('#5E6B63')
LINE = HexColor('#C9D6CE')

SIG_TJARD = 'tjard-signatur.png'

M = 56
TOP = H - 62
BOTTOM = 60
BODY = 9.6
LEAD = 13.6
H1 = 15
H3 = 10.4


def wrap(text, font, size, width):
    words = text.split(' ')
    lines, cur = [], ''
    for w_ in words:
        cand = (cur + ' ' + w_).strip()
        if stringWidth(cand, font, size) <= width:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


TEXT = {
    'de': {
        'file': 'clero-creator-loi.pdf',
        'title': 'LETTER OF INTENT / ABSICHTSERKLÄRUNG',
        'sub': 'Founding-Creator-Programm München · Version 2.0 · September 2026',
        'intro': 'Diese Absichtserklärung wird geschlossen zwischen',
        'creatorTable': [
            ('Name', 'cName'),
        ],
        'hereinafterCreator': '– nachfolgend „Creator" –',
        'und': 'und',
        'cleroTable': [
            ('Unternehmen', 'Clero GmbH'),
            ('Sitz', 'München, Deutschland'),
            ('Handelsregister', 'Amtsgericht München, HRB 315395'),
            ('Geschäftsadresse', 'Dachauer Straße 111, 80335 München'),
            ('Vertreten durch', 'Tjard Püschel, Geschäftsführer'),
            ('E-Mail', 't.pueschel@clero.de'),
        ],
        'hereinafterClero': '– nachfolgend „Clero" –',
        'sections': [
            ('1. Hintergrund', [
                'Clero entwickelt eine Plattform für den Aufbau, die Organisation und die Sichtbarkeit lokaler '
                'Gruppen und Communities. Creator können über Clero eine eigene Community in ihrer Nische aufbauen, '
                'Treffen und Events organisieren und lokal gefunden werden.',
            ]),
            ('2. Interesse an der Nutzung von Clero', [
                'Der Creator bekundet sein grundsätzliches Interesse, Clero ab August 2026 im Rahmen des '
                'öffentlichen Starts von Clero in München zu nutzen, sofern die für ihn relevanten Funktionen wie '
                'geplant verfügbar sind.',
                'Der Creator plant Clero insbesondere zu nutzen, um eine eigene Community aufzubauen, Events und '
                'wiederkehrende Treffen zu organisieren und lokal sichtbar zu werden.',
            ]),
        ],
        's3h': '3. Angaben zum Creator',
        'creatorFields': [
            ('Thema / Nische', 'cTheme'),
            ('Kanäle (Instagram / TikTok / weitere)', 'cChannels'),
            ('Community / Reichweite (ca.)', 'cReach'),
        ],
        'sections2': [
            ('4. Founding-Creator-Programm', [
                'Clero beabsichtigt, den Creator in das Founding-Creator-Programm für München aufzunehmen. Das '
                'Programm umfasst besondere Sichtbarkeit zum Launch, priorisierte Platzierung in der App sowie '
                'direkten Support durch das Clero-Team.',
                'Die Teilnahme am Programm ist für den Creator kostenlos. Die konkreten Konditionen werden '
                'individuell abgestimmt.',
            ]),
            ('5. Unverbindlichkeit', [
                'Diese Erklärung dient ausschließlich der Dokumentation des aktuellen Interesses des Creators an '
                'einer möglichen zukünftigen Nutzung von Clero.',
                'Sie ist rechtlich unverbindlich und begründet weder eine Verpflichtung zur Nutzung, zum Kauf, zur '
                'Zahlung noch zur exklusiven Zusammenarbeit mit Clero. Eine tatsächliche Nutzung der Plattform '
                'setzt insbesondere Produktverfügbarkeit, den finalen Funktionsumfang und die beiderseitige '
                'Abstimmung voraus.',
            ]),
            ('6. Referenznutzung', [
                'Der Creator erklärt sich damit einverstanden, dass Clero seinen Namen, sein Handle und sein '
                'Profilbild zu Referenzzwecken in der externen Kommunikation verwenden darf, insbesondere auf der '
                'Website, in Pitch-Unterlagen und in Gesprächen mit potenziellen Investor:innen.',
                'Eine solche Nutzung erfolgt ausschließlich zu Referenzzwecken und kann jederzeit mit Wirkung für '
                'die Zukunft widerrufen werden.',
            ]),
        ],
        'sig_h': '7. Unterschriften',
        'sig_creator': 'Creator',
        'sig_clero': 'Für die Clero GmbH',
        'creatorSig': [
            ('Name (Vor- und Nachname)', 'sName'),
            ('Haupt-Kanal / Handle', 'sHandle'),
            ('E-Mail / Telefonnummer', 'sContact'),
            ('Ort, Datum', 'sOrtDatum'),
        ],
        'cleroSig': [
            ('Name', 'Tjard Püschel'),
            ('Rolle', 'Geschäftsführer'),
        ],
        'l_sig': 'Unterschrift',
        'l_ortdatum2': 'Ort, Datum',
        'foot': 'Clero GmbH  ·  clero.de  ·  t.pueschel@clero.de',
    },
    'en': {
        'file': 'clero-creator-loi-en.pdf',
        'title': 'LETTER OF INTENT',
        'sub': 'Founding Creator Programme Munich · Version 2.0 · September 2026',
        'intro': 'This Letter of Intent is entered into between',
        'creatorTable': [
            ('Name', 'cName'),
        ],
        'hereinafterCreator': '– hereinafter the "Creator" –',
        'und': 'and',
        'cleroTable': [
            ('Company', 'Clero GmbH'),
            ('Registered seat', 'Munich, Germany'),
            ('Commercial register', 'Local Court of Munich, HRB 315395'),
            ('Business address', 'Dachauer Straße 111, 80335 München'),
            ('Represented by', 'Tjard Püschel, Managing Director'),
            ('Email', 't.pueschel@clero.de'),
        ],
        'hereinafterClero': '– hereinafter "Clero" –',
        'sections': [
            ('1. Background', [
                'Clero is building a platform for creating, organising and finding local groups and communities. '
                'Creators can use Clero to build their own community in their niche, organise meet-ups and events, '
                'and be discovered locally.',
            ]),
            ('2. Interest in using Clero', [
                'The Creator expresses general interest in using Clero from August 2026, as part of Clero’s public '
                'launch in Munich, provided the relevant features are available as planned.',
                'The Creator intends to use Clero in particular to build a community, to organise events and '
                'recurring meet-ups, and to become visible locally.',
            ]),
        ],
        's3h': '3. Creator details',
        'creatorFields': [
            ('Topic / niche', 'cTheme'),
            ('Channels (Instagram / TikTok / other)', 'cChannels'),
            ('Community / reach (approx.)', 'cReach'),
        ],
        'sections2': [
            ('4. Founding Creator Programme', [
                'Clero intends to include the Creator in the Founding Creator Programme for Munich. The programme '
                'includes special visibility at launch, priority placement in the app and direct support from the '
                'Clero team.',
                'Participation in the programme is free of charge for the Creator. Specific terms are agreed '
                'individually.',
            ]),
            ('5. Non-binding nature', [
                'This declaration serves solely to document the Creator’s current interest in a possible future '
                'use of Clero.',
                'It is legally non-binding and creates no obligation to use, purchase, pay for or work exclusively '
                'with Clero. Actual use of the platform depends in particular on product availability, the final '
                'feature set and mutual agreement.',
            ]),
            ('6. Reference use', [
                'The Creator agrees that Clero may use their name, handle and profile picture for reference '
                'purposes in external communication, in particular on the website, in pitch materials and in '
                'conversations with potential investors.',
                'Such use is for reference purposes only and can be revoked at any time with effect for the '
                'future.',
            ]),
        ],
        'sig_h': '7. Signatures',
        'sig_creator': 'Creator',
        'sig_clero': 'For Clero GmbH',
        'creatorSig': [
            ('Name (first and last)', 'sName'),
            ('Main channel / handle', 'sHandle'),
            ('Email / phone number', 'sContact'),
            ('Place, date', 'sOrtDatum'),
        ],
        'cleroSig': [
            ('Name', 'Tjard Püschel'),
            ('Role', 'Managing Director'),
        ],
        'l_sig': 'Signature',
        'l_ortdatum2': 'Place, date',
        'foot': 'Clero GmbH  ·  clero.de  ·  t.pueschel@clero.de',
    },
}


def build(lang):
    t = TEXT[lang]
    coords = {}
    c = canvas.Canvas(t['file'], pagesize=A4)
    y = [TOP]
    page = [0]

    def header():
        c.setFillColor(ACCENT)
        c.rect(0, H - 8, W, 8, stroke=0, fill=1)

    def footer():
        c.setFillColor(LINE)
        c.rect(M, 40, W - 2 * M, 0.6, stroke=0, fill=1)
        c.setFont('Helvetica', 7.4)
        c.setFillColor(GREY)
        c.drawString(M, 28, t['foot'])
        c.drawRightString(W - M, 28, str(page[0] + 1))

    def newpage():
        footer()
        c.showPage()
        page[0] += 1
        header()
        y[0] = TOP

    def ensure(space):
        if y[0] - space < BOTTOM:
            newpage()

    def rule(gap_before=6, gap_after=14):
        y[0] -= gap_before
        c.setFillColor(LINE)
        c.rect(M, y[0], W - 2 * M, 0.6, stroke=0, fill=1)
        y[0] -= gap_after

    def para(text, size=BODY, font='Helvetica', color=INK, lead=LEAD, width=W - 2 * M):
        for ln in wrap(text, font, size, width):
            ensure(lead)
            c.setFont(font, size)
            c.setFillColor(color)
            c.drawString(M, y[0], ln)
            y[0] -= lead

    def heading(text):
        ensure(LEAD + 10)
        y[0] -= 6
        c.setFont('Helvetica-Bold', H3)
        c.setFillColor(GREEN)
        c.drawString(M, y[0], text)
        y[0] -= LEAD + 4

    def dotted(x, yy, w):
        c.setFillColor(LINE)
        c.rect(x, yy - 3.2, w, 0.6, stroke=0, fill=1)
        return {'x': round(x + 3, 1), 'y': round(yy, 1)}

    def field_row(label, key_or_value, static=False, lw=260):
        ensure(22)
        c.setFont('Helvetica', BODY)
        c.setFillColor(GREY)
        c.drawString(M, y[0], label + ':')
        lx = M + stringWidth(label + ':', 'Helvetica', BODY) + 8
        if static:
            c.setFillColor(INK)
            avail = W - M - lx
            lines = wrap(key_or_value, 'Helvetica', BODY, avail)
            c.drawString(lx, y[0], lines[0] if lines else '')
            y[0] -= 20
            for extra in lines[1:]:
                ensure(LEAD)
                c.setFont('Helvetica', BODY)
                c.setFillColor(INK)
                c.drawString(lx, y[0], extra)
                y[0] -= LEAD
            if len(lines) > 1:
                y[0] -= 6
        else:
            coords[key_or_value] = {'p': page[0], **dotted(lx, y[0], min(lw, W - M - lx))}
            y[0] -= 22

    # ---------------- Seite 1: Titel + Parteien ----------------
    header()
    y[0] = TOP

    c.setFont('Helvetica-Bold', H1)
    c.setFillColor(GREEN)
    c.drawString(M, y[0], t['title'])
    y[0] -= 17
    c.setFont('Helvetica', 10)
    c.setFillColor(GREY)
    c.drawString(M, y[0], t['sub'])
    y[0] -= 14
    rule(gap_before=8, gap_after=20)

    para(t['intro'])
    y[0] -= 4

    for label, key in t['creatorTable']:
        field_row(label, key, static=False)
    y[0] -= 4
    para(t['hereinafterCreator'], font='Helvetica-Oblique', color=GREY)
    y[0] -= 10

    para(t['und'])
    y[0] -= 4

    for label, value in t['cleroTable']:
        field_row(label, value, static=True)
    y[0] -= 4
    para(t['hereinafterClero'], font='Helvetica-Oblique', color=GREY)
    y[0] -= 6

    for title, lines in t['sections']:
        heading(title)
        for ln in lines:
            para(ln)
        y[0] -= 4

    # ---------------- Abschnitt 3: Angaben zum Creator ----------------
    heading(t['s3h'])
    for label, key in t['creatorFields']:
        field_row(label, key, static=False, lw=300)
    y[0] -= 4

    for title, lines in t['sections2']:
        heading(title)
        for ln in lines:
            para(ln)
        y[0] -= 4

    # ---------------- Abschnitt 7: Unterschriften ----------------
    ensure(210)  # Creator-Unterschriftsblock nicht auseinanderreissen
    rule(gap_before=6, gap_after=18)
    c.setFont('Helvetica-Bold', 11.5)
    c.setFillColor(GREEN)
    c.drawString(M, y[0], t['sig_h'])
    y[0] -= 22

    c.setFont('Helvetica-Bold', 9.2)
    c.setFillColor(GREY)
    c.drawString(M, y[0], t['sig_creator'].upper())
    y[0] -= 18
    for label, key in t['creatorSig']:
        field_row(label, key, static=False, lw=280)

    ensure(66)
    y[0] -= 20
    c.setFillColor(INK)
    c.setFont('Helvetica', BODY)
    c.drawString(M, y[0], t['l_sig'] + ':')
    sigx = M + stringWidth(t['l_sig'] + ':', 'Helvetica', BODY) + 10
    c.setFillColor(LINE)
    c.rect(sigx, y[0] - 4, 200, 0.6, stroke=0, fill=1)
    coords['sSign'] = {'p': page[0], 'x': round(sigx + 6, 1), 'y': round(y[0] - 1, 1), 'w': 120, 'h': 32}
    y[0] -= 46

    ensure(184)  # Clero-Unterschriftsblock nicht auseinanderreissen
    rule(gap_before=4, gap_after=18)
    c.setFont('Helvetica-Bold', 9.2)
    c.setFillColor(GREY)
    c.drawString(M, y[0], t['sig_clero'].upper())
    y[0] -= 18
    for label, value in t['cleroSig']:
        field_row(label, value, static=True)
    field_row(t['l_ortdatum2'], 'tjard', static=False)

    ensure(66)
    y[0] -= 20
    c.setFillColor(INK)
    c.setFont('Helvetica', BODY)
    c.drawString(M, y[0], t['l_sig'] + ':')
    lx = M + stringWidth(t['l_sig'] + ':', 'Helvetica', BODY) + 10
    c.setFillColor(LINE)
    c.rect(lx, y[0] - 4, 200, 0.6, stroke=0, fill=1)
    try:
        img = ImageReader(SIG_TJARD)
        iw, ih = img.getSize()
        sw = 105.0
        c.drawImage(img, lx + 8, y[0] - 2, width=sw, height=sw * ih / iw, mask='auto')
    except Exception:
        pass
    y[0] -= 30

    footer()
    c.save()
    return coords


out = {}
for lang in ('de', 'en'):
    out[lang] = {'url': TEXT[lang]['file'], **build(lang)}

print(json.dumps(out, indent=2, ensure_ascii=False))
