from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
	login = StringField('Login', validators=[DataRequired(message='To pole jest wymagane.')])
	remember = BooleanField('Pamiętaj mnie')
	submit = SubmitField('Zaloguj')

class AdminLoginForm(FlaskForm):
	login = StringField('Login', validators=[DataRequired(message='To pole jest wymagane.')])
	password = PasswordField('Hasło', validators=[DataRequired()])
	remember = BooleanField('Pamiętaj mnie')
	submit = SubmitField('Zaloguj')