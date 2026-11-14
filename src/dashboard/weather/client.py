from typing import NamedTuple

import httpx

from dashboard.weather.symbols import get_weather_icon

API_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
HEADERS = {"User-Agent": "tui-dashboard/0.1"}


class WeatherDisplay(NamedTuple):
    symbol_line: str
    temperature_line: str


async def get_current_weather(lat: float, lon: float) -> WeatherDisplay:
    # met.no asks clients to use at most 4 decimals for coordinates.
    params = {"lat": f"{lat:.4f}", "lon": f"{lon:.4f}"}

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(API_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

    now = data["properties"]["timeseries"][0]["data"]
    temp = now["instant"]["details"]["air_temperature"]
    next_period = now.get("next_1_hours") or now.get("next_6_hours") or {}
    symbol = next_period.get("summary", {}).get("symbol_code", "unknown")

    return format_response(symbol=symbol, weather_icon=get_weather_icon(symbol), temp=temp)


def format_response(symbol, weather_icon, temp):
    result = " ".join(p.capitalize() for p in symbol.split("_"))
    return WeatherDisplay(f"{result} {weather_icon}", f"{temp}°C")
