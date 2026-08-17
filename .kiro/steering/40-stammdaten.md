---
inclusion: fileMatch
fileMatchPattern: 'daten/**/*.yaml'
---

# Stammdaten ändern

Die Dateien unter `daten/` sind die Grundlage für jeden Standard und für das
Cockpit. Eine unbedachte Änderung hier wirkt sich auf das gesamte Regelwerk
aus — deshalb gelten strengere Regeln als bei Standards.

## Vor jeder Änderung

Prüfe, wer auf die betroffene ID zeigt:

```
grep -rn "PS-BBK" standards/ daten/
```

Eine ID, auf die verwiesen wird, wird **nicht umbenannt und nicht gelöscht**.
Sie wird höchstens ergänzt oder als nicht mehr besetzt gekennzeichnet.

## rollen.yaml

- `id` folgt dem Präfix der Ebene: `PS-` (Abteilung), `BB-` (Betriebsbereich),
  `FKT-` (bestellte Funktion), `SST-` (Schnittstelle).
- `darf_a_sein` ist die wichtigste Angabe der Datei. Sie entscheidet, ob eine
  Rolle Ergebnisverantwortung tragen darf. Setze sie auf `false` für
  ausführende Ebenen (BB-MA) und für beratende Funktionen (FKT-SIFA,
  FKT-BSB, FKT-SIBE, FKT-DSB, SST-REW, SST-SDL). Beratung und Verantwortung
  gehören getrennt — das ist der Kern des Modells.
- `anzahl` ist die Zahl der Stellen, nicht der Personen. Sie speist die
  Plausibilitätsprüfung des RACI-Wächters.
- Eine neue Rolle braucht immer eine `beschreibung`, wenn ihr Zuschnitt nicht
  aus dem Namen hervorgeht.

## themenfelder.yaml

- Jedes Themenfeld hat eine `owner`-Rolle mit `darf_a_sein: true`. Ein
  Themenfeld ohne Verantwortung darf nicht angelegt werden — genau das ist
  der Zustand, den dieses Repository beseitigen soll.
- `fachfunktion` ist die beratende Funktion, nicht die Verantwortung.
- `kritikalitaet: hoch` bedeutet: fehlt hier ein Standard, ist das eine
  Warnung im Cockpit, kein Hinweis. Vergib es für Personenrisiko,
  Versorgungsrisiko oder unmittelbare Betreiberpflichten.
- Das Kürzel im Feld (`TF-BRA` → `BRA`) wird zum Kürzel der Standard-IDs.
  Wähle es dreistellig und sprechend, es begleitet uns dauerhaft.

## pflichtenregister.yaml

- `quelle` ist eine Arbeitsangabe, keine Rechtsauskunft.
- `rechtsstand_geprueft` bleibt `false`, bis SST-REW bestätigt hat.
  **Kein Agent setzt dieses Feld.** Es ist der einzige Punkt, an dem das
  Repository behauptet, etwas rechtlich zu wissen — deshalb ist er
  ausschließlich menschlich besetzt.
- `traeger` ist die Rolle, die die Pflicht im Alltag trägt.
  `delegation_von` ist die Rolle, von der sie übertragen wurde. Beides
  zusammen ergibt die Delegationskette, die im Prüfungsfall zählt.
- Eine neue Pflicht wird angelegt, sobald sie erkannt ist — nicht erst, wenn
  der Standard dazu fertig ist. Die Lücke soll sichtbar sein.

## betriebsbereiche.yaml und schnittstellen.yaml

- Die sieben Betriebsbereiche sind gesetzt. Ändert sich der Zuschnitt, ist das
  ein eigenes Vorhaben mit Spec, keine Nebenbei-Änderung.
- In `schnittstellen.yaml` beschreibt `wir_liefern` unsere Zusagen und
  `wir_erwarten` die des Partners. Formuliere beides mit Frist oder Turnus —
  eine Erwartung ohne Termin ist nicht einforderbar.
- `reifegrad: entwurf` heißt: noch nicht mit dem Partner abgestimmt. Kein
  Standard darf sich auf eine solche Zulieferung als gesichert stützen. Das
  Cockpit weist darauf hin.

## Nach jeder Änderung

```
python3 werkzeuge/ps.py pruefen
python3 werkzeuge/ps.py cockpit
```

Wurde eine Rolle, ein Themenfeld oder eine Pflicht ergänzt, prüfe zusätzlich
mit `ps.py luecken`, ob dadurch eine neue Lücke sichtbar geworden ist. Das ist
kein Fehler, sondern der Zweck der Übung.
