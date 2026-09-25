# Türzwerg — Projektstand zum Übergeben

**Stand: 24.09.2026.** Dieses Dokument ist als Einstieg für einen neuen
Claude-Chat gedacht. Es enthält den kompletten aktuellen Stand: Produkt,
Maße, Material, Marke, Slogans, Shoptexte, FAQ, Logo, offene Punkte.

Wichtig vorweg: **an drei Stellen widersprechen sich ältere Dokumente und
der heutige Konstruktionsstand.** Das ist unten jeweils markiert mit
⚠️ — nicht überlesen, sonst werden veraltete Maße weitergetragen.

---

## 1. Was Türzwerg ist

Eine Schnur mit Griff, die an der Türklinke hängt, damit Kleinkinder
(etwa 1,5 bis 3 Jahre) Zimmertüren allein öffnen können.

**Das Problem:** Türklinken sitzen auf 105 cm. Ein Zweijähriger reicht bis
etwa 90 cm. Dazwischen liegt eine Lücke, die kein Kind überbrücken kann —
und ein Kind, das nicht selbst ins Zimmer kommt, ruft.

**Die Lösung:** Eine Silikonmanschette wird über den Türdrücker geschoben
(hält allein durch Spannung, kein Bohren, kein Kleben). Daran hängt eine
kurze Schnur, unten ein Griff. Das Kind greift, zieht, die Klinke geht
runter, die Tür auf.

**Zwei Namen, ein Zeichen:**
- **Türzwerg** — DACH
- **Doorlino** — international
  (⚠️ noch **nicht** auf Markenkollision geprüft — vor Anmeldung
  recherchieren lassen)

**Firma laut Shopentwurf:** Doorlino UG (haftungsbeschränkt), Deutschland.

---

## 2. Die Bauteile

Drei Teile plus die 3D-druckbaren Gießformen dafür. Alles ist
**parametrisch in Python** konstruiert (reine Standardbibliothek, **kein
numpy** — das ist im Container nicht verfügbar), Netze über Marching
Tetrahedra auf SDFs, Export als STL und 3MF.

### 2.1 Der Reif (Griffring zum Hineingreifen) — **Rev. A φ**, aktuell gewählt

Das ist die aktuell gewählte Fassung. Erzeugt von `reif_eh.REV_A_PHI`
(Klasse `Mix` aus `reif_mix.py`).

| Maß | Wert |
|---|---|
| Außenmaß | **⌀ 72,0 × 14,0 mm** |
| Öffnung (innen) | 48,6 × 38,0 mm |
| Bandbreite oben / seitlich / unten | 19,0 / 11,74 / 15,0 mm |
| Eckradien oben / unten | 7,00 / 4,33 mm (Verhältnis = φ) |
| Griffumfang im Querschnitt | 46,0 mm |
| Knotenkammer | 11 × 9,0 × 12,0 mm, Mund 9,00 mm |
| Bohrtiefe bis Kammer | 8,0 mm |
| Schnurbohrung | ⌀ 4,0 mm, mit 0,5 mm Senkung am Austritt |
| Volumen | 30,5 cm³ |
| Durchbiegung bei 17 N (Shore A 70) | 3,88 mm |

**Die φ-Proportionen:** `b_seite = b_oben/φ` und `eck_oben = 1/φ`. Das
war eine bewusste Entscheidung nach Ihrer Frage „hat es Fibonacci drin?" —
φ dient hier als Proportionierung, nicht als Mechanik.

**Historie der Revisionen** (alle in `reif_eh.py` vergleichbar):
`REV_A`, `REV_A_PHI`, `REV_E`, `REV_E_RUND`, `REV_H72`. Rev. H war
deutlich größer; auf Ihren Wunsch wurde alles auf ⌀ 72 normiert, damit
Rev. E (für die erste Gießform) und die neueren vergleichbar sind.

**STL-Dateien:** `tuerzwerg-zugring-reva-phi.stl`,
`tuerzwerg-zugring-reva-rund.stl`, `tuerzwerg-zugring-reve-rund.stl`,
`tuerzwerg-zugring-revh72.stl`.

### 2.2 Die Manschette (Klinkenmanschette)

Erzeugt von `manschette.py`.

| Maß | Wert |
|---|---|
| Außenmaß | 24,00 × 31,50 × 28,00 mm |
| Bohrung innen | ⌀ 18,0 mm |
| Länge | 28,0 mm |
| Wandstärke | **3,0 mm** (auf Ihren Wunsch für Silikon; PLA hatte weniger) |
| Wandstärke an den Enden | 1,2 mm, über 7 mm ausgelaufen (Kantenverrundung) |
| Knotenkammer | ⌀ 11 mm, 21 mm lang, Achse 11 mm außermittig |
| Schnurbohrung | ⌀ 4,0 mm, 0,5 mm Senkung |
| Volumen | 6,41 cm³ |
| Netz | 496 136 Dreiecke, 0 offene Kanten |

Die Kammerform wurde auf Ihren Wunsch **an die des Reifs angeglichen**
(gerundete Box statt Halbkreis, gerade Stirnwände) — die frühere spitz
zulaufende Form gefiel Ihnen nicht.

**Sitz:** innen 18 mm auf einen 20-mm-Drücker (DIN 18255) = 11 % Untermaß,
das Silikon spannt sich selbst fest.

**STL:** `tuerzwerg-manschette.stl`.

### 2.3 Die Schnur

- **⌀ 4,0 mm** (war früher 5,0 — auf Ihren Hinweis reduziert, damit der
  Knoten nicht durchrutscht)
- Länge **220 mm**
- Material: Paracord 550 (Typ III), Bezug z. B. paracord.eu
- Beide Bohrungen (Reif und Manschette) sind auf 4 mm abgestimmt, mit
  abgeleiteter (nicht fester) Senkung am Austritt

### 2.4 Der Drechsel (zweite Griffvariante)

36 × 90 mm, gedrechselte Form mit breitem Unterteil. Steht im Markenkern
als zweites Sortimentsteil („zum Umfassen", unauffälliger). Konstruktiv
in `griffe.py` / `griffbirne.py`. Aktuell **nicht** im Fokus.

### 2.5 Die Gießformen

⚠️ **Beide sind veraltet und müssen neu gerechnet werden, bevor gegossen
wird.**

- `giessform_revh.py` — Rev. H Gießform, 122 × 135 × 14 mm, drei Körper,
  0 offene Kanten, Überhang 0,11 %. Enthält gute Lösungen: tangentiale
  Viertelkreis-Bögen im Anguss, drei Zentrierzapfen, Trichter.
  **Veraltet**, weil: Kammermund-Korrektur, ⌀4-Bohrung und Senkung fehlen
  — und weil der gewählte Ring jetzt **Rev. A φ** ist, nicht Rev. H.
- `giessform_manschette.py` — **veraltet**, die Manschettengeometrie hat
  sich seitdem erheblich geändert (3 mm Wand, neue Kammer).

**Zwei Regeln, die beim Neubau gelten:**
1. **Entformbarkeit:** Jedes Formteil muss das Gussteil geradlinig
   verlassen können. Eine Mulde darf nie breiter sein als ihre Öffnung.
2. **Drucklage:** Die Überhangprüfung nimmt Aufbau in +z an. Die Hälften
   werden aber **mit der Trennfläche nach oben** gedruckt — ohne die
   Funktion `drucklage()` misst man 17,5 % statt der echten 0,11 %.

---

## 3. Material

### Shore-Härte

Für den Knoten, der nicht durch die 4-mm-Durchführung rutschen darf, und
damit sich ein Kind dranhängen kann:

| Shore A | E-Modul (Gent) |
|---|---|
| 50 | 2,46 MPa |
| 60 | 3,61 MPa |
| 70 | **5,52 MPa** |
| 75 | 7,05 MPa |
| 80 | **9,35 MPa** |

Der Shopentwurf nennt **Shore A 80**; die Rechnungen im Repo laufen
meist mit **A 70**. ⚠️ Das ist noch zu entscheiden.

**Wichtige Erkenntnis:** Das Durchrutschen des Knotens ist **kein
elastisches, sondern ein Weiterreiß-Problem**. Die klassischen
Spritzguss-Silikone (LSR) haben dafür einen geeigneten
Weiterreißwiderstand; RTV-2-Gießsilikone sind in dieser Hinsicht
schwächer. Für den Prototypenguss also bewusst ein RTV-2 mit hohem
Weiterreißwiderstand wählen.

### Rechenwege, die im Projekt verwendet werden

- **Ringdurchbiegung:** δ = 0,149 · F · R³ / (E · I), I = t·b³/12,
  nachgiebigkeitsgewichtet mit (cos θ/2 − 1/π)².
  **Merksatz:** R und b mit demselben Faktor skalieren und t konstant
  lassen ändert δ **nicht**.
- **Knoten-Durchzug:** Neo-Hooke, σ_θ = G(λ² − 1/λ), G = E/3.

---

## 4. Sicherheitsgrenzen (die Zahlen, die alles begründen)

| Grenze | Wert | Folge fürs Produkt |
|---|---|---|
| Schnurlänge Kinder < 3 J. | max. **300 mm** | Schnur ist **220 mm** |
| Fingerfalle | 5–12 mm vermeiden | Öffnungen bewusst größer |
| Kopffalle | ≥ 95 mm vermeiden | Ringöffnung 48,6 × 38,0 |
| Kleinteilezylinder | 31,7 mm | Reif muss größer sein, in **jeder** Lage |
| Vier Kinderfinger | ≈ 44 mm | Öffnung muss das fassen |

⚠️ **Konflikt:** Der Markenkern und der Shopentwurf argumentieren mit
**⌀ 86 mm** („passt durch keine Prüföffnung für Kleinteile"). Der aktuell
gewählte Reif ist **⌀ 72 mm**. 72 mm ist immer noch deutlich größer als
der 31,7-mm-Zylinder, das Argument trägt also weiter — **aber die Zahl
86 muss überall ersetzt werden.** Ebenso „Öffnung 64 × 48" → **48,6 × 38,0**
und „Gewicht 37 g" (neu zu wiegen).

---

## 5. Die Marke

### 5.1 Farben

**Produktfarben** (nur das Produkt trägt Farbe, die Seite selbst ist
farblos — „Papierweiß wie eine lackierte Zimmertür"):

| Name | Hex |
|---|---|
| Mohn | `#D2452B` |
| Salbei | `#55886B` |
| Himmel | `#38689B` |
| Sonne | `#E0982F` |
| Schiefer | `#454A52` |

**Neutrale:**

| Name | Hex |
|---|---|
| Papier | `#FBFAF7` |
| Fläche | `#EFEDE6` |
| Linie | `#E2DFD5` |
| Leise | `#6C675A` |
| Tinte | `#17160F` |

Farbkarte (veröffentlicht):
https://claude.ai/artifact/4E96j9us8zXLpM2r9Beyax
Dort sind die Farben **als Schnur** dargestellt, nicht als Kachel — bei
geflochtenem Material täuscht eine flache Fläche.
⚠️ Die Anbieter-Farbnamen von paracord.eu fehlen noch (Seite war nicht
erreichbar). Kostenlose Muster bestellen und abgleichen.

### 5.2 Schrift

- **Überschriften:** Bricolage Grotesque, nur Gewicht **800**
- **Fließtext:** Figtree, **400** für Text, **600** für Labels/Knöpfe
- Beide über Google Fonts, beide auch kommerziell kostenlos
- Beim Export: **Schrift in Pfade wandeln**

### 5.3 Regeln fürs Zeichen

- Schutzraum rundum: die Höhe des Rings
- Kleinste Größe: **20 mm gedruckt, 24 px am Bildschirm**
- Das Zeichen steht **in der Produktfarbe oder in Tinte — nie in zwei
  Farben**
  ⚠️ Diese Regel haben Sie später selbst aufgeweicht: *„Wenn Farben, dann
  Ring und Mütze in einer unterschiedlichen."* Das ist Ihre Entscheidung
  und im aktuellen Logoentwurf berücksichtigt (Reif und Mütze sind zwei
  getrennte Pfade, also getrennt färbbar).
- Die Wortmarke steht **immer in Tinte**, auch neben farbigem Zeichen
- Benötigte Formate: SVG, PNG 1000×1000 auf Weiß (Amazon/eBay),
  Favicon 512×512

---

## 6. Slogans

### Der gesetzte

> ## Selber aufmachen.
> Englisch: **I can do it myself.**

Begründung: *„Selber!"* ist das Wort, das jedes Kind in diesem Alter
hundertmal am Tag sagt. Der Slogan gehört damit dem Kind, nicht dem
Produkt — und jeder Elternteil erkennt ihn sofort wieder.

**Die Regel für alle Varianten: der Spruch gehört dem Kind, nicht dem
Produkt.**

### Zehn kurze

| # | Deutsch | Gedanke |
|---|---|---|
| 01 | **Selber!** | Das Wort, das ein Zweijähriger hundertmal am Tag sagt |
| 02 | **Türen auf.** | Zwei Wörter, zwei Bedeutungen |
| 03 | **Ich kann das.** | Aus dem Mund des Kindes |
| 04 | **Jede Tür. Allein.** | Der Anspruch, trocken |
| 05 | **Ein Zug genügt.** | Beschreibt die Mechanik, meint mehr |
| 06 | **Die Tür gehört dir.** | Direkt ans Kind |
| 07 | **Groß genug.** | Das Kind wächst nicht — die Klinke kommt herunter |
| 08 | **Reichweite für Kleine.** | Nüchtern, gut für den Shop |
| 09 | **Aufmachen kann ich.** | Trotzig, in der Wortstellung des Kindes |
| 10 | **Einmal ziehen, offen.** | Die Mechanik als Versprechen |

Englisch für Doorlino: *Myself! · Doors open. · I've got this. ·
Every door. Alone. · One pull.*

### Zehn längere

These dahinter: **einprägsam wird ein Satz nicht durch Kürze, sondern
durch ein Mittel.**

| # | Deutsch | Mittel |
|---|---|---|
| 11 | **Nicht das Kind wächst. Die Klinke kommt runter.** | Umkehrung |
| 12 | **Die Tür ist groß. Du auch.** | Antithese |
| 13 | **Erst die Klinke, dann die Welt.** | Steigerung |
| 14 | **Kein Rufen. Kein Hochheben. Einfach ziehen.** | Dreierrhythmus |
| 15 | **Hingehen. Ziehen. Drin.** | Dreierrhythmus |
| 16 | **Das erste Mal ohne Hilfe.** | Der Moment |
| 17 | **Eine Schnur, und die Tür ist keine Wand mehr.** | Bild |
| 18 | **Türen gehen auf, wenn man selber zieht.** | Sprichwort |
| 19 | **Jede Tür im Haus gehört jetzt auch dir.** | Besitz |
| 20 | **Für alle, die noch nicht an die Klinke kommen.** | nüchtern |

Englisch: *The child doesn't grow. The handle comes down. · No calling.
No lifting. Just pull. · Doors open when you pull them yourself.*

### Empfehlung (Stand der Diskussion)

- **01 „Selber!"** als Zeichen-Beigabe auf dem Produkt — kürzer als
  „Selber aufmachen." und sagt dasselbe
- **11 oder 18** als Kopfzeile im Shop
- **14** für Anzeigen und Produktseite — der einzige aus **Elternsicht**;
  alle anderen gehören dem Kind, gekauft wird aber von den Eltern
- **20** als Unterzeile im Regal

---

## 7. Shoptexte

### Ein Satz, was es ist

> Ein Griff an einer Schnur, der die Türklinke auf Kinderhöhe holt.

### Drei Sätze für die Startseite

> Türklinken sitzen auf 105 Zentimetern. Ein Zweijähriger reicht bis 90.
> Der Türzwerg schließt diese Lücke mit einem Silikonring, einer Schnur
> und einem Griff — ohne Bohren, ohne Kleben, in einer halben Minute
> montiert.

### Wenn nur eine Zeile Platz hat

> Der Türgriff für kleine Hände. Ab 1,5 Jahren.

### Hero im Shopentwurf

> **Die Tür geht auf. Ohne dich.**
> Ein Ring an einer Schnur, ein Silikonring auf der Klinke. Mehr ist es
> nicht. Und plötzlich kommt dein Kind allein ins Kinderzimmer.

Badges: *Silikon, ohne Weichmacher · In 30 Sekunden montiert · Passt auf
runde Drücker 18–23 mm*

### Die drei Montageschritte

1. **Manschette aufschieben** — Der Silikonring wird über den Türdrücker
   geschoben. Sein Innendurchmesser ist 11 % kleiner als der Drücker — er
   spannt sich selbst fest.
2. **Schnur einhängen** — Die Schnur ist bereits eingeknotet, der Knoten
   verschwindet in der Manschette. Von außen sieht man nur die Schnur.
3. **Fertig** — Der Ring hängt auf Höhe der Kinderhand. Dein Kind greift
   hinein und zieht — die Klinke geht runter, die Tür auf.

### Preis und Set

- **19,90 €** inkl. MwSt., Versand in DACH kostenlos
- „Die meisten nehmen zwei — Kinderzimmer und Bad."
- Zahlung über Stripe
- Hinweis im Entwurf: *„Der Verkauf startet, sobald die Prüfung nach
  EN 71 abgeschlossen ist."* — bis dahin **Warteliste statt Warenkorb**
- ⚠️ Der Preis ist eine Schätzung. Solange die Herstellkosten nicht
  belastbar sind, ist jede Preisseite geraten.

### Im Karton

- Griffring aus Silikon, ⌀ 86 mm ⚠️ → **⌀ 72 mm**
- Klinkenmanschette, innen ⌀ 18 mm
- Schnur, 220 mm, bereits verknotet

### Argumente „warum diese Maße"

> **Warum die Schnur kurz ist.** 220 mm. Für Kinder unter drei Jahren
> gilt eine Höchstlänge von 300 mm — kürzer als jede Schlinge, die sich
> um einen Hals legen kann. Das ist kein Sparen an Material, das ist die
> Norm.

> **Warum der Ring so groß ist.** 86 mm passen durch keine Prüföffnung
> für Kleinteile, in keiner Lage. Ein kompakter Griff hätte diese Frage
> offengelassen.
> ⚠️ Zahl auf **72 mm** anpassen — das Argument trägt weiter (der
> Kleinteilezylinder misst 31,7 mm), nur die Zahl stimmt nicht mehr.

---

## 8. FAQ (aktueller Wortlaut aus `tuerzwerg-shop.html`)

**Passt das auf meine Türklinke?**
Auf runde Drücker mit 18 bis 23 mm Durchmesser, und das sind die
allermeisten — DIN 18255 normt 20 mm. Miss im Zweifel den Griffteil,
nicht die Rosette. Auf eckige oder stark konische Drücker passt die
Manschette nicht.

**Bleibt die Manschette wirklich sitzen?**
Sie ist innen 18 mm weit und wird auf einen 20-mm-Drücker geschoben —
11 % Untermaß, das Silikon spannt sich auf. Bei sehr glatten,
verchromten Drückern kann sie sich mit der Zeit verdrehen; abziehen und
neu aufschieben dauert fünf Sekunden.

**Kann mein Kind damit die Tür auch zumachen?**
Nur, wenn es die Tür ohnehin schon zuziehen kann. Der Türzwerg dreht die
Klinke — das Öffnen macht er möglich, das Zuziehen bleibt Muskelarbeit.

**Und wenn mein Kind sich hineinhängt?**
Der Ring hält das aus, er verformt sich elastisch und geht in seine Form
zurück. Die Schnur ist auf ein Vielfaches der Betätigungskraft ausgelegt.

**Was ist mit der Türklinke selbst?**
Silikon greift keine Beschichtung an und hinterlässt keine Spuren. Weil
es weich ist, schlägt der Ring auch nicht laut gegen das Türblatt.

### ⚠️ Was an der FAQ noch fehlt bzw. veraltet ist

Diese fünf Antworten sind teilweise überholt und decken die häufigsten
Fragen nicht ab. **Noch zu ergänzen:**
- Welche **Shore-Härte** und warum (A 70 vs. A 80 ist noch offen)
- **Schnurmaterial** (Paracord 550 Typ III) und ob es gewechselt werden kann
- **Reinigung** (spülmaschinenfest? Wie desinfizieren?)
- **Altersfreigabe** und die Begründung über die 300-mm-Norm
- **GPSR** — seit 13.12.2024 Pflicht: Herstellerangaben, Warnhinweise,
  Kontaktstelle
- **EN 71 / CE** — Stand der Prüfung
- Was passiert, wenn die Manschette **zu locker** sitzt (andere
  Drückerdurchmesser)

Bei „Und wenn mein Kind sich hineinhängt?" ist die Antwort jetzt auch
**rechnerisch belegbar**: 3,88 mm Durchbiegung bei 17 N mit Shore A 70.

---

## 9. Shop-Aufbau

**Sechs Seiten, davon vier rechtlich.** Kein Blog, keine Über-uns-Seite,
keine Kategorien. Bei zwei Produkten ist jede zusätzliche Seite ein Ort,
an dem Kunden verlorengehen.

| Seite | Inhalt |
|---|---|
| Startseite | Hero · drei Schritte · beide Produkte · Sicherheit · FAQ |
| Der Reif | Farbe, Menge, Setstaffel, Maße, in den Warenkorb |
| Der Drechsel | gleiche Struktur, gleiche Bausteine |
| Warenkorb / Kasse | SEPA zuerst, dann Karte, PayPal, Klarna |
| Impressum | Pflicht |
| Datenschutz | Pflicht |
| AGB und Widerruf | Pflicht, aus dem Rechtstexte-Abo |
| Versand und Zahlung | Pflicht, Lieferzeiten und Kosten |

**Startseite in dieser Reihenfolge:**
1. Szene und Claim — in drei Sekunden muss klar sein, was das Ding tut
2. Die drei Montageschritte — nimmt die Sorge, etwas an der Mietwohnung
   zu beschädigen
3. Beide Produkte nebeneinander mit Preis
4. Warum Schnur und Ring diese Maße haben — **das stärkste
   Verkaufsargument und gleichzeitig der Abstand zu jedem Nachbau**
5. FAQ, allen voran „passt das auf meine Klinke?"
6. Fuß mit den Rechtslinks

### Shopplattform

Ihre Frage war: niedrigpreisiges Produkt, Shopify schreckt mit 30 ct pro
Kaufvorgang ab. Das Thema wurde besprochen (Shopware/Shopify/
Alternativen), ist aber **nicht abschließend entschieden**. Bei 19,90 €
Warenkorb sind 30 ct Fixgebühr 1,5 % — plus die prozentuale Gebühr. Bei
Zwei-Stück-Bestellungen relativiert es sich.

### Bilder, die gebraucht werden

| Bild | Wofür | Format |
|---|---|---|
| Produkt freigestellt, je Farbe | Shop, Varianten | SVG, später Foto auf Weiß |
| Szene an der Tür | Startseite, Anzeigen | SVG, später Foto im Kinderzimmer |
| Größenvergleich mit Hand | Produktseite, Amazon | SVG / PNG 2000 px |
| Drei Montageschritte | Produktseite, Beipackzettel | Fotos, quer |
| Marktplatz-Hauptbild | Amazon, eBay | PNG 1000×1000, reines Weiß |
| Logo | überall | SVG, PNG 1000, Favicon 512 |

Die vorhandenen Produktzeichnungen (`produktzeichnung.py` →
`tuerzwerg-produkt-teile.svg`, `tuerzwerg-produkt-montiert.svg`) stammen
**aus derselben Geometrie wie die Fertigungsdaten** und stimmen auf den
Zehntelmillimeter. Die Produktfarbe ist dort eine CSS-Variable
`--produkt`, lässt sich also pro Variante umfärben.

---

## 10. Das Logo — aktueller Stand

Die Logoarbeit ist **noch nicht abgeschlossen**. Chronologie:

1. **Acht frühe Konzepte** (Zeichen, Zwergtür, D wie Tür, Am Wort
   aufgehängt, hängendes i, Höhenmarke, Schild)
2. **Fünf gerechnete Fassungen** aus der echten Produktkontur — der
   Umriss ist Außen- und Innenkontur von Rev. A φ, **Punkt für Punkt aus
   derselben Funktion gesampelt, aus der das STL entsteht**. Die
   Innenkontur schwankt zwischen 17,0 und 24,4 mm, also **44 % über den
   Umfang**. Ändert sich das Bauteil, ändert sich das Logo mit.
   → `logo_kontur.py`, gibt auch `tuerzwerg-reif-zeichen.svg` aus (Reif
   allein)
3. **„Zipfel"** — Reif + geometrische Zipfelmütze, tangential
   angeschlossen. Veröffentlicht:
   https://claude.ai/artifact/Fp3AMBYE9yo2tAT4nUbxEk
   → `logo_zipfel.py`
4. **„Schnurzwerg"** — Ihre Skizze: eine Monolinie, die sich zum Zwerg
   knüpft. → `logo_schnurzwerg.py`, `tuerzwerg-schnurzwerg.html`
   **Hier steht die Arbeit.**

### Was beim Schnurzwerg gelernt wurde (wichtig für die Fortsetzung)

Drei Fehler, die jeweils die Form ruiniert haben:

1. **Spirale ≠ Knoten.** Schlaufen, die *um* eine Achse gewickelt sind,
   lesen als **Sprungfeder**. Ihre Skizze macht es umgekehrt: die
   Schlaufen zeigen *aus* der Achse heraus — hinaus, Kehre, zurück, wie
   bei einer Schleife. Das ist der Unterschied zwischen Knoten und Draht.
2. **Die Silhouette darf sich nicht einschnüren.** Wenn die Mütze über
   dem Reif in einem Punkt beginnt, entsteht eine Taille — und aus Reif
   plus aufsteigender Schnur wird optisch eine **Schlinge am Strick**.
   Für ein Kinderprodukt ist das die eine Assoziation, die nicht passieren
   darf. Lösung: die Krempe liegt breiter auf als der Reif.
3. **Schlaufen dürfen außen nicht spitz zulaufen.** Ein einzelner Punkt
   an der Spitze ergibt eine **Blattform** — fünf davon lesen als
   Pflanze. Drei Punkte um die Kehre ergeben eine runde Schlaufe. Und Ein-
   und Ausgang müssen auf verschiedenen Seiten der Achse liegen, damit
   sich die Schnur am Fuß **kreuzt** — diese Kreuzung ist das, was ein
   Auge als „verknotet" liest.

Technisch: **zentripetales Catmull-Rom** (α = ½), in kubische Bézier
umgerechnet. Uniform parametrisiert schlägt die Kurve dort aus, wo die
Stützpunkte ungleich dicht stehen. Formel im Code.

### Offen beim Logo

- Die Blattform ist noch nicht ganz überwunden; die letzte Iteration las
  als Sträußchen. Die Richtung (runde, sich kreuzende Schlaufen, Krempe
  breiter als der Reif, Reif als eigene Linie) stimmt.
- **Kleinstgrößen sind das ungelöste Problem:** Ab 48 px sitzt jede
  Fassung, bei 32 px nur die einfachste, bei 24 px bleibt die Silhouette,
  bei 16 px Matsch. Ein Knoten hat nach unten eine Grenze.
  **Vorschlag:** zwei Größenstufen — ab Etikettgröße das ganze Zeichen,
  für Favicon/Prägung/Nähetikett der **Reif allein** (kommt aus
  `logo_kontur.py`, ist dieselbe Marke, kein zweites Logo).
- Reif und Mütze sind im aktuellen Entwurf **zwei getrennte Pfade**,
  damit Ihr Wunsch „Ring und Mütze in verschiedenen Farben" möglich ist.

---

## 11. Dateien im Repo

Branch: `claude/door-opener-cord-toddlers-i97hxf`

### Kern

| Datei | Zweck |
|---|---|
| `netz.py` | Mesh-Kern: `vernetzen`, `volumen`, `offene_kanten`, `ueberhang`, `abweichung`, `schreibe_stl`, `schreibe_3mf`, Primitive |
| `reif_mix.py` | Klasse `Mix` — der parametrische Reif |
| `reif_eh.py` | Alle Reif-Revisionen im Vergleich, inkl. `REV_A_PHI` |
| `manschette.py` | Die Manschette |
| `produktzeichnung.py` | Shopzeichnungen (Teile + montiert) |
| `logo_kontur.py` | Logopfad aus der echten Bauteilkontur |
| `logo_zipfel.py` | Logoentwurf „Zipfel" |
| `logo_schnurzwerg.py` | Logoentwurf „Schnurzwerg" (Arbeit läuft) |
| `giessform_revh.py` | Gießform Rev. H (veraltet) |
| `giessform_manschette.py` | Gießform Manschette (veraltet) |
| `step_reif.py` | Reif als **STEP** (B-Rep) aus der Parametrik |
| `step_manschette.py` | Manschette als **STEP** (B-Rep) aus der Parametrik |

### CAD-Dateien (STEP, AP214, Millimeter)

Beide sind **nicht** aus dem STL gewandelt, sondern aus derselben
parametrischen Definition neu gebaut — mit Kurven und Flächen statt
Dreiecken, und dadurch genauer als die STLs:

| Teil | Datei | Flächen | größte Abweichung | STL zum Vergleich |
|---|---|---|---|---|
| Reif Rev. A φ | `tuerzwerg-zugring-reva-phi.step` | 21 | 5,7 µm | 207 µm |
| Manschette | `tuerzwerg-manschette.step` | 58 | 4,4 µm | 153 µm |

Bohrungen, Senkungen und Kammerwände stehen darin als echte Zylinder-,
Kegel- und Torusflächen. **Eine bewusste Abweichung:** im Distanzfeld
wird die Knotenkammer mit einem *weichen Minimum* (Radius 0,8)
abgezogen; im STEP ist daraus eine echte Verrundung mit konstantem
Radius 0,8 geworden — fertigbar und bemaßbar, aber nicht auf den
Mikrometer dasselbe. Nachgemessen liegen **alle** Abweichungen über
50 µm genau dort.

Zum Neuerzeugen wird `cadquery` gebraucht (`pip install cadquery`), das
den OpenCASCADE-Kernel mitbringt. Die fertigen STEP-Dateien liegen im
Repo, das Paket ist also nur nötig, wenn sich die Geometrie ändert.

### Dokumente

| Datei | Inhalt |
|---|---|
| `tuerzwerg-markenkern.html` | Markenkern: Zeichen, Farben, Schrift, Slogan, Sortiment, Aufbau |
| `tuerzwerg-shop.html` | Shopentwurf mit FAQ |
| `tuerzwerg-farbkarte.html` | Farbkarte |
| `tuerzwerg-tuergriffe-markt.html` | Marktübersicht Zimmertürgriffe nach Region |

### Veröffentlichte Artefakte

| Was | Link |
|---|---|
| Drücker oder Knauf (Marktanalyse) | https://claude.ai/artifact/E42en4rqMtW2HtoCpqq7QC |
| Türzwerg Farbkarte | https://claude.ai/artifact/4E96j9us8zXLpM2r9Beyax |
| Türzwerg Zeichen (Designleinwand) | https://claude.ai/artifact/We3rsxEL6GX2GtrSQB9s45 |
| Zipfel (Logoentwurf) | https://claude.ai/artifact/Fp3AMBYE9yo2tAT4nUbxEk |

---

## 12. Offene Punkte, nach Dringlichkeit

### Blockierend fürs Verkaufen
1. **EN 71 und CE.** Bis dahin ist die Seite eine Warteliste, kein Shop.
2. **GPSR-Pflichtangaben** (seit 13.12.2024).
3. **Herstellkosten** — ohne sie ist jeder Preis geraten.
4. **Markenkollision „Doorlino"** prüfen lassen.

### Konstruktiv
5. ~~**Knotenkammertiefe**~~ — **gelöst** in der spritzgussgerechten
   Fassung (`manschette_spritzguss.py`): Kanalachse von 11,0 auf 13,5 mm,
   damit **9,0 mm** statt 6,5 mm unter einem ⌀20-Drücker. Kostet 2,5 mm
   Bauhöhe, spart trotzdem Silikon. Praxistest steht weiter aus.

5b. **Spritzgussgerechte Manschette.** Der Hersteller meldete, dass das
   Werkzeug an der innenliegenden Knotenkammer scheitert. Nachgerechnet:
   17,8 % der Hohlraumpunkte sind gegenüber einem axialen Kern
   hinterschnitten → zwei Kerne mit gesteuerter Reihenfolge. Lösung: die
   Stirnwände entfallen, der Kanal läuft durch → **0,03 %**, also ein
   gerader Kern. Dateien: `manschette_spritzguss.py`,
   `step_manschette_sg.py`, `tuerzwerg-manschette-spritzguss.stl/.step`,
   Bild `tuerzwerg-manschette-spritzguss.png`.
   **Verworfen:** der durchlaufende Kanal nimmt der Manschette die
   beiden geschlossenen Ringe an den Stirnseiten, und die tragen die
   Spannkraft am Drücker.

5c. **Quertasche — der tragfähige Weg.** Die Tasche wandert unter den
   Rohrmantel und läuft quer durch den Kiel. Ergebnis: Rohrring auf
   **87 % statt 12 %** der Länge geschlossen (also *besserer* Halt als
   heute), Knotenraum 8,5 mm **unabhängig vom Drückerdurchmesser**
   (heute 7,5 / 6,5 / 5,0 mm bei Ø18 / Ø20 / Ø23 — für keinen genug),
   Werkzeug = zwei Hälften + ein glatter Zylinderkern, **kein Schieber**.
   Kosten: 35 statt 31,5 mm Bauhöhe, 8,4 statt 7,4 g Silikon, Knoten von
   der Seite sichtbar (`TASCHE_BLIND` schließt eine Seite).
   Dateien: `manschette_quertasche.py`, `step_manschette_quer.py`,
   `tuerzwerg-manschette-quertasche.stl/.step/.png`.

5d. **Rundloch durch die Decke — die kleinste Änderung, die trägt.**
   Ø10-Loch senkrecht von oben durch die Decke, durch die Bohrung, in
   den Kiel; nur die letzten 3,5 mm sind Ø4. Weil der Stift **nach oben**
   gezogen wird, erweitert sich das Loch in Entformrichtung überall →
   **0,04 %** Hinterschnitt. Bei waagerechter Trennebene steckt der Stift
   fest in der oberen Hälfte und fährt beim Öffnen von selbst heraus;
   der Bohrungskern braucht eine Ø10-Querbohrung.
   Rohrmantel **62 %** geschlossen (heute 23, Quertasche 99).
   **Außenform unverändert wie das Original** (24,00 × 31,50 × 28,00 mm,
   Kielachse 11,0, Kielradius 8,5) — nachgewiesen: die beiden
   Außenfelder sind rechnerisch identisch (0,000000 µm über 40 000
   Punkte), und die STEP-Fläche liegt außerhalb des Lochs auf 1,1 µm
   auf der Originalkontur.
   Preis: sichtbares Loch oben, 8,4 statt 7,4 g Silikon, und der
   Knotenraum bleibt mit 6,0 mm unter Ø20 zu knapp (Sackstich braucht
   ~9). Ein kürzerer Ø4-Hals hilft etwas: 2,0 mm statt 3,5 → 7,5 mm.
   Dateien: `manschette_rundloch.py`, `step_manschette_rundloch.py`,
   `tuerzwerg-manschette-rundloch.stl/.step/.png`.

⚠️ **Messkorrektur:** Der Rohrmantel wurde zuerst auf halber Wandstärke
   (r = 10,5) abgetastet. An den Stirnseiten ist die Wand auf 1,2 mm
   abgeflacht, der Messkreis lag dort außerhalb des Bauteils und zählte
   fälschlich als offen. Ältere Zahlen in dieser Datei (12 % / 87 %) sind
   dadurch zu niedrig; richtig sind **23 % / 99 %**.
6. **Beide Gießformen neu rechnen** (siehe 2.5).
7. **Shore-Härte festlegen** (A 70 oder A 80) und ein Silikon mit
   passendem Weiterreißwiderstand wählen.

### Inhaltlich
8. **Alle ⌀-86-Angaben auf ⌀ 72 korrigieren**, ebenso Öffnungsmaß und
   Gewicht — in Markenkern, Shopentwurf und FAQ.
9. **FAQ erweitern** (siehe Abschnitt 8).
10. **Logo fertigstellen** (siehe Abschnitt 10).
11. **Shopplattform entscheiden.**
12. **Fotos.** Eltern kaufen Kinderprodukte nach Fotos — vor allem einem,
    auf dem ein Kind die Tür wirklich öffnet. Zeichnungen tragen den
    Start, mehr nicht.
13. **Paracord-Farbmuster** bestellen und mit den fünf Produktfarben
    abgleichen.

---

## 13. Arbeitsregeln, die sich im Projekt bewährt haben

Falls im neuen Chat wieder konstruiert wird — diese Regeln haben
mehrfach Fehler verhindert bzw. aufgedeckt:

- **Gitterartefakt erkennen:** Bleibt das Volumen über mehrere Raster
  gleich, während die Zahl offener Kanten springt, ist es ein
  Gitterartefakt und **kein Loch**. Eine Kante mit nur **einem** Dreieck
  ist ein Loch; Kanten mit drei oder mehr Dreiecken oder Länge null sind
  Quetschstellen des Verneztzers.
- **Messdisziplin:** Ein Messstrahl darf **nie auf der Fläche starten,
  die er messen soll** — das gab mehrfach 0,00 als Ergebnis.
- **Entformbarkeit** und **Drucklage** (siehe 2.5).
- **Visuell prüfen statt rechnen:** Im Container liegt Chromium unter
  `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`. Damit lassen sich
  HTML/SVG headless als PNG rendern und tatsächlich ansehen. Bei der
  Logoarbeit war das der Durchbruch — vorher wurde blind parametriert.
