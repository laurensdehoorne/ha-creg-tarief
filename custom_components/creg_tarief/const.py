"""Constanten voor CREG-tarief."""

DOMAIN = "creg_tarief"
SOURCE_URL = (
    "https://www.creg.be/nl/consumenten/prijzen-en-tarieven/"
    "creg-tarief-voor-terugbetaling-thuisladen-bedrijfswagens"
)
TIMEZONE = "Europe/Brussels"

CONF_REGION = "region"
DEFAULT_REGION = "vlaanderen"
# gewest -> kolomkop in de tabel op de CREG-pagina
REGIONS = {"vlaanderen": "Vlaanderen", "brussel": "Brussel", "wallonie": "Wallonië"}
