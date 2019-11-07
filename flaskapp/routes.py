from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db
from flaskapp.models import User, Project
from flaskapp.forms import LoginForm, AdminCreateGroup
from flask_login import login_user, logout_user, current_user, login_required
import secrets


@app.route('/')
def home():
	return render_template('home.html')


@app.route('/about')
def about():
	return render_template('about.html')


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
	flash('Wylogowałeś się', 'success')
	return redirect(url_for('home'))


@app.route('/project')
@login_required
def project():
	if current_user.is_admin:
		flash('Dostęp do tej strony posiada tylko zwykły użytkownik', 'success')
		return redirect(url_for('admin'))
	return render_template('project.html')


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	if current_user.is_admin:
		form = AdminCreateGroup()
		if form.validate_on_submit():
			x = form.number.data
			while x > 0:
				random_key = secrets.token_hex(16)
				if User.query.filter_by(login=random_key).first():
					continue
				new_user = User(login=random_key)
				db.session.add(new_user)
				x = x - 1
			# group = Group.query.filter_by(name=form.name.data).first()
			db.session.commit()
			flash('Grupa została utworzona', 'success')
			return redirect(url_for('admin'))
	else:
		flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
		return redirect(url_for('home'))
	return render_template('admin.html', title='Panel administracyjny', form=form)

# for i in range(form.number.data):
# 	random_key = secrets.token_hex(16)
# 	new_user = User(login=random_key)
# 	db.session.add(new_user)
