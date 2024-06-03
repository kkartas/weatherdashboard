import pyodbc
import pandas as pd

def fetch_data_from_db():
    connection_string = 'DRIVER={SQL Server};SERVER=your_server;DATABASE=your_db;UID=your_user;PWD=your_password'
    conn = pyodbc.connect(connection_string)
    query = "SELECT * FROM WeatherData"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
