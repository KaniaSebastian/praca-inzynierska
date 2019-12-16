from flask import render_template, url_for, flash, redirect, request, Response, abort
from flaskapp import app, db, bcrypt,admin_password
from flaskapp.models import User, Project, Group
from flaskapp.forms import LoginForm, AdminCreateGroup, AdminLoginForm, CreateProjectForm, UpdateProjectForm, SetUploadTimeForm, SetRatingForm, EditGroupName
from flask_login import login_user, logout_user, current_user, login_required
import secrets, string, os
from datetime import datetime
from distutils.util import strtobool


@app.route('/')
def home():
    # projects = Project.query.all()
    return render_template('home.html', title='Strona główna')


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

# change url in panel.html if route changed
@app.route('/delete_group/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        for section in group.users:
            if section.project:
                section_project = Project.query.filter_by(author=section).first()
                old_file = section_project.image_file
                os.remove(os.path.join(app.root_path, 'static/projects', old_file))
                db.session.delete(Group.query.filter_by(name=section.login).first())
        db.session.delete(group)
        db.session.commit()
        flash('Grupa została usunięta', 'success')
        return redirect(url_for('panel'))
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))


@app.route('/create_section_keys/<int:group_id>', methods=['GET', 'POST'])
@login_required
def create_section_keys(group_id):
    if current_user.is_admin:
        group = Group.query.filter_by(id=group_id).first()
        is_any_project = False
        for section in group.users:
            if section.project and not Group.query.filter_by(name=section.login).first():
                is_any_project = True
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
        db.session.commit()
        if is_any_project:
            flash('Klucze zostały wygenerowane', 'success')
        else:
            flash('Nowe klucze mogą być wygenerowane tylko dla sekcji które przesłały już projekt lub nie posiadają jeszcze użytkowników', 'warning')
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return redirect(url_for('sections', group_id=group_id))


@app.route('/add_user/<int:section_id>', methods=['GET', 'POST'])
@login_required
def add_user(section_id):
    if current_user.is_admin:
        section = User.query.get_or_404(section_id)
        group = Group.query.filter_by(name=section.login).first()
        if group:
            users_num = 1
            while users_num > 0:
                alphabet = string.ascii_letters + string.digits
                random_key = ''.join(secrets.choice(alphabet) for i in range(5))
                if User.query.filter_by(login=random_key).first():
                    continue
                new_user = User(login=random_key, group=group)
                db.session.add(new_user)
                users_num = users_num - 1
            db.session.commit()
            flash('Użytkownik został dodany', 'success')
        else:
            flash('Nowy użytkownik może zostać dodany tylko jeśli sekcja udostępniła już projekt', 'warning')
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return redirect(url_for('sections', group_id=section.group_id))


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    if current_user.is_admin:
        user_to_delete = User.query.get_or_404(user_id)
        user_group = Group.query.get_or_404(user_to_delete.group_id)
        user_section = User.query.filter_by(login=user_group.name).first()
        if len(user_group.users) == 1:
            db.session.delete(user_to_delete)
            db.session.delete(user_group)
        else:
            db.session.delete(user_to_delete)
        db.session.commit()
        flash('Użytkownik został usunięty', 'success')
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return redirect(url_for('sections', group_id=user_section.group_id))


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
        user_groups = list()
        for section in group.users:
            user_groups.append(Group.query.filter_by(name=section.login).first())
        if not group.is_section:
            return redirect((url_for('panel')))
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('admin/sections.html', title='Sekcje', group=group, user_groups=user_groups)

# ????v
@app.route('/project/<int:section_id>')
@login_required
def single_project(section_id):
    if current_user.is_admin:
        project_section = Project.query.filter_by(user_id=section_id).first()
    else:
        flash('Musisz mieć uprawnienia aministratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('project_view.html', title='Pojekt', project=project_section)


@app.route('/projects/<int:group_id>')
@login_required
def projects(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        if not group.is_section:
            abort(404)
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


@app.route('/manage-groups', methods=['GET', 'POST'])
@login_required
def manage_groups():
    if current_user.is_admin:
        set_upload_time_form = SetUploadTimeForm()
        set_rating_form = SetRatingForm()
        group_name_form = EditGroupName()
        groups = Group.query.all()

        if set_upload_time_form.submitTime.data and set_upload_time_form.validate():
            import sys
            print('czas submited', file=sys.stderr)
            group = Group.query.get_or_404(set_upload_time_form.selected_group_id.data)
            group.upload_time = set_upload_time_form.upload_time.data
            db.session.commit()
            flash('Czas na udostępnienie projektu został zaaktualizowany', 'success')
            return redirect(url_for('manage_groups'))
        else:
            for error in set_upload_time_form.upload_time.errors:
                flash(error, 'danger')

        if set_rating_form.submitRating.data and set_rating_form.validate():
            import sys
            print(set_rating_form.is_rating_enabled.data, file=sys.stderr)
            group = Group.query.get_or_404(set_rating_form.selected_group_id.data)
            group.is_rating_enabled = strtobool(set_rating_form.is_rating_enabled.data)
            group.points_per_user = set_rating_form.points.data
            db.session.commit()
            flash('Ocenianie zostało włączone', 'success') if strtobool(set_rating_form.is_rating_enabled.data) else flash('Ocenianie zostało wyłączone', 'success')
            return redirect(url_for('manage_groups'))
        else:
            for error in set_rating_form.points.errors:
                flash(error, 'danger')

        if group_name_form.submitName.data and group_name_form.validate():
            group = Group.query.get_or_404(group_name_form.selected_group_id.data)
            group.name = group_name_form.name.data
            db.session.commit()
            flash('Nazwa grupy zostałą zmieniona', 'success')
            return redirect(url_for('manage_groups'))
        else:
            for error in group_name_form.name.errors:
                flash(error, 'danger')

    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('home'))
    return render_template('admin/manage_groups.html', title='Zarządzanie grupami', groups=groups,
                           set_upload_time_form=set_upload_time_form, set_rating_form=set_rating_form, group_name_form=group_name_form)


# @app.route('/set-upload-time', methods=['GET', 'POST'])
# @login_required
# def manage_groups():
#     if current_user.is_admin:
#         form = ManageGroupForm()
#         groups = Group.query.all()
#     else:
#         flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
#         return redirect(url_for('home'))
#     return render_template('admin/manage_groups.html', title='Zarządzanie grupami', groups=groups, form=form)


@app.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    if not current_user.is_admin and current_user.group.is_section:
        if current_user.project:
            return redirect(url_for('project_view'))
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
        flash('Dostęp do tej strony posiada tylko sekcja', 'warning')
        return redirect(url_for('home'))
    return render_template('project.html', title='Projekt', form=form, legend='Dodaj projekt')


def save_image(image):
    _, extension = os.path.splitext(image.filename)
    image_file_name = secrets.token_hex(5) + extension
    while True:
        if Project.query.filter_by(image_file=image_file_name).first():
            continue
        else:
            break
    image_path = os.path.join(app.root_path, 'static/projects', image_file_name)
    image.save(image_path)
    return image_file_name


@app.route('/project/update', methods=['GET', 'POST'])
@login_required
def update_project():
    if not current_user.is_admin:
        if not current_user.project:
            return redirect(url_for('project'))
        form = UpdateProjectForm()
        user_project = Project.query.filter_by(author=current_user).first()
        if form.validate_on_submit():
            user_project.title = form.title.data
            user_project.description = form.description.data
            # user_project.creators_num = form.creators_num.data
            user_project.date_posted = datetime.now()
            if form.image.data:
                old_file = user_project.image_file
                file = save_image(form.image.data)
                user_project.image_file = file
                os.remove(os.path.join(app.root_path, 'static/projects', old_file))
            db.session.commit()
            flash('Projekt został edytowany', 'success')
            return redirect(url_for('project_view'))
        elif request.method == 'GET':
            form.title.data = user_project.title
            form.description.data = user_project.description
            # form.creators_num.data = user_project.creators_num
    else:
        flash('Dostęp do tej strony posiada tylko zwykły użytkownik', 'warning')
        return redirect(url_for('panel'))
    return render_template('project.html', title='Edytuj projekt', form=form, legend='Edytuj projekt')


@app.route('/project/view', methods=['GET', 'POST'])
@login_required
def project_view():
    if current_user.group.is_section:
        project = current_user.project[0]
    elif not current_user.group.is_section:
        # SPRAWDZIĆ !!!!!!!!
        project = User.query.filter_by(login=current_user.group.name).first().project[0]
    else:
        flash('Dostęp do tej strony posiada tylko zwykły użytkownik', 'warning')
        return redirect(url_for('panel'))
    return render_template('project_view.html', title='Projekt', project=project)


@app.route('/rating', methods=['GET', 'POST'])
@login_required
def rating():
    if not current_user.group.is_section:
        pass
    else:
        flash('Dostęp do tej strony posiada tylko pojedyńczy użytkownik sekcji', 'warning')
        return redirect(url_for('home'))
    return render_template('rating.html', title='Ocenianie prac')