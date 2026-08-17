"""Minimaler YAML-Leser für den in diesem Repo verwendeten Sprachumfang.

Zweck: Das Cockpit und die Prüfung sollen auch auf Rechnern laufen, auf
denen kein "pip install pyyaml" möglich ist. Ist PyYAML vorhanden, wird es
bevorzugt - dieser Leser ist der Rückfallweg.

Unterstützt wird bewusst nur, was in daten/ und in den Standard-Kopfdaten
tatsächlich vorkommt:

  - Zuordnungen (key: wert) und verschachtelte Blöcke über Einrückung
  - Listen als Block (- eintrag) und inline ([a, b, c])
  - Listen von Zuordnungen (- key: wert, Folgezeilen eingerueckt)
  - Faltende Textblöcke (> und |)
  - Kommentare, Anführungszeichen, null/true/false, Zahlen, Datumsangaben

Nicht unterstützt: Anker, Aliase, Mehrfachdokumente, komplexe Schlüssel,
Tags. Wer so etwas braucht, installiert PyYAML - "ps.py selbsttest" prüft,
dass beide Leser auf den Dateien dieses Repos dasselbe Ergebnis liefern.
"""

from __future__ import annotations

import re

_DATUM = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_INT = re.compile(r"^-?\d+$")
_FLOAT = re.compile(r"^-?\d+\.\d+$")


class MiniYamlFehler(ValueError):
    """Wird geworfen, wenn eine Zeile nicht im unterstützten Umfang liegt."""


def laden(text: str):
    """Liest YAML-Text und gibt Zuordnungen, Listen und Skalare zurueck."""
    zeilen = _zeilen_aufbereiten(text)
    if not zeilen:
        return None
    wert, index = _block_lesen(zeilen, 0, zeilen[0][0])
    if index < len(zeilen):
        nr, inhalt = zeilen[index][2], zeilen[index][1]
        raise MiniYamlFehler(f"Zeile {nr}: unerwartete Einrückung bei {inhalt!r}")
    return wert


# --- Vorverarbeitung ------------------------------------------------------


def _zeilen_aufbereiten(text: str):
    """Wandelt Rohtext in (einrückung, inhalt, zeilennummer) ohne Leerzeilen."""
    ergebnis = []
    for nr, roh in enumerate(text.splitlines(), start=1):
        if "\t" in roh[: len(roh) - len(roh.lstrip())]:
            raise MiniYamlFehler(f"Zeile {nr}: Tabulator in der Einrückung")
        ohne_kommentar = _kommentar_entfernen(roh)
        if not ohne_kommentar.strip():
            continue
        einrueckung = len(ohne_kommentar) - len(ohne_kommentar.lstrip(" "))
        ergebnis.append((einrueckung, ohne_kommentar.strip(), nr))
    return ergebnis


def _kommentar_entfernen(zeile: str) -> str:
    """Entfernt Kommentare, lässt # innerhalb von Anführungszeichen stehen."""
    in_anfuehrung = None
    for pos, zeichen in enumerate(zeile):
        if in_anfuehrung:
            if zeichen == in_anfuehrung:
                in_anfuehrung = None
        elif zeichen in "\"'":
            in_anfuehrung = zeichen
        elif zeichen == "#" and (pos == 0 or zeile[pos - 1] in " \t"):
            return zeile[:pos]
    return zeile


# --- Blockleser -----------------------------------------------------------


def _block_lesen(zeilen, index: int, einrueckung: int):
    """Liest einen Block (Liste oder Zuordnung) auf der gegebenen Ebene."""
    if zeilen[index][1].startswith("- ") or zeilen[index][1] == "-":
        return _liste_lesen(zeilen, index, einrueckung)
    return _zuordnung_lesen(zeilen, index, einrueckung)


def _zuordnung_lesen(zeilen, index: int, einrueckung: int):
    ergebnis = {}
    while index < len(zeilen):
        ebene, inhalt, nr = zeilen[index]
        if ebene < einrueckung:
            break
        if ebene > einrueckung:
            raise MiniYamlFehler(f"Zeile {nr}: unerwartete Einrückung bei {inhalt!r}")
        if inhalt.startswith("- "):
            break
        schluessel, rest = _schluessel_trennen(inhalt, nr)
        if rest in (">", "|", ">-", "|-"):
            wert, index = _textblock_lesen(zeilen, index + 1, einrueckung, rest)
        elif rest == "":
            wert, index = _unterblock_lesen(zeilen, index + 1, einrueckung)
        else:
            wert, index = _skalar(rest), index + 1
        ergebnis[schluessel] = wert
    return ergebnis, index


def _liste_lesen(zeilen, index: int, einrueckung: int):
    ergebnis = []
    while index < len(zeilen):
        ebene, inhalt, nr = zeilen[index]
        if ebene < einrueckung or not (inhalt.startswith("- ") or inhalt == "-"):
            break
        if ebene > einrueckung:
            raise MiniYamlFehler(f"Zeile {nr}: unerwartete Einrückung bei {inhalt!r}")
        rest = inhalt[2:].strip() if inhalt != "-" else ""
        if rest == "":
            wert, index = _unterblock_lesen(zeilen, index + 1, einrueckung)
            ergebnis.append(wert)
            continue
        if _ist_zuordnungsanfang(rest):
            # Das Element ist eine Zuordnung: erste Zeile virtuell einrücken,
            # damit Folgezeilen desselben Elements dazugehören.
            innere_ebene = ebene + 2
            virtuell = [(innere_ebene, rest, nr)]
            index += 1
            while index < len(zeilen) and zeilen[index][0] >= innere_ebene:
                virtuell.append(zeilen[index])
                index += 1
            wert, _ = _zuordnung_lesen(virtuell, 0, innere_ebene)
            ergebnis.append(wert)
            continue
        ergebnis.append(_skalar(rest))
        index += 1
    return ergebnis, index


def _unterblock_lesen(zeilen, index: int, einrueckung: int):
    """Liest den Block, der zu einem Schlüssel ohne Inline-Wert gehört."""
    if index >= len(zeilen):
        return None, index
    ebene = zeilen[index][0]
    if ebene > einrueckung:
        return _block_lesen(zeilen, index, ebene)
    if ebene == einrueckung and zeilen[index][1].startswith("- "):
        # In YAML darf eine Liste auf derselben Ebene wie ihr Schlüssel stehen.
        return _liste_lesen(zeilen, index, ebene)
    return None, index


def _textblock_lesen(zeilen, index: int, einrueckung: int, art: str):
    teile = []
    while index < len(zeilen) and zeilen[index][0] > einrueckung:
        teile.append(zeilen[index][1])
        index += 1
    trenner = "\n" if art.startswith("|") else " "
    text = trenner.join(teile)
    if not art.endswith("-"):
        text += "\n"
    return text, index


def _ist_zuordnungsanfang(rest: str) -> bool:
    try:
        _schluessel_trennen(rest, 0)
    except MiniYamlFehler:
        return False
    return True


def _schluessel_trennen(inhalt: str, nr: int):
    """Zerlegt 'schluessel: wert' und beachtet Anführungszeichen."""
    in_anfuehrung = None
    for pos, zeichen in enumerate(inhalt):
        if in_anfuehrung:
            if zeichen == in_anfuehrung:
                in_anfuehrung = None
        elif zeichen in "\"'":
            in_anfuehrung = zeichen
        elif zeichen == ":" and (pos + 1 == len(inhalt) or inhalt[pos + 1] == " "):
            return inhalt[:pos].strip().strip("\"'"), inhalt[pos + 1 :].strip()
    raise MiniYamlFehler(f"Zeile {nr}: kein Schlüssel erkennbar in {inhalt!r}")


# --- Skalare --------------------------------------------------------------


def _skalar(roh: str):
    text = roh.strip()
    if text.startswith("[") and text.endswith("]"):
        inneres = text[1:-1].strip()
        if not inneres:
            return []
        return [_skalar(teil) for teil in _flach_trennen(inneres)]
    if text.startswith("{") and text.endswith("}"):
        inneres = text[1:-1].strip()
        if not inneres:
            return {}
        ergebnis = {}
        for teil in _flach_trennen(inneres):
            schluessel, wert = _schluessel_trennen(teil, 0)
            ergebnis[schluessel] = _skalar(wert)
        return ergebnis
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text in ("null", "~", ""):
        return None
    if text in ("true", "True", "yes"):
        return True
    if text in ("false", "False", "no"):
        return False
    if _INT.match(text):
        return int(text)
    if _FLOAT.match(text):
        return float(text)
    return text


def _flach_trennen(inneres: str):
    """Trennt an Kommas der obersten Ebene."""
    teile, aktuell, tiefe, in_anfuehrung = [], [], 0, None
    for zeichen in inneres:
        if in_anfuehrung:
            if zeichen == in_anfuehrung:
                in_anfuehrung = None
        elif zeichen in "\"'":
            in_anfuehrung = zeichen
        elif zeichen in "[{":
            tiefe += 1
        elif zeichen in "]}":
            tiefe -= 1
        elif zeichen == "," and tiefe == 0:
            teile.append("".join(aktuell).strip())
            aktuell = []
            continue
        aktuell.append(zeichen)
    if "".join(aktuell).strip():
        teile.append("".join(aktuell).strip())
    return teile
