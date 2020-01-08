from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    login = PasswordField('Login', validators=[DataRequired(message='To pole jest wymagane')])
    remember = BooleanField('Pamiętaj mnie')
    recaptcha = RecaptchaField(validators=[Recaptcha(message='Zaznacz, że nie jesteś robotem')])
    submit = SubmitField('Zaloguj')
