#!/usr/bin/env python3
"""Henter værmelding for Alicante fra MET Norway (samme data som Yr) og oppdaterer src/weather.json.

For hver turdag:
  - symbol: værsymbolet for perioden 12–18 UTC (13–19 norsk tid)
  - temp:   høyeste temperatur i perioden 12–18 UTC
  - max/min og nedbør for hele døgnet (lokal tid i Alicante, samme som norsk tid)
Dager som ikke lenger finnes i varselet (passerte dager) beholder verdiene sine.
Kan også kjøres med en lokal JSON-fil som argument (for testing).
"""
import datetime as dt
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEATHER = ROOT / "src" / "weather.json"
URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=38.3452&lon=-0.481"
UA = "blaatur2026-weather/1.0 github.com"
OFFSET = dt.timedelta(hours=1)  # CET i november
WEEKDAYS = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"]


def fetch(source=None):
    if source:
        return json.loads(pathlib.Path(source).read_text(encoding="utf-8"))
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def summarize(forecast, date):
    series = forecast["properties"]["timeseries"]
    temps_day, temps_mid, precip = [], [], 0.0
    sym = None
    for e in series:
        t = dt.datetime.fromisoformat(e["time"].replace("Z", "+00:00"))
        local = t + OFFSET
        details = e["data"]["instant"]["details"]
        if local.date() == date:
            temps_day.append(details["air_temperature"])
            n1 = e["data"].get("next_1_hours")
            if n1:
                precip += n1["details"].get("precipitation_amount", 0.0)
        if t.date() == date and 12 <= t.hour <= 18:
            temps_mid.append(details["air_temperature"])
        if t.date() == date and t.hour == 12:
            n6 = e["data"].get("next_6_hours") or e["data"].get("next_1_hours")
            if n6:
                sym = n6["summary"]["symbol_code"]
    # Krever timesdata for midt på dagen; ellers er dagen ikke dekket godt nok
    if not temps_mid or sym is None:
        return None
    return {
        "symbol": sym.split("_")[0],
        "temp": round(max(temps_mid)),
        "max": round(max(temps_day)),
        "min": round(min(temps_day)),
        "precip": round(precip, 1),
    }


def main():
    forecast = fetch(sys.argv[1] if len(sys.argv) > 1 else None)
    weather = json.loads(WEATHER.read_text(encoding="utf-8"))
    changed = 0
    for d in weather["days"]:
        s = summarize(forecast, dt.date.fromisoformat(d["date"]))
        if s:
            d.update(s)
            d.pop("desc", None)
            changed += 1
    if not changed:
        print("Ingen turdager i varselet – ingenting endret")
        return
    now = dt.datetime.now(dt.timezone.utc) + OFFSET
    weather["updated_text"] = f"sist oppdatert {WEEKDAYS[now.weekday()]} {now.day}. november kl. {now:%H.%M}"
    WEATHER.write_text(json.dumps(weather, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Oppdaterte {changed} dager")


if __name__ == "__main__":
    main()
