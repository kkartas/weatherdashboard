import pyodbc
import pandas as pd
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_db_connection():
    connection_string = os.getenv('DATABASE_URL')
    if not connection_string:
        raise ValueError("No DATABASE_URL found in environment variables")
    return pyodbc.connect(connection_string)

def fetch_data_from_db():
    conn = get_db_connection()
    query = "SELECT * FROM WeatherData"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def save_weather_data(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO WeatherData (
        timestamp,
        outdoor_temperature,
        outdoor_feels_like,
        outdoor_app_temp,
        outdoor_dew_point,
        outdoor_humidity,
        indoor_temperature,
        indoor_humidity,
        solar_w_m2,
        uvi,
        rain_rate_in_hr,
        daily_rain_in,
        event_rain_in,
        hourly_rain_in,
        weekly_rain_in,
        monthly_rain_in,
        yearly_rain_in,
        wind_speed_mph,
        wind_gust_mph,
        wind_direction_deg,
        pressure_relative_inHg,
        pressure_absolute_inHg,
        lightning_distance_mi,
        lightning_count,
        co2_ppm,
        co2_24_hours_average_ppm,
        pm25_aqi,
        pm25_ug_m3,
        pm25_24_hours_aqi,
        battery
    ) VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_query, 
        data['outdoor_temperature'],
        data['outdoor_feels_like'],
        data['outdoor_app_temp'],
        data['outdoor_dew_point'],
        data['outdoor_humidity'],
        data['indoor_temperature'],
        data['indoor_humidity'],
        data['solar_w_m2'],
        data['uvi'],
        data['rain_rate_in_hr'],
        data['daily_rain_in'],
        data['event_rain_in'],
        data['hourly_rain_in'],
        data['weekly_rain_in'],
        data['monthly_rain_in'],
        data['yearly_rain_in'],
        data['wind_speed_mph'],
        data['wind_gust_mph'],
        data['wind_direction_deg'],
        data['pressure_relative_inHg'],
        data['pressure_absolute_inHg'],
        data['lightning_distance_mi'],
        data['lightning_count'],
        data['co2_ppm'],
        data['co2_24_hours_average_ppm'],
        data['pm25_aqi'],
        data['pm25_ug_m3'],
        data['pm25_24_hours_aqi'],
        data['battery']
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Data saved to database")  # Confirmation message

def fetch_weather_data():
    credentials = get_credentials()
    api_key = credentials['api_key']
    application_key = credentials['application_key']
    mac = credentials['mac']

    params = {
        'application_key': application_key,
        'api_key': api_key,
        'mac': mac,
        'call_back': 'all'
    }

    response = requests.get('https://api.ecowitt.net/api/v3/device/real_time', params=params)
    return response.json()

def fetch_and_save_weather_data():
    data = fetch_weather_data()
    if data['code'] == 0:
        weather_data = parse_weather_data(data['data'])
        print(weather_data)  # Print the parsed data for debugging
        save_weather_data(weather_data)
    else:
        print(f"Error fetching data: {data['msg']}")

def parse_weather_data(data):
    parsed_data = {
        'outdoor_temperature': data.get('outdoor', {}).get('temperature', {}).get('value'),
        'outdoor_feels_like': data.get('outdoor', {}).get('feels_like', {}).get('value'),
        'outdoor_app_temp': data.get('outdoor', {}).get('app_temp', {}).get('value'),
        'outdoor_dew_point': data.get('outdoor', {}).get('dew_point', {}).get('value'),
        'outdoor_humidity': data.get('outdoor', {}).get('humidity', {}).get('value'),
        'indoor_temperature': data.get('indoor', {}).get('temperature', {}).get('value'),
        'indoor_humidity': data.get('indoor', {}).get('humidity', {}).get('value'),
        'solar_w_m2': data.get('solar_and_uvi', {}).get('solar', {}).get('value'),
        'uvi': data.get('solar_and_uvi', {}).get('uvi', {}).get('value'),
        'rain_rate_in_hr': data.get('rainfall', {}).get('rain_rate', {}).get('value'),
        'daily_rain_in': data.get('rainfall', {}).get('daily', {}).get('value'),
        'event_rain_in': data.get('rainfall', {}).get('event', {}).get('value'),
        'hourly_rain_in': data.get('rainfall', {}).get('hourly', {}).get('value'),
        'weekly_rain_in': data.get('rainfall', {}).get('weekly', {}).get('value'),
        'monthly_rain_in': data.get('rainfall', {}).get('monthly', {}).get('value'),
        'yearly_rain_in': data.get('rainfall', {}).get('yearly', {}).get('value'),
        'wind_speed_mph': data.get('wind', {}).get('wind_speed', {}).get('value'),
        'wind_gust_mph': data.get('wind', {}).get('wind_gust', {}).get('value'),
        'wind_direction_deg': data.get('wind', {}).get('wind_direction', {}).get('value'),
        'pressure_relative_inHg': data.get('pressure', {}).get('relative', {}).get('value'),
        'pressure_absolute_inHg': data.get('pressure', {}).get('absolute', {}).get('value'),
        'lightning_distance_mi': data.get('lightning', {}).get('distance', {}).get('value'),
        'lightning_count': data.get('lightning', {}).get('count', {}).get('value'),
        'co2_ppm': data.get('indoor_co2', {}).get('co2', {}).get('value'),
        'co2_24_hours_average_ppm': data.get('indoor_co2', {}).get('24_hours_average', {}).get('value'),
        'pm25_aqi': data.get('pm25_ch1', {}).get('real_time_aqi', {}).get('value'),
        'pm25_ug_m3': data.get('pm25_ch1', {}).get('pm25', {}).get('value'),
        'pm25_24_hours_aqi': data.get('pm25_ch1', {}).get('24_hours_aqi', {}).get('value'),
        'battery': data.get('battery', {}).get('sensor_array', {}).get('value')
    }
    
    # Ensure all keys are present and set to None if they are not
    keys = [
        'outdoor_temperature', 'outdoor_feels_like', 'outdoor_app_temp', 'outdoor_dew_point', 
        'outdoor_humidity', 'indoor_temperature', 'indoor_humidity', 'solar_w_m2', 'uvi', 
        'rain_rate_in_hr', 'daily_rain_in', 'event_rain_in', 'hourly_rain_in', 'weekly_rain_in', 
        'monthly_rain_in', 'yearly_rain_in', 'wind_speed_mph', 'wind_gust_mph', 'wind_direction_deg', 
        'pressure_relative_inHg', 'pressure_absolute_inHg', 'lightning_distance_mi', 'lightning_count', 
        'co2_ppm', 'co2_24_hours_average_ppm', 'pm25_aqi', 'pm25_ug_m3', 'pm25_24_hours_aqi', 'battery'
    ]
    
    for key in keys:
        if key not in parsed_data:
            parsed_data[key] = None

    return parsed_data

def save_credentials_to_db(api_key, application_key, mac):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Credentials")
    cursor.execute("INSERT INTO Credentials (api_key, application_key, mac) VALUES (?, ?, ?)", api_key, application_key, mac)
    conn.commit()
    cursor.close()
    conn.close()

def get_credentials():
    conn = get_db_connection()
    query = "SELECT * FROM Credentials"
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0] if not df.empty else {}


def get_last_update_timestamp():
    conn = get_db_connection()
    query = "SELECT MAX(timestamp) as last_update FROM WeatherData"
    df = pd.read_sql(query, conn)
    conn.close()
    if not df.empty:
        return df.iloc[0]['last_update']
    return None
