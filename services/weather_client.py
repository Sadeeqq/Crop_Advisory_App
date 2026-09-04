import requests
from utils.exceptions import WeatherAPIError

OPEN_METEO_URL = 'https://api.open-meteo.com/v1/forecast'

# Open-Meteo's weather_code field follows the WMO code table (WMO-No. 306, Table 4677).
# Confirmed against Open-Meteo's own documented weather_code mapping before use.
WMO_WEATHER_CODES = {
    0: 'Clear sky',
    1: 'Mainly clear',
    2: 'Partly cloudy',
    3: 'Overcast',
    45: 'Fog',
    48: 'Depositing rime fog',
    51: 'Light drizzle',
    53: 'Moderate drizzle',
    55: 'Dense drizzle',
    56: 'Light freezing drizzle',
    57: 'Dense freezing drizzle',
    61: 'Slight rain',
    63: 'Moderate rain',
    65: 'Heavy rain',
    66: 'Light freezing rain',
    67: 'Heavy freezing rain',
    71: 'Slight snow fall',
    73: 'Moderate snow fall',
    75: 'Heavy snow fall',
    77: 'Snow grains',
    80: 'Slight rain showers',
    81: 'Moderate rain showers',
    82: 'Violent rain showers',
    85: 'Slight snow showers',
    86: 'Heavy snow showers',
    95: 'Thunderstorm',
    96: 'Thunderstorm with slight hail',
    99: 'Thunderstorm with heavy hail',
}


def describe_weather_code(code):
    return WMO_WEATHER_CODES.get(code, 'Unknown conditions')


class WeatherClient:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def get_forecast(self):
        params = {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'current': 'temperature_2m,precipitation,relative_humidity_2m,weather_code',
            'hourly': 'temperature_2m,precipitation,precipitation_probability,soil_moisture_0_1cm,weather_code',
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code',
            'timezone': 'auto',
            'forecast_days': 16,
        }

        try:
            response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError('could not connect to the weather service, check your internet connection')
        except requests.exceptions.Timeout:
            raise WeatherAPIError('the weather service took too long to respond')
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f'weather request failed: {e}')

        if response.status_code != 200:
            raise WeatherAPIError(f'weather service returned an error (status {response.status_code})')

        try:
            data = response.json()
        except ValueError:
            raise WeatherAPIError('weather service returned an invalid response')

        if 'current' not in data or 'hourly' not in data:
            raise WeatherAPIError('weather service response is missing expected forecast data')

        return data

    def get_current_conditions(self, data=None):
        if data is None:
            data = self.get_forecast()

        current = data.get('current', {})

        if 'temperature_2m' not in current:
            raise WeatherAPIError('current temperature is not available in the weather response')

        return {
            'time': current.get('time'),
            'temperature': current.get('temperature_2m'),
            'precipitation': current.get('precipitation'),
            'humidity': current.get('relative_humidity_2m'),
            'condition': describe_weather_code(current.get('weather_code')),
        }

    def get_daily_forecast(self, data=None):
        if data is None:
            data = self.get_forecast()

        daily = data.get('daily', {})

        if 'time' not in daily:
            raise WeatherAPIError('daily forecast data is not available in the weather response')

        codes = daily.get('weather_code', [])

        return {
            'time': daily.get('time', []),
            'temp_max': daily.get('temperature_2m_max', []),
            'temp_min': daily.get('temperature_2m_min', []),
            'precipitation_sum': daily.get('precipitation_sum', []),
            'condition': [describe_weather_code(c) for c in codes],
        }
