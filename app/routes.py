from flask import Blueprint, render_template
from app.models import fetch_data_from_db
import plotly.express as px

main = Blueprint('main', __name__)

@main.route('/')
def index():
    df = fetch_data_from_db()
    fig = px.line(df, x='timestamp', y='temperature', title='Temperature Over Time')
    graph = fig.to_html(full_html=False)
    return render_template('index.html', graph=graph)
