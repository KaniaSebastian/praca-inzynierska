from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, ValidationError, TextAreaField, FieldList, FormField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, NumberRange, url, optional, InputRequired, Length
from wtforms.utils import unset_value
from flask import flash
from flask_babel import lazy_gettext


# Custom Form Field
class CustomIntegerField(IntegerField):
    def process_data(self, value):
        if value is not None and value is not unset_value:
            try:
                self.data = int(value)
            except (ValueError, TypeError):
                self.data = None
                raise ValueError(self.gettext(lazy_gettext("Podana wartość nie jest liczbą całkowitą")))
        else:
            self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = int(valuelist[0])
            except ValueError:
                self.data = None
                raise ValueError(self.gettext(lazy_gettext("Podana wartość nie jest liczbą całkowitą")))


class CreateProjectForm(FlaskForm):
    title = StringField(lazy_gettext('Tytuł'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')), Length(max=50, message=lazy_gettext('Tytuł może się składać z maksymalnie 50 znaków.'))])
    file = FileField(lazy_gettext('Projekt'), validators=[FileAllowed(['jpg', 'png', 'pdf'], message=lazy_gettext('Plik musi mieć rozszerzenie jpg, png lub pdf')), FileRequired(message=lazy_gettext('Dodanie pliku jest wymagane'))])
    description = TextAreaField(lazy_gettext('Opis projektu'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')), Length(max=1000, message=lazy_gettext('Opis może się składać z maksymalnie 1000 znaków.'))])
    creators_num = IntegerField(lazy_gettext('Liczba osób pracujących nad projektem'),
                                validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')),
                                            NumberRange(min=0, max=10, message=lazy_gettext('Ta wartość nie może być ujemna i nie większa niż 10'))])
    url = URLField(lazy_gettext('Link do dodatkowych materiałów (opcjonalne)'), validators=[optional(), url(message=lazy_gettext('Nieprawidłowy adres URL'))])
    submit = SubmitField(lazy_gettext('Dodaj'))


class UpdateProjectForm(FlaskForm):
    title = StringField(lazy_gettext('Tytuł'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane.')), Length(max=50, message=lazy_gettext('Tytuł może się składać z maksymalnie 50 znaków.'))])
    file = FileField(lazy_gettext('Projekt'),
                      validators=[FileAllowed(['jpg', 'png', 'pdf'], message=lazy_gettext('Plik musi mieć rozszerzenie jpg, png lub pdf.'))])
    description = TextAreaField(lazy_gettext('Opis projektu'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')), Length(max=1000, message=lazy_gettext('Opis może się składać z maksymalnie 1000 znaków.'))])
    url = URLField(lazy_gettext('Link do dodatkowych materiałów (opcjonalne)'), validators=[optional(), url(message=lazy_gettext('Nieprawidłowy adres URL'))])
    submit = SubmitField(lazy_gettext('Edytuj'))


class PointsEntryForm(FlaskForm):
    points = CustomIntegerField(lazy_gettext('Punkty: '), validators=[InputRequired(message=lazy_gettext('To pole jest wymagane. Wpisz minimum wartość 0.')),
                                                        NumberRange(min=0, max=None,
                                                                    message=lazy_gettext('Ta wartość musi być liczbą nieujemną'))])
    comment_star_1 = TextAreaField(lazy_gettext('Co w pracy zasługuje na pochwałę?'), render_kw={'rows': 1},
                                validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')),
                                            Length(max=1000, message=lazy_gettext('Komentarz może się składać z maksymalnie 1000 znaków.'))])
    comment_star_2 = TextAreaField(lazy_gettext('Druga rzecz, która zasługuje na pochwałę'), render_kw={'rows': 1},
                                   validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')),
                                               Length(max=1000, message=lazy_gettext('Komentarz może się składać z maksymalnie 1000 znaków.'))])
    comment_wish = TextAreaField(lazy_gettext('Co można poprawić w pracy?'), render_kw={'rows': 1},
                                   validators=[DataRequired(message=lazy_gettext('To pole jest wymagane')),
                                               Length(max=1000, message=lazy_gettext('Komentarz może się składać z maksymalnie 1000 znaków.'))])

    def validate_points(self, points):
        if not isinstance(points.data, int) or points.data < 0:
            flash(lazy_gettext('Formularz nie został uzupełniony poprawnie'), 'danger')


class PointsForm(FlaskForm):

    def __init__(self, points_per_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points_per_user = points_per_user

    all_points = FieldList(FormField(PointsEntryForm))
    submit = SubmitField(lazy_gettext('Zatwierdź'))

    def validate_all_points(self, all_points):
        points_sum = 0
        for field in all_points:
            if field.data.get('points'):
                points_sum = points_sum + field.data.get('points')
        if points_sum > self.points_per_user:
            if points_sum > 10000:
                flash(lazy_gettext('Podane wartości są za duże'), 'danger')
                raise ValidationError()
            flash(lazy_gettext('Przydzielono o ') + str(points_sum - self.points_per_user) + lazy_gettext(' pkt. za dużo'), 'danger')
            raise ValidationError()
        elif points_sum < self.points_per_user:
            if points_sum >= 0:
                flash(lazy_gettext('Przydzielono o ') + str(self.points_per_user - points_sum) + lazy_gettext(' pkt. za mało'), 'danger')
            raise ValidationError()
