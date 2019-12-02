from flask import render_template, url_for, flash, redirect, request, Response
from flaskapp import app, db, bcrypt,admin_password
from flaskapp.models import User, Project, Group
from flaskapp.forms import LoginForm, AdminCreateGroup, AdminLoginForm, CreateProjectForm
from flask_login import login_user, logout_user, current_user, login_required
import secrets, string, os


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


@app.route('/logout')
def logout():
    logout_user();
    flash('Wylogowałeś się', 'success')
    return redirect(url_for('home'))


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

            new_group = Group(name=form.name.data, is_section=True)
            db.session.add(new_group)
            db.session.commit()

            users_number = form.number.data
            while users_number > 0:
                # random_key = secrets.token_hex(2)
                alphabet = string.ascii_letters + string.digits
                random_key = ''.join(secrets.choice(alphabet) for i in range(5))
                if User.query.filter_by(login=random_key).first():
                    continue
                new_user = User(login=random_key, group=new_group)
                db.session.add(new_user)
                users_number = users_number - 1
            # group = Group.query.filter_by(name=form.name.data).first()
            db.session.commit()
            flash('Grupa została utworzona', 'success')
            return redirect(url_for('panel'))
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('admin/create_group.html', title='Panel administracyjny', form=form)


@app.route('/create_section_keys/<int:group_id>', methods=['GET', 'POST'])
@login_required
def create_section_keys(group_id):
    if current_user.is_admin:
        group = Group.query.filter_by(id=group_id).first()
        for section in group.users:
            if section.project and not Group.query.filter_by(name=section.login):
                users_num = section.project[0].creators_num
                new_group = Group(name=section.login, is_section=False)
                db.session.add(new_group)
                db.session.commit()

                while users_num > 0:
                    alphabet = string.ascii_letters + string.digits
                    random_key = ''.join(secrets.choice(alphabet) for i in range(5))
                    if User.query.filter_by(login=random_key).first():
                        continue
                    new_user = User(login=random_key, group=new_group)
                    db.session.add(new_user)
                    users_num = users_num - 1
                # for n in range(users_num):
                #     alphabet = string.ascii_letters + string.digits
                #     random_key = ''.join(secrets.choice(alphabet) for i in range(5))
                #     new_user = User(login=random_key, group=new_group)
                #     db.session.add(new_user)
        db.session.commit()
        flash('Klucze zostały wygenerowane', 'success')
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return redirect(url_for('sections', group_id=group_id))


@app.route('/generate-csv/<string:group_name>')
@login_required
def generate_csv(group_name):
    if current_user.is_admin:
        def generate():
            group = Group.query.filter_by(name=group_name).first()
            header = ("Sekcja", "Klucz dostepu")
            yield ",".join(header) + '\n\n'

            for n in range(len(group.users)):
                # group.users[n].login
                section = 'Sekcja ' + str(n+1)
                row = (section, group.users[n].login)
                yield ','.join(row) + '\n'
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=" + group_name.replace(" ", "_") + ".csv"})


@app.route('/sections/<int:group_id>')
@login_required
def sections(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        if not group.is_section:
            return redirect((url_for('panel')))
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('admin/sections.html', title='Sekcje', group=group)


@app.route('/project/<int:section_id>')
@login_required
def single_project(section_id):
    if current_user.is_admin:
        project_section = Project.query.filter_by(user_id=section_id).first()
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('admin/single_project.html', title='Pojekt', project=project_section)


@app.route('/projects/<int:group_id>')
@login_required
def projects(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        number_of_sections = len(group.users)
        projects = list()
        for section in group.users:
            project = Project.query.filter_by(author=section).first()
            if project:
                projects.append(project)
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('admin/projects.html', title='Pojekt', projects=projects, number_of_sections=number_of_sections)


@app.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    if not current_user.is_admin:
        form = CreateProjectForm()
        if form.validate_on_submit():
            file = save_image(form.image.data)
            new_project = Project(title=form.title.data, description=form.description.data,
                                  image_file=file, creators_num=form.creators_num.data, author=current_user)
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



