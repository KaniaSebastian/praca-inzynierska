from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, ValidationError, SelectField, HiddenField, FormField, FieldList
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange, Length, InputRequired, EqualTo
from flaskapp.models import Group, User
from flask_login import current_user
from flaskapp import bcrypt
from flask_babel import lazy_gettext


class AdminLoginForm(FlaskForm):
    login = StringField(lazy_gettext('Login'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane'))])
    password = PasswordField(lazy_gettext('Hasło'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane'))])
    remember = BooleanField(lazy_gettext('Pamiętaj mnie'))
    submit = SubmitField(lazy_gettext('Zaloguj'))


class CreateGroupForm(FlaskForm):
    name = StringField(lazy_gettext('Nazwa grupy'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')), Length(max=20, message=lazy_gettext('Nazwa grupy musi zawierać od 1 do 20 znaków'))])
    number = IntegerField(lazy_gettext('Liczba sekcji w grupie'), validators=[InputRequired(message=lazy_gettext('To pole jest wymagane, a wartość musi być liczbą całkowitą')), NumberRange(min=0, max=100, message=lazy_gettext('Ta wartość nie może być ujemna, ani wększa niż 100'))])
    subject = StringField(lazy_gettext('Przedmiot - skrót od nazwy'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')), Length(max=6, message=lazy_gettext('Skrót może się składać z maksymalnie 6 znaków'))])
    submit = SubmitField(lazy_gettext('Utwórz'))

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        if group:
            raise ValidationError(lazy_gettext('Ta nazwa jest już używana dla innej grupy'))


class SetUploadTimeForm(FlaskForm):
    upload_time = DateTimeLocalField(lazy_gettext('Czas'), format='%Y-%m-%dT%H:%M', validators=[DataRequired(message=lazy_gettext('Formularz nie został uzupełniony poprawnie'))])
    selected_group_id = HiddenField(lazy_gettext('Id'), validators=[DataRequired()])
    submitTime = SubmitField(lazy_gettext('Zatwierdź'))


class SetRatingForm(FlaskForm):
    rating_status = SelectField(lazy_gettext('Ocenianie'), choices=[('disabled', lazy_gettext('Wyłączone (udostępnianie projektów)')), ('enabled', lazy_gettext('Włączone (1 tura - oceniają studenci i nauczyciel)')), ('ended', lazy_gettext('Zakończone (1 tura - można zobaczyć wyniki)')),
                                                                    ('disabled_improvement', lazy_gettext('Poprawa projektów')), ('enabled_improvement', lazy_gettext('Ocenianie (2 tura - ocenia tylko nauczyciel)')), ('ended_improvement', lazy_gettext('Zakończone (2 tura - można zobaczyć wyniki)'))])
    points = IntegerField(lazy_gettext('Pula punktów na użytkownika (ocenianie metodą 1 i 2)'), validators=[DataRequired(message=lazy_gettext('Nieprawidłowa liczba punktów')),
                                                               NumberRange(min=0, max=None, message=lazy_gettext('Ta wartość nie może być ujemna'))])
    points_per_project = IntegerField(lazy_gettext('Punkty na jeden projekt (ocenianie 3 metodą oraz ocenianie przez nauczyciela)'), validators=[DataRequired(message=lazy_gettext('Nieprawidłowa liczba punktów')),
                                      NumberRange(min=0, max=None, message=lazy_gettext('Ta wartość nie może być ujemna'))])
    # rating_type_for_admin = SelectField(lazy_gettext('Metoda oceniania, której użyje nauczyciel'), choices=[('points_pool', lazy_gettext('Metoda 1')), ('points_pool_shuffled', lazy_gettext('Metoda 2'))])
    selected_group_id = HiddenField(lazy_gettext('Id'), validators=[DataRequired()])
    submitRating = SubmitField(lazy_gettext('Zatwierdź'))


class EditGroupNameForm(FlaskForm):
    name = StringField(lazy_gettext('Nazwa grupy'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane.')), Length(max=20, message=lazy_gettext('Nazwa grupy musi zawierać od 1 do 20 znaków'))])
    subject = StringField(lazy_gettext('Przedmiot - skrót od nazwy'), validators=[DataRequired(), Length(max=6, message=lazy_gettext('Skrót może się składać z maksymalnie 6 znaków'))])
    selected_group_id = HiddenField(lazy_gettext('Id'), validators=[DataRequired()])
    submitName = SubmitField(lazy_gettext('Zatwierdź'))

    def validate_name(self, name):
        group = Group.query.filter_by(name=name.data).first()
        group_for_validation = Group.query.get(self.selected_group_id.data)
        if group and group.id != group_for_validation.id:
            raise ValidationError(lazy_gettext('Ta nazwa jest już używana dla innej grupy.'))


class AddAdminForm(FlaskForm):
    login = StringField(lazy_gettext('Login'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane.')),
                                             Length(min=2, max=20, message=lazy_gettext('Login musi zawierać od 2 do 20 znaków'))])
    submit = SubmitField(lazy_gettext('Dodaj'))

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError(lazy_gettext('Administrator o takim loginie już istnieje.'))


class ChangePasswordForm(FlaskForm):
    password = PasswordField(lazy_gettext('Hasło'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane.')), Length(min=4, max=30, message=lazy_gettext('Hasło musi zawierać od 4 do 30 znaków'))])
    confirm_password = PasswordField(lazy_gettext('Potwierdź hasło'),
                                     validators=[DataRequired(message=lazy_gettext('To pole jest wymagane.')), EqualTo('password', message='Hasła różnią się od siebie')])
    old_password = PasswordField(lazy_gettext('Zatwierdź zmiany wpisując stare hasło'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane.'))])
    submit = SubmitField(lazy_gettext('Zmień hasło'))

    def validate_old_password(self, old_password):
        if not bcrypt.check_password_hash(current_user.password, old_password.data):
            raise ValidationError(lazy_gettext('Wpisano nieprawidłowe hasło'))

    def validate_password(self, password):
        if password.data == 'admin':
            raise ValidationError(lazy_gettext('Wybrane hasło jest zbyt proste'))
