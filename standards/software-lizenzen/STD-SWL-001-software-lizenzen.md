---
id: STD-SWL-001
titel: Beschaffung und Nachweis von Software-Lizenzen
themenfeld: TF-SWL
version: 0.4.0
status: in_abstimmung
gueltig_ab: 2026-10-01
letzter_review: 2026-08-01
review_zyklus_monate: 24
owner: PS-TFV
freigabe: PS-AL
rechtsstand_geprueft: false
pflichten: [PFL-016]

geltungsbereich:
  betriebsbereiche: [alle]
  rollen: [BB-L, PS-TFV, PS-BBK]

schnittstellen: [SST-IT, SST-EK]

aufgaben:
  - id: A1
    was: Softwarebedarf melden mit Nutzerkreis, Kostenstelle und Begründung
    takt: anlassbezogen
    frist: mindestens 30 Arbeitstage vor benötigtem Einsatzbeginn
    r: [BB-L]
    a: PS-TFV
    c: [SST-IT]
    i: [PS-CON]
    nachweis: Bedarfsmeldung
    system: IT-Serviceportal

  - id: A2
    was: Tatsächlichen Nutzerkreis je Fachanwendung bestätigen und ungenutzte Lizenzen zurückgeben
    takt: jaehrlich
    frist: bis 31.03.
    r: [PS-BBK]
    a: PS-TFV
    c: [SST-IT]
    i: [PS-CON, PS-AL]
    nachweis: Bestätigte Nutzerliste je Anwendung
    system: Lizenzverwaltung

  - id: A3
    was: Auslaufende Lizenzverträge prüfen und Verlängerung oder Ablösung entscheiden
    takt: quartalsweise
    frist: spätestens 90 Tage vor Vertragsablauf
    r: [PS-TFV]
    a: PS-TFV
    c: [SST-IT, SST-EK, PS-CON]
    i: [PS-AL]
    nachweis: Entscheidungsvermerk
    system: Vertragsablage

  - id: A4
    was: Einsatz von Software außerhalb des freigegebenen Katalogs melden
    takt: anlassbezogen
    frist: unverzüglich bei Kenntnis
    r: [BB-L]
    a: PS-TFV
    c: [SST-IT, FKT-ISB]
    i: [PS-AL]
    nachweis: Meldung mit Bewertung
    system: IT-Serviceportal

kennzahlen:
  - id: KPI-SWL-01
    name: Anteil Fachanwendungen mit bestätigtem Nutzerkreis
    ziel: "100% bis 31.03."
    quelle: Lizenzverwaltung
    takt: jaehrlich
  - id: KPI-SWL-02
    name: Verträge ohne Entscheidung 60 Tage vor Ablauf
    ziel: "0"
    quelle: Vertragsablage
    takt: quartalsweise

eskalation:
  - stufe: 1
    wann: Nutzerkreisbestätigung nach dem 31.03. offen
    an: PS-TFV
  - stufe: 2
    wann: Vertragsablauf in weniger als 30 Tagen ohne Entscheidung
    an: PS-AL
  - stufe: 3
    wann: Nutzung ohne gültige Lizenz festgestellt
    an: PS-AL
---

# Beschaffung und Nachweis von Software-Lizenzen

> **Status: in Abstimmung.** Offen ist die Abgrenzung zu SST-IT bei
> Fachanwendungen der Betriebs- und Leittechnik. Bis zur Freigabe durch
> PS-AL gilt die bisherige Praxis fort.

## 1. Zweck

Fachanwendungen der Produktionssteuerung werden fachlich von uns
verantwortet, aber über die IT beschafft. Dieser Standard klaert, wer den
Bedarf meldet, wer den Nutzerkreis bestätigt und wer die Verlängerung
entscheidet - damit Lizenzen weder ungenutzt weiterlaufen noch unbemerkt
ablaufen.

## 2. Geltungsbereich

Gilt für alle Softwarelizenzen, deren fachliche Verantwortung bei der
Produktionssteuerung oder den Betriebsbereichen liegt.

Nicht erfasst sind Arbeitsplatz-Standardsoftware und Konzernanwendungen -
diese verantwortet SST-IT vollständig.

## 3. Begriffe

**Fachanwendung** ist Software, deren Nutzerkreis und Konfiguration wir
fachlich bestimmen, unabhängig davon, wer den Vertrag hält.

## 4. Ablauf

1. Bedarf wird mit Nutzerkreis und Kostenstelle gemeldet, mit 30
   Arbeitstagen Vorlauf (A1).
2. Einmal jährlich bestätigen wir den tatsächlichen Nutzerkreis und geben
   zurück, was nicht genutzt wird (A2). Das ist der wirksamste Hebel gegen
   stille Kostensteigerung.
3. Auslaufende Verträge werden quartalsweise geprüft, nicht erst bei der
   Kündigungserinnerung des Herstellers (A3).
4. Software außerhalb des Katalogs wird gemeldet, nicht geduldet - auch
   wenn sie fachlich sinnvoll ist. Der Weg dahin ist A1 (A4).

## 5. Nachweise

Bedarfsmeldungen, bestätigte Nutzerlisten und Entscheidungsvermerke werden
für die Vertragslaufzeit zuzüglich drei Jahren aufbewahrt.

## 6. Schnittstellen

SST-IT liefert quartalsweise die Lizenzbestandsliste je Kostenstelle und
warnt 90 Tage vor Vertragsverlängerung vor. Diese Zulieferung ist noch im
Reifegrad Entwurf - siehe daten/organisation/schnittstellen.yaml.

## 7. Abweichungen

Eine kurzfristige Beschaffung unter 30 Arbeitstagen Vorlauf genehmigt PS-AL
bei betrieblicher Dringlichkeit.

## 8. Änderungshistorie

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-05-01 | Ersterstellung | PS-RWM |
| 0.4.0 | 2026-08-01 | Jährliche Nutzerkreisbestätigung ergänzt (A2) | PS-TFV |
