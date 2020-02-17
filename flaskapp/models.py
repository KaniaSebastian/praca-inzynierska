from flaskapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    project = db.relationship('Project', backref='author', uselist=False, lazy=True, cascade="all, delete")
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    did_rate = db.Column(db.Boolean, default=False)
    section_number = db.Column(db.Integer)

    def __repr__(self):
        return f"User('{self.login}', admin={self.is_admin})"


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    date_posted = db.Column(db.DateTime)
    upload_file = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text(1500), nullable=False)
    optional_link = db.Column(db.String)
    creators_num = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    last_editor = db.Column(db.String)

    def __repr__(self):
        return f"Project('{self.title}', 'author_id={self.user_id}', score={self.score})"


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    is_containing_sections = db.Column(db.Boolean, nullable=False, default=False)
    users = db.relationship('User', backref='group', lazy=True, cascade="all, delete")
    upload_time = db.Column(db.DateTime)
    subject = db.Column(db.String(6))
    rating_status = db.Column(db.String, default='disabled')
    points_per_user = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Group ({self.name}, is_containing_sections={self.is_containing_sections}, users({len(self.users)}):{self.users})"
