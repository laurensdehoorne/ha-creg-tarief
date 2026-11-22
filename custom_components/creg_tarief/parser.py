"""Parsing van de CREG-pagina. Geen Home Assistant-imports, dus los testbaar.

Alles faalt luid (ParseError): liever een onbeschikbare sensor dan een fout getal.
"""
from __future__ import annotations

import re
from datetime import date
from html.parser import HTMLParser

from .const import REGIONS

EXPECTED_HEADER = ["Kwartaal", "Vlaanderen", "Brussel", "Wallonië"]
_QUARTER = re.compile(r"^Q([1-4])/(\d{4})$")
_VALUE = re.compile(r"^\d{1,3},\d{1,4}$")  # eurocent, decimale komma
MIN_CENT, MAX_CENT = 5.0, 150.0  # plausibiliteitsgrenzen in c€/kWh

Quarter = tuple[int, int]  # (jaar, kwartaal)


class ParseError(ValueError):
    """De pagina heeft niet de verwachte structuur."""


class _Tables(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append([])
        elif tag == "tr" and self.tables:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None and self.tables:
            self.tables[-1].append(self._row)
            self._row = None


def parse_page(html: str, region: str) -> dict[Quarter, float]:
    """Geef {(jaar, kwartaal): tarief in EUR/kWh} voor het gewest."""
    if region not in REGIONS:
        raise ParseError(f"Onbekend gewest: {region}")
    p = _Tables()
    p.feed(html)
    table = next((t for t in p.tables if t and t[0] == EXPECTED_HEADER), None)
    if table is None:
        raise ParseError(
            f"Geen tabel met kolommen {EXPECTED_HEADER} gevonden "
            f"(gevonden koppen: {[t[0] for t in p.tables if t]})"
        )
    col = EXPECTED_HEADER.index(REGIONS[region])
    result: dict[Quarter, float] = {}
    for row in table[1:]:
        if len(row) != len(EXPECTED_HEADER):
            raise ParseError(f"Rij met {len(row)} kolommen in plaats van 4: {row}")
        m = _QUARTER.match(row[0])
        if not m:
            raise ParseError(f"Ongeldig kwartaal: {row[0]!r}")
        if not _VALUE.match(row[col]):
            raise ParseError(f"Ongeldig tarief voor {row[0]}: {row[col]!r}")
        cent = float(row[col].replace(",", "."))
        if not MIN_CENT <= cent <= MAX_CENT:
            raise ParseError(f"Onwaarschijnlijk tarief voor {row[0]}: {cent} c/kWh")
        key = (int(m.group(2)), int(m.group(1)))
        if key in result:
            raise ParseError(f"Kwartaal {row[0]} komt dubbel voor")
        result[key] = round(cent / 100, 5)
    if not result:
        raise ParseError("Tabel bevat geen rijen")
    return result


def quarter_of(d: date) -> Quarter:
    return d.year, (d.month - 1) // 3 + 1


def next_quarter(q: Quarter) -> Quarter:
    return (q[0], q[1] + 1) if q[1] < 4 else (q[0] + 1, 1)


def quarter_start(q: Quarter) -> date:
    return date(q[0], (q[1] - 1) * 3 + 1, 1)


def label(q: Quarter) -> str:
    return f"Q{q[1]}/{q[0]}"


def select(table: dict[Quarter, float], today: date) -> dict:
    """Huidig en volgend kwartaal op basis van de datum (niet de bovenste rij).

    Ontbreekt het huidige kwartaal, dan ParseError: nooit een ander kwartaal tonen.
    """
    cur = quarter_of(today)
    if cur not in table:
        raise ParseError(f"Geen tarief voor huidig kwartaal {label(cur)}")
    nxt = next_quarter(cur)
    return {
        "kwartaal": label(cur),
        "tarief": table[cur],
        "volgend_kwartaal": label(nxt),
        "volgend_tarief": table.get(nxt),
        "volgend_tarief_vanaf": quarter_start(nxt),
    }
