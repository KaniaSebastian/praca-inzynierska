from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = PasswordField('Login', validators=[DataRequired(message='To pole jest wymagane')])
    remember = BooleanField('Pamiętaj mnie')
    submit = SubmitField('Zaloguj')
