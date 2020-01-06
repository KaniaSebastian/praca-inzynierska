from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, ValidationError, SelectField, HiddenField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange, Length
from flaskapp.models import Group


class AdminLoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(message='To pole jest wymagane')])
    password = PasswordField('Hasło', validators=[DataRequired(message='To pole jest wymagane')])
    remember = BooleanField('Pamiętaj mnie')
    submit = SubmitField('Zaloguj')


class AdminCreateGroup(FlaskForm):
    name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane'), Length(max=20, message='Nazwa grupy musi zawierać od 1 do 20 znaków')])
    number = IntegerField('Ilość sekcji w grupie', validators=[DataRequired(message='To pole jest wymagane, a wartość musi być liczbą całkowitą'),
                                                               NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna')])
    subject = StringField('Przedmiot - prefix', validators=[DataRequired()])
    submit = SubmitField('Utwórz')

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group:
            raise ValidationError('Ta nazwa jest już używana dla innej grupy')


class SetUploadTimeForm(FlaskForm):
    upload_time = DateTimeLocalField('Czas', format='%Y-%m-%dT%H:%M', validators=[DataRequired(message='Formularz nie został uzupełniony poprawnie')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitTime = SubmitField('Zatwierdź')


class SetRatingForm(FlaskForm):
    rating_status = SelectField('Ocenianie', choices=[('disabled', 'Wyłączone'), ('enabled', 'Włączone'), ('ended', 'Zakończone')])
    points = IntegerField('Punkty na użytkownika', validators=[DataRequired(message='Nieprawidłowa ilość punktów'),
                                                               NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitRating = SubmitField('Zatwierdź')


class EditGroupNameForm(FlaskForm):
    name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane.'), Length(max=20, message='Nazwa grupy musi zawierać od 1 do 20 znaków')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitName = SubmitField('Zatwierdź')

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group:
            raise ValidationError('Ta nazwa jest już używana dla innej grupy.')