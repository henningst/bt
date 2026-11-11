# Blåtur 2026

Avsløringssiden for blåturen, publisert med GitHub Pages.

## Slik henger det sammen

| Fil | Hva |
|---|---|
| `index.html` | Den ferdige siden. Bygges automatisk – ikke rediger den direkte. |
| `src/shell.html` | Malen: stil, avgangstavle, animasjoner og prank-en. |
| `src/content.html` | Program, info om byen, karusell og kart. `<!--WEATHER-->` byttes ut med været. |
| `src/board.json` | Det som står på tavla etter prank-en. |
| `src/weather.json` | Værdata. Oppdateres automatisk. |
| `scripts/build.py` | Bygger `index.html` fra `src/`. |
| `scripts/update_weather.py` | Henter vær fra MET Norway (samme data som Yr). |

Innholdet kodes i base64 i `index.html`, så reisemålet ikke står i klartekst i kildekoden.

## Oppdatere innhold

1. Endre filer i `src/`.
2. Kjør `python3 scripts/build.py`.
3. Commit og push. GitHub Pages publiserer innen et minutt eller to.

## Værmeldingen

Workflowen **Oppdater værmelding** kjører hver tredje time fra 11. til 15. november, henter nytt varsel,
bygger siden og pusher. Den kan også startes manuelt under *Actions → Oppdater værmelding → Run workflow*.
