import requests
import pyodbc
from datetime import datetime, timezone
import os
import logging

def get_weather_data(application_key, api_key, mac_code):
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
        wind_data = data['data']['wind']
        pressure_data = data['data']['pressure']

        # Insert Temperature data
        if 'temperature' in outdoor_data:
            cursor.execute("""
                INSERT INTO dbo.Temperature (DeviceMAC, RecordedTime, Value, Unit)
                VALUES (?, ?, ?, ?)
            """, (mac, recorded_time, outdoor_data['temperature']['value'], outdoor_data['temperature']['unit']))
        
        # Insert Humidity data
        if 'humidity' in outdoor_data:
            cursor.execute("""
                INSERT INTO dbo.Humidity (DeviceMAC, RecordedTime, Value, Unit)
                VALUES (?, ?, ?, ?)
            """, (mac, recorded_time, outdoor_data['humidity']['value'], outdoor_data['humidity']['unit']))
        
        # Insert Solar and UV Index data
        if 'solar' in solar_uv_data and 'uvi' in solar_uv_data:
            cursor.execute("""
                INSERT INTO dbo.SolarUVIndex (DeviceMAC, RecordedTime, SolarRadiation, UVIndex, SolarUnit, UVUnit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (mac, recorded_time, solar_uv_data['solar']['value'], solar_uv_data['uvi']['value'], solar_uv_data['solar']['unit'], solar_uv_data['uvi']['unit']))

        # Insert Rainfall data
        if 'rain_rate' in outdoor_data:
            rain_data = outdoor_data['rain_rate']
            cursor.execute("""
                INSERT INTO dbo.Rainfall (DeviceMAC, RecordedTime, RainRate, Daily, Weekly, Monthly, Yearly, Unit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (mac, recorded_time, rain_data['value'], rain_data['value'], rain_data['value'], rain_data['value'], rain_data['value'], rain_data['unit']))
        
        # Insert Wind data
        cursor.execute("""
            INSERT INTO dbo.Wind (DeviceMAC, RecordedTime, Speed, Gust, Direction, SpeedUnit)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            mac, 
            recorded_time, 
            wind_data['wind_speed']['value'], 
            wind_data['wind_gust']['value'], 
            wind_data['wind_direction']['value'], 
            wind_data['wind_speed']['unit']
        ))

        # Insert Pressure data
        cursor.execute("""
            INSERT INTO dbo.Pressure (DeviceMAC, RecordedTime, RelativePressure, AbsolutePressure, Unit)
            VALUES (?, ?, ?, ?, ?)
        """, (
            mac, 
            recorded_time, 
            pressure_data['relative']['value'], 
            pressure_data['absolute']['value'], 
            pressure_data['relative']['unit']
        ))

        # Insert Battery status
        if 'sensor_array' in solar_uv_data:
            battery_data = solar_uv_data['sensor_array']
            cursor.execute("""
                INSERT INTO dbo.Battery (DeviceMAC, RecordedTime, Status)
                VALUES (?, ?, ?)
            """, (mac, recorded_time, battery_data['value']))

        conn.commit()
        logging.info("Data inserted successfully.")
    except pyodbc.Error as db_err:
        logging.error(f"Database error: {db_err}")
        conn.rollback()
    except Exception as e:
        logging.error(f"General error during data insertion: {e}")
        conn.rollback()

def fetch_and_store_weather_data():
    """Fetch and store weather data into the database."""
    conn = None
    try:
        conn_string = os.getenv('SQL_CONNECTION_STRING')
        application_key = os.getenv('ECOWITT_APPLICATION_KEY')
        api_key = os.getenv('ECOWITT_API_KEY')
        mac_code = os.getenv('ECOWITT_MAC_CODE')

        if not all([conn_string, application_key, api_key, mac_code]):
            raise Exception("Missing one or more required environment variables.")
        
        conn = pyodbc.connect(conn_string)
        data = get_weather_data(application_key, api_key, mac_code)
        if data:
            insert_data(conn, mac_code, data)
        else:
            logging.error("No data to insert or fetch error occurred.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
