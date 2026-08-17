# Entwurf — Regelwerk und Cockpit

## Überblick

Das System besteht aus vier Schichten. Jede hat genau eine Aufgabe, und der
Datenfluss geht nur in eine Richtung — von den Stammdaten zur Darstellung.
Dadurch gibt es keine Stelle, an der zwei Wahrheiten entstehen können.

```
  daten/*.yaml            Stammdaten: Rollen, Themenfelder, Bereiche,
        │                 Schnittstellen, Betreiberpflichten
        ▼
  standards/**/*.md       Regelwerk: Kopfdaten (YAML) + Fließtext (Markdown)
        │                 Kopfdaten verweisen auf Stammdaten-IDs
        ▼
  werkzeuge/ps.py         Modell, Prüfung, Auswertungen
        │
        ├──► Konsole      pruefen, status, luecken, faellig, rollenblatt
        ├──► rollout/     Zielgruppenfassungen (agentengestützt)
        └──► cockpit/     eine erzeugte HTML-Seite
```

Der zweite Kreislauf sind die Agenten: Sie lesen dieselben Dateien, ändern
`daten/` und `standards/` und stoßen die Werkzeuge an. Sie stehen nie
zwischen Daten und Darstellung.

## Entwurfsentscheidungen

**Markdown mit YAML-Kopf statt Datenbank.** Ein Standard ist ein Dokument,
das Menschen lesen, kommentieren und in der Abstimmung ändern. Er gehört in
ein Format, das jeder öffnen kann und das Git versionieren kann. Die
maschinell auswertbaren Angaben stehen im Kopf, die Begründung im Text. Eine
Datenbank hätte die Auswertung erleichtert und die Abstimmung erschwert — für
diese Abteilung ist die Abstimmung der schwierigere Teil.

**Rollen statt Personen.** Personen wechseln, Rollen bleiben. Die Zuordnung
Rolle zu Person wird bewusst außerhalb geführt, im Organigramm und in den
schriftlichen Bestellungen. So bleibt das Regelwerk über Personalwechsel
hinweg gültig und enthält keine personenbezogenen Daten.

**Genau ein A je Aufgabe, technisch erzwungen.** Die häufigste Schwäche
interner Vorgaben ist geteilte Verantwortung. Die Prüfung lässt das nicht zu.
Ergänzend trennt `darf_a_sein` beratende von verantwortenden Rollen: Eine
Fachkraft für Arbeitssicherheit berät, sie verantwortet nicht.

**Abgeleitete Werte werden nicht gespeichert.** Der nächste Reviewtermin
ergibt sich aus `letzter_review` plus Zyklus. Die Pflichtenabdeckung ergibt
sich aus den Verweisen der Standards. Was berechnet werden kann, wird
berechnet — sonst driftet es auseinander.

**Der Rechtsstand ist der einzige menschliche Vorbehalt im Datenmodell.**
`rechtsstand_geprueft` ist bewusst ein eigenes Feld und nicht Teil des Status.
Ein Standard kann fachlich gelten und rechtlich unbestätigt sein — genau
dieser Zustand ist in der Praxis der Normalfall und soll sichtbar bleiben,
statt in einer Sammelangabe zu verschwinden.

**Zwei YAML-Leser.** PyYAML, wenn vorhanden, sonst `miniyaml.py` mit dem
Sprachumfang, den dieses Repository tatsächlich benutzt. Der Befehl
`selbsttest` vergleicht beide auf allen Dateien und schlägt bei Abweichung
fehl. Ohne diesen Vergleich wäre der zweite Leser ein Risiko statt einer
Absicherung.

## Bausteine

### Datenschicht `daten/`

| Datei | Inhalt | Zentrale Angabe |
|---|---|---|
| `organisation/rollen.yaml` | alle Rollen mit Ebene | `darf_a_sein` |
| `organisation/betriebsbereiche.yaml` | die sieben Bereiche | Kopfzahl, Bereitschaft |
| `organisation/schnittstellen.yaml` | Partnervereinbarungen | `wir_liefern`, `wir_erwarten`, `reifegrad` |
| `themenfelder.yaml` | Themenfelder | `owner`, `kritikalitaet` |
| `pflichtenregister.yaml` | Betreiberpflichten | `traeger`, `rechtsstand_geprueft` |

### Regelwerksschicht `standards/`

Ein Verzeichnis je Themenfeld, eine Datei je Standard. Der Kopf ist
maschinenlesbar und wird vollständig geprüft; der Text folgt acht festen
Abschnitten. Abschnitt 4 verweist auf die Aufgaben-IDs des Kopfes, damit
Beschreibung und Verantwortung nicht auseinanderlaufen.

### Werkzeugschicht `werkzeuge/`

- `miniyaml.py` — YAML-Rückfallleser, ohne Abhängigkeiten.
- `ps.py` — lädt alles in ein Objekt `Welt`, prüft, wertet aus, bietet die
  Befehle an. Die Prüfung liefert `Befund`-Objekte mit drei Schweregraden:
  *Fehler* blockiert, *Warnung* gehört in die Abteilungsrunde, *Hinweis* ist
  eine Vormerkung.
- `cockpit.py` — erzeugt aus derselben `Welt` eine einzelne HTML-Datei.

### Darstellungsschicht `cockpit/`

Eine Datei, in sich geschlossen: keine externen Schriftarten, keine
Bibliotheken, keine Bilder. Sie funktioniert offline, im Intranet, als
Mailanhang und im Ausdruck. Hell und dunkel sind über Farbtoken abgedeckt.

Aufbau in der Reihenfolge, in der eine Abteilungsrunde sie braucht: Lagebild,
Handlungsbedarf, Themenfelder, Standards, Wer-macht-was, Jahrestakt,
Schnittstellen, Betriebsbereiche, Pflichtenregister.

## Fehlerbehandlung

Drei Schweregrade statt einer Ja/Nein-Antwort, weil ein Regelwerk immer
unfertig ist. Ein fehlender Standard für ein Themenfeld ist kein Fehler,
sondern Arbeitsvorrat — er darf die Prüfung nicht blockieren, muss aber
sichtbar bleiben.

Die Prüfung sammelt alle Befunde und bricht nicht beim ersten ab. Auch ein
unlesbarer YAML-Kopf führt nur bei dieser einen Datei zum Abbruch. Schlägt
PyYAML an einem unmöglichen Wert wie `2026-13-01` fehl, übernimmt der eigene
Leser, der solche Werte als Text behält — so werden alle übrigen Fehler
derselben Datei trotzdem benannt.

## Prüfstrategie

- `ps.py pruefen` gegen das echte Regelwerk, Rückgabewert 1 bei Fehlern. Damit
  eignet es sich als Hook und als Prüfschritt in einer Pipeline.
- `ps.py selbsttest` vergleicht beide YAML-Leser auf allen Dateien.
- Ein absichtlich fehlerhafter Standard wurde gegen die Prüfung gehalten; alle
  gesetzten Fehler wurden einzeln erkannt.
- Das Cockpit wurde in hellem und dunklem Erscheinungsbild gerendert und auf
  waagerechten Überlauf geprüft.

## Bewusst nicht enthalten

- **Keine Anbindung an SAP, Schulungsverwaltung oder Fuhrparksystem.** Das
  Regelwerk benennt Nachweise und Ablageorte, führt sie aber nicht. Eine
  Anbindung wäre ein eigenes Vorhaben mit eigener Spec.
- **Keine Zuordnung Rolle zu Person.** Bewusst außerhalb.
- **Keine Fristenüberwachung einzelner Vorgänge.** Das System steuert
  Vorgaben, nicht Vorgänge. Ob Fahrzeug X geprüft ist, steht im
  Fuhrparksystem, nicht hier.
