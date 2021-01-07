from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import SubmitField, BooleanField, PasswordField, FieldList, FormField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length
from flask_babel import lazy_gettext
from flask import flash

from flaskapp.users.forms import CustomIntegerField


class LoginForm(FlaskForm):
    login = PasswordField(lazy_gettext('Login'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane'))])
    remember = BooleanField(lazy_gettext('Pamiętaj mnie'))
    recaptcha = RecaptchaField(validators=[Recaptcha(message=lazy_gettext('Zaznacz, że nie jesteś robotem'))])
    submit = SubmitField(lazy_gettext('Zaloguj'))


class PointsPoolPerProjectEntryForm(FlaskForm):
    points = CustomIntegerField(lazy_gettext('Punkty: '), validators=[InputRequired(message=lazy_gettext('To pole jest wymagane. Wpisz minimum wartość 0.')),
                                                        NumberRange(min=1, max=None,
                                                                    message=lazy_gettext('Ta wartość musi być liczbą większą niż 0'))])
    distinction = BooleanField(lazy_gettext('Wyróżnij'))
    comment_star_1 = TextAreaField(lazy_gettext('Co w pracy zasługuje na pochwałę?'), render_kw={'rows': 1},
                                   validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')),
                                               Length(max=1000, message=lazy_gettext(
                                                   'Komentarz może się składać z maksymalnie 1000 znaków.'))])
    comment_star_2 = TextAreaField(lazy_gettext('Druga rzecz, która zasługuje na pochwałę.'), render_kw={'rows': 1},
                                   validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')),
                                               Length(max=1000, message=lazy_gettext(
                                                   'Komentarz może się składać z maksymalnie 1000 znaków.'))])
    comment_wish = TextAreaField(lazy_gettext('Co można poprawić w pracy?'), render_kw={'rows': 1},
                                 validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')),
                                             Length(max=1000, message=lazy_gettext(
                                                 'Komentarz może się składać z maksymalnie 1000 znaków.'))])

    def validate_points(self, points):
        if not isinstance(points.data, int) or points.data < 0:
            flash(lazy_gettext('Formularz nie został uzupełniony poprawnie'), 'danger')


class PointsPoolPerProjectForm(FlaskForm):

    def __init__(self, points_per_project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points_per_project = points_per_project

    all_points = FieldList(FormField(PointsPoolPerProjectEntryForm))
    submit = SubmitField(lazy_gettext('Zatwierdź'))

    def validate_all_points(self, all_points):
        number_of_distinctions = 0
        for field in all_points:
            # distinction validation
            number_of_distinctions += int(field.data.get('distinction'))
            if number_of_distinctions > 2:
                flash(lazy_gettext('Nie można przydzielić więcej niż 2 wyróżnień'), 'danger')
                raise ValidationError()

            # points validation
            if field.data.get('points'):
                if field.data.get('points') > self.points_per_project:
                    flash(lazy_gettext('Nie można przydzielić więcej niż ' + str(self.points_per_project) + ' punktów na jeden projekt'), 'danger')
                    raise ValidationError()
            if field.data.get('points') == 0:
                flash(lazy_gettext('Każdy projekt musi otrzymać minimum jeden punkt'), 'danger')
                raise ValidationError()

