from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import fetch_data_from_db, save_credentials_to_db, get_credentials
from app.forms import SettingsForm
import plotly.express as px
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    df = fetch_data_from_db()
    fig = px.line(df, x='timestamp', y='temperature', title='Temperature Over Time')
    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph)

@main.route('/settings', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        api_key = form.api_key.data
        save_credentials_to_db(api_key)
        flash('Settings have been saved.', 'success')
        return redirect(url_for('main.index'))
    
    credentials = get_credentials()
    form.api_key.data = credentials.get('api_key', '')
    return render_template('settings.html', form=form)
