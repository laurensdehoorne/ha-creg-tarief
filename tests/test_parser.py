import importlib.util
import sys
import types
from datetime import date
from pathlib import Path

import pytest

root = Path(__file__).parent.parent / "custom_components" / "creg_tarief"
pkg = types.ModuleType("ct")
pkg.__path__ = [str(root)]
sys.modules["ct"] = pkg
for n in ("const", "parser"):
    s = importlib.util.spec_from_file_location(f"ct.{n}", root / f"{n}.py")
    m = importlib.util.module_from_spec(s)
    sys.modules[f"ct.{n}"] = m
    s.loader.exec_module(m)
from ct.parser import ParseError, parse_page, select  # noqa: E402

HTML = (Path(__file__).parent / "fixtures" / "creg_pagina.html").read_text("utf-8")


def test_fixture_waarden_vlaanderen():
    t = parse_page(HTML, "vlaanderen")
    assert t[(2026, 4)] == 0.3225
    assert t[(2027, 1)] == 0.3616
    assert len(t) == 8


def test_andere_gewesten():
    assert parse_page(HTML, "brussel")[(2026, 4)] == 0.3688
    assert parse_page(HTML, "wallonie")[(2027, 1)] == 0.4188


def test_kwartaal_op_datum_niet_bovenste_rij():
    t = parse_page(HTML, "vlaanderen")
    s = select(t, date(2026, 11, 22))
    assert (s["kwartaal"], s["tarief"]) == ("Q4/2026", 0.3225)
    assert (s["volgend_kwartaal"], s["volgend_tarief"]) == ("Q1/2027", 0.3616)


def test_kwartaalgrenzen():
    t = parse_page(HTML, "vlaanderen")
    assert select(t, date(2026, 11, 22))["volgend_tarief_vanaf"] == date(2027, 1, 1)
    assert select(t, date(2026, 12, 31))["volgend_tarief_vanaf"] == date(2027, 1, 1)
    assert select(t, date(2026, 9, 30))["kwartaal"] == "Q3/2026"
    assert select(t, date(2026, 10, 1))["kwartaal"] == "Q4/2026"
    assert select(t, date(2026, 12, 31))["kwartaal"] == "Q4/2026"
    assert select(t, date(2027, 1, 1))["volgend_tarief"] is None


def test_huidig_kwartaal_ontbreekt():
    t = parse_page(HTML, "vlaanderen")
    with pytest.raises(ParseError):
        select(t, date(2027, 4, 1))


@pytest.mark.parametrize(
    "bad",
    [
        "<html></html>",
        HTML.replace("<th>Vlaanderen</th>", "<th>Flandre</th>"),
        HTML.replace("36,16", "n/a"),
        HTML.replace("36,16", "3616"),
        HTML.replace("36,16", "0,16"),
        HTML.replace("Q1/2027", "1e kwartaal"),
        HTML.replace("<td>41,36</td>", ""),
        HTML.replace("Q4/2026", "Q1/2027"),
    ],
)
def test_gewijzigde_pagina_geeft_duidelijke_fout(bad):
    with pytest.raises(ParseError):
        parse_page(bad, "vlaanderen")


def test_onbekend_gewest():
    with pytest.raises(ParseError):
        parse_page(HTML, "mars")
