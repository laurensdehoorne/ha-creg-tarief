# CREG-tarief thuisladen (Home Assistant)

Haalt het **CREG-tarief voor terugbetaling thuisladen van bedrijfswagens** op, per kwartaal, voor Vlaanderen, Brussel of Wallonië. De FOD Financiën gebruikt dit tarief (circulaire 2024/C/77) als maximaal vast bedrag per kWh.

Bron: [CREG – Tarief voor terugbetaling thuisladen bedrijfswagens](https://www.creg.be/nl/consumenten/prijzen-en-tarieven/creg-tarief-voor-terugbetaling-thuisladen-bedrijfswagens). De pagina bevat al het tarief van het volgende kwartaal vóór het ingaat.

## Installatie (HACS)
1. HACS → ⋮ → *Aangepaste repositories* → `https://github.com/laurensdehoorne/ha-creg-tarief`, categorie **Integratie**.
2. Installeer *CREG-tarief thuisladen* en herstart Home Assistant.
3. Instellingen → Apparaten & diensten → *Integratie toevoegen* → **CREG-tarief thuisladen** → kies het gewest (standaard Vlaanderen).

## Sensor
`sensor.creg_tarief_vlaanderen_creg_tarief` (naam hangt af van het gewest) — tarief van het **huidige kwartaal** in `EUR/kWh`. Het kwartaal wordt bepaald met de huidige datum in Europe/Brussels, niet met de bovenste rij van de tabel.

| Attribuut | Voorbeeld |
|---|---|
| `kwartaal` | `Q4/2026` |
| `volgend_kwartaal` | `Q1/2027` |
| `volgend_tarief` | `0.3616` (leeg als nog niet gepubliceerd) |
| `volgend_tarief_vanaf` | `2027-01-01` (ingangsdatum van het volgende tarief) |
| `bron_url` | link naar de CREG-pagina |
| `laatst_opgehaald` | ISO-tijdstip van de laatste geslaagde fetch |

De CREG publiceert het tarief van het volgende kwartaal weken op voorhand, dus de pagina wordt zuinig opgehaald:

- **wekelijks** als het tarief van het volgende kwartaal er al staat;
- **dagelijks** zolang het volgende kwartaal nog niet gepubliceerd is;
- **na een uur** opnieuw als de pagina niet bereikbaar was.

Bij de kwartaalwissel schakelt de sensor om middernacht (Brussel) naar het nieuwe tarief, zonder de pagina opnieuw op te halen.

De laatst opgehaalde tabel wordt bewaard (ook over een herstart heen). Is de CREG-pagina even niet bereikbaar, dan blijft de sensor die waarde tonen; `laatst_opgehaald` toont hoe oud ze is. De sensor wordt **niet beschikbaar** (nooit een fout getal) als de pagina wel bereikbaar is maar de tabel gewijzigd of onleesbaar is, of als het huidige kwartaal ontbreekt. De reden staat in het HA-log.

## Voorbeeld: laadkost van een sessie
```yaml
template:
  - sensor:
      - name: "Laadkost laatste sessie"
        unit_of_measurement: "EUR"
        device_class: monetary
        state: >
          {{ (states('sensor.laadpaal_sessie_energie') | float(0)
              * states('sensor.creg_tarief_vlaanderen_creg_tarief') | float(0)) | round(2) }}
```
(Pas de entiteitsnamen aan; controleer ze onder Ontwikkelaarstools → Toestanden.)

## Tests
```bash
pip install pytest && pytest -q tests
```
De tests draaien op een opgeslagen kopie van de CREG-pagina (`tests/fixtures/`). `CREG_Tariff_EV.csv` staat er ter referentie bij: dat zijn maandgemiddelden, niet de kwartaaltarieven, en wordt niet gebruikt.

*Niet-officiële integratie; geen product van de CREG.*
