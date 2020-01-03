from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, ValidationError, TextAreaField, SelectField, HiddenField, FieldList, FormField, Field
from wtforms.fields.html5 import DateTimeLocalField, URLField
from wtforms.validators import DataRequired, NumberRange, url, optional, InputRequired
from wtforms.utils import unset_value
from flaskapp.models import Group
from flask import flash


# Custom Form Field
class CustomIntegerField(IntegerField):
    def process_data(self, value):
        if value is not None and value is not unset_value:
            try:
                self.data = int(value)
            except (ValueError, TypeError):
                self.data = None
                raise ValueError(self.gettext("Podana wartość nie jest liczbą"))
        else:
            self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = int(valuelist[0])
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Podana wartość nie jest liczbą"))


class LoginForm(FlaskForm):
    login = PasswordField('Login', validators=[DataRequired(message='To pole jest wymagane')])
    remember = BooleanField('Pamiętaj mnie')
    submit = SubmitField('Zaloguj')


class AdminLoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(message='To pole jest wymagane')])
    password = PasswordField('Hasło', validators=[DataRequired(message='To pole jest wymagane')])
    remember = BooleanField('Pamiętaj mnie')
    submit = SubmitField('Zaloguj')


class AdminCreateGroup(FlaskForm):
    name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane')])
    number = IntegerField('Ilość sekcji w grupie', validators=[DataRequired(message='To pole jest wymagane, a wartość musi być liczbą całkowitą'),
                                                               NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna')])
    subject = StringField('Przedmiot - prefix', validators=[DataRequired()])
    submit = SubmitField('Utwórz')

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group:
            raise ValidationError('Ta nazwa jest już używana dla innej grupy')


class CreateProjectForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired(message='To pole jest wymagane')])
    image = FileField('Projekt', validators=[FileAllowed(['jpg', 'png'], message='Plik musi mieć rozszerzenie jpg lub '
                                                                                 'png'),
                                             FileRequired(message='Dodanie pliku jest wymagane')])
    description = TextAreaField('Opis projektu', validators=[DataRequired(message='To pole jest wymagane')])
    creators_num = IntegerField('Ilość osób pracujących nad projektem',
                                validators=[DataRequired(message='To pole jest wymagane'),
                                            NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna')])
    url = URLField('Link do dodatkowych materiałów (opcjonalne)', validators=[optional(), url(message='Nieprawidłowy adres URL')])
    submit = SubmitField('Dodaj')


class UpdateProjectForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired(message='To pole jest wymagane.')])
    image = FileField('Projekt', validators=[FileAllowed(['jpg', 'png'], message='Plik musi mieć rozszerzenie jpg lub '
                                                                                 'png.')])
    description = TextAreaField('Opis projektu', validators=[DataRequired(message='To pole jest wymagane')])
    # creators_num = IntegerField('Ilość osób pracujących nad projektem',
    #                             validators=[DataRequired(message='To pole jest wymagane.'),
    #                                         NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna.')])
    url = URLField('Link do dodatkowych materiałów (opcjonalne)', validators=[optional(), url(message='Nieprawidłowy adres URL')])
    submit = SubmitField('Edytuj')


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
    name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane.')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitName = SubmitField('Zatwierdź')

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group:
            raise ValidationError('Ta nazwa jest już używana dla innej grupy.')


class PointsEntryForm(FlaskForm):
    points = CustomIntegerField('Punkty: ', validators=[InputRequired(message='Nieprawidłowa wartość'),
                                                  NumberRange(min=0, max=None,
                                                              message='Ta wartość musi być liczbą nieujemną')])


class PointsForm(FlaskForm):

    def __init__(self, points_per_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points_per_user = points_per_user

    all_points = FieldList(FormField(PointsEntryForm))
    submit = SubmitField('Zatwierdź')

    def validate_all_points(self, all_points):
        points_sum = 0
        for field in all_points:
            if field.data.get('points'):
                points_sum = points_sum + field.data.get('points')
        if points_sum > self.points_per_user:
            flash('Przydzielono o ' + str(points_sum - self.points_per_user) + ' punktów za dużo', 'danger')
            raise ValidationError()
        elif points_sum < self.points_per_user:
            flash('Przydzielono o ' + str(self.points_per_user - points_sum) + ' punktów za mało', 'danger')
            raise ValidationError()
