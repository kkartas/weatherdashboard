import logging
import azure.functions as func
import requests
import pyodbc
from datetime import datetime, timezone
import os

def fetch_weather_data(application_key, api_key, mac_code):
    """Fetch weather data from the Ecowitt API using provided credentials and device information."""
    try:
        url = "https://api.ecowitt.net/api/v3/device/real_time"
        params = {
            'application_key': application_key,
            'api_key': api_key,
            'mac': mac_code,
            'call_back': 'all'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()  # Will raise an HTTPError for bad HTTP responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP error occurred: {e}")
        return None

def convert_epoch_to_datetime(epoch_time):
    """Convert Unix epoch time to ISO 8601 datetime string."""
    return datetime.fromtimestamp(int(epoch_time), tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

def insert_data(conn, mac, data):
    """Insert weather data into the SQL database using the provided connection."""
    cursor = conn.cursor()
    try:
        # Parse and prepare data for insertion
        recorded_time = convert_epoch_to_datetime(data['time'])
        outdoor_data = data['data']['outdoor']
        solar_uv_data = data['data']['solar_and_uvi']
        
        # Insert Temperature, Humidity, and Apparent Temperature
        for key in ['temperature', 'humidity', 'app_temp']:
            if key in outdoor_data:
                cursor.execute("""
                    INSERT INTO WeatherData (DeviceMAC, RecordedTime, DataType, Value, Unit)
                    VALUES (?, ?, ?, ?, ?)
                """, (mac, recorded_time, key, outdoor_data[key]['value'], outdoor_data[key]['unit']))

        # Insert Solar and UV Index data
        for key in ['solar', 'uvi']:
            if key in solar_uv_data:
                cursor.execute("""
                    INSERT INTO WeatherData (DeviceMAC, RecordedTime, DataType, Value, Unit)
                    VALUES (?, ?, ?, ?, ?)
                """, (mac, recorded_time, key, solar_uv_data[key]['value'], solar_uv_data[key].get('unit', '')))

        # Insert Rainfall data
        rain_data = data['data']['rainfall']
        for key in ['rain_rate', 'daily', 'hourly', 'weekly', 'monthly', 'yearly']:
            if key in rain_data:
                cursor.execute("""
                    INSERT INTO WeatherData (DeviceMAC, RecordedTime, DataType, Value, Unit)
                    VALUES (?, ?, ?, ?, ?)
                """, (mac, recorded_time, key, rain_data[key]['value'], rain_data[key]['unit']))

        # Insert Wind data
        wind_data = data['data']['wind']
        cursor.execute("""
            INSERT INTO WeatherData (DeviceMAC, RecordedTime, DataType, Value, Value2, Unit)
            VALUES (?, ?, 'wind_speed', ?, ?, ?)
        """, (mac, recorded_time, wind_data['wind_speed']['value'], wind_data['wind_gust']['value'], wind_data['wind_speed']['unit']))

        # Insert Pressure data
        pressure_data = data['data']['pressure']
        cursor.execute("""
            INSERT INTO WeatherData (DeviceMAC, RecordedTime, DataType, Value, Value2, Unit)
            VALUES (?, ?, 'pressure', ?, ?, ?)
        """, (mac, recorded_time, pressure_data['relative']['value'], pressure_data['absolute']['value'], pressure_data['relative']['unit']))

        # Insert Battery status
        battery_data = data['data']['battery']
        cursor.execute("""
            INSERT INTO WeatherData (DeviceMAC, RecordedTime, DataType, Value)
            VALUES (?, ?, 'battery', ?)
        """, (mac, recorded_time, battery_data['sensor_array']['value']))

        conn.commit()
        logging.info("Data inserted successfully.")
    except pyodbc.Error as db_err:
        logging.error(f"Database error: {db_err}")
        conn.rollback()
    except Exception as e:
        logging.error(f"General error during data insertion: {e}")
        conn.rollback()

def main(mytimer: func.TimerRequest) -> None:
    """Main function to orchestrate the fetching and storing of weather data."""
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', datetime.utcnow())

    conn = None
    try:
        conn_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
        application_key = os.getenv('ECOWITT_APPLICATION_KEY')
        api_key = os.getenv('ECOWITT_API_KEY')
        mac_code = os.getenv('ECOWITT_MAC_CODE')

        if not all([conn_string, application_key, api_key, mac_code]):
            raise Exception("Missing one or more required environment variables.")
        
        conn = pyodbc.connect(conn_string)
        data = fetch_weather_data(application_key, api_key, mac_code)
        if data:
            insert_data(conn, mac_code, data)
        else:
            logging.error("No data to insert or fetch error occurred.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

