# Changelog

## v0.2.3
- Home Assistant-conventies: `entry.runtime_data` i.p.v. `hass.data`, `_async_setup` in de coordinator, `PARALLEL_UPDATES`.
- Sensornaam, gewestlabels en attribuutnamen zitten nu in de vertalingen (nl/en) in plaats van in de code.

## v0.2.2
- Tijdzone Europe/Brussels wordt één keer bij het importeren opgebouwd (`const.BRUSSELS`) in plaats van in de event loop, zodat Home Assistant niet kan blokkeren op trage schijven.

## v0.2.1
- Engelse vertaling toegevoegd (`translations/en.json`), zodat de configuratie ook in andere talen dan Nederlands teksten toont.

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
