---
# ==========================================================================
# PFLICHTFELDER - ohne diese schlägt "ps.py pruefen" fehl
# ==========================================================================
id: STD-XXX-000                 # STD-<Themenfeldkuerzel ohne TF->-<laufende Nr.>
titel: Kurzer, aktiver Titel
themenfeld: TF-XXX              # muss in daten/themenfelder.yaml existieren
version: 0.1.0                  # semantisch: major = Pflichten aendern sich
status: entwurf                 # entwurf | in_abstimmung | gueltig | ausgesetzt | archiviert
gueltig_ab: 2026-01-01
letzter_review: 2026-01-01
review_zyklus_monate: 12        # naechster Review wird daraus berechnet
owner: PS-TFV                   # traegt den Standard fachlich, muss darf_a_sein haben
freigabe: PS-AL                 # wer den Status auf gueltig setzen darf
rechtsstand_geprueft: false     # nur SST-REW bestaetigt das, niemals ein Agent
pflichten: []                   # IDs aus daten/pflichtenregister.yaml, z.B. [PFL-001]

geltungsbereich:
  betriebsbereiche: [alle]      # "alle" oder Liste von BB-IDs
  rollen: []                    # wen betrifft der Standard operativ

schnittstellen: []              # SST-IDs, die mitwirken oder betroffen sind

# ==========================================================================
# AUFGABEN - das Herzstück: wer macht was wann und weist es wie nach
# Regeln: genau ein A pro Aufgabe, mindestens ein R, jede Aufgabe hat
# Takt, Frist und Nachweis. Sonst ist es keine Vorgabe, sondern ein Wunsch.
# ==========================================================================
aufgaben:
  - id: A1
    was: Was konkret zu tun ist, in einem Satz, aktiv formuliert
    takt: jaehrlich             # taeglich|woechentlich|monatlich|quartalsweise|
                                # halbjaehrlich|jaehrlich|zweijaehrlich|
                                # vierjaehrlich|anlassbezogen|laufend|einmalig
    frist: bis 31.03. des Jahres
    r: [BB-MV]                  # fuehrt aus (mindestens eine Rolle)
    a: BB-L                     # verantwortet das Ergebnis (genau eine Rolle)
    c: []                       # wird fachlich beteiligt
    i: []                       # wird informiert
    nachweis: Welches Dokument den Vollzug belegt
    system: Wo der Nachweis liegt

kennzahlen:
  - id: KPI-XXX-01
    name: Was gemessen wird
    ziel: ">= 95%"
    quelle: Woher der Wert kommt
    takt: quartalsweise

eskalation:
  - stufe: 1
    wann: Frist um mehr als 10 Arbeitstage überschritten
    an: PS-BBK
  - stufe: 2
    wann: Frist um mehr als 20 Arbeitstage überschritten
    an: PS-TFV
  - stufe: 3
    wann: Pflichtverletzung mit Personen- oder Anlagenrisiko
    an: PS-AL
---

# {{titel}}

## 1. Zweck

Warum es diesen Standard gibt. Ein Absatz, kein Aufsatz. Wenn der Zweck nicht
in vier Sätzen erklärbar ist, sind es zwei Standards.

## 2. Geltungsbereich

Für wen und wo dieser Standard gilt - und ausdrücklich auch, wofür er
nicht gilt. Abgrenzung verhindert die häufigste Rückfrage.

## 3. Begriffe

Nur Begriffe, die im Haus unterschiedlich verwendet werden.

## 4. Ablauf

Der Ablauf in der Reihenfolge, in der er passiert. Jeder Schritt verweist auf
eine Aufgaben-ID aus dem Kopf (A1, A2, ...), damit Text und Verantwortung
nicht auseinanderlaufen.

## 5. Nachweise

Was aufbewahrt wird, wie lange, und wer es im Prüfungsfall vorlegt.

## 6. Schnittstellen

Was wir von Partnern brauchen und was wir liefern. Verweis auf
daten/organisation/schnittstellen.yaml statt Wiederholung.

## 7. Abweichungen

Wie eine begründete Abweichung beantragt wird und wer sie genehmigt.
Ein Standard ohne Abweichungsweg wird umgangen statt geändert.

## 8. Änderungshistorie

| Version | Datum | Änderung | Autor |
|---|---|---|---|
| 0.1.0 | 2026-01-01 | Ersterstellung | PS-RWM |
