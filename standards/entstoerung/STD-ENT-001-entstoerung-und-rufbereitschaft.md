---
id: STD-ENT-001
titel: Entstörung und Rufbereitschaft
themenfeld: TF-ENT
version: 3.0.0
status: gueltig
gueltig_ab: 2026-07-01
letzter_review: 2026-06-15
review_zyklus_monate: 12
owner: PS-TFV
freigabe: PS-AL
rechtsstand_geprueft: false
pflichten: [PFL-020, PFL-004]

geltungsbereich:
  betriebsbereiche: [alle]
  rollen: [BB-L, BB-MV, BB-MA, PS-DIS]

schnittstellen: [SST-NF, SST-SDL, SST-AM]

aufgaben:
  - id: A1
    was: Bereitschaftsplan für das Folgequartal erstellen und veröffentlichen
    takt: quartalsweise
    frist: bis 15. des Vormonats vor Quartalsbeginn
    r: [BB-MV]
    a: BB-L
    c: [PS-DIS]
    i: [SST-NF, PS-BBK]
    nachweis: Freigegebener Bereitschaftsplan
    system: Dispositionssystem

  - id: A2
    was: Erreichbarkeit und Besetzung der Bereitschaft täglich prüfen
    takt: taeglich
    frist: bis 07:00 Uhr
    r: [PS-DIS]
    a: PS-DIS
    c: []
    i: [BB-L]
    nachweis: Tagesprotokoll Disposition
    system: Dispositionssystem

  - id: A3
    was: Störungsmeldung aufnehmen, klassifizieren und Einsatz auslösen
    takt: laufend
    frist: Klassifizierung binnen 15 Minuten nach Eingang
    r: [PS-DIS]
    a: PS-DIS
    c: [SST-NF]
    i: [BB-MV]
    nachweis: Störungsdatensatz mit Zeitstempeln
    system: Störungsmanagement

  - id: A4
    was: Störung beheben und Anlagenzustand wiederherstellen
    takt: laufend
    frist: gemäß Reaktionszeit der Störungsklasse
    r: [BB-MA, SST-SDL]
    a: BB-MV
    c: [SST-NF]
    i: [PS-DIS]
    nachweis: Einsatzbericht mit Maßnahme und Ursache
    system: Störungsmanagement

  - id: A5
    was: Störungsdokumentation auf Vollständigkeit prüfen und nachfordern
    takt: woechentlich
    frist: bis Freitag 12:00 Uhr für die Vorwoche
    r: [PS-DIS]
    a: PS-TFV
    c: [PS-BBK]
    i: [BB-L]
    nachweis: Vollständigkeitsprüfung
    system: Cockpit

  - id: A6
    was: Wiederkehrende Störungen auswerten und Erneuerungsanstoß prüfen
    takt: quartalsweise
    frist: bis zum 15. Arbeitstag nach Quartalsende
    r: [PS-TFV]
    a: PS-TFV
    c: [SST-AM, BB-L]
    i: [PS-AL]
    nachweis: Auswertung Häufungsanlagen mit Empfehlung
    system: Cockpit

  - id: A7
    was: Großstörung nachbereiten und Erkenntnisse in Standards überführen
    takt: anlassbezogen
    frist: binnen 20 Arbeitstagen nach Wiederversorgung
    r: [PS-TFV]
    a: PS-AL
    c: [BB-L, SST-NF, FKT-SIFA]
    i: [SST-GF]
    nachweis: Nachbereitungsbericht mit Maßnahmenplan
    system: Regelwerksablage

kennzahlen:
  - id: KPI-ENT-01
    name: Einhaltung der Reaktionszeit je Störungsklasse
    ziel: ">= 95%"
    quelle: Störungsmanagement
    takt: monatlich
  - id: KPI-ENT-02
    name: Vollständig dokumentierte Störungen binnen 24 Stunden
    ziel: ">= 90%"
    quelle: Störungsmanagement
    takt: monatlich
  - id: KPI-ENT-03
    name: Anlagen mit mehr als drei Störungen in 12 Monaten
    ziel: "rückläufig gegenüber Vorjahr"
    quelle: Störungsmanagement
    takt: quartalsweise

eskalation:
  - stufe: 1
    wann: Bereitschaftsplatz nicht besetzt
    an: PS-DIS
  - stufe: 2
    wann: Reaktionszeit in einer Störungsklasse zweimal im Monat überschritten
    an: PS-TFV
  - stufe: 3
    wann: Großstörung oder Versorgungsunterbrechung mit Meldepflicht
    an: PS-AL
---

# Entstörung und Rufbereitschaft

## 1. Zweck

Die Entstörung ist die Leistung, an der wir als Betreiber am sichtbarsten
gemessen werden. Dieser Standard regelt, wie die Bereitschaft geplant, die
Meldung aufgenommen, der Einsatz gesteuert und die Erkenntnis daraus
weiterverwendet wird.

## 2. Geltungsbereich

Gilt für alle Störungen an Energieanlagen in der Betriebsverantwortung der
sieben Betriebsbereiche, rund um die Uhr, mit eigenem Personal wie mit
Servicedienstleistern.

Planbare Instandsetzung nach Zustandsbefund ist keine Störung und folgt
TF-IHS.

## 3. Begriffe

**Störungsklasse** bestimmt die Reaktionszeit. Die Klassifizierung erfolgt
bei Meldungseingang durch die Disposition, nicht durch die meldende Stelle.

**Reaktionszeit** ist die Spanne von der Klassifizierung bis zum Eintreffen
vor Ort, nicht bis zur Wiederversorgung.

## 4. Ablauf

1. Der Bereitschaftsplan steht vor Quartalsbeginn und ist für Netzführung
   und Disposition einsehbar (A1). Die tägliche Besetzungsprüfung fängt
   kurzfristige Ausfälle ab (A2).
2. Meldungen laufen über die Disposition. Sie klassifiziert binnen 15
   Minuten und löst den Einsatz aus (A3).
3. Die Behebung erfolgt durch eigenes Personal oder Dienstleister; die
   Ergebnisverantwortung bleibt bei der Meisterei (A4).
4. Die Dokumentation wird wöchentlich geprüft. Was nach einer Woche fehlt,
   fehlt dauerhaft (A5).
5. Quartalsweise werten wir Häufungen aus. Eine Anlage mit wiederkehrenden
   Störungen ist ein Erneuerungsanstoß an das Anlagenmanagement, kein
   Dauerzustand (A6).
6. Nach Großstörungen fließt die Erkenntnis in die Standards zurück -
   das ist die Verbindung zwischen Betrieb und Regelwerk (A7).

## 5. Nachweise

Störungsdatensätze mit Zeitstempeln, Einsatzberichte und
Nachbereitungsberichte. Aufbewahrung mindestens fünf Jahre, bei
meldepflichtigen Ereignissen länger nach Vorgabe von SST-REW.

## 6. Schnittstellen

SST-NF meldet Störungen mit Kundenbetroffenheit unverzüglich und erhält
nach Wiederversorgung die Störungsdaten.
SST-SDL hält die vertraglichen Reaktionszeiten ein und dokumentiert binnen
24 Stunden.
SST-AM erhält die Auswertung der Häufungsanlagen als Grundlage der
Erneuerungsplanung.

## 7. Abweichungen

Von den Reaktionszeiten wird nicht abgewichen. Ist die Bereitschaft
nachweislich nicht besetzbar, entscheidet PS-AL über eine befristete
Ersatzregelung mit einem benachbarten Betriebsbereich.

## 8. Änderungshistorie

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2022-09-01 | Ersterstellung | PS-RWM |
| 2.0.0 | 2024-04-01 | Klassifizierung an Disposition übertragen | PS-TFV |
| 2.2.0 | 2025-08-01 | Wöchentliche Dokumentationsprüfung (A5) | PS-TFV |
| 3.0.0 | 2026-06-15 | Häufungsauswertung als Erneuerungsanstoß (A6), Nachbereitung Großstörung (A7) | PS-TFV |
