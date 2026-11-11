#!/usr/bin/env python3
"""Bygger index.html fra src/.

src/shell.html   – sidens mal (stil, tavle, animasjoner). Inneholder __PAYLOAD__.
src/content.html – innholdet som vises etter avsløringen. <!--WEATHER--> byttes med værseksjonen.
src/board.json   – det som står på tavla (by, flyplasskode, status).
src/weather.json – værdata, oppdateres av scripts/update_weather.py.

Innholdet kodes i base64 så reisemålet ikke står i klartekst i kildekoden.
"""
import base64
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

SUN = ('<circle cx="22" cy="20" r="8" fill="var(--amber)"/><g stroke="var(--amber)" stroke-width="2.4" '
       'stroke-linecap="round"><path d="M22 4v4M22 32v4M6 20h4M34 20h4M10.7 8.7l2.8 2.8M30.5 28.5l2.8 2.8'
       'M10.7 31.3l2.8-2.8M30.5 11.5l2.8-2.8"/></g>')
CLOUD_S = '<path d="M28 40h16a7 7 0 0 0 0-14 10 10 0 0 0-19-2 7.5 7.5 0 0 0 3 16z" fill="var(--cloud)"/>'
CLOUD_L = '<path d="M18 42h24a9 9 0 0 0 0-18 13 13 0 0 0-25-2 10 10 0 0 0 1 20z" fill="var(--cloud)"/>'
DROPS = ('<g stroke="var(--sea)" stroke-width="2.6" stroke-linecap="round">'
         '<path d="M24 46l-2 5M32 46l-2 5M40 46l-2 5"/></g>')
BOLT = '<path d="M33 40l-6 9h5l-3 7 9-11h-5l3-5z" fill="var(--amber)"/>'

# Yr/MET-symbolkode (uten _day/_night) -> (norsk tekst, ikon)
SYMBOLS = {
    "clearsky": ("Klarvær", SUN),
    "fair": ("Lettskyet", SUN + CLOUD_S),
    "partlycloudy": ("Delvis skyet", SUN + CLOUD_L),
    "cloudy": ("Skyet", CLOUD_L),
    "fog": ("Tåke", CLOUD_L),
    "lightrainshowers": ("Lette regnbyger", SUN + CLOUD_L + DROPS),
    "rainshowers": ("Regnbyger", SUN + CLOUD_L + DROPS),
    "heavyrainshowers": ("Kraftige regnbyger", SUN + CLOUD_L + DROPS),
    "lightrain": ("Lett regn", CLOUD_L + DROPS),
    "rain": ("Regn", CLOUD_L + DROPS),
    "heavyrain": ("Kraftig regn", CLOUD_L + DROPS),
}
WEEKDAYS = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]


def symbol(code):
    code = code.split("_")[0]
    if code in SYMBOLS:
        return SYMBOLS[code]
    if "thunder" in code:
        return ("Torden", CLOUD_L + BOLT)
    if "rain" in code or "sleet" in code:
        return ("Regnbyger" if "showers" in code else "Regn", CLOUD_L + DROPS)
    return ("Skyet", CLOUD_L)


def num(x):
    return f"{x:g}".replace(".", ",")


def weather_section(w):
    import datetime as dt
    cards = []
    for d in w["days"]:
        day = dt.date.fromisoformat(d["date"])
        desc, icon = symbol(d["symbol"])
        cards.append(
            f'<div class="wx"><div class="wx-day"><b>{WEEKDAYS[day.weekday()]}</b>'
            f'<span>{day.day:02d}.{day.month:02d}</span></div>'
            f'<svg viewBox="0 0 56 56" aria-hidden="true">{icon}</svg>'
            f'<span class="wx-t">{round(d["temp"])}°</span><span class="wx-d">{desc}</span>'
            f'<span class="wx-m">Maks/min {round(d["max"])}° / {round(d["min"])}° · {num(round(d["precip"], 1))} mm</span></div>'
        )
    return (
        '<section class="weather"><p class="eyebrow">Midt på dagen, kl. 13–19</p><h2>Været</h2>'
        f'<div class="wxgrid">{"".join(cards)}</div>'
        '<p class="src">Kilde: <a href="https://www.yr.no/nb/v%C3%A6rvarsel/daglig-tabell/2-2521978/Spania/Valencia/Alicante/Alicante" '
        f'target="_blank" rel="noopener">Yr</a>, <span id="wx-updated">{w["updated_text"]}</span>. '
        'Oppdateres automatisk flere ganger om dagen.</p></section>'
    )


def build():
    shell = (SRC / "shell.html").read_text(encoding="utf-8")
    content = (SRC / "content.html").read_text(encoding="utf-8")
    board = json.loads((SRC / "board.json").read_text(encoding="utf-8"))
    weather = json.loads((SRC / "weather.json").read_text(encoding="utf-8"))

    html = content.replace("<!--WEATHER-->", weather_section(weather))
    payload = dict(board, html=html)
    encoded = base64.b64encode(json.dumps(payload, ensure_ascii=False).encode("utf-8")).decode("ascii")
    out = shell.replace("__PAYLOAD__", encoded)
    assert "ALICANTE" not in out, "Reisemålet står i klartekst"
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print("Bygget index.html")


if __name__ == "__main__":
    build()
