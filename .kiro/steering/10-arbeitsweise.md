---
inclusion: always
---

# Arbeitsweise und Aufbau des Repositories

## Wo was liegt

```
daten/                      Stammdaten - die eine Wahrheit
  organisation/
    rollen.yaml             alle Rollen-IDs, Ebenen, wer A sein darf
    betriebsbereiche.yaml   die sieben Bereiche
    schnittstellen.yaml     was wir liefern, was wir erwarten
  themenfelder.yaml         die Themenfelder mit Verantwortung
  pflichtenregister.yaml    Betreiberpflichten mit Träger und Turnus

standards/<themenfeld>/     die Standards, ein Markdown je Standard
  _vorlagen/                Vorlage - nie direkt bearbeiten

rollout/                    Zielgruppenfassungen, aus Standards abgeleitet
werkzeuge/                  ps.py (Prüfung, Auswertung), cockpit.py, miniyaml.py
cockpit/index.html          erzeugte Gesamtsicht - niemals von Hand ändern

.kiro/steering/             diese Anweisungen
.kiro/specs/                Spezifikationen für größere Vorhaben
.kiro/hooks/                Auslöser für wiederkehrende Aufgaben
```

## Die Werkzeuge

Immer über die Kommandozeile, nie durch Nachbauen der Logik im Kopf:

| Befehl | Zweck |
|---|---|
| `python3 werkzeuge/ps.py pruefen` | Regelwerk gegen alle Regeln prüfen, Rückgabewert 1 bei Fehlern |
| `python3 werkzeuge/ps.py status` | Kurzlage — der beste erste Befehl in einer neuen Sitzung |
| `python3 werkzeuge/ps.py luecken` | ungedeckte Pflichten, Themenfelder ohne Standard |
| `python3 werkzeuge/ps.py faellig --tage 90` | anstehende Reviews |
| `python3 werkzeuge/ps.py rollenblatt BB-MV` | Wer-macht-was-wann für eine Rolle |
| `python3 werkzeuge/ps.py neu TF-BRA "Titel"` | neuen Standard aus der Vorlage anlegen |
| `python3 werkzeuge/ps.py cockpit` | Cockpit neu bauen |
| `python3 werkzeuge/ps.py selbsttest` | prüft den YAML-Rückfallleser gegen PyYAML |

`ps.py neu` vergibt die nächste freie ID und legt die Datei am richtigen Ort
an. Lege Standards nie von Hand an — die ID-Vergabe würde kollidieren.

## Verbindliche Regeln beim Ändern

1. **Erst lesen, dann ändern.** Vor jeder Änderung an einem Themenfeld:
   `ps.py status` und den bestehenden Standard des Feldes lesen. Doppelte
   Regelungen zum selben Sachverhalt sind der häufigste Fehler.
2. **Stammdaten vor Standards.** Fehlt eine Rolle, ein Themenfeld oder eine
   Pflicht, ergänze zuerst `daten/`, dann den Standard. Ein Standard, der auf
   eine unbekannte ID zeigt, ist ein Fehler und kein Zwischenstand.
3. **IDs sind unveränderlich.** `STD-*`, `TF-*`, `PFL-*`, `KPI-*`, Rollen-IDs
   und Betriebsbereichs-IDs werden nie umbenannt. Sie stehen in Aushängen,
   Protokollen und E-Mails im ganzen Unternehmen.
4. **Bezeichner bleiben ASCII, Text bekommt Umlaute.** Schlüssel und
   Aufzählungswerte in YAML (`gueltig`, `jaehrlich`, `halbjaehrlich`) sind
   Bezeichner und bleiben, wie sie sind. Jeder Text, den ein Mensch liest —
   `titel`, `was`, `frist`, `nachweis`, Fließtext — wird in korrektem Deutsch
   mit Umlauten geschrieben.
5. **Nach der Änderung prüfen und bauen.** `ps.py pruefen`, danach
   `ps.py cockpit`. Ein Commit mit Fehlern im Regelwerk geht nicht raus.
6. **Änderungshistorie fortschreiben.** Jede inhaltliche Änderung an einem
   Standard erhöht die Version und bekommt eine Zeile in Abschnitt 8.
   Ändern sich Pflichten für die Betriebsbereiche, ist es eine Major-Version.

## Was du nicht tust

- `cockpit/index.html` von Hand bearbeiten. Die Datei ist ein Erzeugnis.
- `rechtsstand_geprueft` auf `true` setzen.
- Den Status auf `gueltig` setzen.
- Personennamen ins Regelwerk schreiben.
- Eine Prüfung mit `--nur-fehler` als bestanden melden, wenn Warnungen offen
  sind — Warnungen benennst du im Ergebnisbericht.
- Bestehende Standards stillschweigend umschreiben. Änderungen an einem
  gültigen Standard werden benannt und begründet.
