---
id: STD-ARB-001
titel: Jährliche Unterweisung der Beschäftigten
themenfeld: TF-ARB
version: 2.1.0
status: gueltig
gueltig_ab: 2025-01-01
letzter_review: 2025-06-01
review_zyklus_monate: 12
owner: PS-TFV
freigabe: PS-AL
rechtsstand_geprueft: false
pflichten: [PFL-002, PFL-021]

geltungsbereich:
  betriebsbereiche: [alle]
  rollen: [BB-L, BB-MV, BB-MA]

schnittstellen: [SST-HR, SST-SDL]

aufgaben:
  - id: A1
    was: Unterweisungsthemen des Folgejahres festlegen und veröffentlichen
    takt: jaehrlich
    frist: bis 30.11. für das Folgejahr
    r: [PS-TFV]
    a: PS-TFV
    c: [FKT-SIFA, FKT-BAD]
    i: [BB-L, PS-AL]
    nachweis: Unterweisungsplan mit Themenliste
    system: Regelwerksablage / Cockpit

  - id: A2
    was: Unterweisungstermine im Bereich planen und Teilnehmende zuordnen
    takt: jaehrlich
    frist: bis 31.01. des laufenden Jahres
    r: [BB-MV]
    a: BB-L
    c: [PS-BBK]
    i: [SST-HR]
    nachweis: Terminplan je Meisterei
    system: Schulungsverwaltung

  - id: A3
    was: Unterweisung durchführen und Teilnahme dokumentieren
    takt: jaehrlich
    frist: bis 31.10. des laufenden Jahres
    r: [BB-MV]
    a: BB-L
    c: [FKT-SIBE]
    i: [PS-BBK]
    nachweis: Unterschriebener Unterweisungsnachweis je Person
    system: Personalakte / Schulungsverwaltung

  - id: A4
    was: Neu eintretende oder versetzte Beschäftigte vor Tätigkeitsaufnahme unterweisen
    takt: anlassbezogen
    frist: vor dem ersten Arbeitseinsatz
    r: [BB-MV]
    a: BB-L
    c: [FKT-SIFA]
    i: [SST-HR]
    nachweis: Erstunterweisungsnachweis
    system: Personalakte

  - id: A5
    was: Nachweis der Unterweisung des Dienstleisterpersonals einfordern
    takt: jaehrlich
    frist: vor Ersteinsatz, danach jährlich bis 31.10.
    r: [PS-BBK]
    a: PS-TFV
    c: [SST-EK]
    i: [BB-L]
    nachweis: Bestätigung des Dienstleisters je eingesetzter Person
    system: Auftragsakte

  - id: A6
    was: Unterweisungsquote je Betriebsbereich auswerten und Lücken melden
    takt: quartalsweise
    frist: bis zum 10. Arbeitstag nach Quartalsende
    r: [PS-CON]
    a: PS-TFV
    c: [PS-BBK]
    i: [PS-AL, BB-L]
    nachweis: Quartalsauswertung
    system: Cockpit

kennzahlen:
  - id: KPI-ARB-01
    name: Unterweisungsquote eigene Beschäftigte
    ziel: ">= 98% bis 31.10."
    quelle: Schulungsverwaltung
    takt: quartalsweise
  - id: KPI-ARB-02
    name: Anteil Erstunterweisungen vor Einsatzbeginn
    ziel: "100%"
    quelle: Personalakte
    takt: quartalsweise

eskalation:
  - stufe: 1
    wann: Quote im Bereich am 30.09. unter 80%
    an: PS-BBK
  - stufe: 2
    wann: Quote am 31.10. unter 98%
    an: PS-TFV
  - stufe: 3
    wann: Beschäftigte ohne gültige Unterweisung im Einsatz
    an: PS-AL
---

# Jährliche Unterweisung der Beschäftigten

## 1. Zweck

Jede Person, die in unseren Energieanlagen arbeitet, muss die Gefährdungen
ihrer Tätigkeit und die geltenden Schutzmaßnahmen kennen. Die Unterweisung
ist der Nachweis, dass wir als Betreiber dieser Pflicht nachgekommen sind.
Dieser Standard legt fest, wer sie plant, durchführt und nachhält - für
eigene Beschäftigte und für Dienstleisterpersonal gleichermaßen.

## 2. Geltungsbereich

Gilt für alle Beschäftigten in allen sieben Betriebsbereichen sowie für
Fremdpersonal, das in unseren Anlagen tätig wird.

Nicht Gegenstand dieses Standards sind fachliche Qualifikationsnachweise
(Schaltberechtigung, Befähigung zur Prüfung) - diese regelt TF-QUA.

## 3. Begriffe

**Unterweisung** meint die tätigkeitsbezogene Belehrung vor Ort, nicht die
allgemeine E-Learning-Pflichtschulung des Konzerns. Beides ist zu leisten,
nur Ersteres fällt unter diesen Standard.

**Einsatzbeginn** ist der erste Tag mit eigenständiger Tätigkeit an oder in
einer Anlage, nicht der Vertragsbeginn.

## 4. Ablauf

1. Die Themenliste für das Folgejahr entsteht bis 30.11. aus drei Quellen:
   Pflichtthemen, Erkenntnissen aus Unfällen und Beinaheunfällen des
   laufenden Jahres, sowie neuen oder geänderten Standards (A1).
2. Die Bereiche planen ihre Termine bis 31.01. und ordnen die Teilnehmenden
   den Terminen zu (A2).
3. Die Durchführung erfolgt bis 31.10., damit das vierte Quartal als Puffer
   für Nachholtermine bleibt (A3).
4. Wer neu dazukommt oder die Tätigkeit wechselt, wird vor dem ersten
   Einsatz unterwiesen - unabhängig vom Jahreszyklus (A4).
5. Für Dienstleisterpersonal fordern wir den Nachweis an, statt selbst zu
   unterweisen. Ohne Nachweis kein Einsatz (A5).
6. Die Auswertung läuft quartalsweise, damit die Lücke im September
   sichtbar wird und nicht erst im Dezember (A6).

## 5. Nachweise

Unterweisungsnachweise werden mindestens fünf Jahre aufbewahrt. Im
Prüfungsfall legt die Betriebsbereichsleitung sie vor. Die
Produktionssteuerung liefert die Gesamtübersicht, nicht die Einzelbelege.

## 6. Schnittstellen

SST-HR stellt die Schulungsverwaltung und die Teilnehmendenlisten.
SST-SDL liefert Nachweise für das eigene Personal gemäß Vertrag - die
Anforderung dazu steht in der Schnittstellenvereinbarung, nicht im
Einzelauftrag.

## 7. Abweichungen

Eine Verschiebung über den 31.10. hinaus genehmigt PS-TFV auf schriftlichen
Antrag der Betriebsbereichsleitung mit neuem Termin. Eine Abweichung von der
Unterweisung selbst gibt es nicht.

## 8. Änderungshistorie

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 1.0.0 | 2023-02-01 | Ersterstellung | PS-RWM |
| 2.0.0 | 2025-01-01 | Dienstleisterpersonal aufgenommen (A5), Quote als KPI | PS-TFV |
| 2.1.0 | 2025-06-01 | Quartalsauswertung ergänzt (A6), Eskalationsstufen geschärft | PS-TFV |
