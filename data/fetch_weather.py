import requests

def fetch_weather_data(api_url, api_key):
    params = {
        'api_key': api_key,
        'application': 'weather_app',
        'format': 'json'
    }
    response = requests.get(api_url, params=params)
    return response.json()
