from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel, lazy_gettext

app = Flask(__name__)
babel = Babel(app)
app.config['SECRET_KEY'] = '66334d8be4b779a6f829916546c8e7df'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LebXs0UAAAAAFQBK8V3c5CIno49c8CqU6zbg4F9'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LebXs0UAAAAADCSxIr0hjMBw9nr_wKygHL6B1jE'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['LANGUAGES'] = {
    'en': 'English',
    'pl': 'Polish'
}


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())
#    return 'en'


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'
login_manager.login_message = 'Musisz się zalogować, aby zobaczyć tę stronę.'
login_manager.login_message_category = 'info'

from flaskapp.admin.routes import admin
from flaskapp.users.routes import users
from flaskapp.main.routes import main
from flaskapp.errors.handlers import errors

app.register_blueprint(admin)
app.register_blueprint(users)
app.register_blueprint(main)
app.register_blueprint(errors)
