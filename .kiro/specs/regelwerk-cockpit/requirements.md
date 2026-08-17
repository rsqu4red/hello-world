# Anforderungen — Regelwerk und Cockpit der Produktionssteuerung

## Einleitung

Die Produktionssteuerung verantwortet als Anlagenbetreiber die Instandhaltung,
die Instandsetzung und Entstörung sowie den Anstoß zur Erneuerung von
Energieanlagen. In der Abteilung landen Themen aus sehr unterschiedlichen
Feldern — von Brandschutz über Lizenzmanagement bis Fuhrpark — und alle
müssen in sieben Betriebsbereichen mit insgesamt 600 Mitarbeitenden
gleichförmig umgesetzt werden.

Dieses System hält die Vorgaben der Abteilung an einer Stelle, macht
Verantwortung und Fristen eindeutig, zeigt Lücken auf und liefert die
Fassungen, die in der Einheit und bei den Schnittstellenpartnern ankommen.

Die Abnahmekriterien sind in der Form *WENN … DANN SOLL …* formuliert, damit
jedes einzeln prüfbar ist.

---

## Anforderung 1 — Eindeutige Verantwortung je Aufgabe

**Anwenderziel:** Als Abteilungsleitung will ich, dass zu jeder Vorgabe genau
eine Rolle das Ergebnis verantwortet, damit bei Rückfragen und im
Prüfungsfall niemand auf jemand anderen zeigen kann.

**Abnahmekriterien**

1. WENN eine Aufgabe keine oder mehr als eine verantwortliche Rolle (A) hat,
   DANN SOLL die Prüfung einen Fehler melden und mit Rückgabewert 1 enden.
2. WENN eine Aufgabe keine ausführende Rolle (R) hat, DANN SOLL die Prüfung
   einen Fehler melden.
3. WENN eine Rolle mit `darf_a_sein: false` als A eingetragen ist, DANN SOLL
   die Prüfung einen Fehler melden.
4. WENN eine Aufgabe eine Rolle nennt, die nicht in `rollen.yaml` steht,
   DANN SOLL die Prüfung einen Fehler mit Angabe der Rolle melden.
5. WENN ein Standard einen Personennamen statt einer Rolle enthält, DANN SOLL
   dies in der Abstimmung beanstandet werden.

---

## Anforderung 2 — Jede Vorgabe ist terminiert und nachweisbar

**Anwenderziel:** Als Betriebsbereichsleitung will ich zu jeder Vorgabe wissen,
bis wann sie zu erfüllen ist und woran der Vollzug erkennbar ist, damit ich
sie steuern kann statt sie zu erinnern.

**Abnahmekriterien**

1. WENN eine Aufgabe keinen Takt aus der festen Liste hat, DANN SOLL die
   Prüfung einen Fehler melden.
2. WENN eine Aufgabe keine Frist oder keinen Nachweis hat, DANN SOLL die
   Prüfung einen Fehler melden.
3. WENN eine Aufgabe keinen Ablageort (`system`) nennt, DANN SOLL die Prüfung
   eine Warnung melden.
4. WENN ein gültiger Standard keine Kennzahl enthält, DANN SOLL die Prüfung
   eine Warnung melden, weil seine Wirkung sonst nicht messbar ist.
5. WENN ein gültiger Standard keinen Eskalationsweg enthält, DANN SOLL die
   Prüfung eine Warnung melden.

---

## Anforderung 3 — Betreiberpflichten sind nachvollziehbar gedeckt

**Anwenderziel:** Als Abteilungsleitung will ich jederzeit sagen können,
welche Betreiberpflicht durch welchen Standard umgesetzt wird, damit ich
gegenüber Geschäftsführung und Prüfern auskunftsfähig bin.

**Abnahmekriterien**

1. WENN eine Pflicht im Register von keinem Standard referenziert wird,
   DANN SOLL die Prüfung eine Warnung melden und das Cockpit sie als
   ungedeckt ausweisen.
2. WENN ein Standard eine Pflicht referenziert, die es nicht gibt, DANN SOLL
   die Prüfung einen Fehler melden.
3. Das Cockpit SOLL die Abdeckungsquote als Kennzahl ausweisen.
4. WENN eine Pflicht den Rechtsstand nicht bestätigt hat, DANN SOLL das
   Cockpit dies getrennt von der Abdeckung ausweisen.
5. WENN ein Standard den Status `gueltig` hat und `rechtsstand_geprueft` auf
   `false` steht, DANN SOLL die Prüfung eine Warnung melden.

---

## Anforderung 4 — Kein Agent erteilt Rechtsauskunft

**Anwenderziel:** Als Abteilungsleitung will ich, dass die Automatisierung
niemals behauptet, etwas sei rechtlich verbindlich, damit wir uns nicht auf
eine Aussage stützen, die niemand verantwortet.

**Abnahmekriterien**

1. Das Feld `rechtsstand_geprueft` SOLL ausschließlich durch einen Menschen
   nach Bestätigung durch SST-REW auf `true` gesetzt werden.
2. WENN ein Agent eine Rechtsgrundlage vorschlägt, DANN SOLL sie als
   ungeprüfte Arbeitshypothese gekennzeichnet sein.
3. Der Status `gueltig` SOLL ausschließlich durch PS-AL gesetzt werden.
4. Die Steering-Dokumente SOLLEN diese Grenzen an jeder Stelle wiederholen,
   an der ein Agent in Versuchung geraten könnte.

---

## Anforderung 5 — Vorgaben erreichen ihre Zielgruppe

**Anwenderziel:** Als Monteur will ich auf einer Seite sehen, was ich zu tun
habe, ohne einen achtseitigen Standard zu lesen.

**Abnahmekriterien**

1. WENN ein Standard gültig ist, DANN SOLL sich je operativer Zielrolle ein
   Einseiter erzeugen lassen, der nur deren Aufgaben enthält.
2. Das Werkzeug SOLL ein Rollenblatt über alle Standards hinweg erzeugen, das
   alle Aufgaben einer Rolle mit Beteiligungsart, Takt und Frist zeigt.
3. WENN ein Standard noch nicht gültig ist, DANN SOLL eine erzeugte Fassung
   deutlich als Entwurf gekennzeichnet sein.
4. Jede Aussage in einer Rolloutfassung SOLL auf eine Aufgaben-ID des
   Standards zurückführbar sein.

---

## Anforderung 6 — Das Gesamtbild ist erzeugt, nicht gepflegt

**Anwenderziel:** Als Abteilungsleitung will ich eine Übersicht, die nie
veraltet, weil niemand daran denken musste, sie zu aktualisieren.

**Abnahmekriterien**

1. Das Cockpit SOLL vollständig aus `daten/` und `standards/` erzeugt werden.
2. Das Cockpit SOLL ohne Netzzugang, ohne externe Schriftarten und ohne
   Javascript-Bibliotheken funktionieren, damit es per Mail und im Intranet
   nutzbar ist.
3. WENN ein Standard geändert wird, DANN SOLL das Cockpit über einen Hook neu
   gebaut werden.
4. Das Cockpit SOLL in hellem und dunklem Erscheinungsbild lesbar sein und
   sich ausdrucken lassen.

---

## Anforderung 7 — Reviews werden nicht vergessen

**Anwenderziel:** Als Themenfeldverantwortliche will ich rechtzeitig erfahren,
dass ein Standard zur Durchsicht ansteht.

**Abnahmekriterien**

1. Der nächste Reviewtermin SOLL aus `letzter_review` und
   `review_zyklus_monate` berechnet und nicht separat gepflegt werden.
2. WENN der Termin überschritten ist, DANN SOLL die Prüfung eine Warnung mit
   Angabe der Überschreitung in Tagen melden.
3. WENN der Termin in weniger als 90 Tagen liegt, DANN SOLL ein Hinweis
   erscheinen.
4. Das Werkzeug SOLL eine nach Fälligkeit sortierte Liste ausgeben können.

---

## Anforderung 8 — Das System läuft auf einem verwalteten Firmenrechner

**Anwenderziel:** Als Abteilung wollen wir das System ohne
Softwareinstallation nutzen können, weil auf unseren Rechnern keine Pakete
nachinstalliert werden dürfen.

**Abnahmekriterien**

1. Alle Werkzeuge SOLLEN allein mit der Standardbibliothek von Python 3
   lauffähig sein.
2. WENN PyYAML nicht verfügbar ist, DANN SOLL der mitgelieferte YAML-Leser
   verwendet werden.
3. Der Selbsttest SOLL nachweisen, dass beide Leser auf allen Dateien dieses
   Repositories dasselbe Ergebnis liefern.
4. WENN eine Datei einen unmöglichen Wert enthält, DANN SOLL die Prüfung
   alle Einzelfehler benennen und nicht nach dem ersten abbrechen.
