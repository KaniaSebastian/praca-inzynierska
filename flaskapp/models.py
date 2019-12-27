from datetime import datetime
from flaskapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    project = db.relationship('Project', backref='author', lazy=True, cascade="all, delete")
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)

    def __repr__(self):
        return f"User('{self.login}', admin={self.is_admin})"


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    image_file = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    optional_link = db.Column(db.String)
    creators_num = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer)
    # last_editor = db.Column()

    def __repr__(self):
        return f"Project('{self.title}', '{self.date_posted}')"


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    is_section = db.Column(db.Boolean, nullable=False, default=False)
    users = db.relationship('User', backref='group', lazy=True, cascade="all, delete")
    # subject = db.Column(db.String)
    upload_time = db.Column(db.DateTime)
    rating_status = db.Column(db.String, default='disabled')
    points_per_user = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Group ({self.name}, is_section={self.is_section}, {self.users})"
