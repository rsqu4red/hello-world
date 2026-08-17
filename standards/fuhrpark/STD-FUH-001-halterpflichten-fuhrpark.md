---
id: STD-FUH-001
titel: Halterpflichten im Fuhrpark
themenfeld: TF-FUH
version: 1.1.0
status: gueltig
gueltig_ab: 2025-12-01
letzter_review: 2025-11-01
review_zyklus_monate: 12
owner: PS-TFV
freigabe: PS-AL
rechtsstand_geprueft: false
pflichten: [PFL-013, PFL-014]

geltungsbereich:
  betriebsbereiche: [alle]
  rollen: [BB-L, BB-MV, BB-MA]

schnittstellen: [SST-EK, SST-HR]

aufgaben:
  - id: A1
    was: Führerscheinkontrolle für alle Fahrberechtigten durchführen
    takt: halbjaehrlich
    frist: bis 31.03. und 30.09.
    r: [BB-MV]
    a: FKT-FPV
    c: [SST-HR]
    i: [BB-L]
    nachweis: Kontrollnachweis je Person mit Datum
    system: Fuhrparkverwaltung

  - id: A2
    was: UVV-Prüfung der Fahrzeuge und Aufbauten beauftragen und überwachen
    takt: jaehrlich
    frist: vor Ablauf der letzten Prüfung
    r: [BB-MV]
    a: FKT-FPV
    c: [SST-SDL]
    i: [PS-BBK]
    nachweis: UVV-Prüfbericht
    system: Fuhrparkverwaltung

  - id: A3
    was: Fahrer:innen zu Ladungssicherung und Fahrzeugnutzung unterweisen
    takt: jaehrlich
    frist: gemeinsam mit der Unterweisung nach STD-ARB-001
    r: [BB-MV]
    a: BB-L
    c: [FKT-FPV, FKT-SIFA]
    i: [PS-TFV]
    nachweis: Unterweisungsnachweis
    system: Schulungsverwaltung

  - id: A4
    was: Fahrzeugschäden und Unfälle melden und auswerten
    takt: anlassbezogen
    frist: Meldung binnen 24 Stunden, Auswertung quartalsweise
    r: [BB-MV]
    a: FKT-FPV
    c: [FKT-SIFA]
    i: [PS-AL, BB-L]
    nachweis: Schadensmeldung und Quartalsauswertung
    system: Fuhrparkverwaltung

  - id: A5
    was: Fahrzeugbedarf und Ersatzbeschaffung für das Folgejahr melden
    takt: jaehrlich
    frist: bis 30.09.
    r: [BB-L]
    a: FKT-FPV
    c: [SST-EK, PS-CON]
    i: [PS-AL]
    nachweis: Bedarfsmeldung mit Begründung
    system: Beschaffungsablage

kennzahlen:
  - id: KPI-FUH-01
    name: Fahrzeuge mit gültiger UVV-Prüfung
    ziel: "100%"
    quelle: Fuhrparkverwaltung
    takt: monatlich
  - id: KPI-FUH-02
    name: Durchgeführte Führerscheinkontrollen im Termin
    ziel: "100%"
    quelle: Fuhrparkverwaltung
    takt: halbjaehrlich

eskalation:
  - stufe: 1
    wann: Kontrolltermin um mehr als 10 Arbeitstage überschritten
    an: FKT-FPV
  - stufe: 2
    wann: Fahrzeug ohne gültige UVV-Prüfung im Einsatz
    an: PS-TFV
  - stufe: 3
    wann: Fahrt ohne gültige Fahrerlaubnis festgestellt
    an: PS-AL
---

# Halterpflichten im Fuhrpark

## 1. Zweck

Die Halterverantwortung für rund 300 Fahrzeuge liegt beim Unternehmen und
ist an die Fuhrparkverantwortung und die Betriebsbereiche delegiert. Dieser
Standard beschreibt, welche Kontrollen wann stattfinden und wie sie
nachgewiesen werden - denn die Delegation wirkt nur, wenn die Kontrolle
dokumentiert ist.

## 2. Geltungsbereich

Gilt für alle Dienstfahrzeuge, Anhänger und Sonderfahrzeuge in der Nutzung
der sieben Betriebsbereiche, einschließlich Poolfahrzeugen.

Nicht erfasst sind Mietfahrzeuge unter 30 Tagen Nutzungsdauer; hier gilt die
Regelung des Vermieters, die Unterweisung nach A3 bleibt gleichwohl Pflicht.

## 3. Begriffe

**Fahrberechtigt** ist, wer im Fuhrparksystem hinterlegt ist und dessen
Führerscheinkontrolle nicht älter als sechs Monate ist. Beides muss
zutreffen.

## 4. Ablauf

1. Die Führerscheinkontrolle läuft in zwei festen Wellen im Jahr, damit
   sie planbar bleibt (A1).
2. Die UVV-Prüfung wird fahrzeugbezogen überwacht. Maßgeblich ist das
   Datum der letzten Prüfung, nicht das Kalenderjahr (A2).
3. Die Fahrzeugunterweisung wird mit der Jahresunterweisung gebündelt,
   damit kein zweiter Termin entsteht (A3).
4. Schäden werden binnen 24 Stunden gemeldet und quartalsweise ausgewertet;
   Häufungen fließen in die Unterweisungsthemen des Folgejahres (A4).
5. Der Bedarf für das Folgejahr wird bis 30.09. gemeldet, passend zum
   Budgetprozess (A5).

## 5. Nachweise

Kontrollnachweise, UVV-Prüfberichte und Schadensmeldungen werden in der
Fuhrparkverwaltung geführt und mindestens fünf Jahre aufbewahrt.

## 6. Schnittstellen

SST-EK führt die Beschaffung auf Basis der Bedarfsmeldung.
SST-HR meldet Ein- und Austritte, damit Fahrberechtigungen aktuell bleiben.

## 7. Abweichungen

Eine Verschiebung der Führerscheinkontrolle ist bei längerer Abwesenheit
zulässig; die Kontrolle erfolgt vor der nächsten Fahrt. Die Fahrberechtigung
ruht bis dahin.

## 8. Änderungshistorie

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2024-11-01 | Ersterstellung | PS-RWM |
| 1.1.0 | 2025-11-01 | Bedarfsmeldung an Budgetprozess angebunden (A5) | PS-TFV |
