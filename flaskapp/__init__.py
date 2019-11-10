from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '66334d8be4b779a6f829916546c8e7df'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Musisz się zalogować, aby zobaczyć tę stronę.'
login_manager.login_message_category = 'info'

admin_password = '$2b$12$V4dBXyIe9Iu9IfkZyntMtuPfW8DP7X2DQtGGLuG6gmbv3WMgqSG.K'

from flaskapp import routes