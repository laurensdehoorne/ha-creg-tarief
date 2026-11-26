"""Constanten voor CREG-tarief."""
from zoneinfo import ZoneInfo

DOMAIN = "creg_tarief"
SOURCE_URL = (
    "https://www.creg.be/nl/consumenten/prijzen-en-tarieven/"
    "creg-tarief-voor-terugbetaling-thuisladen-bedrijfswagens"
)
TIMEZONE = "Europe/Brussels"
# Eén keer bij het importeren opgebouwd (niet in de event loop).
BRUSSELS = ZoneInfo(TIMEZONE)

CONF_REGION = "region"
DEFAULT_REGION = "vlaanderen"
# gewest -> kolomkop in de tabel op de CREG-pagina
REGIONS = {"vlaanderen": "Vlaanderen", "brussel": "Brussel", "wallonie": "Wallonië"}
