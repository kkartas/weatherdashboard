import os
import requests

def fetch_weather_data(api_key):
    """Fetch weather data from the Ecowitt API using the provided API key."""
    url = "http://api.ecowitt.net"
    params = {
        'api_key': api_key,
        'data_type': 'all',  # Assuming 'all' fetches all available data types
        'location': 'your_location_here'  # Modify as needed or make it configurable
    }
    response = requests.get(url, params=params)
    return response.json()  # Convert response to JSON

def main():
    # Retrieve the API key from an environment variable
    api_key = os.getenv('ECOWITT_API_KEY')
    if not api_key:
        print("API key is not set. Please set the ECOWITT_API_KEY environment variable.")
        return
    
    # Fetch and print the weather data
    data = fetch_weather_data(api_key)
    print(data)

if __name__ == '__main__':
    main()
