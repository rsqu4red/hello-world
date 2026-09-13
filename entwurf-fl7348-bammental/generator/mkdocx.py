# -*- coding: utf-8 -*-
"""Erläuterungsbericht (DOCX) zum Vorentwurf Wochenendhaus Fl. 7348."""
import sys, os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

OUT = sys.argv[1]
PNG = sys.argv[2]
doc = Document()
for s in doc.sections:
    s.page_height = Cm(29.7); s.page_width = Cm(21.0)
    s.left_margin = s.right_margin = Cm(2.2); s.top_margin = Cm(2.0); s.bottom_margin = Cm(2.0)
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)

def H(t, lvl=1):
    p = doc.add_heading(t, level=lvl)
    for r in p.runs: r.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)
    return p
def P(t, bold=False, italic=False, size=None, align=None):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if align: p.alignment = align
    p.paragraph_format.space_after = Pt(6)
    return p
def B(items):
    for it in items:
        p = doc.add_paragraph(it, style="List Bullet"); p.paragraph_format.space_after = Pt(2)
def T(rows, header=True, widths=None):
    t = doc.add_table(rows=0, cols=len(rows[0])); t.style = "Light Grid Accent 1"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, r in enumerate(rows):
        cells = t.add_row().cells
        for j, c in enumerate(r):
            cells[j].text = ""
            run = cells[j].paragraphs[0].add_run(str(c)); run.font.size = Pt(9)
            if header and i == 0: run.bold = True
            if widths: cells[j].width = Cm(widths[j])
    doc.add_paragraph()
    return t
def IMG(name, w=16.5, cap=None):
    p = os.path.join(PNG, name)
    if os.path.exists(p):
        doc.add_picture(p, width=Cm(w))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        if cap: P(cap, italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)

# ---------------------------------------------------------------- Titel
P("ERLÄUTERUNGSBERICHT ZUM VORENTWURF", bold=True, size=16)
P("Neubau eines Wochenendhauses in Holzbauweise", bold=True, size=13)
P("Grenzweg 12 · 69245 Bammental · Gemarkung Bammental · Flurstück 7348")
P("Bebauungsplan „Wochenendhausgebiet – 1. Änderung (Neufassung)“ der Gemeinde Bammental (Plan-Nr. BP 0806, Büro Piske, Satzungsbeschluss 11.09.2008, in Kraft 19.09.2008)")
P("Bauherr: Familie Schneider · Stand: Vorentwurf 09/2026 · Zweck: Vorabstimmung mit der Gemeinde Bammental und der unteren Baurechtsbehörde vor Einreichung des Bauantrags", size=9.5)
P("Hinweis: Dieser Vorentwurf dient der planungsrechtlichen Vorabstimmung (Bauvoranfrage). Bauantrag, Statik, Wärmeschutznachweis und amtlicher Lageplan folgen durch bauvorlageberechtigte Entwurfsverfasser bzw. Vermesser.", italic=True, size=9)

# ---------------------------------------------------------------- 1
H("1. Anlass und Ziel")
P("Der Bauherr beabsichtigt, auf dem Flurstück 7348 im Sondergebiet „Wochenendhausgebiet“ ein Wochenendhaus zu errichten. Für das Grundstück setzt der Bebauungsplan ein Baufenster von ca. 7,20 × 5,20 m (37,44 m², aus dem Plan abgegriffen: 8,29 mm × 5,98 mm bei 34,50 mm = 30 m) fest. Es ist das einzige Baufenster im Plangebiet, das innerhalb des 30-m-Waldabstandsstreifens liegt.")
P("Ziel der Vorabstimmung ist es, (1) die Genehmigungsfähigkeit eines zeitgemäßen, natürlich gestalteten Holzhauses im Baufenster zu klären (Variante A) und (2) die Haltung der Gemeinde zu einer moderaten Überschreitung der Baugrenze bei Einhaltung der zulässigen Grundfläche von 65 m² abzufragen (Variante B, Befreiung nach § 31 Abs. 2 BauGB).")

# ---------------------------------------------------------------- 2
H("2. Grundstück und Umgebung")
B([
    "Lage: Nordost-Ecke des Plangebiets am Grenzweg; im Osten grenzt der Wald (außerhalb des Geltungsbereichs) unmittelbar an, im Westen und Süden liegen weitere Wochenendhausgrundstücke (7349, 7354).",
    "Bestand: offene, leicht geneigte Wiese; Gehölzsaum am Waldrand; keine Fällungen für das Vorhaben erforderlich. Vorhandene Bäume außerhalb des Baufensters bleiben gemäß Festsetzung 9 erhalten.",
    "Umgebung: kleinmaßstäbliche, eingeschossige Wochenendhäuser mit Satteldächern; Baukörper treten hinter dem Baumbestand zurück.",
    "Erschließung: über den Grenzweg; Trinkwasser-, Abwasser- (Trennsystem) und Stromanschluss werden mit der Gemeinde abgestimmt.",
    "Grundstücksgröße: gemäß Liegenschaftskataster (Mindestgröße lt. Festsetzung 4: 900 m²) – Katasterauszug wird dem Bauantrag beigefügt.",
])

# ---------------------------------------------------------------- 3
H("3. Entwurfskonzept")
P("Das Haus greift die Archetyp-Form der Wochenendhäuser im Gebiet auf – ein einfacher, eingeschossiger Baukörper mit Satteldach – und übersetzt sie in eine ruhige, natürliche Holzarchitektur:")
B([
    "Ein einziges, klares Volumen ohne Anbauten, Gauben oder Dachaufbauten; First parallel zur langen Seite (Ost–West).",
    "Steiles Satteldach (Variante A 45°, Variante B 38°) unter der zulässigen Firsthöhe von 5,50 m; Deckung aus matt beschichtetem, anthrazitfarbenem Stehfalzblech (kein unbeschichtetes Kupfer/Zink/Blei – Festsetzung 7.1). Alternativ extensive Dachbegrünung (Hinweis des B-Plans).",
    "Fassade aus unbehandelter, sägerauer Lärche in horizontaler Schalung, die in wenigen Jahren gleichmäßig silbergrau vergraut und sich farblich in Rinde, Schatten und Waldboden einfügt. Keine Putzflächen, keine glänzenden Oberflächen.",
    "Die einzige große Öffnung – eine bodentiefe Hebe-Schiebetür – richtet sich nach Süden zur eigenen Wiese. Zum Grenzweg (Nord) und zum Wald (Ost) bleibt das Haus mit wenigen kleinen Fenstern ruhig und geschlossen.",
    "Ein hölzerner Schiebeladen aus vertikalen Lärchenlatten dient als Sonnen-, Sturm- und Einbruchschutz und lässt das Haus bei Abwesenheit als geschlossenen Holzkörper erscheinen.",
    "Eine niedrige, unüberdachte Holzterrasse (3,0 m tief, gesamte Gebäudebreite, Festsetzung 5.1) legt das Haus in die Wiese; keine Geländer, keine Überdachung.",
    "Gründung auf Punkt-/Schraubfundamenten mit hinterlüftetem Kriechraum: minimaler Bodeneingriff, kein Keller, keine Bodenplatte, rückbaubar. Fußbodenoberkante ca. 0,20–0,30 m über Gelände (Festsetzung 2.2).",
    "Vorgefertigter Holzrahmenbau mit Holzfaserdämmung – kurze Bauzeit am empfindlichen Waldrand.",
])
IMG("06_Isometrie_A.png", 15.5, "Abb. 1: Schema-Isometrie Variante A (Blatt 6 der Planmappe)")

# ---------------------------------------------------------------- 4
H("4. Varianten")
H("4.1 Variante A – Bebauung im Baufenster (Regelfall)", 2)
P("Außenmaß 7,20 × 5,20 m = 37,44 m² Grundfläche; Außenkante Gebäude = Baugrenze. Dachüberstände (Traufe 0,40 m, Ortgang 0,30 m) liegen innerhalb der Maße der örtlichen Bauvorschriften (Traufe max. 0,80 m, Ortgang 0,20–0,60 m) und treten als untergeordnete Bauteile geringfügig über die Baugrenze (§ 23 Abs. 3 i. V. m. Abs. 2 Satz 2 BauNVO).")
T([["Raum", "Fläche"], ["Wohnen / Essen / Kochen", "17,9 m²"], ["Schlafen", "7,0 m²"], ["Bad / WC / Technik", "4,7 m²"], ["Wohnfläche EG netto", "≈ 29,6 m²"],
   ["Schlafempore (optional, kein Vollgeschoss)", "≈ 12,0 m²"], ["Terrasse (unüberdacht)", "21,6 m²"]], widths=[10, 4])
P("Kennwerte: Traufhöhe 2,70 m, Firsthöhe 5,30 m über FOK EG (zul. 5,50 m), Dachneigung 45°, I Vollgeschoss, offene Bauweise.")
IMG("03_Grundriss_A.png", 16.5, "Abb. 2: Grundriss EG Variante A (Blatt 3)")
IMG("04_Ansichten_A.png", 16.5, "Abb. 3: Ansichten Variante A (Blatt 4)")

H("4.2 Variante B – 8,40 × 6,80 m (Antrag auf Befreiung von der Baugrenze)", 2)
P("Außenmaß 8,40 × 6,80 m = 57,12 m² Grundfläche (zulässige GR 65 m² eingehalten). Das Maß entspricht der nach den örtlichen Bauvorschriften ohnehin überdachbaren Fläche (Baufenster + max. Dachüberstand 0,80 m Traufe / 0,60 m Ortgang: 8,40 × 6,80 m). Die Baugrenze wird je Seite um 0,60 m (Traufseiten) bzw. 0,80 m (Giebelseiten) überschritten; das Haus wird dafür mit sehr kurzen Dachüberständen (0,40 / 0,30 m) ausgeführt, so dass die überdachte Gesamtfläche (9,00 × 7,60 m) nur unwesentlich größer ist als bei einem Haus im Baufenster mit maximalem Dachüberstand.")
T([["Raum", "Fläche"], ["Wohnen / Essen / Kochen", "28,5 m²"], ["Schlafen", "12,1 m²"], ["Bad / WC / Technik", "6,8 m²"], ["Wohnfläche EG netto", "≈ 47,4 m²"], ["Terrasse", "25,2 m²"]], widths=[10, 4])
P("Kennwerte: Traufhöhe 2,60 m, Firsthöhe 5,26 m, Dachneigung 38°, I Vollgeschoss.")
IMG("07_Grundriss_B.png", 16.5, "Abb. 4: Grundriss EG Variante B (Blatt 7)")

H("4.3 Begründung des Befreiungsantrags (Variante B), § 31 Abs. 2 BauGB", 2)
B([
    "Grundzüge der Planung nicht berührt: Art der Nutzung (Wochenendhaus), Zahl der Vollgeschosse (I), Firsthöhe (≤ 5,50 m), offene Bauweise und die maximale Grundfläche von 65 m² werden eingehalten. Die Baugrenze dient hier der Lage des Baukörpers auf dem Grundstück, nicht der Begrenzung des Bauvolumens – dieses regelt die GR von 65 m².",
    "Städtebaulich vertretbar: Die Überschreitung liegt vollständig innerhalb der Fläche, die nach den örtlichen Bauvorschriften mit Dachüberständen ohnehin überdacht werden darf (8,40 × 6,80 m). Nach außen ist kein größerer Baukörper wahrnehmbar als bei einem Haus im Baufenster mit maximalem Dachüberstand.",
    "Keine Nachteile für den Forst: Der Abstand zum Waldrand verringert sich um lediglich 0,80 m; das Baufenster liegt bereits planerisch im 30-m-Streifen. Keine Fällungen, keine Nebengebäude im Waldabstand.",
    "Keine Nachteile für Nachbarn: Abstandsflächen nach LBO werden eingehalten (Ostseite ≈ 3,4 m zur Grenze, übrige Seiten deutlich mehr); keine Verschattung, keine Einsicht (geschlossene Nord-/Ostfassaden).",
    "Kein Präzedenzfall: Das Flurstück 7348 ist das einzige Baugrundstück, dessen Baufenster im Waldabstandsstreifen liegt; die Situation ist nicht auf andere Grundstücke übertragbar.",
    "Vorteil für Bauqualität und Klimaschutz: Massivere, energieeffizientere Konstruktion mit größerem Dämmquerschnitt; Wärmebrücken und Materialverschnitt verringern sich bei Wandlängen im Rastermaß der Holzbauvorfertigung.",
    "Interessen der Allgemeinheit gewahrt; Vorhaben ist mit den öffentlichen Belangen vereinbar (§ 31 Abs. 2 Nr. 2 BauGB: städtebaulich vertretbar).",
])

# ---------------------------------------------------------------- 5
H("5. Nachweis der Festsetzungen des Bebauungsplans")
T([
    ["Nr.", "Festsetzung", "Anforderung", "Variante A", "Variante B"],
    ["1.1", "Art der Nutzung SO Wochenendhaus", "nur Wochenendhäuser", "✔", "✔"],
    ["NS", "Grundfläche GR max.", "65 m²", "37,44 m² ✔", "57,12 m² ✔"],
    ["NS", "Vollgeschosse", "I", "I ✔ (Empore kein VG)", "I ✔"],
    ["NS", "Bauweise", "offen", "✔", "✔"],
    ["§ 9 (1) 2", "Baugrenze", "7,20 × 5,20 m", "✔ (Dachüberstand untergeordnet)", "Befreiung § 31 (2) BauGB"],
    ["2.1", "GRZ inkl. Nebenanlagen", "≤ 0,15", "≈ 0,09 (bei 900 m²) ✔", "≈ 0,12 ✔"],
    ["2.2", "FOK EG über Gelände", "bergs. ≤ 0,20 / tals. ≤ 0,80 m", "≈ 0,20–0,30 m ✔", "✔"],
    ["2.3", "Firsthöhe ab FOK EG", "≤ 5,50 m", "5,30 m ✔", "5,26 m ✔"],
    ["3", "Abstand seitl. Grenzen (Flächen [1])", "≥ 5,0 m", "nicht [1]-Fläche; LBO ≥ 2,5 m ✔", "✔"],
    ["4", "Mindestgrundstücksgröße", "900 m²", "Kataster", "Kataster"],
    ["5.1", "Terrasse", "ganze Breite, ≤ 6,0 m tief", "7,20 × 3,00 m ✔", "8,40 × 3,00 m ✔"],
    ["5.2", "Garage/Carport/überdachter Sitzplatz", "nur im Baufenster", "keine ✔", "keine ✔"],
    ["7.1", "Dachflächen", "kein unbesch. Cu/Zn/Pb", "beschichtetes Stehfalzblech ✔", "✔"],
    ["7.2", "Stellplätze/Wege", "wasserdurchlässig", "Schotterrasen/Kies ✔", "✔"],
    ["9", "Baumbestand außerhalb Baufenster", "erhalten", "✔", "✔"],
    ["öBV § 3", "Dachüberstand Traufe / Ortgang", "≤ 0,80 / 0,20–0,60 m", "0,40 / 0,30 m ✔", "0,40 / 0,30 m ✔"],
    ["Hinw.", "Zisterne", "≥ 0,02 m³/m² Dach", "3 m³ ✔", "3 m³ ✔"],
    ["LBO § 4 (3)", "Waldabstand 30 m", "Ausnahme Baurechtsbehörde/Forst", "beantragen", "beantragen"],
], widths=[1.6, 4.2, 3.6, 3.6, 3.6])

# ---------------------------------------------------------------- 6
H("6. Konstruktion, Material, Technik")
T([
    ["Bauteil", "Ausführung"],
    ["Gründung", "Punkt-/Schraubfundamente frostfrei, Holzbalkendecke gedämmt, hinterlüfteter Kriechraum; keine Bodenplatte, kein Keller"],
    ["Außenwand ≈ 30 cm", "Lärche sägerau 24 mm horizontal, offene Fuge; Konterlattung; Holzrahmen 60/200 mit Holzfaserdämmung; Installationsebene; Innenbekleidung Fichte/Tanne weiß lasiert"],
    ["Dach", "Sparren 80/240 gedämmt; diffusionsoffene Unterdeckbahn; Hinterlüftung; Doppelstehfalz aus beschichtetem Stahl-/Aluminiumblech, anthrazit matt (RAL 7016/7022). Option: extensives Gründach"],
    ["Fenster/Türen", "Holz-Alu, außen anthrazit, 3-fach-Verglasung; Hebe-Schiebetür Süd; Schiebeladen aus Lärchenlatten"],
    ["Terrasse", "Lärche/Douglasie, aufgeständert auf Stelzlagern, ca. 0,30 m über Gelände, ohne Geländer, unüberdacht"],
    ["Heizung", "Kaminofen (Wochenendnutzung) + elektrische Direktheizung/Infrarot; keine Öl-/Gastanks"],
    ["Wasser", "Trinkwasser und Abwasser gemäß Vorgaben der Gemeinde (Trennsystem); Regenwasser in Zisterne ≥ 3 m³, Überlauf versickernd"],
    ["Außenanlagen", "Kiesweg, 1 Stellplatz 5,0 × 2,5 m als Schotterrasen, Bestandsbäume erhalten, Wildwiese belassen"],
    ["Photovoltaik (Option)", "dachintegrierte, matte Module in Dachfarbe auf der Südfläche"],
], widths=[3.5, 13])

# ---------------------------------------------------------------- 7
H("7. Offene Punkte / Fragen an die Gemeinde")
B([
    "Bestätigung, dass Dachüberstände im Rahmen der örtlichen Bauvorschriften (Traufe ≤ 0,80 m, Ortgang 0,20–0,60 m) als untergeordnete Bauteile über die Baugrenze treten dürfen.",
    "Bereitschaft zum gemeindlichen Einvernehmen (§ 36 BauGB) für Variante B (Befreiung Baugrenze bei Einhaltung GR 65 m²).",
    "Waldabstand § 4 Abs. 3 LBO BW: Ausnahme durch die untere Baurechtsbehörde im Benehmen mit der Forstbehörde; Erfahrung der Gemeinde mit Nachbargrundstücken.",
    "Erschließung: Lage der Hausanschlüsse (Wasser, Kanal, Strom) am Grenzweg; Anforderungen an Trennsystem/Versickerung.",
    "Artenschutz: Notwendigkeit einer Vorprüfung (Brutvögel, Orchidee Listera ovata) und zulässiges Zeitfenster für Bauarbeiten.",
    "Empfehlung der Gemeinde zu Dachbegrünung vs. Stehfalzdach im Ortsbild.",
])

# ---------------------------------------------------------------- 8
H("8. Anlagen")
B([
    "Planmappe „01_Vorentwurf_Plaene_Fl7348_Bammental.pdf“ (12 Blätter, A3): Deckblatt, Lageplan, Grundriss/Ansichten/Schnitt/Isometrie je Variante, Nachweis Festsetzungen, Gestaltung",
    "Bebauungsplan „Wochenendhausgebiet – 1. Änderung (Neufassung)“ mit Messung des Baufensters (Bauherr, 04.06.2023)",
    "Vorentwurf Dachüberstand (Bauherr, 04.06.2023)",
    "Drohnenfoto des Grundstücks mit markiertem Baufenster",
    "Referenzbilder Gestaltung (Holz-Cabin mit Stehfalzdach)",
    "Visualisierungen (unverbindlich) – siehe Prompts „03_Bildprompts_Visualisierung.md“",
])
doc.save(OUT)
print("OK", OUT)
