#!/usr/bin/env python3
"""Erzeugt clero-creator-loi.pdf (DE) und clero-creator-loi-en.pdf (EN).

Die Seiten sind so gebaut, dass die Stempel-Koordinaten fuer pdf-lib
(Client-seitiges Befuellen im Browser) exakt bekannt sind. Das Skript
gibt am Ende ein JS-Objekt aus, das 1:1 in creator.html kann.
"""
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor

W, H = A4
INK = HexColor('#14332B')
GREEN = HexColor('#213B2C')
ACCENT = HexColor('#82FF41')
GREY = HexColor('#5E6B63')
LINE = HexColor('#C9D6CE')

M = 56              # Seitenrand
BODY = 10.2
LEAD = 15.2

TEXT = {
    'de': {
        'file': 'clero-creator-loi.pdf',
        'title': 'LETTER OF INTENT / ABSICHTSERKLÄRUNG',
        'sub': 'Founding-Creator-Programm München',
        'intro': 'Diese Absichtserklärung wird geschlossen zwischen',
        'party_a_suffix': ', nachfolgend „Creator“,',
        'party_b': ['und Clero UG (haftungsbeschränkt) (in Gründung), vertreten durch Tjard Püschel,', 'Gründer.'],
        'sections': [
            ('1. Hintergrund', [
                'Clero entwickelt eine Plattform für den Aufbau, die Organisation und die Sichtbarkeit',
                'lokaler Gruppen und Communities. Creator können über Clero eine eigene Community',
                'in ihrer Nische aufbauen, Treffen und Events organisieren und lokal gefunden werden.',
            ]),
            ('2. Interesse an der Nutzung von Clero', [
                'Der Creator bekundet sein grundsätzliches Interesse, Clero ab August 2026 im Rahmen',
                'des öffentlichen Starts von Clero in München zu nutzen, sofern die für ihn relevanten',
                'Funktionen wie geplant verfügbar sind.',
                '',
                'Der Creator plant Clero insbesondere zu nutzen, um eine eigene Community aufzubauen,',
                'Events und wiederkehrende Treffen zu organisieren und lokal sichtbar zu werden.',
            ]),
            ('3. Angaben zum Creator', None),   # Platzhalter-Block, wird separat gezeichnet
            ('4. Founding-Creator-Programm', [
                'Clero beabsichtigt, den Creator in das Founding-Creator-Programm für München',
                'aufzunehmen. Das Programm umfasst besondere Sichtbarkeit zum Launch, priorisierte',
                'Platzierung in der App sowie direkten Support durch das Clero-Team.',
                '',
                'Die Teilnahme am Programm ist für den Creator kostenlos. Die konkreten Konditionen',
                'werden individuell abgestimmt.',
            ]),
        ],
        'f_theme': 'Thema / Nische:',
        'f_channels': 'Kanäle (Instagram / TikTok / weitere):',
        'f_reach': 'Community / Reichweite (ca.):',
        'sections2': [
            ('5. Unverbindlichkeit', [
                'Diese Erklärung dient ausschließlich der Dokumentation des aktuellen Interesses des',
                'Creators an einer möglichen zukünftigen Nutzung von Clero.',
                '',
                'Sie ist rechtlich unverbindlich und begründet weder eine Verpflichtung zur Nutzung,',
                'zum Kauf, zur Zahlung noch zur exklusiven Zusammenarbeit mit Clero. Eine tatsächliche',
                'Nutzung der Plattform setzt insbesondere Produktverfügbarkeit, den finalen',
                'Funktionsumfang und die beiderseitige Abstimmung voraus.',
            ]),
            ('6. Referenznutzung', [
                'Der Creator erklärt sich damit einverstanden, dass Clero seinen Namen, sein Handle',
                'und sein Profilbild zu Referenzzwecken in der externen Kommunikation verwenden darf,',
                'insbesondere auf der Website, in Pitch-Unterlagen und in Gesprächen mit potenziellen',
                'Investor:innen.',
                '',
                'Eine solche Nutzung erfolgt ausschließlich zu Referenzzwecken und kann jederzeit mit',
                'Wirkung für die Zukunft widerrufen werden.',
            ]),
        ],
        'sig_h': '7. Unterschriften',
        'sig_creator': 'Creator',
        'l_name': 'Name:',
        'l_handle': 'Haupt-Kanal / Handle:',
        'l_contact': 'E-Mail / Telefonnummer:',
        'l_ortdatum': 'Ort, Datum:',
        'l_sig': 'Unterschrift:',
        'sig_clero': 'Gründer von Clero',
        'l_name2': 'Name: Tjard Püschel',
        'l_role2': 'Rolle: Gründer',
        'l_ortdatum2': 'Ort, Datum: München,',
        'foot': 'Clero UG (haftungsbeschränkt) i.G.  ·  clero.de  ·  n.emrich@clero.de',
    },
    'en': {
        'file': 'clero-creator-loi-en.pdf',
        'title': 'LETTER OF INTENT',
        'sub': 'Founding Creator Programme Munich',
        'intro': 'This letter of intent is entered into between',
        'party_a_suffix': ', hereinafter the “Creator”,',
        'party_b': ['and Clero UG (haftungsbeschränkt) (in formation), represented by Tjard Püschel,', 'Founder.'],
        'sections': [
            ('1. Background', [
                'Clero is building a platform for creating, organising and finding local groups and',
                'communities. Creators can use Clero to build their own community in their niche,',
                'organise meet-ups and events, and be discovered locally.',
            ]),
            ('2. Interest in using Clero', [
                'The Creator expresses general interest in using Clero from August 2026, as part of',
                'Clero’s public launch in Munich, provided the relevant features are available as',
                'planned.',
                '',
                'The Creator intends to use Clero in particular to build a community, to organise',
                'events and recurring meet-ups, and to become visible locally.',
            ]),
            ('3. Creator details', None),
            ('4. Founding Creator Programme', [
                'Clero intends to include the Creator in the Founding Creator Programme for Munich.',
                'The programme includes special visibility at launch, priority placement in the app',
                'and direct support from the Clero team.',
                '',
                'Participation in the programme is free of charge for the Creator. Specific terms are',
                'agreed individually.',
            ]),
        ],
        'f_theme': 'Topic / niche:',
        'f_channels': 'Channels (Instagram / TikTok / other):',
        'f_reach': 'Community / reach (approx.):',
        'sections2': [
            ('5. Non-binding nature', [
                'This declaration serves solely to document the Creator’s current interest in a possible',
                'future use of Clero.',
                '',
                'It is legally non-binding and creates no obligation to use, purchase, pay for or work',
                'exclusively with Clero. Actual use of the platform depends in particular on product',
                'availability, the final feature set and mutual agreement.',
            ]),
            ('6. Reference use', [
                'The Creator agrees that Clero may use their name, handle and profile picture for',
                'reference purposes in external communication, in particular on the website, in pitch',
                'materials and in conversations with potential investors.',
                '',
                'Such use is for reference purposes only and can be revoked at any time with effect',
                'for the future.',
            ]),
        ],
        'sig_h': '7. Signatures',
        'sig_creator': 'Creator',
        'l_name': 'Name:',
        'l_handle': 'Main channel / handle:',
        'l_contact': 'Email / phone number:',
        'l_ortdatum': 'Place, date:',
        'l_sig': 'Signature:',
        'sig_clero': 'Founder of Clero',
        'l_name2': 'Name: Tjard Püschel',
        'l_role2': 'Role: Founder',
        'l_ortdatum2': 'Place, date: Munich,',
        'foot': 'Clero UG (haftungsbeschränkt) i.G.  ·  clero.de  ·  n.emrich@clero.de',
    },
}


def build(lang):
    t = TEXT[lang]
    coords = {}
    c = canvas.Canvas(t['file'], pagesize=A4)

    def header():
        c.setFillColor(ACCENT)
        c.rect(0, H - 8, W, 8, stroke=0, fill=1)

    def footer():
        c.setFillColor(LINE)
        c.rect(M, 46, W - 2 * M, 0.6, stroke=0, fill=1)
        c.setFont('Helvetica', 7.6)
        c.setFillColor(GREY)
        c.drawString(M, 34, t['foot'])

    def rule(y):
        c.setFillColor(LINE)
        c.rect(M, y, W - 2 * M, 0.6, stroke=0, fill=1)

    def dotted(x, y, w):
        """Ausfuell-Linie zeichnen und Stempel-Koordinate zurueckgeben."""
        c.setFillColor(LINE)
        c.rect(x, y - 3.5, w, 0.6, stroke=0, fill=1)
        return {'x': round(x + 3, 1), 'y': round(y, 1)}

    # ---------------- Seite 1 ----------------
    header()
    y = H - 62

    c.setFont('Helvetica-Bold', 15)
    c.setFillColor(GREEN)
    c.drawString(M, y, t['title'])
    y -= 17
    c.setFont('Helvetica', 10)
    c.setFillColor(GREY)
    c.drawString(M, y, t['sub'])
    y -= 16
    rule(y)
    y -= 26

    c.setFont('Helvetica', BODY)
    c.setFillColor(INK)
    c.drawString(M, y, t['intro'])
    y -= 22

    # Vertragspartei A: Creator-Name auf Linie
    coords['cName'] = {'p': 0, **dotted(M, y, 240)}
    c.setFont('Helvetica', BODY)
    c.setFillColor(INK)
    c.drawString(M + 246, y, t['party_a_suffix'])
    y -= 24

    for ln in t['party_b']:
        c.drawString(M, y, ln)
        y -= LEAD
    y -= 14

    def section(title, lines):
        nonlocal y
        c.setFont('Helvetica-Bold', 10.6)
        c.setFillColor(GREEN)
        c.drawString(M, y, title)
        y -= 17
        c.setFont('Helvetica', BODY)
        c.setFillColor(INK)
        for ln in lines:
            if ln:
                c.drawString(M, y, ln)
            y -= LEAD if ln else 7
        y -= 12

    for title, lines in t['sections']:
        if lines is None:
            # Angaben-Block mit Ausfuell-Linien
            c.setFont('Helvetica-Bold', 10.6)
            c.setFillColor(GREEN)
            c.drawString(M, y, title)
            y -= 20
            c.setFont('Helvetica', BODY)
            for key, label, lw in (('cTheme', t['f_theme'], 300),
                                   ('cChannels', t['f_channels'], 220),
                                   ('cReach', t['f_reach'], 300)):
                c.setFillColor(INK)
                c.drawString(M, y, label)
                lx = M + c.stringWidth(label, 'Helvetica', BODY) + 8
                coords[key] = {'p': 0, **dotted(lx, y, min(lw, W - M - lx))}
                y -= 22
            y -= 6
        else:
            section(title, lines)

    footer()
    c.showPage()

    # ---------------- Seite 2 ----------------
    header()
    y = H - 62
    c.setFont('Helvetica', BODY)

    for title, lines in t['sections2']:
        section(title, lines)

    y -= 4
    rule(y)
    y -= 24

    c.setFont('Helvetica-Bold', 11.5)
    c.setFillColor(GREEN)
    c.drawString(M, y, t['sig_h'])
    y -= 24

    # -- Creator-Block
    c.setFont('Helvetica-Bold', 9.6)
    c.setFillColor(GREY)
    c.drawString(M, y, t['sig_creator'].upper())
    y -= 20

    c.setFont('Helvetica', BODY)
    for key, label, lw in (('sName', t['l_name'], 300),
                           ('sHandle', t['l_handle'], 300),
                           ('sContact', t['l_contact'], 300),
                           ('sOrtDatum', t['l_ortdatum'], 300)):
        c.setFillColor(INK)
        c.drawString(M, y, label)
        lx = M + c.stringWidth(label, 'Helvetica', BODY) + 8
        coords[key] = {'p': 1, **dotted(lx, y, min(lw, W - M - lx))}
        y -= 24

    y -= 18   # extra Luft, damit die Unterschrift nicht in die Zeile darueber laeuft
    c.setFillColor(INK)
    c.drawString(M, y, t['l_sig'])
    sigx = M + c.stringWidth(t['l_sig'], 'Helvetica', BODY) + 10
    c.setFillColor(LINE)
    c.rect(sigx, y - 4, 210, 0.6, stroke=0, fill=1)
    coords['sSign'] = {'p': 1, 'x': round(sigx + 6, 1), 'y': round(y - 1, 1), 'w': 120, 'h': 32}
    y -= 40

    rule(y)
    y -= 24

    # -- Clero-Block
    c.setFont('Helvetica-Bold', 9.6)
    c.setFillColor(GREY)
    c.drawString(M, y, t['sig_clero'].upper())
    y -= 20
    c.setFont('Helvetica', BODY)
    c.setFillColor(INK)
    c.drawString(M, y, t['l_name2'])
    y -= 22
    c.drawString(M, y, t['l_role2'])
    y -= 22
    c.drawString(M, y, t['l_ortdatum2'])
    lx = M + c.stringWidth(t['l_ortdatum2'], 'Helvetica', BODY) + 8
    coords['tjard'] = {'p': 1, **dotted(lx, y, 150)}
    y -= 26

    c.setFillColor(INK)
    c.drawString(M, y, t['l_sig'])
    c.setFillColor(LINE)
    c.rect(M + c.stringWidth(t['l_sig'], 'Helvetica', BODY) + 10, y - 4, 210, 0.6, stroke=0, fill=1)

    footer()
    c.showPage()
    c.save()
    return coords


out = {}
for lang in ('de', 'en'):
    out[lang] = {'url': TEXT[lang]['file'], **build(lang)}

print(json.dumps(out, indent=2, ensure_ascii=False))
