---
id: STD-ERN-001
titel: Erneuerungsanstoß und Übergabe an das Projektmanagement
themenfeld: TF-ERN
version: 0.2.0
status: entwurf
gueltig_ab: 2026-11-01
letzter_review: 2026-08-10
review_zyklus_monate: 12
owner: PS-TFV
freigabe: PS-AL
rechtsstand_geprueft: false
pflichten: [PFL-022, PFL-018]

geltungsbereich:
  betriebsbereiche: [alle]
  rollen: [BB-L, PS-TFV, PS-BBK]

schnittstellen: [SST-AM, SST-PM, SST-NF]

aufgaben:
  - id: A1
    was: Zustandsbewertung je Anlagenklasse erheben und plausibilisieren
    takt: jaehrlich
    frist: bis 31.08.
    r: [BB-L]
    a: PS-TFV
    c: [PS-BBK]
    i: [SST-AM]
    nachweis: Zustandsbewertung je Anlage
    system: Anlagenstammdaten

  - id: A2
    was: Erneuerungsanstoß mit technischer Begründung an das Anlagenmanagement melden
    takt: anlassbezogen
    frist: binnen 20 Arbeitstagen nach Feststellung
    r: [PS-TFV]
    a: PS-TFV
    c: [BB-L]
    i: [PS-AL, SST-AM]
    nachweis: Anstoßmeldung mit Zustandsdaten und Störungshistorie
    system: Anlagenmanagement-Portal

  - id: A3
    was: Betriebliche Anforderungen zu Projektbeginn einbringen
    takt: anlassbezogen
    frist: vor Abschluss der Vorplanung
    r: [PS-BBK]
    a: PS-TFV
    c: [BB-L, FKT-VEFK, FKT-BSB]
    i: [SST-PM]
    nachweis: Anforderungsliste im Projektordner
    system: Projektablage

  - id: A4
    was: Anlagenverantwortung für die Bauphase benennen
    takt: anlassbezogen
    frist: vor Baubeginn
    r: [BB-L]
    a: FKT-VEFK
    c: [SST-PM, SST-NF]
    i: [PS-BBK]
    nachweis: Schriftliche Benennung
    system: Projektablage

  - id: A5
    was: Anlage nach Fertigstellung übernehmen und Restpunkte festhalten
    takt: anlassbezogen
    frist: am Tag der Abnahme
    r: [BB-L]
    a: PS-TFV
    c: [SST-PM, FKT-VEFK]
    i: [SST-AM, PS-AL]
    nachweis: Übergabeprotokoll mit Restpunkteliste
    system: Projektablage

  - id: A6
    was: Erledigung der Restpunkte nachhalten
    takt: monatlich
    frist: bis zum 10. Arbeitstag des Folgemonats
    r: [PS-BBK]
    a: PS-TFV
    c: [SST-PM]
    i: [BB-L]
    nachweis: Restpunktestatus
    system: Cockpit

kennzahlen:
  - id: KPI-ERN-01
    name: Erneuerungsanstöße mit Entscheidung des Anlagenmanagements binnen 40 Arbeitstagen
    ziel: ">= 90%"
    quelle: Anlagenmanagement-Portal
    takt: quartalsweise
  - id: KPI-ERN-02
    name: Übergaben mit vollständiger Dokumentation am Abnahmetag
    ziel: ">= 95%"
    quelle: Projektablage
    takt: quartalsweise
  - id: KPI-ERN-03
    name: Restpunkte älter als 90 Tage
    ziel: "0"
    quelle: Cockpit
    takt: monatlich

eskalation:
  - stufe: 1
    wann: Anstoß ohne Rückmeldung nach 40 Arbeitstagen
    an: PS-TFV
  - stufe: 2
    wann: Übergabe ohne vollständige Dokumentation angeboten
    an: PS-AL
  - stufe: 3
    wann: Inbetriebnahme ohne benannte Anlagenverantwortung
    an: PS-AL
---

# Erneuerungsanstoß und Übergabe an das Projektmanagement

> **Status: Entwurf.** Abzustimmen mit SST-AM (Frist in A2 und KPI-ERN-01)
> und SST-PM (Umfang der Übergabedokumentation in A5). Vor der Abstimmung
> keine Verteilung in die Betriebsbereiche.

## 1. Zweck

Wir betreiben die Anlagen und sehen als Erste, wenn eine Anlage das Ende
ihrer Nutzungsdauer erreicht. Entschieden wird die Erneuerung aber im
Anlagenmanagement und umgesetzt im Projektmanagement. Dieser Standard
beschreibt den Weg vom Befund bis zur Rückübernahme der erneuerten Anlage
- inklusive der beiden Stellen, an denen es erfahrungsgemäß klemmt: der
fehlenden Rückmeldung auf einen Anstoß und der unvollständigen
Übergabedokumentation.

## 2. Geltungsbereich

Gilt für alle Erneuerungsvorhaben an Anlagen in unserer
Betriebsverantwortung, unabhängig von der Investitionshöhe.

Instandsetzung im laufenden Betrieb ist keine Erneuerung und folgt TF-IHS.

## 3. Begriffe

**Erneuerungsanstoß** ist die begründete Meldung an das Anlagenmanagement,
dass eine Anlage ersetzt werden sollte. Er ist keine Beauftragung und kein
Budgetantrag.

**Restpunkt** ist eine bei Abnahme festgestellte, noch offene Leistung mit
vereinbartem Termin. Ohne Termin wird kein Restpunkt akzeptiert.

## 4. Ablauf

1. Die jährliche Zustandsbewertung ist die Datengrundlage (A1). Sie wird
   plausibilisiert, bevor sie das Haus verlässt.
2. Ein Anstoß entsteht aus Zustandsbewertung, Störungshäufung nach
   STD-ENT-001 A6 oder einem Einzelbefund und geht binnen 20 Arbeitstagen
   raus (A2).
3. Entscheidet das Anlagenmanagement für die Erneuerung, bringen wir
   unsere betrieblichen Anforderungen vor Abschluss der Vorplanung ein (A3).
4. Vor Baubeginn steht die Anlagenverantwortung für die Bauphase schriftlich
   fest (A4).
5. Die Übernahme erfolgt gegen Protokoll mit Restpunkteliste (A5), deren
   Abarbeitung monatlich nachgehalten wird (A6).

## 5. Nachweise

Zustandsbewertungen, Anstoßmeldungen, Anforderungslisten,
Übergabeprotokolle und Restpunktestände. Aufbewahrung bis zur nächsten
Erneuerung der Anlage, mindestens zehn Jahre.

## 6. Schnittstellen

SST-AM entscheidet über gemeldete Anstöße binnen 40 Arbeitstagen.
SST-PM bindet uns ab Vorplanung ein und übergibt mit vollständiger
Dokumentation gemäß Checkliste.
Beide Zusagen stehen in daten/organisation/schnittstellen.yaml und sind
Gegenstand des monatlichen Jourfixes.

## 7. Abweichungen

Eine Übernahme ohne vollständige Dokumentation ist möglich, wenn PS-AL
zustimmt und die fehlenden Unterlagen als Restpunkt mit Termin erfasst sind.

## 8. Änderungshistorie

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-07-15 | Ersterstellung | PS-RWM |
| 0.2.0 | 2026-08-10 | Restpunktenachverfolgung ergänzt (A6) | PS-TFV |
