# Aufgaben — Aufbau und Einführung

Abgehakte Punkte sind im Repository umgesetzt. Die offenen Punkte sind die
Einführungsarbeit, die nur die Abteilung selbst leisten kann — dort stecken
die Entscheidungen, die kein Agent treffen darf.

## 1. Grundgerüst

- [x] 1.1 Stammdaten anlegen: Rollen, Betriebsbereiche, Themenfelder,
      Schnittstellen, Pflichtenregister
      _Anforderungen: 1, 3_
- [x] 1.2 Rollenmodell mit `darf_a_sein` zur Trennung von Beratung und
      Verantwortung
      _Anforderungen: 1.3_
- [x] 1.3 Standardvorlage mit vollständigem Kopfdatensatz und acht
      Textabschnitten
      _Anforderungen: 1, 2_

## 2. Werkzeuge

- [x] 2.1 YAML-Rückfallleser ohne Abhängigkeiten (`miniyaml.py`)
      _Anforderungen: 8.1, 8.2_
- [x] 2.2 Selbsttest, der beide Leser auf allen Dateien vergleicht
      _Anforderungen: 8.3_
- [x] 2.3 Prüfung mit drei Schweregraden und Rückgabewert 1 bei Fehlern
      _Anforderungen: 1.1–1.4, 2.1–2.5, 3.1–3.5, 7.2, 7.3_
- [x] 2.4 Auswertungen: `status`, `luecken`, `faellig`, `rollenblatt`
      _Anforderungen: 3.3, 5.2, 7.4_
- [x] 2.5 `neu` mit automatischer ID-Vergabe
      _Anforderungen: 1_
- [x] 2.6 Robuste Fehlerbehandlung: alle Befunde einer Datei statt Abbruch
      beim ersten
      _Anforderungen: 8.4_

## 3. Cockpit

- [x] 3.1 Erzeugte HTML-Seite ohne externe Abhängigkeiten
      _Anforderungen: 6.1, 6.2_
- [x] 3.2 Lagebild, Handlungsbedarf, Themenfelder, Standards, Rollen,
      Jahrestakt, Schnittstellen, Bereiche, Pflichten
      _Anforderungen: 3.3, 3.4, 5.2, 6.1_
- [x] 3.3 Helles und dunkles Erscheinungsbild, druckbar
      _Anforderungen: 6.4_

## 4. Agentensystem

- [x] 4.1 Steering: Auftrag, Arbeitsweise, Agententeam, Standardformat,
      Stammdaten
      _Anforderungen: 4.4_
- [x] 4.2 Acht Agentenrollen mit Auftrag, Grenzen und Übergabepunkten
      _Anforderungen: 4_
- [x] 4.3 Hooks für Standardänderung, Stammdatenänderung, Triage, Anlegen,
      Review, Rollout, Lücken, Schnittstellen, Lagebericht
      _Anforderungen: 6.3, 7.1_
- [x] 4.4 Rolloutvorlagen für die vier Zielgruppenfassungen
      _Anforderungen: 5.1, 5.3, 5.4_

## 5. Beispielinhalte

- [x] 5.1 Sechs Standards über verschiedene Themenfelder als Muster
- [x] 5.2 Bewusst unterschiedliche Zustände: überfälliger Review, Standard in
      Abstimmung, Standard im Entwurf, ungedeckte Pflichten

---

## 6. Einführung in der Abteilung — offen

- [ ] 6.1 Platzhalter durch echte Angaben ersetzen: Bezeichnungen und Sitze
      der sieben Betriebsbereiche, tatsächliche Kopfzahlen, reale
      Systemnamen in den Feldern `system`
- [ ] 6.2 Rollenmodell mit der Abteilungsleitung abgleichen: Fehlt eine Rolle?
      Ist `darf_a_sein` überall richtig gesetzt? Sind die bestellten
      Funktionen vollständig?
- [ ] 6.3 Themenfelder bestätigen und Verantwortung je Feld namentlich
      hinterlegen — im Organigramm, nicht im Repository
- [ ] 6.4 Pflichtenregister mit SST-REW durchgehen und `rechtsstand_geprueft`
      setzen. Erst danach ist die Abdeckungsquote belastbar
      _Anforderungen: 4.1_
- [ ] 6.5 Bestehende Vorgaben der Abteilung in das Format überführen — pro
      Woche ein Themenfeld, beginnend bei Kritikalität hoch
- [ ] 6.6 Die zehn Themenfelder ohne Standard priorisieren
      (Hook „Lückenanalyse") und in eine Jahresplanung überführen
- [ ] 6.7 Schnittstellenvereinbarungen in den Jourfixes bestätigen lassen;
      Reifegrad von `entwurf` auf `abgestimmt` oder `vereinbart` heben
- [ ] 6.8 Ablageort für das Cockpit festlegen (Intranet, Laufwerk) und
      festlegen, wer es in welchem Rhythmus neu baut
- [ ] 6.9 Rolloutfassungen für die vier gültigen Standards erzeugen und in
      einer Meisterei gegenlesen lassen, bevor sie in alle Bereiche gehen
- [ ] 6.10 Review-Radar terminieren: fester Monatstermin, an dem der Hook
      läuft und die Ergebnisse in die Abteilungsrunde gehen
