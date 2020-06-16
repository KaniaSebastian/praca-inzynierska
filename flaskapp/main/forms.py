from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext


class LoginForm(FlaskForm):
    login = PasswordField(lazy_gettext('Login'), validators=[DataRequired(message=lazy_gettext('To pole jest wymagane'))])
    remember = BooleanField(lazy_gettext('Pamiętaj mnie'))
    recaptcha = RecaptchaField(validators=[Recaptcha(message=lazy_gettext('Zaznacz, że nie jesteś robotem'))])
    submit = SubmitField(lazy_gettext('Zaloguj'))
