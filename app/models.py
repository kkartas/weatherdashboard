import pyodbc
import pandas as pd
from flask import current_app

def get_db_connection():
    connection_string = current_app.config['SQLALCHEMY_DATABASE_URI']
    return pyodbc.connect(connection_string)

def fetch_data_from_db():
    conn = get_db_connection()
    query = "SELECT * FROM WeatherData"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def save_credentials_to_db(api_key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("IF NOT EXISTS (SELECT * FROM Credentials) BEGIN CREATE TABLE Credentials (api_key NVARCHAR(50)) END")
    cursor.execute("DELETE FROM Credentials")
    cursor.execute("INSERT INTO Credentials (api_key) VALUES (?)", api_key)
    conn.commit()
    cursor.close()
    conn.close()

def get_credentials():
    conn = get_db_connection()
    query = "SELECT api_key FROM Credentials"
    df = pd.read_sql(query, conn)
    conn.close()
    return df.iloc[0] if not df.empty else {}
