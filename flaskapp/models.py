from flaskapp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(30))
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    # user_role = db.Column(db.String(30))
    project = db.relationship('Project', backref='author', uselist=False, lazy=True, cascade="all, delete")
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    did_rate = db.Column(db.Boolean, default=False)
    section_number = db.Column(db.Integer)
    admin_groups = db.relationship('Group', foreign_keys="[Group.admin_id]", backref='admin', lazy=True)  # add cascade?
    rating_type = db.Column(db.String(50), nullable=True)

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
    last_editor = db.Column(db.String)
    score_points_pool = db.Column(db.Integer, default=0)
    score_points_pool_shuffled = db.Column(db.Integer, default=0)
    score_pool_per_project = db.Column(db.Integer, default=0)
    score_admin = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Project('{self.title}', 'author_id={self.user_id}')"


# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.Text(1500), nullable=False)
#     project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
#     author_type = db.Column(db.String(30))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    is_containing_sections = db.Column(db.Boolean, nullable=False, default=False)
    users = db.relationship('User', foreign_keys="[User.group_id]", backref='group', lazy=True, cascade="all, delete")
    upload_time = db.Column(db.DateTime)
    subject = db.Column(db.String(6))
    rating_status = db.Column(db.String, default='disabled')
    points_per_user = db.Column(db.Integer, default=0)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    points_per_project = db.Column(db.Integer, default=0)
    # rating_type_for_admin = db.Column(db.String(50), nullable=True, default='points_pool')

    def __repr__(self):
        return f"Group ({self.name}, is_containing_sections={self.is_containing_sections}, users({len(self.users)}):{self.users})"


# class Questionnaire(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.Text(1500), nullable=False)