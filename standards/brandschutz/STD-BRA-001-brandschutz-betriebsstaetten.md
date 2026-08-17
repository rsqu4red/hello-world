---
id: STD-BRA-001
titel: Organisatorischer Brandschutz an Betriebsstätten und Anlagen
themenfeld: TF-BRA
version: 1.3.0
status: gueltig
gueltig_ab: 2026-03-01
letzter_review: 2026-02-01
review_zyklus_monate: 12
owner: PS-TFV
freigabe: PS-AL
rechtsstand_geprueft: false
pflichten: [PFL-005, PFL-006, PFL-007]

geltungsbereich:
  betriebsbereiche: [alle]
  rollen: [BB-L, BB-MV, BB-MA]

schnittstellen: [SST-SDL, SST-PM]

aufgaben:
  - id: A1
    was: Brandschutzordnung Teil A, B und C je Betriebsstätte prüfen und fortschreiben
    takt: zweijaehrlich
    frist: bis 30.06. des Prüfjahres
    r: [FKT-BSB]
    a: PS-TFV
    c: [BB-L, FKT-SIFA]
    i: [PS-AL]
    nachweis: Fortschreibungsvermerk mit Datum und Unterschrift
    system: Regelwerksablage

  - id: A2
    was: Feuerlöscher und Wandhydranten prüfen lassen
    takt: zweijaehrlich
    frist: vor Ablauf der Prüfplakette
    r: [SST-SDL]
    a: BB-L
    c: [FKT-BSB]
    i: [PS-BBK]
    nachweis: Prüfprotokoll und Plakette
    system: Instandhaltungssystem

  - id: A3
    was: Flucht- und Rettungswege sowie Brandschutztüren begehen und Mängel erfassen
    takt: quartalsweise
    frist: bis zum Quartalsende
    r: [BB-MV]
    a: BB-L
    c: [FKT-BSB]
    i: [PS-BBK]
    nachweis: Begehungsprotokoll mit Mängelliste
    system: Mängelmanagement

  - id: A4
    was: Brandschutzhelfer benennen, ausbilden und Ausbildung auffrischen
    takt: dreijaehrlich
    frist: vor Ablauf der Ausbildungsgültigkeit
    r: [BB-MV]
    a: BB-L
    c: [FKT-BSB, SST-HR]
    i: [PS-TFV]
    nachweis: Teilnahmebescheinigung und Benennungsliste
    system: Schulungsverwaltung

  - id: A5
    was: Räumungsübung an besetzten Standorten durchführen
    takt: zweijaehrlich
    frist: bis 30.09. des Übungsjahres
    r: [FKT-BSB]
    a: BB-L
    c: [FKT-SIFA]
    i: [PS-TFV, PS-AL]
    nachweis: Übungsprotokoll mit Auswertung
    system: Regelwerksablage

  - id: A6
    was: Brandschutzanforderungen in Erneuerungsprojekten vor Planungsfreigabe einbringen
    takt: anlassbezogen
    frist: vor Abschluss der Vorplanung
    r: [FKT-BSB]
    a: PS-TFV
    c: [SST-PM]
    i: [BB-L]
    nachweis: Stellungnahme im Projektordner
    system: Projektablage

  - id: A7
    was: Erledigung der Mängel aus Begehungen nachhalten
    takt: monatlich
    frist: bis zum 10. Arbeitstag des Folgemonats
    r: [PS-BBK]
    a: PS-TFV
    c: [BB-L]
    i: [PS-AL]
    nachweis: Mängelstatusbericht
    system: Cockpit

kennzahlen:
  - id: KPI-BRA-01
    name: Anteil Betriebsstätten mit aktueller Brandschutzordnung
    ziel: "100%"
    quelle: Regelwerksablage
    takt: halbjaehrlich
  - id: KPI-BRA-02
    name: Offene Brandschutzmängel älter als 60 Tage
    ziel: "0"
    quelle: Mängelmanagement
    takt: monatlich
  - id: KPI-BRA-03
    name: Brandschutzhelferquote je besetztem Standort
    ziel: ">= 10% der Anwesenden"
    quelle: Schulungsverwaltung
    takt: jaehrlich

eskalation:
  - stufe: 1
    wann: Mängel aus Begehung nach 30 Tagen ohne Maßnahme
    an: PS-BBK
  - stufe: 2
    wann: Prüfplakette an Löscheinrichtung abgelaufen
    an: PS-TFV
  - stufe: 3
    wann: Flucht- oder Rettungsweg dauerhaft versperrt
    an: PS-AL
---

# Organisatorischer Brandschutz an Betriebsstätten und Anlagen

## 1. Zweck

Brandschutz scheitert selten am Konzept und fast immer an der Nachverfolgung.
Dieser Standard legt die wiederkehrenden Pflichten fest, benennt für jede
einen Verantwortlichen und macht den Mängelstatus monatlich sichtbar.

## 2. Geltungsbereich

Gilt für alle besetzten Betriebsstätten und alle unbesetzten Anlagen der
sieben Betriebsbereiche.

Der anlagentechnische Brandschutz in Umspannwerken - insbesondere
Löschanlagen und Ölauffangeinrichtungen - wird über die
Instandhaltungsanleitungen in TF-IHS abgedeckt und ist hier nur insoweit
enthalten, als er Gegenstand der Begehung ist.

## 3. Begriffe

**Besetzter Standort** ist eine Betriebsstätte mit regelmäßig anwesenden
Beschäftigten. Alle übrigen Anlagen gelten als unbesetzt und unterliegen
nicht der Räumungsübung.

## 4. Ablauf

1. Die Brandschutzordnung wird alle zwei Jahre geprüft, nicht nur bei
   Anlass - der Anlass wird sonst übersehen (A1).
2. Löscheinrichtungen werden über den Servicedienstleister geprüft. Die
   Terminüberwachung bleibt bei uns, nicht beim Dienstleister (A2).
3. Die quartalsweise Begehung ist das Rückgrat: sie erzeugt die Mängel,
   die in A7 nachgehalten werden (A3).
4. Brandschutzhelfer und Räumungsübungen folgen ihren eigenen Zyklen
   (A4, A5).
5. In Erneuerungsprojekten bringen wir Brandschutzanforderungen vor
   Abschluss der Vorplanung ein. Danach kostet jede Anforderung ein
   Änderungsverfahren (A6).

## 5. Nachweise

Begehungsprotokolle, Prüfprotokolle und Übungsauswertungen werden
mindestens fünf Jahre aufbewahrt. Die Brandschutzordnung wird in der
jeweils gültigen Fassung vorgehalten, Vorversionen archiviert.

## 6. Schnittstellen

SST-SDL führt die Prüfung der Löscheinrichtungen aus und meldet
Ergebnisse ins Instandhaltungssystem zurück.
SST-PM bindet FKT-BSB ab Vorplanung ein - dies ist Teil der
Schnittstellenvereinbarung mit dem Projektmanagement.

## 7. Abweichungen

Eine Verschiebung der Räumungsübung genehmigt PS-TFV im Einvernehmen mit
FKT-BSB, maximal um sechs Monate. Fristen an Löscheinrichtungen sind nicht
verschiebbar.

## 8. Änderungshistorie

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2024-05-01 | Ersterstellung | PS-RWM |
| 1.1.0 | 2025-04-01 | Begehungsturnus von halbjährlich auf quartalsweise | PS-TFV |
| 1.2.0 | 2025-10-01 | Einbindung Projektmanagement ergänzt (A6) | PS-TFV |
| 1.3.0 | 2026-02-01 | Mängelnachverfolgung als eigene Aufgabe (A7) und KPI-BRA-02 | PS-TFV |
