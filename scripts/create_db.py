import pyodbc
from dotenv import load_dotenv
import os

def create_database():
    # Load environment variables
    load_dotenv()
    
    # Get the connection string from the environment variables
    server = os.getenv('SQL_SERVER')
    user = os.getenv('SQL_USER')
    password = os.getenv('SQL_PASSWORD')
    master_connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=master;UID={user};PWD={password}"
    weatherdb_connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=WeatherDB;UID={user};PWD={password}"

    # Connect to the master database to create the WeatherDB database if it doesn't exist
    try:
        with pyodbc.connect(master_connection_string, autocommit=True) as conn:
            cursor = conn.cursor()
            cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'WeatherDB') BEGIN CREATE DATABASE WeatherDB END")
            cursor.close()
            print("Database 'WeatherDB' created or already exists.")
    except pyodbc.Error as e:
        print("Error creating database:", e)
    
    # Connect to the WeatherDB database to create tables
    try:
        with pyodbc.connect(weatherdb_connection_string) as conn:
            cursor = conn.cursor()

            # Create the WeatherData table if it doesn't exist
            cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'WeatherData')
            BEGIN
                CREATE TABLE WeatherData (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    timestamp DATETIME DEFAULT GETDATE(),
                    outdoor_temperature FLOAT,
                    outdoor_feels_like FLOAT,
                    outdoor_app_temp FLOAT,
                    outdoor_dew_point FLOAT,
                    outdoor_humidity FLOAT,
                    indoor_temperature FLOAT,
                    indoor_humidity FLOAT,
                    solar_w_m2 FLOAT,
                    uvi FLOAT,
                    rain_rate_in_hr FLOAT,
                    daily_rain_in FLOAT,
                    event_rain_in FLOAT,
                    hourly_rain_in FLOAT,
                    weekly_rain_in FLOAT,
                    monthly_rain_in FLOAT,
                    yearly_rain_in FLOAT,
                    wind_speed_mph FLOAT,
                    wind_gust_mph FLOAT,
                    wind_direction_deg FLOAT,
                    pressure_relative_inHg FLOAT,
                    pressure_absolute_inHg FLOAT,
                    lightning_distance_mi FLOAT,
                    lightning_count INT,
                    co2_ppm FLOAT,
                    co2_24_hours_average_ppm FLOAT,
                    pm25_aqi FLOAT,
                    pm25_ug_m3 FLOAT,
                    pm25_24_hours_aqi FLOAT,
                    battery FLOAT
                )
            END
            """)
            
            # Create the Credentials table if it doesn't exist
            cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Credentials')
            BEGIN
                CREATE TABLE Credentials (
                    api_key NVARCHAR(50),
                    application_key NVARCHAR(50),
                    mac NVARCHAR(50)
                )
            END
            """)
            
            # Commit and close the connection
            conn.commit()
            cursor.close()
            print("Tables 'WeatherData' and 'Credentials' created or already exist.")
    except pyodbc.Error as e:
        print("Error creating tables:", e)

if __name__ == '__main__':
    create_database()
