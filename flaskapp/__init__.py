from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LebXs0UAAAAAFQBK8V3c5CIno49c8CqU6zbg4F9'
app.config['RECAPTCHA_PRIVATE_KEY'] = 'your_recaptcha_key'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

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
