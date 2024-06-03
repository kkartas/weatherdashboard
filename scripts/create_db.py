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
        conn = pyodbc.connect(master_connection_string)
        cursor = conn.cursor()
        cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'WeatherDB') BEGIN EXEC('CREATE DATABASE WeatherDB') END")
        conn.commit()
        cursor.close()
        conn.close()
        print("Database 'WeatherDB' created or already exists.")
    except pyodbc.Error as e:
        print("Error creating database:", e)
    
    # Connect to the WeatherDB database to create tables
    try:
        conn = pyodbc.connect(weatherdb_connection_string)
        cursor = conn.cursor()

        # Create the WeatherData table if it doesn't exist
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'WeatherData')
        BEGIN
            CREATE TABLE WeatherData (
                id INT PRIMARY KEY IDENTITY(1,1),
                temperature FLOAT,
                humidity FLOAT,
                wind_speed FLOAT,
                timestamp DATETIME DEFAULT GETDATE()
            )
        END
        """)

        # Create the Credentials table if it doesn't exist
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Credentials')
        BEGIN
            CREATE TABLE Credentials (
                api_key NVARCHAR(50)
            )
        END
        """)
        
        # Commit and close the connection
        conn.commit()
        cursor.close()
        conn.close()
        print("Tables 'WeatherData' and 'Credentials' created or already exist.")
    except pyodbc.Error as e:
        print("Error creating tables:", e)

if __name__ == '__main__':
    create_database()
