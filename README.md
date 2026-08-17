# Regelwerk der Produktionssteuerung

Ein Kiro-Arbeitsbereich, in dem die Abteilung Produktionssteuerung ihre
Vorgaben führt: wer was bis wann tut, wie es nachgewiesen wird, und wo noch
etwas fehlt. Sieben Betriebsbereiche, 600 Mitarbeitende, ein Regelwerk.

Aus denselben Dateien entstehen die Prüfung, das Cockpit und die Fassungen
für die einzelnen Zielgruppen. Es gibt keine zweite Liste, die jemand
nachpflegen müsste.

## In fünf Minuten

```bash
python3 werkzeuge/ps.py status      # Wo stehen wir?
python3 werkzeuge/ps.py luecken     # Was ist noch nicht geregelt?
python3 werkzeuge/ps.py cockpit     # Gesamtsicht bauen
```

Dann `cockpit/index.html` im Browser öffnen.

Es wird nichts installiert. Python 3 genügt; PyYAML wird genutzt, wenn es da
ist, sonst greift der mitgelieferte Leser.

## Wie das Regelwerk aufgebaut ist

**Stammdaten** in `daten/` sind die eine Wahrheit: Rollen, Betriebsbereiche,
Themenfelder, Schnittstellenvereinbarungen, Betreiberpflichten.

**Standards** in `standards/` sind Markdown-Dateien mit maschinenlesbarem
Kopf. Im Kopf stehen die Aufgaben — und eine Aufgabe ist erst dann eine
Aufgabe, wenn sie Takt, Frist, genau eine verantwortliche Rolle, mindestens
eine ausführende Rolle und einen Nachweis hat. Die Prüfung lässt nichts
anderes durch.

**Drei Grundregeln**, die alles zusammenhalten:

1. Rollen, keine Personen. Personen wechseln, Rollen bleiben.
2. Genau ein A je Aufgabe. Zwei Verantwortliche sind keiner.
3. Beratung ist nicht Verantwortung. Wer berät (Sicherheitsfachkraft,
   Brandschutzbeauftragter), steht unter C, nie unter A.

## Die Befehle

| Befehl | Zweck |
|---|---|
| `ps.py status` | Kurzlage — der beste erste Befehl |
| `ps.py pruefen` | Regelwerk gegen alle Regeln prüfen |
| `ps.py luecken` | ungedeckte Pflichten, Themenfelder ohne Standard |
| `ps.py faellig --tage 90` | anstehende Reviews |
| `ps.py rollenblatt BB-MV` | alle Aufgaben einer Rolle über alle Standards |
| `ps.py neu TF-BRA "Titel"` | neuen Standard anlegen (vergibt die ID) |
| `ps.py cockpit` | Cockpit neu bauen |
| `ps.py selbsttest` | prüft den YAML-Rückfallleser gegen PyYAML |

Alle Befehle akzeptieren `--heute JJJJ-MM-TT`, um mit einem anderen Stichtag
zu rechnen.

## Das Agentensystem

In `.kiro/` steht, wie Kiro in diesem Arbeitsbereich arbeitet.

**Steering** (`.kiro/steering/`) gilt immer und beschreibt Auftrag,
Arbeitsweise, das Agententeam sowie — nur beim Bearbeiten der jeweiligen
Dateien — das Standardformat und die Regeln für Stammdaten.

**Acht Agentenrollen** bilden den Weg eines Themas ab:

| | Rolle | Wofür |
|---|---|---|
| A1 | Themen-Triage | einordnen, bevor jemand formuliert |
| A2 | Standard-Architekt | prüffähigen Standard bauen |
| A3 | Pflichten-Prüfer | Lücken zwischen Pflicht und Regelung |
| A4 | RACI-Wächter | trägt die Verantwortung wirklich? |
| A5 | Schnittstellen-Lotse | sind Erwartungen beidseitig vereinbart? |
| A6 | Rollout-Redakteur | die vier Zielgruppenfassungen |
| A7 | Review-Radar | nichts veraltet unbemerkt |
| A8 | Cockpit-Kurator | Gesamtbild aktuell und ehrlich |

**Hooks** (`.kiro/hooks/`) starten das: Zwei laufen selbsttätig bei Änderungen
an `standards/` und `daten/`, sieben starten Sie bei Bedarf — Thema aufnehmen,
Standard anlegen, Review-Radar, Rollout-Paket, Lückenanalyse,
Schnittstellen-Check, Lagebericht.

**Zwei Stellen sind Agenten gesperrt.** Der Status `gueltig` wird von der
Abteilungsleitung gesetzt, und `rechtsstand_geprueft` ausschließlich nach
Bestätigung durch Recht und Compliance. Das System schlägt Rechtsgrundlagen
vor, aber es behauptet nie, etwas sei rechtlich verbindlich.

## Einen neuen Standard aufsetzen

```bash
python3 werkzeuge/ps.py neu TF-OBJ "Zutrittssicherung unbesetzter Anlagen"
```

Legt die Datei am richtigen Ort an und vergibt die nächste freie ID. Danach
die Aufgaben füllen — das ist die eigentliche Arbeit — und prüfen lassen.
Bequemer geht es über den Hook „Neuen Standard anlegen": Der Agent fragt nach
dem tatsächlichen Ablauf, baut den Entwurf und nennt die Punkte, die in der
Abstimmung strittig werden.

Der neue Standard startet im Status `entwurf` und geht über `in_abstimmung`
zur Freigabe. Erst danach werden die Rolloutfassungen erzeugt.

## Was noch zu tun ist

Die Stammdaten enthalten Platzhalter: Die Bezeichnungen der sieben
Betriebsbereiche, die Kopfzahlen und die Systemnamen sind Beispielwerte und
müssen durch die echten ersetzt werden. Das Pflichtenregister ist eine
fachliche Arbeitsgrundlage und noch von keiner Stelle rechtlich bestätigt.

Die vollständige Einführungsliste steht in
`.kiro/specs/regelwerk-cockpit/tasks.md` unter Abschnitt 6.

## Aufbau

```
daten/            Stammdaten (Rollen, Bereiche, Themenfelder, Pflichten)
standards/        das Regelwerk, ein Verzeichnis je Themenfeld
rollout/          Zielgruppenfassungen und ihre Vorlagen
werkzeuge/        ps.py, cockpit.py, miniyaml.py
cockpit/          erzeugte Gesamtsicht — nicht von Hand ändern
.kiro/            Steering, Specs, Hooks, MCP-Konfiguration
```
