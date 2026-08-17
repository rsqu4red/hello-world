---
inclusion: fileMatch
fileMatchPattern: 'standards/**/*.md'
---

# Format eines Standards

Diese Anweisung gilt, sobald du eine Datei unter `standards/` bearbeitest.
Verbindliche Vorlage: #[[file:standards/_vorlagen/standard-vorlage.md]]

## Kopfdaten

Alle Pflichtfelder aus der Vorlage müssen gefüllt sein. `ps.py pruefen`
erzwingt das, aber richte dich nicht nach dem Prüfer, sondern nach dem Zweck.

| Feld | Regel |
|---|---|
| `id` | `STD-<Kürzel>-<lfd. Nr.>`, Kürzel identisch zum Themenfeld. Nie ändern. Vergabe nur über `ps.py neu`. |
| `version` | Semantisch. Major, wenn sich Pflichten für die Betriebsbereiche ändern. Minor bei neuer Aufgabe oder Kennzahl. Patch bei Textkorrektur. |
| `status` | `entwurf` → `in_abstimmung` → `gueltig`. Den letzten Schritt macht PS-AL. |
| `letzter_review` | Datum der letzten inhaltlichen Durchsicht, nicht der letzten Textänderung. |
| `review_zyklus_monate` | 12 bei hoher Kritikalität, sonst 24. |
| `owner` | Rolle, die den Standard fachlich trägt. Muss `darf_a_sein: true` haben. |
| `rechtsstand_geprueft` | Bleibt `false`, bis SST-REW schriftlich bestätigt hat. Kein Agent ändert das. |
| `pflichten` | Alle `PFL-*`, die dieser Standard operativ umsetzt. Leer nur, wenn es wirklich keine gibt. |

## Aufgaben — die eigentliche Substanz

Eine Aufgabe ist die kleinste Einheit, die jemand tun, terminieren und
nachweisen kann. Sie ist keine Absichtserklärung.

```yaml
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
```

**Regeln, die der Prüfer erzwingt:**
- Genau **ein A**. Eine Aufgabe mit zwei Verantwortlichen hat keinen.
- Mindestens **ein R**. A und R dürfen dieselbe Rolle sein, wenn sie es
  tatsächlich selbst tut.
- `takt` aus der festen Liste. Freitext wird abgewiesen.
- `frist`, `nachweis` und `system` sind Pflicht.
- Alle genannten Rollen existieren in `daten/organisation/rollen.yaml`.
- Rollen mit `darf_a_sein: false` (BB-MA, FKT-SIFA, FKT-BSB, SST-SDL, …)
  dürfen nicht A sein. Beratende Funktionen gehören nach C.

**Regeln, die der Prüfer nicht erzwingen kann — dafür bist du zuständig:**
- Die Frist muss zum Takt passen. „quartalsweise" mit „bis 31.03." ist ein
  Widerspruch.
- Der Nachweis muss *existieren können*. „Dokumentierte Sensibilisierung" ist
  keiner, „unterschriebene Teilnehmerliste" schon.
- Das `system` muss ein System sein, das es im Haus gibt.
- Formuliere `was` aktiv und mit einem Verb am Anfang: „Prüfplakette vor
  Ablauf erneuern lassen", nicht „Erneuerung der Prüfplakette".

## Fließtext

Acht Abschnitte, feste Reihenfolge, keine zusätzlichen Kapitel:

1. **Zweck** — warum es den Standard gibt, vier Sätze.
2. **Geltungsbereich** — für wen, wo, und ausdrücklich wofür *nicht*.
3. **Begriffe** — nur, was im Haus uneinheitlich verwendet wird.
4. **Ablauf** — in zeitlicher Reihenfolge, jeder Schritt verweist auf eine
   Aufgaben-ID (A1, A2 …). So laufen Text und Verantwortung nicht auseinander.
5. **Nachweise** — was wie lange aufbewahrt wird und wer es vorlegt.
6. **Schnittstellen** — Verweis auf `schnittstellen.yaml`, keine Wiederholung.
7. **Abweichungen** — wer eine begründete Abweichung genehmigt. Ein Standard
   ohne Abweichungsweg wird umgangen statt geändert.
8. **Änderungshistorie** — jede Version eine Zeile.

## Sprache

Deutsch, sachlich, kurze Hauptsätze. Aktiv statt Passiv. Die betroffene Rolle
wird benannt, nicht „man". Keine Werbesprache, keine Verstärker
(„selbstverständlich", „unbedingt"). Umlaute und ß korrekt ausschreiben.

Schreib so, dass der Satz auch in einer Betriebsversammlung vorgelesen werden
kann, ohne dass jemand nachfragt, was gemeint ist.
