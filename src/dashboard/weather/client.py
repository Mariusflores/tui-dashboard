import httpx
from dashboard.weather.symbols import get_weather_icon


async def get_current_weather():
    URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=59.9139&lon=10.7522"
    HEADERS = {'User-Agent': 'tui-dashboard/0.1'}


    async with httpx.AsyncClient() as client:
        response = await client.get(URL, headers=HEADERS)
        response.raise_for_status
        data = response.json()
        now = data["properties"]["timeseries"][0]
        temp = now["data"]["instant"]["details"]["air_temperature"]
        symbol = now["data"]["next_1_hours"]["summary"]["symbol_code"]

    
    return format_response(symbol=symbol, weather_icon=get_weather_icon(symbol), temp=temp)

def format_response(symbol, weather_icon, temp):
    return [f"{str.capitalize(symbol)} {weather_icon}", f"{temp}°C"] 

