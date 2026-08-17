#!/usr/bin/env python3
"""Werkzeug der Produktionssteuerung: Regelwerk prüfen, auswerten, darstellen.

Aufrufe:

  python3 werkzeuge/ps.py pruefen              Regelwerk gegen die Regeln prüfen
  python3 werkzeuge/ps.py status               Kurzlage für Menschen und Agenten
  python3 werkzeuge/ps.py faellig --tage 90    anstehende und überfällige Reviews
  python3 werkzeuge/ps.py rollenblatt BB-MV    Wer-macht-was-wann für eine Rolle
  python3 werkzeuge/ps.py luecken              Pflichten und Themenfelder ohne Standard
  python3 werkzeuge/ps.py neu TF-BRA "Titel"   neuen Standard aus der Vorlage anlegen
  python3 werkzeuge/ps.py cockpit              cockpit/index.html bauen
  python3 werkzeuge/ps.py selbsttest           YAML-Rückfallleser gegen PyYAML prüfen

"pruefen" endet mit Rückgabewert 1, sobald ein Fehler gefunden wurde -
damit lässt es sich in einen Hook oder eine Pipeline hängen.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import miniyaml  # noqa: E402

WURZEL = Path(__file__).resolve().parent.parent
DATEN = WURZEL / "daten"
STANDARDS = WURZEL / "standards"
VORLAGE = STANDARDS / "_vorlagen" / "standard-vorlage.md"

STATUS_WERTE = ["entwurf", "in_abstimmung", "gueltig", "ausgesetzt", "archiviert"]
TAKT_WERTE = [
    "taeglich", "woechentlich", "monatlich", "quartalsweise", "halbjaehrlich",
    "jaehrlich", "zweijaehrlich", "dreijaehrlich", "vierjaehrlich",
    "anlassbezogen", "laufend", "einmalig",
]
TAKT_REIHENFOLGE = {wert: nr for nr, wert in enumerate(TAKT_WERTE)}
# Aufzaehlungswerte bleiben ASCII-Bezeichner, gelesen wird die deutsche Fassung.
TAKT_ANZEIGE = {
    "taeglich": "täglich", "woechentlich": "wöchentlich", "monatlich": "monatlich",
    "quartalsweise": "quartalsweise", "halbjaehrlich": "halbjährlich",
    "jaehrlich": "jährlich", "zweijaehrlich": "zweijährlich",
    "dreijaehrlich": "dreijährlich", "vierjaehrlich": "vierjährlich",
    "anlassbezogen": "anlassbezogen", "laufend": "laufend", "einmalig": "einmalig",
}
PFLICHTFELDER = [
    "id", "titel", "themenfeld", "version", "status", "gueltig_ab",
    "letzter_review", "review_zyklus_monate", "owner", "freigabe",
    "rechtsstand_geprueft", "geltungsbereich", "aufgaben",
]
ID_MUSTER = re.compile(r"^STD-[A-Z]{3}-\d{3}$")


# --- YAML-Zugang ----------------------------------------------------------


def yaml_laden(text: str):
    """Liest YAML mit PyYAML, fällt sonst auf den mitgelieferten Leser zurück."""
    try:
        import yaml
    except ImportError:
        return miniyaml.laden(text)
    try:
        return _datumsangaben_vereinheitlichen(yaml.safe_load(text))
    except Exception:  # noqa: BLE001 - PyYAML wirft hier auch blanke ValueError
        # PyYAML bricht schon an einem unmöglichen Datum wie 2026-13-01 ab und
        # verdeckt damit alle übrigen Fehler der Datei. Der eigene Leser behält
        # solche Werte als Text, sodass die Prüfung sie einzeln benennen kann.
        return miniyaml.laden(text)


def _datumsangaben_vereinheitlichen(wert):
    """PyYAML liefert date-Objekte, der Rückfallleser Text - hier vereinheitlicht."""
    if isinstance(wert, dict):
        return {s: _datumsangaben_vereinheitlichen(w) for s, w in wert.items()}
    if isinstance(wert, list):
        return [_datumsangaben_vereinheitlichen(w) for w in wert]
    if isinstance(wert, (dt.datetime, dt.date)):
        return wert.isoformat()
    return wert


def datei_laden(pfad: Path):
    return yaml_laden(pfad.read_text(encoding="utf-8"))


# --- Datenmodell ----------------------------------------------------------


@dataclass
class Befund:
    schwere: str  # fehler | warnung | hinweis
    ort: str
    text: str

    def __str__(self) -> str:
        kennung = {"fehler": "FEHLER ", "warnung": "WARNUNG", "hinweis": "HINWEIS"}
        return f"{kennung[self.schwere]}  {self.ort:<28} {self.text}"


@dataclass
class Standard:
    pfad: Path
    kopf: dict
    text: str

    @property
    def id(self) -> str:
        return str(self.kopf.get("id", self.pfad.stem))

    @property
    def aufgaben(self) -> list:
        return self.kopf.get("aufgaben") or []

    def naechster_review(self):
        letzter = datum(self.kopf.get("letzter_review"))
        monate = self.kopf.get("review_zyklus_monate")
        if letzter is None or not isinstance(monate, int):
            return None
        return monate_addieren(letzter, monate)

    def resttage(self, heute: dt.date):
        faellig = self.naechster_review()
        return None if faellig is None else (faellig - heute).days


@dataclass
class Welt:
    """Alles, was das Werkzeug kennt - einmal geladen, überall verwendet."""

    rollen: dict = field(default_factory=dict)
    themenfelder: dict = field(default_factory=dict)
    betriebsbereiche: dict = field(default_factory=dict)
    schnittstellen: list = field(default_factory=list)
    pflichten: dict = field(default_factory=dict)
    standards: list = field(default_factory=list)
    heute: dt.date = field(default_factory=dt.date.today)

    def rolle_name(self, rollen_id: str) -> str:
        eintrag = self.rollen.get(rollen_id)
        return eintrag["name"] if eintrag else rollen_id

    def themenfeld_name(self, tf_id: str) -> str:
        eintrag = self.themenfelder.get(tf_id)
        return eintrag["name"] if eintrag else tf_id

    def standard(self, std_id: str):
        for eintrag in self.standards:
            if eintrag.id == std_id:
                return eintrag
        return None


def datum(wert):
    if isinstance(wert, dt.date):
        return wert
    if isinstance(wert, str):
        try:
            return dt.date.fromisoformat(wert)
        except ValueError:
            return None
    return None


def monate_addieren(start: dt.date, monate: int) -> dt.date:
    monat_gesamt = start.month - 1 + monate
    jahr = start.year + monat_gesamt // 12
    monat = monat_gesamt % 12 + 1
    letzter_tag = [31, 29 if _schaltjahr(jahr) else 28, 31, 30, 31, 30,
                   31, 31, 30, 31, 30, 31][monat - 1]
    return dt.date(jahr, monat, min(start.day, letzter_tag))


def _schaltjahr(jahr: int) -> bool:
    return jahr % 4 == 0 and (jahr % 100 != 0 or jahr % 400 == 0)


def welt_laden(heute: dt.date | None = None) -> Welt:
    welt = Welt(heute=heute or dt.date.today())

    rollen = datei_laden(DATEN / "organisation" / "rollen.yaml")
    welt.rollen = {eintrag["id"]: eintrag for eintrag in rollen.get("rollen", [])}

    themen = datei_laden(DATEN / "themenfelder.yaml")
    welt.themenfelder = {e["id"]: e for e in themen.get("themenfelder", [])}

    bereiche = datei_laden(DATEN / "organisation" / "betriebsbereiche.yaml")
    welt.betriebsbereiche = {e["id"]: e for e in bereiche.get("betriebsbereiche", [])}

    schnitt = datei_laden(DATEN / "organisation" / "schnittstellen.yaml")
    welt.schnittstellen = schnitt.get("schnittstellen", [])

    pflichten = datei_laden(DATEN / "pflichtenregister.yaml")
    welt.pflichten = {e["id"]: e for e in pflichten.get("pflichten", [])}

    welt.standards = standards_laden()
    return welt


def standards_laden() -> list:
    ergebnis = []
    for pfad in sorted(STANDARDS.rglob("*.md")):
        if "_vorlagen" in pfad.parts:
            continue
        kopf, text = kopfdaten_trennen(pfad.read_text(encoding="utf-8"))
        ergebnis.append(Standard(pfad=pfad, kopf=kopf or {}, text=text))
    return ergebnis


def kopfdaten_trennen(inhalt: str):
    """Trennt den YAML-Kopf vom Fließtext eines Standards."""
    if not inhalt.startswith("---"):
        return None, inhalt
    teile = inhalt.split("\n---", 2)
    if len(teile) < 2:
        return None, inhalt
    kopf_text = teile[0][3:]
    rest = teile[1].lstrip("-\n")
    try:
        return yaml_laden(kopf_text), rest
    except Exception as fehler:  # noqa: BLE001 - Meldung reicht, Abbruch nicht
        return {"__fehler__": str(fehler)}, rest


# --- Prüfung -------------------------------------------------------------


def pruefen(welt: Welt) -> list:
    befunde = []
    befunde += _daten_pruefen(welt)
    gesehene_ids = {}
    for standard in welt.standards:
        befunde += _standard_pruefen(welt, standard, gesehene_ids)
    befunde += _abdeckung_pruefen(welt)
    reihenfolge = {"fehler": 0, "warnung": 1, "hinweis": 2}
    return sorted(befunde, key=lambda b: (reihenfolge[b.schwere], b.ort))


def _daten_pruefen(welt: Welt) -> list:
    befunde = []
    for tf_id, themenfeld in welt.themenfelder.items():
        for feld in ("owner", "fachfunktion"):
            rolle = themenfeld.get(feld)
            if rolle and rolle not in welt.rollen:
                befunde.append(Befund("fehler", tf_id,
                                      f"{feld} verweist auf unbekannte Rolle {rolle}"))
        owner = themenfeld.get("owner")
        if owner and owner in welt.rollen and not welt.rollen[owner].get("darf_a_sein"):
            befunde.append(Befund("fehler", tf_id,
                                  f"owner {owner} darf keine Ergebnisverantwortung tragen"))

    for pfl_id, pflicht in welt.pflichten.items():
        if pflicht.get("themenfeld") not in welt.themenfelder:
            befunde.append(Befund("fehler", pfl_id,
                                  f"unbekanntes Themenfeld {pflicht.get('themenfeld')}"))
        for feld in ("traeger", "delegation_von"):
            rolle = pflicht.get(feld)
            if rolle and rolle not in welt.rollen:
                befunde.append(Befund("fehler", pfl_id,
                                      f"{feld} verweist auf unbekannte Rolle {rolle}"))

    for vereinbarung in welt.schnittstellen:
        partner = vereinbarung.get("partner")
        if partner not in welt.rollen:
            befunde.append(Befund("fehler", "schnittstellen.yaml",
                                  f"unbekannter Partner {partner}"))
        elif welt.rollen[partner].get("ebene") != "schnittstelle":
            befunde.append(Befund("warnung", "schnittstellen.yaml",
                                  f"{partner} ist nicht als Schnittstelle geführt"))
        if vereinbarung.get("reifegrad") == "entwurf":
            befunde.append(Befund("hinweis", f"Schnittstelle {partner}",
                                  "Vereinbarung noch im Entwurf - Zulieferung nicht verlässlich"))

    for bb_id, bereich in welt.betriebsbereiche.items():
        for feld in ("leitung", "koordination_ps"):
            rolle = bereich.get(feld)
            if rolle and rolle not in welt.rollen:
                befunde.append(Befund("fehler", bb_id,
                                      f"{feld} verweist auf unbekannte Rolle {rolle}"))
    return befunde


def _standard_pruefen(welt: Welt, standard: Standard, gesehene_ids: dict) -> list:
    befunde = []
    ort = standard.pfad.relative_to(WURZEL).as_posix()
    kopf = standard.kopf

    if not kopf:
        return [Befund("fehler", ort, "kein YAML-Kopf gefunden")]
    if "__fehler__" in kopf:
        return [Befund("fehler", ort, f"YAML-Kopf nicht lesbar: {kopf['__fehler__']}")]

    for feld in PFLICHTFELDER:
        if kopf.get(feld) in (None, "", []):
            befunde.append(Befund("fehler", ort, f"Pflichtfeld fehlt oder ist leer: {feld}"))
    if befunde:
        return befunde

    ort = standard.id
    std_id = standard.id
    if not ID_MUSTER.match(std_id):
        befunde.append(Befund("fehler", ort, "ID entspricht nicht dem Muster STD-XXX-000"))
    if std_id in gesehene_ids:
        befunde.append(Befund("fehler", ort, f"ID doppelt vergeben, bereits in {gesehene_ids[std_id]}"))
    gesehene_ids[std_id] = standard.pfad.name
    if std_id not in standard.pfad.name:
        befunde.append(Befund("warnung", ort, f"Dateiname enthält die ID nicht: {standard.pfad.name}"))

    themenfeld = kopf.get("themenfeld")
    if themenfeld not in welt.themenfelder:
        befunde.append(Befund("fehler", ort, f"unbekanntes Themenfeld {themenfeld}"))
    elif ID_MUSTER.match(std_id) and std_id.split("-")[1] != str(themenfeld).split("-")[1]:
        befunde.append(Befund("warnung", ort,
                              f"ID-Kürzel passt nicht zum Themenfeld {themenfeld}"))

    if kopf.get("status") not in STATUS_WERTE:
        befunde.append(Befund("fehler", ort,
                              f"Status {kopf.get('status')!r} ist nicht zulässig"))

    for feld in ("gueltig_ab", "letzter_review"):
        if datum(kopf.get(feld)) is None:
            befunde.append(Befund("fehler", ort, f"{feld} ist kein Datum im Format JJJJ-MM-TT"))
    zyklus = kopf.get("review_zyklus_monate")
    if not isinstance(zyklus, int) or zyklus <= 0:
        befunde.append(Befund("fehler", ort, "review_zyklus_monate muss eine positive Zahl sein"))

    for feld in ("owner", "freigabe"):
        rolle = kopf.get(feld)
        if rolle not in welt.rollen:
            befunde.append(Befund("fehler", ort, f"{feld}: unbekannte Rolle {rolle}"))
        elif not welt.rollen[rolle].get("darf_a_sein"):
            befunde.append(Befund("fehler", ort,
                                  f"{feld}: {rolle} darf keine Ergebnisverantwortung tragen"))

    for pfl_id in kopf.get("pflichten") or []:
        if pfl_id not in welt.pflichten:
            befunde.append(Befund("fehler", ort, f"unbekannte Pflicht {pfl_id}"))

    geltung = kopf.get("geltungsbereich") or {}
    bereiche = geltung.get("betriebsbereiche") or []
    for bb_id in bereiche:
        if bb_id != "alle" and bb_id not in welt.betriebsbereiche:
            befunde.append(Befund("fehler", ort, f"unbekannter Betriebsbereich {bb_id}"))
    if not bereiche:
        befunde.append(Befund("fehler", ort, "geltungsbereich.betriebsbereiche ist leer"))
    for rolle in geltung.get("rollen") or []:
        if rolle not in welt.rollen:
            befunde.append(Befund("fehler", ort, f"geltungsbereich: unbekannte Rolle {rolle}"))

    for partner in kopf.get("schnittstellen") or []:
        if partner not in welt.rollen:
            befunde.append(Befund("fehler", ort, f"unbekannte Schnittstelle {partner}"))

    befunde += _aufgaben_pruefen(welt, standard, ort)
    befunde += _kennzahlen_pruefen(standard, ort)
    befunde += _eskalation_pruefen(welt, standard, ort)
    befunde += _reife_pruefen(welt, standard, ort)
    return befunde


def _aufgaben_pruefen(welt: Welt, standard: Standard, ort: str) -> list:
    befunde = []
    gesehen = set()
    for nummer, aufgabe in enumerate(standard.aufgaben, start=1):
        if not isinstance(aufgabe, dict):
            befunde.append(Befund("fehler", ort, f"Aufgabe {nummer} ist keine Zuordnung"))
            continue
        kennung = aufgabe.get("id") or f"#{nummer}"
        stelle = f"{ort} {kennung}"
        if kennung in gesehen:
            befunde.append(Befund("fehler", stelle, "Aufgaben-ID doppelt vergeben"))
        gesehen.add(kennung)

        for feld in ("was", "frist", "nachweis"):
            if not aufgabe.get(feld):
                befunde.append(Befund("fehler", stelle, f"Feld {feld} fehlt"))
        if not aufgabe.get("system"):
            befunde.append(Befund("warnung", stelle, "kein Ablageort (system) angegeben"))

        if aufgabe.get("takt") not in TAKT_WERTE:
            befunde.append(Befund("fehler", stelle,
                                  f"Takt {aufgabe.get('takt')!r} ist nicht zulässig"))

        verantwortlich = aufgabe.get("a")
        if isinstance(verantwortlich, list):
            befunde.append(Befund("fehler", stelle,
                                  "genau eine Rolle darf verantwortlich (a) sein"))
        elif not verantwortlich:
            befunde.append(Befund("fehler", stelle, "keine verantwortliche Rolle (a) benannt"))
        elif verantwortlich not in welt.rollen:
            befunde.append(Befund("fehler", stelle, f"a: unbekannte Rolle {verantwortlich}"))
        elif not welt.rollen[verantwortlich].get("darf_a_sein"):
            befunde.append(Befund("fehler", stelle,
                                  f"a: {verantwortlich} darf keine Ergebnisverantwortung tragen"))

        ausfuehrende = aufgabe.get("r") or []
        if not ausfuehrende:
            befunde.append(Befund("fehler", stelle, "keine ausführende Rolle (r) benannt"))
        for feld in ("r", "c", "i"):
            werte = aufgabe.get(feld) or []
            if isinstance(werte, str):
                befunde.append(Befund("warnung", stelle, f"{feld} sollte eine Liste sein"))
                werte = [werte]
            for rolle in werte:
                if rolle not in welt.rollen:
                    befunde.append(Befund("fehler", stelle, f"{feld}: unbekannte Rolle {rolle}"))
    if not standard.aufgaben:
        befunde.append(Befund("fehler", ort, "keine Aufgaben definiert - der Standard ist unverbindlich"))
    return befunde


def _kennzahlen_pruefen(standard: Standard, ort: str) -> list:
    befunde = []
    kennzahlen = standard.kopf.get("kennzahlen") or []
    if not kennzahlen and standard.kopf.get("status") == "gueltig":
        befunde.append(Befund("warnung", ort, "gültiger Standard ohne Kennzahl - Wirkung nicht messbar"))
    for nummer, kennzahl in enumerate(kennzahlen, start=1):
        stelle = f"{ort} {kennzahl.get('id') or '#' + str(nummer)}"
        for feld in ("name", "ziel", "quelle"):
            if not kennzahl.get(feld):
                befunde.append(Befund("warnung", stelle, f"Kennzahl ohne {feld}"))
    return befunde


def _eskalation_pruefen(welt: Welt, standard: Standard, ort: str) -> list:
    befunde = []
    stufen = standard.kopf.get("eskalation") or []
    if not stufen and standard.kopf.get("status") == "gueltig":
        befunde.append(Befund("warnung", ort, "kein Eskalationsweg definiert"))
    letzte = 0
    for eintrag in stufen:
        stufe = eintrag.get("stufe")
        if not isinstance(stufe, int) or stufe <= letzte:
            befunde.append(Befund("warnung", ort, f"Eskalationsstufen nicht aufsteigend bei {stufe!r}"))
        else:
            letzte = stufe
        empfaenger = eintrag.get("an")
        if empfaenger not in welt.rollen:
            befunde.append(Befund("fehler", ort, f"Eskalation an unbekannte Rolle {empfaenger}"))
        if not eintrag.get("wann"):
            befunde.append(Befund("warnung", ort, f"Eskalationsstufe {stufe} ohne Auslöser"))
    return befunde


def _reife_pruefen(welt: Welt, standard: Standard, ort: str) -> list:
    befunde = []
    kopf = standard.kopf
    status = kopf.get("status")

    if status == "gueltig" and not kopf.get("rechtsstand_geprueft"):
        befunde.append(Befund("warnung", ort,
                              "gültig, aber Rechtsstand nicht durch SST-REW bestätigt"))

    gueltig_ab = datum(kopf.get("gueltig_ab"))
    if status == "gueltig" and gueltig_ab and gueltig_ab > welt.heute:
        befunde.append(Befund("hinweis", ort,
                              f"Status gültig, wirksam erst ab {gueltig_ab.isoformat()}"))

    resttage = standard.resttage(welt.heute)
    if resttage is not None:
        if resttage < 0:
            befunde.append(Befund("warnung", ort,
                                  f"Review seit {abs(resttage)} Tagen überfällig "
                                  f"(fällig war {standard.naechster_review().isoformat()})"))
        elif resttage <= 90:
            befunde.append(Befund("hinweis", ort,
                                  f"Review in {resttage} Tagen fällig "
                                  f"({standard.naechster_review().isoformat()})"))
    return befunde


def _abdeckung_pruefen(welt: Welt) -> list:
    befunde = []
    belegte_themenfelder = {s.kopf.get("themenfeld") for s in welt.standards}
    for tf_id, themenfeld in welt.themenfelder.items():
        if tf_id not in belegte_themenfelder:
            schwere = "warnung" if themenfeld.get("kritikalitaet") == "hoch" else "hinweis"
            befunde.append(Befund(schwere, tf_id,
                                  f"Themenfeld ohne Standard: {themenfeld['name']}"))

    gedeckt = set()
    for standard in welt.standards:
        gedeckt.update(standard.kopf.get("pflichten") or [])
    for pfl_id, pflicht in welt.pflichten.items():
        if pfl_id not in gedeckt:
            befunde.append(Befund("warnung", pfl_id,
                                  f"Pflicht ohne Standard: {pflicht['titel']}"))
        elif not pflicht.get("rechtsstand_geprueft"):
            befunde.append(Befund("hinweis", pfl_id, "Rechtsstand noch nicht bestätigt"))
    return befunde


# --- Auswertungen ---------------------------------------------------------


def aufgaben_der_rolle(welt: Welt, rollen_id: str) -> list:
    """Alle Aufgaben, an denen eine Rolle beteiligt ist, mit ihrer Beteiligungsart."""
    ergebnis = []
    for standard in welt.standards:
        if standard.kopf.get("status") in ("archiviert", "ausgesetzt"):
            continue
        for aufgabe in standard.aufgaben:
            if not isinstance(aufgabe, dict):
                continue
            arten = []
            if aufgabe.get("a") == rollen_id:
                arten.append("A")
            if rollen_id in (aufgabe.get("r") or []):
                arten.append("R")
            if rollen_id in (aufgabe.get("c") or []):
                arten.append("C")
            if rollen_id in (aufgabe.get("i") or []):
                arten.append("I")
            if arten:
                ergebnis.append((standard, aufgabe, "".join(arten)))
    ergebnis.sort(key=lambda e: (TAKT_REIHENFOLGE.get(e[1].get("takt"), 99), e[0].id))
    return ergebnis


def faellige_standards(welt: Welt, tage: int) -> list:
    ergebnis = []
    for standard in welt.standards:
        if standard.kopf.get("status") == "archiviert":
            continue
        resttage = standard.resttage(welt.heute)
        if resttage is not None and resttage <= tage:
            ergebnis.append((standard, resttage))
    ergebnis.sort(key=lambda e: e[1])
    return ergebnis


def luecken(welt: Welt) -> dict:
    belegte = {s.kopf.get("themenfeld") for s in welt.standards}
    gedeckt = set()
    for standard in welt.standards:
        gedeckt.update(standard.kopf.get("pflichten") or [])
    return {
        "themenfelder": [tf for tf_id, tf in welt.themenfelder.items() if tf_id not in belegte],
        "pflichten": [p for pfl_id, p in welt.pflichten.items() if pfl_id not in gedeckt],
        "ungeprueft": [s for s in welt.standards
                       if s.kopf.get("status") == "gueltig"
                       and not s.kopf.get("rechtsstand_geprueft")],
    }


def kennzahlen_der_lage(welt: Welt) -> dict:
    nach_status = {wert: 0 for wert in STATUS_WERTE}
    for standard in welt.standards:
        status = standard.kopf.get("status")
        if status in nach_status:
            nach_status[status] += 1
    offene = luecken(welt)
    aufgaben = sum(len(s.aufgaben) for s in welt.standards)
    gedeckte_pflichten = len(welt.pflichten) - len(offene["pflichten"])
    return {
        "standards": len(welt.standards),
        "nach_status": nach_status,
        "aufgaben": aufgaben,
        "themenfelder": len(welt.themenfelder),
        "themenfelder_ohne_standard": len(offene["themenfelder"]),
        "pflichten": len(welt.pflichten),
        "pflichten_gedeckt": gedeckte_pflichten,
        "pflichten_quote": round(100 * gedeckte_pflichten / max(len(welt.pflichten), 1)),
        "review_ueberfaellig": len([s for s, t in faellige_standards(welt, 0)]),
        "review_bald": len([s for s, t in faellige_standards(welt, 90) if t >= 0]),
        "rechtsstand_offen": len(offene["ungeprueft"]),
        "mitarbeitende": sum(b.get("mitarbeitende", 0) for b in welt.betriebsbereiche.values()),
    }


# --- Befehle --------------------------------------------------------------


def befehl_pruefen(welt: Welt, args) -> int:
    befunde = pruefen(welt)
    fehler = [b for b in befunde if b.schwere == "fehler"]
    warnungen = [b for b in befunde if b.schwere == "warnung"]
    hinweise = [b for b in befunde if b.schwere == "hinweis"]

    for befund in befunde:
        if args.nur_fehler and befund.schwere != "fehler":
            continue
        print(befund)

    print()
    print(f"{len(welt.standards)} Standards geprüft: "
          f"{len(fehler)} Fehler, {len(warnungen)} Warnungen, {len(hinweise)} Hinweise")
    return 1 if fehler else 0


def befehl_status(welt: Welt, args) -> int:
    lage = kennzahlen_der_lage(welt)
    befunde = pruefen(welt)
    fehler = len([b for b in befunde if b.schwere == "fehler"])

    print(f"Lage der Produktionssteuerung, Stand {welt.heute.isoformat()}")
    print("=" * 64)
    print(f"Betriebsbereiche      {len(welt.betriebsbereiche)} mit {lage['mitarbeitende']} Mitarbeitenden")
    print(f"Themenfelder          {lage['themenfelder']}, davon {lage['themenfelder_ohne_standard']} ohne Standard")
    print(f"Standards             {lage['standards']} mit {lage['aufgaben']} Aufgaben")
    for status, anzahl in lage["nach_status"].items():
        if anzahl:
            print(f"                      {anzahl}x {status}")
    print(f"Betreiberpflichten    {lage['pflichten_gedeckt']} von {lage['pflichten']} durch einen Standard gedeckt ({lage['pflichten_quote']}%)")
    print(f"Reviews               {lage['review_ueberfaellig']} überfällig, {lage['review_bald']} in den nächsten 90 Tagen")
    print(f"Rechtsstand           {lage['rechtsstand_offen']} gültige Standards ohne Bestätigung durch SST-REW")
    print(f"Prüfung               {fehler} Fehler im Regelwerk")

    faellig = faellige_standards(welt, 90)
    if faellig:
        print()
        print("Nächste Termine:")
        for standard, resttage in faellig:
            zustand = f"überfällig seit {abs(resttage)} Tagen" if resttage < 0 else f"in {resttage} Tagen"
            print(f"  {standard.id:<14} {standard.kopf.get('titel', '')[:44]:<46} {zustand}")
    return 0


def befehl_faellig(welt: Welt, args) -> int:
    faellig = faellige_standards(welt, args.tage)
    if not faellig:
        print(f"Kein Review in den nächsten {args.tage} Tagen fällig.")
        return 0
    print(f"Reviews bis {monate_addieren(welt.heute, 0) + dt.timedelta(days=args.tage)}:")
    print()
    for standard, resttage in faellig:
        zustand = f"überfällig ({abs(resttage)} Tage)" if resttage < 0 else f"in {resttage} Tagen"
        print(f"{standard.id:<14} {standard.naechster_review().isoformat()}  {zustand:<26} "
              f"{standard.kopf.get('owner')}  {standard.kopf.get('titel', '')}")
    return 0


def befehl_rollenblatt(welt: Welt, args) -> int:
    rollen_id = args.rolle
    if rollen_id not in welt.rollen:
        print(f"Unbekannte Rolle {rollen_id}. Bekannt sind:", file=sys.stderr)
        for kennung, rolle in welt.rollen.items():
            print(f"  {kennung:<12} {rolle['name']}", file=sys.stderr)
        return 1

    rolle = welt.rollen[rollen_id]
    beteiligungen = aufgaben_der_rolle(welt, rollen_id)
    zeilen = [
        f"# Rollenblatt {rollen_id} - {rolle['name']}",
        "",
        f"Stand {welt.heute.isoformat()}. Erzeugt aus dem Regelwerk, nicht von Hand gepflegt.",
        "",
        f"Beteiligung an {len(beteiligungen)} Aufgaben aus "
        f"{len({b[0].id for b in beteiligungen})} Standards.",
        "",
        "A = verantwortet das Ergebnis, R = führt aus, C = wird beteiligt, I = wird informiert",
        "",
        "| Rolle | Aufgabe | Takt | Frist | Nachweis | Standard |",
        "|---|---|---|---|---|---|",
    ]
    for standard, aufgabe, art in beteiligungen:
        zeilen.append(
            f"| **{art}** | {aufgabe.get('was', '')} | "
            f"{TAKT_ANZEIGE.get(aufgabe.get('takt'), aufgabe.get('takt', ''))} | "
            f"{aufgabe.get('frist', '')} | {aufgabe.get('nachweis', '')} | "
            f"{standard.id} |"
        )
    ausgabe = "\n".join(zeilen) + "\n"

    if args.ausgabe:
        ziel = Path(args.ausgabe)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(ausgabe, encoding="utf-8")
        print(f"Rollenblatt geschrieben: {ziel}")
    else:
        print(ausgabe)
    return 0


def befehl_luecken(welt: Welt, args) -> int:
    offene = luecken(welt)
    print("Themenfelder ohne Standard")
    print("-" * 64)
    for themenfeld in offene["themenfelder"] or []:
        print(f"  {themenfeld['id']:<10} {themenfeld['name']:<44} Kritikalität {themenfeld.get('kritikalitaet')}")
    if not offene["themenfelder"]:
        print("  keine")

    print()
    print("Betreiberpflichten ohne Standard")
    print("-" * 64)
    for pflicht in offene["pflichten"] or []:
        print(f"  {pflicht['id']:<10} {pflicht['titel'][:50]:<52} {pflicht.get('themenfeld')}")
    if not offene["pflichten"]:
        print("  keine")

    print()
    print("Gültige Standards ohne bestätigten Rechtsstand")
    print("-" * 64)
    for standard in offene["ungeprueft"] or []:
        print(f"  {standard.id:<14} {standard.kopf.get('titel', '')}")
    if not offene["ungeprueft"]:
        print("  keine")
    return 0


def befehl_neu(welt: Welt, args) -> int:
    themenfeld = args.themenfeld
    if themenfeld not in welt.themenfelder:
        print(f"Unbekanntes Themenfeld {themenfeld}. Bekannt sind:", file=sys.stderr)
        for kennung, eintrag in welt.themenfelder.items():
            print(f"  {kennung:<10} {eintrag['name']}", file=sys.stderr)
        return 1

    kuerzel = themenfeld.split("-")[1]
    vorhandene = [s.id for s in welt.standards if s.id.startswith(f"STD-{kuerzel}-")]
    naechste = max([int(s.split("-")[2]) for s in vorhandene], default=0) + 1
    neue_id = f"STD-{kuerzel}-{naechste:03d}"

    ordner = STANDARDS / _ordnername(welt.themenfelder[themenfeld]["name"])
    ziel = ordner / f"{neue_id}-{_dateiname(args.titel)}.md"
    if ziel.exists():
        print(f"Datei existiert bereits: {ziel}", file=sys.stderr)
        return 1

    vorlage = VORLAGE.read_text(encoding="utf-8")
    inhalt = (vorlage
              .replace("STD-XXX-000", neue_id)
              .replace("id: STD-XXX-000", f"id: {neue_id}")
              .replace("titel: Kurzer, aktiver Titel", f"titel: {args.titel}")
              .replace("themenfeld: TF-XXX", f"themenfeld: {themenfeld}")
              .replace("KPI-XXX-01", f"KPI-{kuerzel}-01")
              .replace("gueltig_ab: 2026-01-01", f"gueltig_ab: {welt.heute.isoformat()}")
              .replace("letzter_review: 2026-01-01", f"letzter_review: {welt.heute.isoformat()}")
              .replace("| 0.1.0 | 2026-01-01 |", f"| 0.1.0 | {welt.heute.isoformat()} |")
              .replace("# {{titel}}", f"# {args.titel}"))
    if "owner" in welt.themenfelder[themenfeld]:
        inhalt = inhalt.replace("owner: PS-TFV", f"owner: {welt.themenfelder[themenfeld]['owner']}")

    ordner.mkdir(parents=True, exist_ok=True)
    ziel.write_text(inhalt, encoding="utf-8")
    print(f"Neuer Standard angelegt: {ziel.relative_to(WURZEL)}")
    print(f"ID {neue_id}, Themenfeld {themenfeld}, Status entwurf")
    print()
    print("Nächste Schritte:")
    print("  1. Aufgaben mit Takt, Frist, Nachweis und genau einem A je Aufgabe füllen")
    print("  2. Pflichten aus daten/pflichtenregister.yaml verknüpfen")
    print("  3. python3 werkzeuge/ps.py pruefen")
    return 0


def befehl_cockpit(welt: Welt, args) -> int:
    import cockpit
    ziel = Path(args.ausgabe) if args.ausgabe else WURZEL / "cockpit" / "index.html"
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(cockpit.bauen(welt, pruefen(welt)), encoding="utf-8")
    print(f"Cockpit gebaut: {ziel.relative_to(WURZEL) if ziel.is_relative_to(WURZEL) else ziel}")
    return 0


def befehl_selbsttest(welt: Welt, args) -> int:
    """Prüft, dass der Rückfallleser dasselbe liefert wie PyYAML."""
    try:
        import yaml
    except ImportError:
        print("PyYAML nicht installiert - Vergleich nicht möglich, "
              "der Rückfallleser ist ohnehin aktiv.")
        return 0

    dateien = sorted(DATEN.rglob("*.yaml"))
    abweichungen = 0
    for pfad in dateien:
        text = pfad.read_text(encoding="utf-8")
        erwartet = _datumsangaben_vereinheitlichen(yaml.safe_load(text))
        try:
            tatsaechlich = miniyaml.laden(text)
        except miniyaml.MiniYamlFehler as fehler:
            print(f"FEHLER  {pfad.name}: {fehler}")
            abweichungen += 1
            continue
        if erwartet != tatsaechlich:
            print(f"ABWEICHUNG  {pfad.name}")
            abweichungen += 1
        else:
            print(f"ok          {pfad.name}")

    for pfad in sorted(STANDARDS.rglob("*.md")):
        text = pfad.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        kopf_text = text.split("\n---", 2)[0][3:]
        erwartet = _datumsangaben_vereinheitlichen(yaml.safe_load(kopf_text))
        try:
            tatsaechlich = miniyaml.laden(kopf_text)
        except miniyaml.MiniYamlFehler as fehler:
            print(f"FEHLER  {pfad.name}: {fehler}")
            abweichungen += 1
            continue
        if erwartet != tatsaechlich:
            print(f"ABWEICHUNG  {pfad.name}")
            abweichungen += 1
        else:
            print(f"ok          {pfad.name}")

    print()
    print("Selbsttest bestanden." if not abweichungen
          else f"{abweichungen} Abweichungen - PyYAML installieren oder miniyaml.py erweitern.")
    return 1 if abweichungen else 0


def _ordnername(name: str) -> str:
    return _dateiname(name)


def _dateiname(text: str) -> str:
    ersetzungen = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
                   "Ä": "ae", "Ö": "oe", "Ü": "ue"}
    for alt, neu in ersetzungen.items():
        text = text.replace(alt, neu)
    text = re.sub(r"[^A-Za-z0-9]+", "-", text.lower()).strip("-")
    return text[:60]


def main(argv=None) -> int:
    zerleger = argparse.ArgumentParser(
        prog="ps.py", description="Regelwerk der Produktionssteuerung pruefen und auswerten")
    zerleger.add_argument("--heute", help="Stichtag im Format JJJJ-MM-TT, sonst heute")
    unterbefehle = zerleger.add_subparsers(dest="befehl", required=True)

    b = unterbefehle.add_parser("pruefen", help="Regelwerk gegen die Regeln prüfen")
    b.add_argument("--nur-fehler", action="store_true", dest="nur_fehler")
    b.set_defaults(funktion=befehl_pruefen)

    b = unterbefehle.add_parser("status", help="Kurzlage ausgeben")
    b.set_defaults(funktion=befehl_status)

    b = unterbefehle.add_parser("faellig", help="anstehende Reviews")
    b.add_argument("--tage", type=int, default=90)
    b.set_defaults(funktion=befehl_faellig)

    b = unterbefehle.add_parser("rollenblatt", help="Wer-macht-was-wann für eine Rolle")
    b.add_argument("rolle")
    b.add_argument("--ausgabe", help="Zieldatei, sonst Ausgabe auf der Konsole")
    b.set_defaults(funktion=befehl_rollenblatt)

    b = unterbefehle.add_parser("luecken", help="ungedeckte Pflichten und Themenfelder")
    b.set_defaults(funktion=befehl_luecken)

    b = unterbefehle.add_parser("neu", help="neuen Standard aus der Vorlage anlegen")
    b.add_argument("themenfeld")
    b.add_argument("titel")
    b.set_defaults(funktion=befehl_neu)

    b = unterbefehle.add_parser("cockpit", help="cockpit/index.html bauen")
    b.add_argument("--ausgabe")
    b.set_defaults(funktion=befehl_cockpit)

    b = unterbefehle.add_parser("selbsttest", help="YAML-Rückfallleser gegen PyYAML prüfen")
    b.set_defaults(funktion=befehl_selbsttest)

    args = zerleger.parse_args(argv)
    stichtag = datum(args.heute) if args.heute else None
    if args.heute and stichtag is None:
        print(f"--heute: {args.heute!r} ist kein Datum im Format JJJJ-MM-TT", file=sys.stderr)
        return 2
    return args.funktion(welt_laden(stichtag), args)


if __name__ == "__main__":
    raise SystemExit(main())
