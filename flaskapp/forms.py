from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, ValidationError, TextAreaField, SelectField, HiddenField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange
from flaskapp.models import Group


class LoginForm(FlaskForm):
    login = PasswordField('Login', validators=[DataRequired(message='To pole jest wymagane.')])
    remember = BooleanField('Pamiętaj mnie')
    submit = SubmitField('Zaloguj')


class AdminLoginForm(FlaskForm):
    login = StringField('Login', validators=[DataRequired(message='To pole jest wymagane.')])
    password = PasswordField('Hasło', validators=[DataRequired(message='To pole jest wymagane.')])
    remember = BooleanField('Pamiętaj mnie')
    submit = SubmitField('Zaloguj')


class AdminCreateGroup(FlaskForm):
    name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane.')])
    number = IntegerField('Ilość sekcji w grupie', validators=[DataRequired(message='To pole jest wymagane, a wartość '
                                                                                    'musi być liczbą całkowitą.'),
                                                               NumberRange(min=0, max=None,
                                                                           message='Ta wartość nie może być ujemna.')])

    submit = SubmitField('Utwórz')

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group:
            raise ValidationError('Ta nazwa jest już używana dla innej grupy.')


class CreateProjectForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired(message='To pole jest wymagane.')])
    image = FileField('Projekt', validators=[FileAllowed(['jpg', 'png'], message='Plik musi mieć rozszerzenie jpg lub '
                                                                                 'png.'),
                                             FileRequired(message='Dodanie pliku jest wymagane.')])
    description = TextAreaField('Opis projektu', validators=[DataRequired(message='To pole jest wymagane.')])
    creators_num = IntegerField('Ilość osób pracujących nad projektem',
                                validators=[DataRequired(message='To pole jest wymagane.'),
                                            NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna.')])
    submit = SubmitField('Dodaj')


class UpdateProjectForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired(message='To pole jest wymagane.')])
    image = FileField('Projekt', validators=[FileAllowed(['jpg', 'png'], message='Plik musi mieć rozszerzenie jpg lub '
                                                                                 'png.')])
    description = TextAreaField('Opis projektu', validators=[DataRequired(message='To pole jest wymagane.')])
    # creators_num = IntegerField('Ilość osób pracujących nad projektem',
    #                             validators=[DataRequired(message='To pole jest wymagane.'),
    #                                         NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna.')])
    submit = SubmitField('Edytuj')


class SetUploadTimeForm(FlaskForm):
    upload_time = DateTimeLocalField('Czas', format='%Y-%m-%dT%H:%M', validators=[DataRequired(message='Formularz nie został uzupełniony poprawnie')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitTime = SubmitField('Zatwierdź')


class SetRatingForm(FlaskForm):
    is_rating_enabled = SelectField('Ocenianie', choices=[('False', 'Wyłączone'), ('True', 'Włączone')])
    points = IntegerField('Punkty na użytkownika', validators=[DataRequired(message='Nieprawidłowa ilość punktów'),
                                                               NumberRange(min=0, max=None, message='Ta wartość nie może być ujemna.')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitRating = SubmitField('Zatwierdź')


class EditGroupName(FlaskForm):
    name = StringField('Nazwa grupy', validators=[DataRequired(message='To pole jest wymagane.')])
    selected_group_id = HiddenField('Id', validators=[DataRequired()])
    submitName = SubmitField('Zatwierdź')
