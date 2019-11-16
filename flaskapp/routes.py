from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt,admin_password
from flaskapp.models import User, Project, Group
from flaskapp.forms import LoginForm, AdminCreateGroup, AdminLoginForm
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
	if form.validate_on_submit():
		user = User.query.filter_by(login=form.login.data).first()
		if user and user.is_admin:
			return redirect(url_for('admin_login'))
		if user:
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			flash('Zalogowałeś się', 'success')
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
		flash('Dostęp do tej strony posiada tylko zwykły użytkownik', 'warning')
		return redirect(url_for('panel'))
	return render_template('project.html')


@app.route('/panel', methods=['GET', 'POST'])
@login_required
def panel():
	if current_user.is_admin:
		pass
	else:
		flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
		return redirect(url_for('home'))
	return render_template('admin/panel.html', title='Panel administracyjny')


@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
	if current_user.is_admin:
		form = AdminCreateGroup()
		if form.validate_on_submit():

			new_group = Group(name=form.name.data)
			db.session.add(new_group)
			db.session.commit()

			x = form.number.data
			while x > 0:
				random_key = secrets.token_hex(16)
				if User.query.filter_by(login=random_key).first():
					continue
				new_user = User(login=random_key, group=new_group)
				db.session.add(new_user)
				x = x - 1
			# group = Group.query.filter_by(name=form.name.data).first()
			db.session.commit()
			flash('Grupa została utworzona', 'success')
			return redirect(url_for('create_group'))
	else:
		flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
		return redirect(url_for('home'))
	return render_template('admin/create_group.html', title='Panel administracyjny', form=form)


@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = AdminLoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(login=form.login.data).first()
		if user and bcrypt.check_password_hash(admin_password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			flash('Zalogowałeś się', 'success')
			return redirect(next_page) if next_page else redirect(url_for('panel'))
		else:
			flash('Logowanie nieudane. Sprawdź poprawność wpisanych danych', 'danger')
	return render_template('admin/login_admin.html', title='Zaloguj się jako administrator', form=form)
