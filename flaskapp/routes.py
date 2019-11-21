from flask import render_template, url_for, flash, redirect, request, Response
from flaskapp import app, db, bcrypt,admin_password
from flaskapp.models import User, Project, Group
from flaskapp.forms import LoginForm, AdminCreateGroup, AdminLoginForm, CreateProjectForm
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os


@app.route('/')
def home():
    projects = Project.query.all()
    return render_template('home.html', title='Strona główna', projects=projects)


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
            return redirect(url_for('admin_login', admin_name=form.login.data))
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


@app.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    if not current_user.is_admin:
        form = CreateProjectForm()
        if form.validate_on_submit():
            file = save_image(form.image.data)
            new_project = Project(title=form.title.data, description=form.description.data,
                                  image_file=file, author=current_user)
            db.session.add(new_project)
            db.session.commit()
            flash('Projekt został dodany', 'success')
            return redirect(url_for('project'))
    else:
        flash('Dostęp do tej strony posiada tylko zwykły użytkownik', 'warning')
        return redirect(url_for('panel'))
    return render_template('project.html', title='Projekt', form=form)


def save_image(image):
    _, extension = os.path.splitext(image.filename)
    image_file_name = current_user.login + extension
    image_path = os.path.join(app.root_path, 'static/projects', image_file_name)
    image.save(image_path)
    return image_file_name


@app.route('/panel', methods=['GET', 'POST'])
@login_required
def panel():
    if current_user.is_admin:
        groups = Group.query.all()
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('admin/panel.html', title='Panel administracyjny', groups=groups)


@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if current_user.is_admin:
        form = AdminCreateGroup()
        if form.validate_on_submit():
            if form.group_type.data == 'section':
                new_group = Group(name=form.name.data, is_section=True)
            else:
                new_group = Group(name=form.name.data, is_section=False)
            db.session.add(new_group)
            db.session.commit()

            x = form.number.data
            while x > 0:
                random_key = secrets.token_hex(2)
                if User.query.filter_by(login=random_key).first():
                    continue
                new_user = User(login=random_key, group=new_group)
                db.session.add(new_user)
                x = x - 1
            # group = Group.query.filter_by(name=form.name.data).first()
            db.session.commit()
            flash('Grupa została utworzona', 'success')
            return redirect(url_for('panel'))
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('admin/create_group.html', title='Panel administracyjny', form=form)


@app.route('/login/<string:admin_name>', methods=['GET', 'POST'])
def admin_login(admin_name):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AdminLoginForm()
    if admin_name and not form.login.data:
        form.login.data = admin_name
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and user.is_admin and bcrypt.check_password_hash(admin_password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Zalogowałeś się', 'success')
            return redirect(next_page) if next_page else redirect(url_for('panel'))
        else:
            flash('Logowanie nieudane. Sprawdź poprawność wpisanych danych', 'danger')
    return render_template('admin/login_admin.html', title='Zaloguj się jako administrator', form=form)


@app.route('/generate-csv/<string:group_name>')
@login_required
def generate_csv(group_name):
    if current_user.is_admin:
        def generate():
            group = Group.query.filter_by(name=group_name).first()
            header = ("Klucz dostepu", "Imie i nazwisko", "", "Sekcje", "Osoby")
            yield ",".join(header) + '\n\n'

            for n in range(len(group.users)):
                # group.users[n].login
                if n < 10:
                    row = (group.users[n].login, "", "", "Sekcja " + str(n+1) + ':')
                    yield ",".join(row) + '\n'
                else:
                    row = group.users[n].login
                    yield row + '\n'
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=" + group_name.replace(" ", "_") + ".csv"})
