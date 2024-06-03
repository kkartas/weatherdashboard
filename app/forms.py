from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SettingsForm(FlaskForm):
    api_key = StringField('API Key', validators=[DataRequired()])
    application_key = StringField('Application Key', validators=[DataRequired()])
    mac = StringField('MAC', validators=[DataRequired()])
    submit = SubmitField('Save')
