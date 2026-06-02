import httpx
from dashboard.weather.symbols import get_weather_icon

def fetch_data():
    URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=59.9139&lon=10.7522"
    HEADERS = {'User-Agent': 'tui-dashboard/0.1'}

    response = httpx.get(URL, headers=HEADERS)

    data = response.json()

    now = data["properties"]["timeseries"][0]
    temp = now["data"]["instant"]["details"]["air_temperature"]
    symbol = now["data"]["next_1_hours"]["summary"]["symbol_code"]

    
    return format_response(symbol=symbol, weather_icon=get_weather_icon(symbol), temp=temp)

def format_response(symbol, weather_icon, temp):

    capitalized_symbol = symbol[0].upper() + symbol[1:]
    
    return [f"{capitalized_symbol} {get_weather_icon(symbol)}", f"{temp}°C"] 

