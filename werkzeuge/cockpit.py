"""Baut aus dem Regelwerk eine einzelne, in sich geschlossene HTML-Seite.

Die Seite ist bewusst ohne externe Abhaengigkeiten: keine Schriftarten aus
dem Netz, kein Javascript-Framework, keine Bilder. Sie laesst sich per
E-Mail verschicken, ins Intranet legen oder ausdrucken.

Aufruf ueber: python3 werkzeuge/ps.py cockpit
"""

from __future__ import annotations

import datetime as dt
from html import escape

import ps

TAKT_ANZEIGE = ps.TAKT_ANZEIGE
STATUS_ANZEIGE = {
    "entwurf": ("Entwurf", "neutral"),
    "in_abstimmung": ("in Abstimmung", "warn"),
    "gueltig": ("gültig", "ok"),
    "ausgesetzt": ("ausgesetzt", "krit"),
    "archiviert": ("archiviert", "neutral"),
}
EBENEN_ANZEIGE = {
    "ps": "Produktionssteuerung",
    "betrieb": "Betriebsbereiche",
    "funktion": "Bestellte Funktionen",
    "schnittstelle": "Schnittstellen",
}

CSS = """
:root {
  --ground: #f5f7f8;
  --surface: #ffffff;
  --surface-still: #eef1f3;
  --ink: #14191d;
  --ink-leise: #5a6672;
  --ink-still: #7e8994;
  --linie: #dde2e6;
  --linie-stark: #c3ccd3;
  --akzent: #1d5a72;
  --akzent-leise: #e4eef2;
  --ok: #2c7350;
  --ok-feld: #e3f0e9;
  --warn: #8f6511;
  --warn-feld: #f7eed9;
  --krit: #a83730;
  --krit-feld: #f8e6e4;
  --schrift-titel: Georgia, "Iowan Old Style", "Times New Roman", serif;
  --schrift-text: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
  --schrift-daten: ui-monospace, "SF Mono", "Cascadia Mono", "Roboto Mono", Menlo, Consolas, monospace;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground: #10151a;
    --surface: #172026;
    --surface-still: #1e2930;
    --ink: #e7ecef;
    --ink-leise: #a2aeb8;
    --ink-still: #7d8993;
    --linie: #2a363e;
    --linie-stark: #3c4a54;
    --akzent: #82b8ce;
    --akzent-leise: #1c2e38;
    --ok: #6fbd92;
    --ok-feld: #162c22;
    --warn: #d8ab54;
    --warn-feld: #2e2718;
    --krit: #e08a83;
    --krit-feld: #33201e;
  }
}

:root[data-theme="dark"] {
  --ground: #10151a;
  --surface: #172026;
  --surface-still: #1e2930;
  --ink: #e7ecef;
  --ink-leise: #a2aeb8;
  --ink-still: #7d8993;
  --linie: #2a363e;
  --linie-stark: #3c4a54;
  --akzent: #82b8ce;
  --akzent-leise: #1c2e38;
  --ok: #6fbd92;
  --ok-feld: #162c22;
  --warn: #d8ab54;
  --warn-feld: #2e2718;
  --krit: #e08a83;
  --krit-feld: #33201e;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--ground);
  color: var(--ink);
  font-family: var(--schrift-text);
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

.huelle {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 24px 96px;
  display: flex;
  flex-direction: column;
  gap: 44px;
}

/* --- Kopf --- */
.kopf {
  padding: 48px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-bottom: 2px solid var(--linie-stark);
  padding-bottom: 26px;
}
.kopf .marke {
  font-family: var(--schrift-daten);
  font-size: 11px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--akzent);
}
.kopf h1 {
  font-family: var(--schrift-titel);
  font-size: clamp(30px, 4.4vw, 46px);
  line-height: 1.1;
  font-weight: 600;
  margin: 0;
  text-wrap: balance;
  letter-spacing: -0.015em;
}
.kopf p {
  margin: 0;
  color: var(--ink-leise);
  max-width: 62ch;
}
.stand {
  font-family: var(--schrift-daten);
  font-size: 12px;
  color: var(--ink-still);
}

/* --- Navigation --- */
.sprungmarken {
  position: sticky;
  top: 0;
  z-index: 10;
  background: color-mix(in srgb, var(--ground) 92%, transparent);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--linie);
  margin: 0 -24px;
  padding: 10px 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 18px;
  font-size: 13px;
}
.sprungmarken a {
  color: var(--ink-leise);
  text-decoration: none;
  padding: 2px 0;
  border-bottom: 2px solid transparent;
}
.sprungmarken a:hover { color: var(--akzent); border-bottom-color: var(--akzent); }
.sprungmarken a:focus-visible { outline: 2px solid var(--akzent); outline-offset: 3px; }

/* --- Abschnitte --- */
section { display: flex; flex-direction: column; gap: 18px; scroll-margin-top: 64px; }
section > header { display: flex; flex-direction: column; gap: 4px; }
section h2 {
  font-family: var(--schrift-titel);
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.01em;
}
section header p { margin: 0; color: var(--ink-leise); max-width: 72ch; font-size: 14px; }

/* --- Kennzahlen --- */
.kennzahlen {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(168px, 1fr));
  gap: 12px;
}
.kachel {
  background: var(--surface);
  border: 1px solid var(--linie);
  border-left: 3px solid var(--linie-stark);
  border-radius: 3px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.kachel.ok { border-left-color: var(--ok); }
.kachel.warn { border-left-color: var(--warn); }
.kachel.krit { border-left-color: var(--krit); }
.kachel .wert {
  font-family: var(--schrift-daten);
  font-size: 30px;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
}
.kachel.ok .wert { color: var(--ok); }
.kachel.warn .wert { color: var(--warn); }
.kachel.krit .wert { color: var(--krit); }
.kachel .titel {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--ink-leise);
}
.kachel .fuss { font-size: 12px; color: var(--ink-still); }

/* --- Tabellen --- */
.tabellenrahmen {
  overflow-x: auto;
  background: var(--surface);
  border: 1px solid var(--linie);
  border-radius: 3px;
}
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
thead th {
  text-align: left;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--ink-leise);
  font-weight: 600;
  padding: 10px 14px;
  border-bottom: 1px solid var(--linie-stark);
  white-space: nowrap;
  background: var(--surface-still);
}
tbody td { padding: 9px 14px; border-bottom: 1px solid var(--linie); vertical-align: top; }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover { background: var(--surface-still); }
td.zahl, th.zahl { text-align: right; font-family: var(--schrift-daten); font-variant-numeric: tabular-nums; }
td.kennung { font-family: var(--schrift-daten); font-size: 12.5px; white-space: nowrap; }
td.knapp { white-space: nowrap; }

/* --- Marken --- */
.marker {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
  padding: 2px 7px;
  border-radius: 2px;
  white-space: nowrap;
  background: var(--surface-still);
  color: var(--ink-leise);
  border: 1px solid var(--linie-stark);
}
.marker.ok { background: var(--ok-feld); color: var(--ok); border-color: transparent; }
.marker.warn { background: var(--warn-feld); color: var(--warn); border-color: transparent; }
.marker.krit { background: var(--krit-feld); color: var(--krit); border-color: transparent; }
.marker.akzent { background: var(--akzent-leise); color: var(--akzent); border-color: transparent; }
.raci {
  font-family: var(--schrift-daten);
  font-size: 11px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 2px;
  background: var(--akzent-leise);
  color: var(--akzent);
}

/* --- Handlungsbedarf --- */
.befunde { display: flex; flex-direction: column; gap: 8px; }
.befund {
  display: grid;
  grid-template-columns: 116px 148px 1fr;
  gap: 14px;
  align-items: baseline;
  background: var(--surface);
  border: 1px solid var(--linie);
  border-left: 3px solid var(--linie-stark);
  border-radius: 3px;
  padding: 10px 14px;
  font-size: 13.5px;
}
.befund.warn { border-left-color: var(--warn); }
.befund.krit { border-left-color: var(--krit); }
.befund .ort { font-family: var(--schrift-daten); font-size: 12.5px; color: var(--ink-leise); }
@media (max-width: 700px) {
  .befund { grid-template-columns: 1fr; gap: 3px; }
}

/* --- Aufklappbares --- */
details {
  background: var(--surface);
  border: 1px solid var(--linie);
  border-radius: 3px;
}
details + details { margin-top: 8px; }
summary {
  cursor: pointer;
  padding: 11px 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: baseline;
  list-style: none;
  font-size: 14px;
}
summary::-webkit-details-marker { display: none; }
summary::before {
  content: "▸";
  color: var(--ink-still);
  font-size: 11px;
  transition: transform 0.12s ease;
}
details[open] > summary::before { transform: rotate(90deg); }
details[open] > summary { border-bottom: 1px solid var(--linie); }
summary:hover { background: var(--surface-still); }
summary:focus-visible { outline: 2px solid var(--akzent); outline-offset: -2px; }
summary .name { font-weight: 600; }
summary .kennung { font-family: var(--schrift-daten); font-size: 12px; color: var(--ink-leise); }
summary .rechts { margin-left: auto; display: flex; gap: 8px; align-items: baseline; }
.inhalt { padding: 0; }
.inhalt > .tabellenrahmen { border: none; border-radius: 0; }

/* --- Schnittstellenkarten --- */
.karten { display: grid; grid-template-columns: repeat(auto-fit, minmax(330px, 1fr)); gap: 12px; }
.karte {
  background: var(--surface);
  border: 1px solid var(--linie);
  border-radius: 3px;
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.karte h3 {
  margin: 0;
  font-family: var(--schrift-titel);
  font-size: 17px;
  font-weight: 600;
}
.karte .thema { font-size: 13px; color: var(--ink-leise); margin: 0; }
.karte h4 {
  margin: 0 0 4px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--ink-still);
  font-weight: 600;
}
.karte ul { margin: 0; padding-left: 17px; font-size: 13px; display: flex; flex-direction: column; gap: 3px; }
.karte li::marker { color: var(--ink-still); }
.karte .fuss {
  font-size: 12px;
  color: var(--ink-still);
  border-top: 1px solid var(--linie);
  padding-top: 9px;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 14px;
}

/* --- Taktband --- */
.taktband { display: flex; flex-direction: column; gap: 6px; }
.taktzeile { display: grid; grid-template-columns: 132px 1fr 44px; gap: 12px; align-items: center; font-size: 13px; }
.taktzeile .balken { background: var(--surface-still); border-radius: 2px; height: 20px; overflow: hidden; }
.taktzeile .balken span { display: block; height: 100%; background: var(--akzent); opacity: 0.72; }
.taktzeile .anzahl { font-family: var(--schrift-daten); font-variant-numeric: tabular-nums; text-align: right; color: var(--ink-leise); }

/* --- Fuss --- */
.fussnote {
  border-top: 1px solid var(--linie);
  padding-top: 20px;
  font-size: 12.5px;
  color: var(--ink-still);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.fussnote code {
  font-family: var(--schrift-daten);
  background: var(--surface-still);
  padding: 1px 5px;
  border-radius: 2px;
}
a { color: var(--akzent); }

@media print {
  .sprungmarken { display: none; }
  details { break-inside: avoid; }
  details:not([open]) > summary::before { content: ""; }
}
"""


def bauen(welt: ps.Welt, befunde: list) -> str:
    lage = ps.kennzahlen_der_lage(welt)
    teile = [
        _kopf(welt, lage),
        _navigation(),
        _lagebild(welt, lage),
        _handlungsbedarf(welt, befunde),
        _themenfelder(welt),
        _standards(welt),
        _rollen(welt),
        _taktuebersicht(welt),
        _schnittstellen(welt),
        _betriebsbereiche(welt),
        _pflichten(welt),
        _fuss(welt),
    ]
    return (
        f"<title>Cockpit Produktionssteuerung</title>\n"
        f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<style>{CSS}</style>\n"
        f"<div class=\"huelle\">\n" + "\n".join(teile) + "\n</div>\n"
    )


# --- Bausteine ------------------------------------------------------------


def _kopf(welt: ps.Welt, lage: dict) -> str:
    return f"""
<header class="kopf">
  <div class="marke">Produktionssteuerung · Anlagenbetrieb</div>
  <h1>Cockpit Produktionssteuerung</h1>
  <p>Alle Vorgaben der Abteilung an einer Stelle: welcher Standard gilt, wer
     verantwortet ihn, was ist bis wann zu tun und wo klafft eine Lücke.
     Diese Seite wird aus dem Regelwerk erzeugt und nicht von Hand gepflegt.</p>
  <div class="stand">Stand {welt.heute.strftime('%d.%m.%Y')} · {lage['standards']} Standards ·
     {lage['aufgaben']} Aufgaben · {len(welt.betriebsbereiche)} Betriebsbereiche ·
     {lage['mitarbeitende']} Mitarbeitende</div>
</header>
"""


def _navigation() -> str:
    punkte = [
        ("lagebild", "Lagebild"), ("handlungsbedarf", "Handlungsbedarf"),
        ("themenfelder", "Themenfelder"), ("standards", "Standards"),
        ("rollen", "Wer macht was"), ("takt", "Jahrestakt"),
        ("schnittstellen", "Schnittstellen"), ("bereiche", "Betriebsbereiche"),
        ("pflichten", "Pflichtenregister"),
    ]
    marken = "".join(f'<a href="#{ziel}">{text}</a>' for ziel, text in punkte)
    return f'<nav class="sprungmarken">{marken}</nav>'


def _kachel(wert, titel: str, fuss: str = "", stufe: str = "") -> str:
    klasse = f"kachel {stufe}".strip()
    fusszeile = f'<div class="fuss">{escape(fuss)}</div>' if fuss else ""
    return (f'<div class="{klasse}"><div class="wert">{escape(str(wert))}</div>'
            f'<div class="titel">{escape(titel)}</div>{fusszeile}</div>')


def _lagebild(welt: ps.Welt, lage: dict) -> str:
    gueltig = lage["nach_status"]["gueltig"]
    in_arbeit = lage["nach_status"]["entwurf"] + lage["nach_status"]["in_abstimmung"]
    kacheln = [
        _kachel(lage["standards"], "Standards", f"{gueltig} gültig, {in_arbeit} in Arbeit"),
        _kachel(lage["aufgaben"], "verbindliche Aufgaben", "mit Takt, Frist und Nachweis"),
        _kachel(f"{lage['pflichten_quote']}%", "Pflichten gedeckt",
                f"{lage['pflichten_gedeckt']} von {lage['pflichten']} Betreiberpflichten",
                "ok" if lage["pflichten_quote"] >= 80 else "warn"),
        _kachel(lage["review_ueberfaellig"], "Reviews überfällig",
                f"{lage['review_bald']} weitere in den nächsten 90 Tagen",
                "krit" if lage["review_ueberfaellig"] else "ok"),
        _kachel(lage["rechtsstand_offen"], "Rechtsstand offen", "gültig ohne Bestätigung SST-REW",
                "warn" if lage["rechtsstand_offen"] else "ok"),
        _kachel(lage["themenfelder_ohne_standard"], "Themenfelder ohne Standard",
                f"von {lage['themenfelder']} Themenfeldern",
                "warn" if lage["themenfelder_ohne_standard"] else "ok"),
    ]
    return f"""
<section id="lagebild">
  <header>
    <h2>Lagebild</h2>
    <p>Sieben Zahlen, die in der Abteilungsrunde reichen. Alles darunter ist die Herleitung.</p>
  </header>
  <div class="kennzahlen">{''.join(kacheln)}</div>
</section>
"""


def _handlungsbedarf(welt: ps.Welt, befunde: list) -> str:
    stufe_klasse = {"fehler": "krit", "warnung": "warn", "hinweis": ""}
    stufe_text = {"fehler": ("Fehler", "krit"), "warnung": ("zu klären", "warn"),
                  "hinweis": ("Vormerkung", "")}
    sichtbar = [b for b in befunde if b.schwere in ("fehler", "warnung")]

    if not sichtbar:
        zeilen = ('<div class="befund"><span></span><span></span>'
                  '<span>Kein offener Punkt. Das Regelwerk ist vollständig und aktuell.</span></div>')
    else:
        zeilen = "".join(
            f'<div class="befund {stufe_klasse[b.schwere]}">'
            f'<span><span class="marker {stufe_text[b.schwere][1]}">{stufe_text[b.schwere][0]}</span></span>'
            f'<span class="ort">{escape(b.ort)}</span>'
            f'<span>{escape(b.text)}</span></div>'
            for b in sichtbar
        )
    hinweise = len([b for b in befunde if b.schwere == "hinweis"])
    return f"""
<section id="handlungsbedarf">
  <header>
    <h2>Handlungsbedarf</h2>
    <p>Aus der Prüfung des Regelwerks abgeleitet, nach Dringlichkeit sortiert.
       Fehler blockieren die Freigabe, Punkte zum Klären gehören in die nächste
       Abteilungsrunde. {hinweise} weitere Vormerkungen sind ausgeblendet.</p>
  </header>
  <div class="befunde">{zeilen}</div>
</section>
"""


def _themenfelder(welt: ps.Welt) -> str:
    zeilen = []
    for tf_id, themenfeld in welt.themenfelder.items():
        standards = [s for s in welt.standards if s.kopf.get("themenfeld") == tf_id]
        pflichten = [p for p in welt.pflichten.values() if p.get("themenfeld") == tf_id]
        gedeckt = {pfl for s in standards for pfl in (s.kopf.get("pflichten") or [])}
        aufgaben = sum(len(s.aufgaben) for s in standards)

        if not standards:
            marke = ('<span class="marker krit">kein Standard</span>'
                     if themenfeld.get("kritikalitaet") == "hoch"
                     else '<span class="marker warn">kein Standard</span>')
        elif all(s.kopf.get("status") == "gueltig" for s in standards):
            marke = '<span class="marker ok">geregelt</span>'
        else:
            marke = '<span class="marker warn">in Arbeit</span>'

        fach = themenfeld.get("fachfunktion")
        zeilen.append(
            f"<tr>"
            f'<td class="kennung">{escape(tf_id)}</td>'
            f"<td><strong>{escape(themenfeld['name'])}</strong><br>"
            f'<span style="color:var(--ink-still);font-size:12.5px">{escape(themenfeld.get("beschreibung", ""))}</span></td>'
            f'<td class="knapp">{escape(themenfeld.get("kritikalitaet", ""))}</td>'
            f'<td class="kennung">{escape(themenfeld.get("owner", ""))}'
            f'{"<br>" + escape(fach) if fach else ""}</td>'
            f'<td class="zahl">{len(standards)}</td>'
            f'<td class="zahl">{aufgaben}</td>'
            f'<td class="zahl">{len(gedeckt)} / {len(pflichten)}</td>'
            f'<td class="knapp">{marke}</td>'
            f"</tr>"
        )
    return f"""
<section id="themenfelder">
  <header>
    <h2>Themenfelder</h2>
    <p>Jedes Thema, das in der Abteilung landet, hat genau ein Feld und genau eine
       Verantwortung. Felder ohne Standard sind keine Nachlässigkeit, sondern die
       Arbeitsvorratsliste — sichtbar statt vergessen.</p>
  </header>
  <div class="tabellenrahmen">
    <table>
      <thead><tr>
        <th>Feld</th><th>Themenfeld</th><th>Kritikalität</th><th>Verantwortung</th>
        <th class="zahl">Std.</th><th class="zahl">Aufg.</th><th class="zahl">Pflichten</th><th>Stand</th>
      </tr></thead>
      <tbody>{''.join(zeilen)}</tbody>
    </table>
  </div>
</section>
"""


def _standards(welt: ps.Welt) -> str:
    bloecke = []
    for standard in sorted(welt.standards, key=lambda s: s.id):
        kopf = standard.kopf
        text, stufe = STATUS_ANZEIGE.get(kopf.get("status"), (kopf.get("status", "?"), "neutral"))
        resttage = standard.resttage(welt.heute)
        if resttage is None:
            review = '<span class="marker">Review unbekannt</span>'
        elif resttage < 0:
            review = f'<span class="marker krit">Review {abs(resttage)} Tage überfällig</span>'
        elif resttage <= 90:
            review = f'<span class="marker warn">Review in {resttage} Tagen</span>'
        else:
            review = f'<span class="marker">Review {standard.naechster_review().strftime("%m/%Y")}</span>'

        rechtsstand = ('<span class="marker ok">Rechtsstand bestätigt</span>'
                       if kopf.get("rechtsstand_geprueft")
                       else '<span class="marker warn">Rechtsstand offen</span>')

        aufgabenzeilen = "".join(
            f"<tr>"
            f'<td class="kennung">{escape(str(a.get("id", "")))}</td>'
            f"<td>{escape(str(a.get('was', '')))}</td>"
            f'<td class="knapp">{escape(TAKT_ANZEIGE.get(a.get("takt"), str(a.get("takt", ""))))}</td>'
            f"<td>{escape(str(a.get('frist', '')))}</td>"
            f'<td class="kennung"><span class="raci">A</span> {escape(str(a.get("a", "")))}</td>'
            f'<td class="kennung"><span class="raci">R</span> {escape(", ".join(a.get("r") or []))}</td>'
            f"<td>{escape(str(a.get('nachweis', '')))}</td>"
            f"</tr>"
            for a in standard.aufgaben if isinstance(a, dict)
        )

        geltung = kopf.get("geltungsbereich") or {}
        bereiche = geltung.get("betriebsbereiche") or []
        bereichstext = ("alle sieben Betriebsbereiche" if "alle" in bereiche
                        else ", ".join(bereiche))
        pflichten = ", ".join(kopf.get("pflichten") or []) or "keine verknüpft"
        partner = ", ".join(kopf.get("schnittstellen") or []) or "keine"

        bloecke.append(f"""
<details>
  <summary>
    <span class="kennung">{escape(standard.id)}</span>
    <span class="name">{escape(str(kopf.get('titel', '')))}</span>
    <span class="rechts">
      <span class="marker">v{escape(str(kopf.get('version', '')))}</span>
      {review}
      <span class="marker {stufe}">{escape(text)}</span>
    </span>
  </summary>
  <div class="inhalt">
    <div class="tabellenrahmen">
      <table>
        <thead><tr><th>Nr.</th><th>Aufgabe</th><th>Takt</th><th>Frist</th>
        <th>verantwortet</th><th>führt aus</th><th>Nachweis</th></tr></thead>
        <tbody>{aufgabenzeilen}</tbody>
      </table>
    </div>
    <div class="karte" style="border:none;border-top:1px solid var(--linie);border-radius:0">
      <div class="fuss" style="border:none;padding-top:0">
        <span>Verantwortung {escape(str(kopf.get('owner', '')))}</span>
        <span>Freigabe {escape(str(kopf.get('freigabe', '')))}</span>
        <span>gültig ab {escape(str(kopf.get('gueltig_ab', '')))}</span>
        <span>Reviewzyklus {escape(str(kopf.get('review_zyklus_monate', '')))} Monate</span>
        <span>Geltung: {escape(bereichstext)}</span>
        <span>Pflichten: {escape(pflichten)}</span>
        <span>Schnittstellen: {escape(partner)}</span>
        <span>{rechtsstand}</span>
      </div>
    </div>
  </div>
</details>
""")
    return f"""
<section id="standards">
  <header>
    <h2>Standards</h2>
    <p>Aufklappen zeigt die verbindlichen Aufgaben mit Takt, Frist, Verantwortung
       und Nachweis. Was hier nicht steht, ist nicht vorgegeben.</p>
  </header>
  <div>{''.join(bloecke)}</div>
</section>
"""


def _rollen(welt: ps.Welt) -> str:
    gruppen = {}
    for rollen_id, rolle in welt.rollen.items():
        beteiligungen = ps.aufgaben_der_rolle(welt, rollen_id)
        if not beteiligungen:
            continue
        gruppen.setdefault(rolle.get("ebene", "sonstige"), []).append((rollen_id, rolle, beteiligungen))

    abschnitte = []
    for ebene, anzeige in EBENEN_ANZEIGE.items():
        eintraege = gruppen.get(ebene)
        if not eintraege:
            continue
        bloecke = []
        for rollen_id, rolle, beteiligungen in sorted(eintraege, key=lambda e: e[0]):
            verantwortet = len([b for b in beteiligungen if "A" in b[2]])
            fuehrt_aus = len([b for b in beteiligungen if "R" in b[2]])
            zeilen = "".join(
                f"<tr>"
                f'<td class="knapp"><span class="raci">{escape(art)}</span></td>'
                f"<td>{escape(str(aufgabe.get('was', '')))}</td>"
                f'<td class="knapp">{escape(TAKT_ANZEIGE.get(aufgabe.get("takt"), str(aufgabe.get("takt", ""))))}</td>'
                f"<td>{escape(str(aufgabe.get('frist', '')))}</td>"
                f'<td class="kennung">{escape(standard.id)}</td>'
                f"</tr>"
                for standard, aufgabe, art in beteiligungen
            )
            anzahl = rolle.get("anzahl")
            # Rollen, die nur beraten oder informiert werden, haben null A und
            # null R - ohne die Gesamtzahl saehen sie unbeteiligt aus.
            marken = [f'<span class="marker">{len(beteiligungen)} Aufgaben</span>']
            if verantwortet:
                marken.append(f'<span class="marker akzent">{verantwortet} verantwortet</span>')
            if fuehrt_aus:
                marken.append(f'<span class="marker">{fuehrt_aus} führt aus</span>')
            if not verantwortet and not fuehrt_aus:
                marken.append('<span class="marker">nur beteiligt</span>')

            bloecke.append(f"""
<details>
  <summary>
    <span class="kennung">{escape(rollen_id)}</span>
    <span class="name">{escape(rolle['name'])}</span>
    <span class="rechts">
      {f'<span class="marker">{anzahl}x besetzt</span>' if anzahl else ''}
      {''.join(marken)}
    </span>
  </summary>
  <div class="inhalt"><div class="tabellenrahmen"><table>
    <thead><tr><th>Rolle</th><th>Aufgabe</th><th>Takt</th><th>Frist</th><th>Standard</th></tr></thead>
    <tbody>{zeilen}</tbody>
  </table></div></div>
</details>
""")
        abschnitte.append(
            f'<h3 style="font-family:var(--schrift-titel);font-size:16px;margin:14px 0 6px">'
            f'{escape(anzeige)}</h3>{"".join(bloecke)}'
        )

    return f"""
<section id="rollen">
  <header>
    <h2>Wer macht was, wann</h2>
    <p>Dieselben Aufgaben, nach Rolle sortiert statt nach Standard. Das ist die Sicht,
       die in die Einheit geht: eine Rolle klappt auf und sieht ihre vollständige Liste.
       <strong>A</strong> verantwortet das Ergebnis, <strong>R</strong> führt aus,
       <strong>C</strong> wird beteiligt, <strong>I</strong> wird informiert.</p>
  </header>
  <div>{''.join(abschnitte)}</div>
</section>
"""


def _taktuebersicht(welt: ps.Welt) -> str:
    zaehler = {}
    for standard in welt.standards:
        if standard.kopf.get("status") in ("archiviert", "ausgesetzt"):
            continue
        for aufgabe in standard.aufgaben:
            if isinstance(aufgabe, dict):
                zaehler[aufgabe.get("takt")] = zaehler.get(aufgabe.get("takt"), 0) + 1
    if not zaehler:
        return ""
    hoechster = max(zaehler.values())
    zeilen = []
    for takt in ps.TAKT_WERTE:
        anzahl = zaehler.get(takt, 0)
        if not anzahl:
            continue
        breite = round(100 * anzahl / hoechster)
        zeilen.append(
            f'<div class="taktzeile"><span>{escape(TAKT_ANZEIGE.get(takt, takt))}</span>'
            f'<span class="balken"><span style="width:{breite}%"></span></span>'
            f'<span class="anzahl">{anzahl}</span></div>'
        )
    return f"""
<section id="takt">
  <header>
    <h2>Jahrestakt</h2>
    <p>Wie sich die verbindlichen Aufgaben über die Wiederholzyklen verteilen —
       von der täglichen Prüfung bis zur einmaligen Festlegung. Ein Übergewicht bei
       „anlassbezogen" heißt: viel hängt daran, dass jemand den Anlass erkennt.</p>
  </header>
  <div class="taktband">{''.join(zeilen)}</div>
</section>
"""


def _schnittstellen(welt: ps.Welt) -> str:
    reife = {"vereinbart": ("vereinbart", "ok"), "abgestimmt": ("abgestimmt", "warn"),
             "entwurf": ("Entwurf", "krit")}
    karten = []
    for vereinbarung in welt.schnittstellen:
        partner = vereinbarung.get("partner", "")
        text, stufe = reife.get(vereinbarung.get("reifegrad"), (vereinbarung.get("reifegrad", ""), ""))
        liefern = "".join(f"<li>{escape(str(p))}</li>" for p in vereinbarung.get("wir_liefern") or [])
        erwarten = "".join(f"<li>{escape(str(p))}</li>" for p in vereinbarung.get("wir_erwarten") or [])
        karten.append(f"""
<div class="karte">
  <div>
    <h3>{escape(welt.rolle_name(partner))}</h3>
    <p class="thema">{escape(str(vereinbarung.get('thema', '')))}</p>
  </div>
  <div><h4>Wir liefern</h4><ul>{liefern}</ul></div>
  <div><h4>Wir erwarten</h4><ul>{erwarten}</ul></div>
  <div class="fuss">
    <span class="marker {stufe}">{escape(text)}</span>
    <span>Jourfixe {escape(str(vereinbarung.get('turnus_jourfixe', '—')))}</span>
    <span>Eskalation: {escape(str(vereinbarung.get('eskalation', '—')))}</span>
  </div>
</div>
""")
    return f"""
<section id="schnittstellen">
  <header>
    <h2>Schnittstellen</h2>
    <p>Was wir liefern und was wir erwarten — je Partner an einer Stelle. Damit ist
       „das hättet ihr machen müssen" auf ein Dokument zurückführbar statt auf Erinnerung.</p>
  </header>
  <div class="karten">{''.join(karten)}</div>
</section>
"""


def _betriebsbereiche(welt: ps.Welt) -> str:
    zeilen = []
    for bb_id, bereich in welt.betriebsbereiche.items():
        geltende = [
            s for s in welt.standards
            if s.kopf.get("status") == "gueltig"
            and ("alle" in ((s.kopf.get("geltungsbereich") or {}).get("betriebsbereiche") or [])
                 or bb_id in ((s.kopf.get("geltungsbereich") or {}).get("betriebsbereiche") or []))
        ]
        aufgaben = sum(len(s.aufgaben) for s in geltende)
        klassen = ", ".join(bereich.get("anlagenklassen") or [])
        zeilen.append(
            f"<tr>"
            f'<td class="kennung">{escape(bb_id)}</td>'
            f"<td><strong>{escape(bereich['name'])}</strong></td>"
            f'<td class="knapp">{escape(str(bereich.get("sitz", "")))}</td>'
            f'<td class="zahl">{bereich.get("mitarbeitende", "")}</td>'
            f"<td>{escape(klassen)}</td>"
            f'<td class="knapp">{"ja" if bereich.get("bereitschaft") else "nein"}</td>'
            f'<td class="zahl">{len(geltende)}</td>'
            f'<td class="zahl">{aufgaben}</td>'
            f"</tr>"
        )
    return f"""
<section id="bereiche">
  <header>
    <h2>Betriebsbereiche</h2>
    <p>Sieben Bereiche, eine Vorgabe. Die Spalten rechts zeigen, wie viele gültige
       Standards und Aufgaben im jeweiligen Bereich tatsächlich ankommen.</p>
  </header>
  <div class="tabellenrahmen">
    <table>
      <thead><tr><th>Kürzel</th><th>Bereich</th><th>Sitz</th><th class="zahl">MA</th>
      <th>Anlagenklassen</th><th>Bereitschaft</th><th class="zahl">Standards</th>
      <th class="zahl">Aufgaben</th></tr></thead>
      <tbody>{''.join(zeilen)}</tbody>
    </table>
  </div>
</section>
"""


def _pflichten(welt: ps.Welt) -> str:
    zeilen = []
    for pfl_id, pflicht in welt.pflichten.items():
        deckend = [s.id for s in welt.standards if pfl_id in (s.kopf.get("pflichten") or [])]
        if deckend:
            marke = f'<span class="marker ok">{escape(", ".join(deckend))}</span>'
        else:
            marke = '<span class="marker krit">kein Standard</span>'
        geprueft = ('<span class="marker ok">bestätigt</span>' if pflicht.get("rechtsstand_geprueft")
                    else '<span class="marker warn">offen</span>')
        zeilen.append(
            f"<tr>"
            f'<td class="kennung">{escape(pfl_id)}</td>'
            f"<td>{escape(pflicht['titel'])}</td>"
            f'<td class="kennung">{escape(str(pflicht.get("themenfeld", "")))}</td>'
            f"<td>{escape(str(pflicht.get('quelle', '')))}</td>"
            f"<td>{escape(str(pflicht.get('turnus', '')))}</td>"
            f'<td class="kennung">{escape(str(pflicht.get("traeger", "")))}</td>'
            f'<td class="knapp">{marke}</td>'
            f'<td class="knapp">{geprueft}</td>'
            f"</tr>"
        )
    return f"""
<section id="pflichten">
  <header>
    <h2>Pflichtenregister</h2>
    <p>Die Betreiberpflichten, die wir tragen, und der Standard, der jede davon
       operativ umsetzt. Die Spalte Rechtsstand ist bewusst getrennt: eine Pflicht gilt
       erst dann als bestätigt, wenn Recht und Compliance sie geprüft hat — kein Agent
       setzt dieses Feld.</p>
  </header>
  <div class="tabellenrahmen">
    <table>
      <thead><tr><th>Nr.</th><th>Pflicht</th><th>Feld</th><th>Quelle</th><th>Turnus</th>
      <th>Träger</th><th>umgesetzt durch</th><th>Rechtsstand</th></tr></thead>
      <tbody>{''.join(zeilen)}</tbody>
    </table>
  </div>
</section>
"""


def _fuss(welt: ps.Welt) -> str:
    return f"""
<footer class="fussnote">
  <div>Erzeugt am {dt.datetime.now().strftime('%d.%m.%Y um %H:%M')} aus dem Regelwerk im
     Verzeichnis <code>standards/</code> und den Stammdaten in <code>daten/</code>.</div>
  <div>Neu bauen mit <code>python3 werkzeuge/ps.py cockpit</code>,
     prüfen mit <code>python3 werkzeuge/ps.py pruefen</code>.</div>
  <div>Die Rollenangaben sind Rollen, keine Personen. Die Zuordnung Rolle zu Person
     wird im Organigramm und in den schriftlichen Bestellungen geführt.</div>
</footer>
"""
