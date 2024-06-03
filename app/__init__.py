from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.models import fetch_and_save_weather_data
from app.routes import main

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.register_blueprint(main)

    # Setup APScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=fetch_and_save_weather_data, trigger="interval", minutes=5)
    scheduler.start()

    return app
