from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, ValidationError
from wtforms.validators import DataRequired, NumberRange
from flaskapp.models import Group


class LoginForm(FlaskForm):
	login = StringField('Login', validators=[DataRequired(message='To pole jest wymagane.')])
	remember = BooleanField('Pamiętaj mnie')
	submit = SubmitField('Zaloguj')


# class AdminLoginForm(FlaskForm):
# 	login = StringField('Login', validators=[DataRequired(message='To pole jest wymagane.')])
# 	password = PasswordField('Hasło', validators=[DataRequired()])
# 	remember = BooleanField('Pamiętaj mnie')
# 	submit = SubmitField('Zaloguj')


class AdminCreateGroup(FlaskForm):
	name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane.')])
	number = IntegerField('Ilość osób w grupie', validators=[DataRequired(message='Ilość osób jest wymagana i musi być liczbą całkowitą.'),
															 NumberRange(min=0, max=None, message='Ilość osób nie może być ujemna.')])
	submit = SubmitField('Utwórz')

	def validate_name(self, name):
		group = Group.query.filter_by(name=name.data).first()
		if group:
			raise ValidationError('Ta nazwa jest już używana dla innej grupy.')
