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
    name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane'), Length(max=14, message='Nazwa grupy musi zawierać od 1 do 14 znaków')])
    number = IntegerField('Liczba sekcji w grupie', validators=[DataRequired(message='To pole jest wymagane, a wartość musi być liczbą całkowitą'),
                                                               NumberRange(min=0, max=100, message='Ta wartość nie może być ujemna, ani wększa niż 100')])
    subject = StringField('Przedmiot - skrót od nazwy', validators=[DataRequired(message='To pole jest wymagane'), Length(max=3, message='Skrót może się składać z maksymalnie 3 znaków')])
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
    points = IntegerField('Punkty na użytkownika', validators=[DataRequired(message='Nieprawidłowa liczba punktów'),
                                                               NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitRating = SubmitField('Zatwierdź')


class EditGroupNameForm(FlaskForm):
    name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane.'), Length(max=14, message='Nazwa grupy musi zawierać od 1 do 14 znaków')])
    subject = StringField('Przedmiot - skrót od nazwy', validators=[DataRequired(), Length(max=3, message='Skrót może się składać z maksymalnie 3 znaków.')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitName = SubmitField('Zatwierdź')

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        group_for_validation = Group.query.get(self.selected_group_id.data)
        if group and group.id != group_for_validation.id:
            raise ValidationError('Ta nazwa jest już używana dla innej grupy.')
