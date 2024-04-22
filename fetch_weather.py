import logging
import azure.functions as func
import requests
import pyodbc
from datetime import datetime, timezone
import os

def fetch_weather_data(application_key, api_key, mac_code):
    try:
        url = "https://api.ecowitt.net/api/v3/device/real_time"
        params = {
            'application_key': application_key,
            'api_key': api_key,
            'mac': mac_code,
            'call_back': 'all'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()  # Will raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP error occurred: {e}")
        return None

def convert_epoch_to_datetime(epoch_time):
    return datetime.fromtimestamp(int(epoch_time), tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')

def insert_data(conn, mac, data):
    cursor = conn.cursor()
    try:
        temp = data['data']['outdoor']['temperature']
        recorded_time = convert_epoch_to_datetime(temp['time'])
        cursor.execute("""
            INSERT INTO Temperature (DeviceMAC, RecordedTime, Value, Unit, Location)
            VALUES (?, ?, ?, ?, ?)
        """, (mac, recorded_time, temp['value'], temp['unit'], 'outdoor'))
        
        conn.commit()
        logging.info("Data inserted successfully.")
    except pyodbc.Error as e:
        logging.error(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        logging.error(f"An error occurred during data insertion: {e}")
        conn.rollback()

def main(mytimer: func.TimerRequest):
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', datetime.utcnow())

    conn_string = os.getenv('AZURE_SQL_CONNECTION_STRING')
    application_key = os.getenv('ECOWITT_APPLICATION_KEY')
    api_key = os.getenv('ECOWITT_API_KEY')
    mac_code = os.getenv('ECOWITT_MAC_CODE')

    try:
        conn = pyodbc.connect(conn_string)
        data = fetch_weather_data(application_key, api_key, mac_code)
        if data:
            insert_data(conn, mac_code, data)
        else:
            logging.info("No data to insert or fetch error occurred.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
