#!/usr/bin/env python3
"""Erzeugt clero-loi.pdf (DE) und clero-loi-en.pdf (EN) - das Host-LOI fuer die
Founding-30-Bewerbung (eintragen.html / verzeichnis.html).

Basiert inhaltlich auf dem am 2026-09-10 zugelieferten Word-Template
"Clero_LOI_Template_EN.docx" (Version 2.0, September 2026). Deutsche Fassung
ist eine Uebersetzung davon.

Gleiches Prinzip wie build_creator_loi.py: die Seiten werden so gebaut, dass
die Stempel-Koordinaten fuer pdf-lib (Client-seitiges Befuellen im Browser)
exakt bekannt sind. Das Skript gibt am Ende ein JS-Objekt aus, das 1:1 als
LOI_FIELDS in eintragen.html / verzeichnis.html kann.

Unterschied zu build_creator_loi.py: hier wird mit einem laufenden y-Cursor
und automatischem Seitenumbruch gearbeitet (das neue Template hat deutlich
mehr Inhalt als das Creator-LOI), statt mit fest verdrahteten y-Werten.
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
BOTTOM = 60           # unterhalb dieser y-Position wird umgebrochen
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
        'file': 'clero-loi.pdf',
        'title': 'LETTER OF INTENT / ABSICHTSERKLÄRUNG',
        'sub': 'Version 2.0 · September 2026',
        'intro': 'Diese Absichtserklärung wird geschlossen zwischen',
        'communityTable': [
            ('Name der Community', 'gname'),
            ('Rechtsform / Art', 'legalform'),
            ('Adresse / Sitz', 'address'),
            ('Vertreten durch (Name)', 'cRepName'),
            ('Rolle / Funktion', 'cRole'),
            ('E-Mail', 'cEmail'),
            ('Telefon (optional)', 'cPhone'),
            ('Instagram / Website', 'cLink'),
        ],
        'hereinafterCommunity': '– nachfolgend „die Community" –',
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
                'Clero entwickelt eine Plattform für die Sichtbarkeit, Organisation und das Auffinden lokaler '
                'Gruppen und Communities. Communities können darüber ihre Mitglieder verwalten, Events organisieren '
                'und intern kommunizieren.',
            ]),
        ],
        's2h': '2. Angaben zur Community',
        's2intro': 'Die folgenden Angaben macht die Community nach bestem Wissen. Clero darf sie in der in Abschnitt 5 beschriebenen Weise verwenden.',
        'membersTable': [
            ('Aktive Mitglieder', 'members'),
            ('Stand (Datum)', 'asOf'),
            ('Grundlage der Zählung', 'z.B. Mitglieder der WhatsApp-Gruppe, Newsletter-Abonnent:innen, Teilnehmer:innen der letzten drei Monate'),
            ('Vorgesehene:r Host bei Clero', 'host'),
        ],
        'activeDef': 'Aktives Mitglied ist, wer innerhalb der letzten drei Monate an mindestens einer Aktivität der '
                      'Community teilgenommen hat oder Mitglied des Hauptkanals der Community ist (z.B. WhatsApp-Gruppe, '
                      'Newsletter, Mitgliederliste).',
        'sections2': [
            ('3. Beabsichtigte Nutzung', [
                'Die Community bekundet ihr grundsätzliches Interesse, Clero ab dem öffentlichen Start von Clero in '
                'München zu nutzen, sofern die für die Community relevanten Funktionen verfügbar sind.',
                'Die Community beabsichtigt, Clero insbesondere für die Organisation der Community, mehr Sichtbarkeit '
                'sowie die Koordination von Events und die gemeinsame Kommunikation zu nutzen.',
                'Darüber hinaus beabsichtigt die Community:',
                'a)  an einem gemeinsamen Onboarding-Termin mit Clero teilzunehmen;',
                'b)  eine:n Host zu benennen, der/die die Community auf Clero einrichtet und betreut;',
                'c)  ihre Mitglieder einmalig innerhalb von 30 Tagen nach dem Start über die Community auf Clero zu informieren.',
                'Diese Absichten sind ausdrücklich unverbindlich (siehe Abschnitt 4).',
            ]),
            ('4. Unverbindlichkeit', [
                'Diese Erklärung dient ausschließlich der Dokumentation des aktuellen Interesses der Community an '
                'einer möglichen zukünftigen Nutzung von Clero.',
                'Sie ist rechtlich unverbindlich und begründet weder eine Verpflichtung zur Nutzung der Plattform, '
                'zum Kauf, zur Zahlung noch zu einer exklusiven Partnerschaft. Eine tatsächliche Nutzung setzt '
                'insbesondere Produktverfügbarkeit, den finalen Funktionsumfang und eine gesonderte Vereinbarung voraus.',
                'Jede Partei kann diese Erklärung jederzeit in Textform ohne Angabe von Gründen beenden.',
            ]),
            ('5. Referenznutzung', [
                'Die Community erlaubt Clero, ihren Namen und ihr Logo zu Referenzzwecken in der externen '
                'Kommunikation zu verwenden, insbesondere auf der Website, in Präsentations- und Pitch-Unterlagen, '
                'in Gesprächen mit potenziellen Investor:innen sowie in einem Investoren-Datenraum.',
                'In diesem Zusammenhang darf Clero auch die unter Abschnitt 2 angegebene Mitgliederzahl nennen.',
                'Eine solche Nutzung erfolgt ausschließlich zu Referenzzwecken und kann jederzeit mit Wirkung für die '
                'Zukunft in Textform widerrufen werden.',
            ]),
            ('6. Daten und Vertraulichkeit', [
                'Mit Unterzeichnung dieser Erklärung werden keine personenbezogenen Daten von Mitgliedern an Clero '
                'übermittelt. Jede spätere Verarbeitung personenbezogener Daten bedarf einer gesonderten, rechtlich '
                'zulässigen Grundlage.',
                'Beide Parteien behandeln vertrauliche Informationen, die im Rahmen ihrer Gespräche ausgetauscht '
                'werden, vertraulich.',
            ]),
        ],
        'sig_h': '7. Unterschriften',
        'sig_community': 'Für die Community',
        'sig_clero': 'Für die Clero GmbH',
        'communitySig': [
            ('Name (Vor- und Nachname)', 'sName'),
            ('Rolle / Funktion', 'sRole'),
            ('Ort, Datum', 'sPlace'),
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
        'file': 'clero-loi-en.pdf',
        'title': 'LETTER OF INTENT',
        'sub': 'Version 2.0 · September 2026',
        'intro': 'This Letter of Intent is entered into between',
        'communityTable': [
            ('Name of the community', 'gname'),
            ('Legal form / type', 'legalform'),
            ('Address or seat', 'address'),
            ('Represented by (name)', 'cRepName'),
            ('Role / function', 'cRole'),
            ('Email', 'cEmail'),
            ('Phone (optional)', 'cPhone'),
            ('Instagram / website', 'cLink'),
        ],
        'hereinafterCommunity': '– hereinafter "the Community" –',
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
                'Clero is developing a platform for the discovery, organisation and visibility of local groups and '
                'communities. Communities can use it to manage their members, organise events and communicate '
                'internally.',
            ]),
        ],
        's2h': '2. Information about the community',
        's2intro': 'The following information is provided by the Community to the best of its knowledge. Clero may use it in the manner described in section 5.',
        'membersTable': [
            ('Active members', 'members'),
            ('As of (date)', 'asOf'),
            ('Basis of the count', 'e.g. members of the WhatsApp group, newsletter subscribers, participants over the last three months'),
            ('Intended host on Clero', 'host'),
        ],
        'activeDef': 'An active member is a person who has taken part in at least one activity of the Community '
                      'within the last three months, or who is a member of the Community’s main channel (e.g. '
                      'WhatsApp group, newsletter, membership list).',
        'sections2': [
            ('3. Intended use', [
                'The Community expresses its general interest in using Clero from the public launch of Clero in '
                'Munich onwards, provided that the functionalities relevant to the Community are available.',
                'The Community intends to use Clero in particular for community organisation, increased visibility, '
                'and the coordination of events and shared communication.',
                'In addition, the Community intends to:',
                'a)  take part in a joint onboarding session with Clero;',
                'b)  appoint a host who will set up and manage the Community on Clero;',
                'c)  inform its members once about the Community on Clero within 30 days of the launch.',
                'These intentions are expressly non-binding (see section 4).',
            ]),
            ('4. Non-binding nature', [
                'This declaration serves solely to document the Community’s current interest in a possible '
                'future use of Clero.',
                'It is legally non-binding and does not create any obligation to use the platform, to purchase, to '
                'pay, or to enter into an exclusive partnership. Any actual use is subject to product availability, '
                'the final scope of features, and a separate agreement.',
                'Either party may end this declaration at any time in text form without giving reasons.',
            ]),
            ('5. Reference use', [
                'The Community permits Clero to use its name and logo for reference purposes in external '
                'communication, in particular on the website, in presentation and pitch materials, in conversations '
                'with potential investors, and in an investor data room.',
                'In this context, Clero may also state the membership figure provided under section 2.',
                'Such use is strictly for reference purposes and may be revoked at any time in text form with effect '
                'for the future.',
            ]),
            ('6. Data and confidentiality', [
                'No personal data of members is transferred to Clero by signing this declaration. Any later '
                'processing of personal data requires a separate and legally permissible basis.',
                'Both parties will treat confidential information exchanged during their discussions as '
                'confidential.',
            ]),
        ],
        'sig_h': '7. Signatures',
        'sig_community': 'For the Community',
        'sig_clero': 'For Clero GmbH',
        'communitySig': [
            ('Name (first and last)', 'sName'),
            ('Role / function', 'sRole'),
            ('Place, date', 'sPlace'),
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
        """Eine Tabellenzeile: Label links, danach entweder ein statischer Wert
        (static=True) oder eine Ausfuelllinie mit Stempel-Koordinate."""
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

    for label, key in t['communityTable']:
        field_row(label, key, static=False)
    y[0] -= 4
    para(t['hereinafterCommunity'], font='Helvetica-Oblique', color=GREY)
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

    # ---------------- Abschnitt 2: Angaben zur Community ----------------
    heading(t['s2h'])
    para(t['s2intro'])
    y[0] -= 4
    for label, key in t['membersTable']:
        static = label in (t['membersTable'][2][0],)  # nur "Grundlage der Zaehlung" ist statisch
        field_row(label, key, static=static)
    y[0] -= 4
    c.setFont('Helvetica-Oblique', 8.4)
    c.setFillColor(GREY)
    for ln in wrap(t['activeDef'], 'Helvetica-Oblique', 8.4, W - 2 * M):
        ensure(12)
        c.setFont('Helvetica-Oblique', 8.4)
        c.setFillColor(GREY)
        c.drawString(M, y[0], ln)
        y[0] -= 12
    y[0] -= 8

    for title, lines in t['sections2']:
        heading(title)
        for ln in lines:
            para(ln)
        y[0] -= 4

    # ---------------- Abschnitt 7: Unterschriften ----------------
    ensure(196)  # Community-Unterschriftsblock (Heading+Zeilen+Signatur) nicht auseinanderreissen
    rule(gap_before=6, gap_after=18)
    c.setFont('Helvetica-Bold', 11.5)
    c.setFillColor(GREEN)
    c.drawString(M, y[0], t['sig_h'])
    y[0] -= 22

    c.setFont('Helvetica-Bold', 9.2)
    c.setFillColor(GREY)
    c.drawString(M, y[0], t['sig_community'].upper())
    y[0] -= 18
    for label, key in t['communitySig']:
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

    ensure(184)  # Clero-Unterschriftsblock (Trenner+Heading+Zeilen+Signatur) nicht auseinanderreissen
    rule(gap_before=4, gap_after=18)
    c.setFont('Helvetica-Bold', 9.2)
    c.setFillColor(GREY)
    c.drawString(M, y[0], t['sig_clero'].upper())
    y[0] -= 18
    for label, value in t['cleroSig']:
        field_row(label, value, static=True)
    field_row(t['l_ortdatum2'], 'tjardDate', static=False)

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
