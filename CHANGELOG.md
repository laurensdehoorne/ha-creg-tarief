# Changelog

## v0.2.0
- Icoon voor de sensor (`mdi:ev-station`) en eigen brand-icoon voor de integratie.
- Nieuw attribuut `volgend_tarief_vanaf`: datum waarop het volgende tarief ingaat.
- Kwartaalwissel exact om middernacht (Brussel).
- Laatst opgehaalde tabel wordt bewaard: bij een netwerkfout (ook na herstart) blijft het tarief beschikbaar. Enkel een onleesbare pagina maakt de sensor onbeschikbaar.
- Minder vaak ophalen: wekelijks als het volgende kwartaal al gepubliceerd is, anders dagelijks; na een netwerkfout na een uur.
- Compatibel met recente Home Assistant-versies (vereist nu minstens 2024.11).
- HACS: land `BE`, categorie `energy.energy_prices`.

## v0.1.0
- Eerste versie.
