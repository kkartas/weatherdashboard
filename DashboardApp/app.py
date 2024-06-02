from flask import Flask, render_template, jsonify
import pyodbc
import os
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from fetch_weather import fetch_and_store_weather_data

app = Flask(__name__)

def get_db_connection():
    """Get a database connection using environment variables."""
    conn = pyodbc.connect(os.getenv('SQL_CONNECTION_STRING'))
    return conn

@app.route('/')
def home():
    """Serve the main dashboard page."""
    return render_template('index.html')

@app.route('/api/weatherdata')
def get_weather_data():
    """API endpoint to fetch weather data from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT RecordedTime, DeviceMAC, Value, Unit FROM Temperature
        UNION ALL
        SELECT RecordedTime, DeviceMAC, Value, Unit FROM Humidity
        UNION ALL
        SELECT RecordedTime, DeviceMAC, SolarRadiation, UVIndex FROM SolarUVIndex
        UNION ALL
        SELECT RecordedTime, DeviceMAC, Speed, Gust FROM Wind
        UNION ALL
        SELECT RecordedTime, DeviceMAC, RelativePressure, AbsolutePressure FROM Pressure
        """)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    results = []
    for row in data:
        results.append(dict(zip(columns, row)))
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    # Set up the scheduler to fetch weather data every 60 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=fetch_and_store_weather_data, trigger="interval", minutes=60)
    scheduler.start()

    try:
        # Start the Flask web server
        app.run(debug=True)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
