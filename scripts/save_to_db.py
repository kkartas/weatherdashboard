import pyodbc
from data.fetch_weather import fetch_weather_data

def save_to_sql_server(data):
    connection_string = 'DRIVER={SQL Server};SERVER=your_server;DATABASE=your_db;UID=your_user;PWD=your_password'
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO WeatherData (temperature, humidity, wind_speed, ...) 
    VALUES (?, ?, ?, ...)
    """
    for entry in data:
        cursor.execute(insert_query, entry['temperature'], entry['humidity'], entry['wind_speed'], ...)
    
    conn.commit()
    cursor.close()
    conn.close()

# Example usage
api_url = 'https://api.ecowitt.net/v3/weather_data'
api_key = 'your_api_key_here'
weather_data = fetch_weather_data(api_url, api_key)
save_to_sql_server(weather_data)
