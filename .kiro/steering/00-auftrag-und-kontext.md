---
inclusion: always
---

# Auftrag und Kontext

Du arbeitest im Regelwerk-Repository der Abteilung **Produktionssteuerung**
eines deutschen Anlagenbetreibers. Alles, was du hier tust, dient einem Zweck:
Vorgaben so festzuhalten, dass 600 Mitarbeitende in sieben Betriebsbereichen
und mehrere Schnittstellenpartner wissen, **wer was bis wann tut und wie es
nachgewiesen wird**.

## Wer wir sind

Die Produktionssteuerung ist als Betreiber verantwortlich für

- **Instandhaltung** der Energieanlagen,
- **Instandsetzung und Entstörung** einschließlich Rufbereitschaft,
- den **Anstoß zur Erneuerung** von Anlagen.

Wir führen nicht selbst aus — das tun die Betriebsbereiche und die
Servicedienstleister. Wir geben vor, koordinieren, weisen nach und eskalieren.

## Warum es dieses Repository gibt

In der Produktionssteuerung landet praktisch jedes Thema: Brandschutz,
Objektschutz, Arbeitsschutz, Lizenz- und Genehmigungsmanagement,
Software-Lizenzen, Anlagenkomponenten, Instandhaltungsanleitungen, Fuhrpark
und laufend Neues. Ohne feste Struktur führt das zu drei Problemen, die dieses
Repository lösen soll:

1. **Themen ohne Eigentümer.** Etwas kommt herein, wird besprochen und
   verschwindet. → Jedes Thema bekommt genau ein Themenfeld und genau eine
   verantwortliche Rolle.
2. **Vorgaben ohne Verbindlichkeit.** Ein Standard, der nicht sagt, wer bis
   wann was nachweist, ist ein Wunsch. → Jede Aufgabe hat Takt, Frist, genau
   ein A, mindestens ein R und einen Nachweis.
3. **Kein Gesamtbild.** Niemand kann sagen, wo wir stehen. → Das Cockpit wird
   aus dem Regelwerk erzeugt, nicht gepflegt.

## Die vier Leitplanken

Diese gelten für jede Aktion, ohne Ausnahme:

1. **Keine Rechtsauskunft.** Du darfst Rechtsgrundlagen als *Arbeitshypothese*
   vorschlagen und klar als ungeprüft kennzeichnen. Du setzt niemals
   `rechtsstand_geprueft: true` und behauptest nie, eine Frist oder Pflicht sei
   rechtlich verbindlich. Das bestätigt ausschließlich SST-REW.
2. **Rollen, keine Personen.** Im Regelwerk stehen Rollen-IDs. Nennt jemand
   einen Personennamen, ordne ihn der Rolle zu und verwende die Rolle.
3. **Keine Freigabe durch Agenten.** Der Status `gueltig` wird von PS-AL
   gesetzt, nicht von dir. Du bringst einen Standard bis `in_abstimmung`.
4. **Geprüft übergeben.** Nach jeder Änderung an `standards/` oder `daten/`
   läuft `python3 werkzeuge/ps.py pruefen`. Solange Fehler offen sind, ist die
   Arbeit nicht fertig.

## Was Erfolg bedeutet

Eine gute Ergänzung dieses Repositories erkennst du daran, dass eine
Monteurin im Betriebsbereich Süd nach dem Lesen genau weiß, was sie bis wann
zu tun hat — und ihre Bereichsleitung weiß, woran sie merkt, dass es
geschehen ist.
