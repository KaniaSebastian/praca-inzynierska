from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, IntegerField, ValidationError, TextAreaField, FieldList, FormField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, NumberRange, url, optional, InputRequired, Length
from wtforms.utils import unset_value
from flask import flash


# Custom Form Field
class CustomIntegerField(IntegerField):
    def process_data(self, value):
        if value is not None and value is not unset_value:
            try:
                self.data = int(value)
            except (ValueError, TypeError):
                self.data = None
                raise ValueError(self.gettext("Podana wartość nie jest liczbą całkowitą"))
        else:
            self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = int(valuelist[0])
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Podana wartość nie jest liczbą całkowitą"))


class CreateProjectForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired(message='To pole jest wymagane'), Length(max=100, message='Tytuł może się składać z maksymalnie 100 znaków.')])
    file = FileField('Projekt', validators=[FileAllowed(['jpg', 'png', 'pdf'], message='Plik musi mieć rozszerzenie jpg, png lub pdf'), FileRequired(message='Dodanie pliku jest wymagane')])
    description = TextAreaField('Opis projektu', validators=[DataRequired(message='To pole jest wymagane'), Length(max=1000, message='Opis może się składać z maksymalnie 1000 znaków.')])
    creators_num = IntegerField('Liczba osób pracujących nad projektem',
                                validators=[DataRequired(message='To pole jest wymagane'),
                                            NumberRange(min=0, max=10, message='Ta wartość nie może być ujemna i nie większa niż 10')])
    url = URLField('Link do dodatkowych materiałów (opcjonalne)', validators=[optional(), url(message='Nieprawidłowy adres URL')])
    submit = SubmitField('Dodaj')


class UpdateProjectForm(FlaskForm):
    title = StringField('Tytuł', validators=[DataRequired(message='To pole jest wymagane.'), Length(max=100, message='Tytuł może się składać z maksymalnie 100 znaków.')])
    file = FileField('Projekt',
                      validators=[FileAllowed(['jpg', 'png', 'pdf'], message='Plik musi mieć rozszerzenie jpg, png lub pdf.')])
    description = TextAreaField('Opis projektu', validators=[DataRequired(message='To pole jest wymagane'), Length(max=1000, message='Opis może się składać z maksymalnie 1000 znaków.')])
    url = URLField('Link do dodatkowych materiałów (opcjonalne)', validators=[optional(), url(message='Nieprawidłowy adres URL')])
    submit = SubmitField('Edytuj')


class PointsEntryForm(FlaskForm):
    points = CustomIntegerField('Punkty: ', validators=[InputRequired(message='Nieprawidłowa wartość'),
                                                        NumberRange(min=0, max=None,
                                                                    message='Ta wartość musi być liczbą nieujemną')])

    def validate_points(self, points):
        if not isinstance(points.data, int) or points.data < 0:
            flash('Formularz nie został uzupełniony poprawnie', 'danger')


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
            if points_sum > 1000:
                flash('Podane wartości są za duże', 'danger')
                raise ValidationError()
            flash('Przydzielono o ' + str(points_sum - self.points_per_user) + ' pkt. za dużo', 'danger')
            raise ValidationError()
        elif points_sum < self.points_per_user:
            if points_sum >= 0:
                flash('Przydzielono o ' + str(self.points_per_user - points_sum) + ' pkt. za mało', 'danger')
            raise ValidationError()
