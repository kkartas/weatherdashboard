from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import fetch_data_from_db, save_credentials_to_db, get_credentials, fetch_and_save_weather_data, get_last_update_timestamp
from app.forms import SettingsForm
import plotly.express as px

main = Blueprint('main', __name__)

@main.route('/')
def index():
    df = fetch_data_from_db()
    last_update = None
    try:
        last_update = get_last_update_timestamp()
    except Exception as e:
        print(f"Error fetching last update timestamp: {e}")
    
    fig = px.line(df, x='timestamp', y='outdoor_temperature', title='Outdoor Temperature Over Time')
    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph, last_update=last_update)

@main.route('/settings', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        api_key = form.api_key.data
        application_key = form.application_key.data
        mac = form.mac.data
        save_credentials_to_db(api_key, application_key, mac)
        flash('Settings have been saved.', 'success')
        return redirect(url_for('main.index'))
    
    credentials = get_credentials()
    form.api_key.data = credentials.get('api_key', '')
    form.application_key.data = credentials.get('application_key', '')
    form.mac.data = credentials.get('mac', '')
    return render_template('settings.html', form=form)

@main.route('/fetch_data', methods=['POST'])
def fetch_data():
    fetch_and_save_weather_data()
    flash('Weather data fetched and saved successfully.', 'success')
    return redirect(url_for('main.index'))
