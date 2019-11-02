from flask import render_template, url_for, flash, redirect, request
from flaskapp import app
from flaskapp.models import User, Project
from flaskapp.forms import LoginForm, AdminLoginForm
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def home():
	return render_template('home.html')


@app.route('/about')
def about():
	return 'about page'


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	# form_admin = AdminLoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(login=form.login.data).first()
		if user:
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Logowanie nieudane. Sprawdź poprawność wpisanych danych', 'danger')

	return render_template('login.html', title='Zaloguj się', form=form)


@app.route('/logout')
def logout():
	logout_user();
	return redirect(url_for('home'))


@app.route('/project')
@login_required
def project():
	return render_template('project.html')
