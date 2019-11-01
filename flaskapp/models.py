from datetime import datetime
from flaskapp import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	login = db.Column(db.String(20), unique=True, nullable=False)
	projects = db.relationship('Project', backref='author', lazy=True)
	# image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

	def __repr__(self):
		return f"User('{self.login}')"


class Project(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120), nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	description = db.Column(db.Text, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"Project('{self.title}', '{self.date_posted}')"
