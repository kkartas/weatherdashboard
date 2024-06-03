I apologize for that. Here is the correctly formatted `README.md`:

```markdown
# Weather Dashboard

Weather Dashboard is a Python-based web application that fetches real-time weather data from the Ecowitt API, stores it in an SQL Server database, and displays it using beautiful graphics in a web interface. The application also includes a settings page for users to input their Ecowitt API credentials.

## Features

- Fetches real-time weather data from Ecowitt API.
- Stores weather data in an SQL Server database.
- Displays weather data in a web interface with interactive charts.
- Includes a settings page for managing Ecowitt API credentials.
- Automatically fetches weather data every 5 minutes.

## Requirements

- Python 3.7+
- SQL Server
- Virtualenv
- Visual Studio Code (optional, but recommended)

## Installation

Follow these steps to set up and run the Weather Dashboard application on your local machine.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/weather-dashboard.git
cd weather-dashboard
```

### Step 2: Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory of the project and add the following environment variables:

```plaintext
SQL_SERVER=your_server
SQL_USER=your_user
SQL_PASSWORD=your_password
DATABASE_URL=DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server;DATABASE=WeatherDB;UID=your_user;PWD=your_password
API_KEY=your_api_key
APPLICATION_KEY=your_application_key
MAC=your_device_mac
```

### Step 5: Create the Database

Run the script to create the database and tables:

```bash
python scripts/create_db.py
```

### Step 6: Run the Application

```bash
python run.py
```

Open your web browser and navigate to `http://127.0.0.1:5000` to view the application.

## Usage

### Settings

- Navigate to `http://127.0.0.1:5000/settings` to enter and save your Ecowitt API credentials.

### Fetching Data

- The application automatically fetches weather data every 5 minutes.
- You can also manually fetch data by clicking the "Fetch Weather Data" button on the homepage.

### Viewing Data

- The homepage displays a line chart of the outdoor temperature over time.
- The last update timestamp is displayed below the chart.

## Project Structure

```
weather-dashboard/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── forms.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── settings.html
│   ├── static/
│   │   └── style.css
├── scripts/
│   └── create_db.py
├── .env
├── requirements.txt
├── run.py
└── README.md
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you would like to contribute to this project.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
```

This `README.md` file includes all the necessary information and is properly formatted for GitHub. You can now copy and paste it directly into your GitHub repository. Adjust the repository URL and other specific details as needed.