
SYMBOLS = {
    # Clear sky
    "clearsky_day": "☀️",
    "clearsky_night": "🌙",
    "clearsky_polartwilight": "🌙",

    # Fair (mostly clear)
    "fair_day": "🌤️",
    "fair_night": "🌙",
    "fair_polartwilight": "🌙",

    # Partly cloudy
    "partlycloudy_day": "⛅",
    "partlycloudy_night": "☁️",
    "partlycloudy_polartwilight": "☁️",

    # Cloudy
    "cloudy": "☁️",

    # Fog
    "fog": "🌫️",

    # Rain
    "rain": "🌧️",
    "lightrain": "🌦️",
    "heavyrain": "🌧️",

    # Rain showers
    "rainshowers_day": "🌦️",
    "rainshowers_night": "🌧️",
    "rainshowers_polartwilight": "🌧️",
    "lightrainshowers_day": "🌦️",
    "lightrainshowers_night": "🌧️",
    "lightrainshowers_polartwilight": "🌧️",
    "heavyrainshowers_day": "🌧️",
    "heavyrainshowers_night": "🌧️",
    "heavyrainshowers_polartwilight": "🌧️",

    # Rain and thunder
    "rainandthunder": "⛈️",
    "lightrainandthunder": "⛈️",
    "heavyrainandthunder": "⛈️",
    "rainshowersandthunder_day": "⛈️",
    "rainshowersandthunder_night": "⛈️",
    "rainshowersandthunder_polartwilight": "⛈️",
    "lightrainshowersandthunder_day": "⛈️",
    "lightrainshowersandthunder_night": "⛈️",
    "lightrainshowersandthunder_polartwilight": "⛈️",
    "heavyrainshowersandthunder_day": "⛈️",
    "heavyrainshowersandthunder_night": "⛈️",
    "heavyrainshowersandthunder_polartwilight": "⛈️",

    # Sleet
    "sleet": "🌨️",
    "lightsleet": "🌨️",
    "heavysleet": "🌨️",
    "sleetshowers_day": "🌨️",
    "sleetshowers_night": "🌨️",
    "sleetshowers_polartwilight": "🌨️",
    "lightsleetshowers_day": "🌨️",
    "lightsleetshowers_night": "🌨️",
    "lightsleetshowers_polartwilight": "🌨️",
    "heavysleetshowers_day": "🌨️",
    "heavysleetshowers_night": "🌨️",
    "heavysleetshowers_polartwilight": "🌨️",

    # Sleet and thunder
    "sleetandthunder": "⛈️",
    "lightsleetandthunder": "⛈️",
    "heavysleetandthunder": "⛈️",
    "sleetshowersandthunder_day": "⛈️",
    "sleetshowersandthunder_night": "⛈️",
    "sleetshowersandthunder_polartwilight": "⛈️",
    "lightssleetshowersandthunder_day": "⛈️",
    "lightssleetshowersandthunder_night": "⛈️",
    "lightssleetshowersandthunder_polartwilight": "⛈️",
    "heavysleetshowersandthunder_day": "⛈️",
    "heavysleetshowersandthunder_night": "⛈️",
    "heavysleetshowersandthunder_polartwilight": "⛈️",

    # Snow
    "snow": "❄️",
    "lightsnow": "🌨️",
    "heavysnow": "❄️",
    "snowshowers_day": "🌨️",
    "snowshowers_night": "🌨️",
    "snowshowers_polartwilight": "🌨️",
    "lightsnowshowers_day": "🌨️",
    "lightsnowshowers_night": "🌨️",
    "lightsnowshowers_polartwilight": "🌨️",
    "heavysnowshowers_day": "❄️",
    "heavysnowshowers_night": "❄️",
    "heavysnowshowers_polartwilight": "❄️",

    # Snow and thunder
    "snowandthunder": "⛈️",
    "lightsnowandthunder": "⛈️",
    "heavysnowandthunder": "⛈️",
    "snowshowersandthunder_day": "⛈️",
    "snowshowersandthunder_night": "⛈️",
    "snowshowersandthunder_polartwilight": "⛈️",
    "lightssnowshowersandthunder_day": "⛈️",
    "lightssnowshowersandthunder_night": "⛈️",
    "lightssnowshowersandthunder_polartwilight": "⛈️",
    "heavysnowshowersandthunder_day": "⛈️",
    "heavysnowshowersandthunder_night": "⛈️",
    "heavysnowshowersandthunder_polartwilight": "⛈️",
}


def get_weather_icon(symbol):

    response = SYMBOLS.get(symbol)

    if response is None:
        response = "?"
    return response