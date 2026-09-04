import requests
from utils.exceptions import GeocodingError

GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search'


class GeocodingClient:
    def geocode(self, place_name, country_hint='Nigeria'):
        params = {
            'name': f'{place_name}, {country_hint}',
            'count': 5,
            'language': 'en',
            'format': 'json',
        }

        try:
            response = requests.get(GEOCODING_URL, params=params, timeout=10)
        except requests.exceptions.ConnectionError:
            raise GeocodingError('could not connect to the location service, check your internet connection')
        except requests.exceptions.Timeout:
            raise GeocodingError('the location service took too long to respond')
        except requests.exceptions.RequestException as e:
            raise GeocodingError(f'location request failed: {e}')

        if response.status_code != 200:
            raise GeocodingError(f'location service returned an error (status {response.status_code})')

        try:
            data = response.json()
        except ValueError:
            raise GeocodingError('location service returned an invalid response')

        results = data.get('results', [])
        if not results:
            raise GeocodingError(f'could not find coordinates for {place_name}, {country_hint}')

        # prefer a result actually in Nigeria if the search matched places elsewhere too
        nigeria_results = [r for r in results if r.get('country_code') == 'NG']
        best = nigeria_results[0] if nigeria_results else results[0]

        if 'latitude' not in best or 'longitude' not in best:
            raise GeocodingError('location service response is missing coordinates')

        return {
            'latitude': best['latitude'],
            'longitude': best['longitude'],
            'resolved_name': best.get('name'),
        }
