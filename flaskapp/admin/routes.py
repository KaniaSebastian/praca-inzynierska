from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, Response
from flaskapp import app, db, bcrypt, admin_password
from flaskapp.models import User, Project, Group
from flaskapp.admin.forms import AdminCreateGroup, AdminLoginForm, SetUploadTimeForm, SetRatingForm, EditGroupNameForm
from flaskapp.admin.utils import remove_accents, add_users
from flask_login import login_user, current_user, login_required
import os

admin = Blueprint('admin', __name__)


@admin.route('/login/<string:admin_name>/<int:remember>', methods=['GET', 'POST'])
def admin_login(admin_name, remember):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = AdminLoginForm()
    if admin_name and not form.login.data:
        form.login.data = admin_name
        form.remember.data = True if remember == 1 else False
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and user.is_admin and bcrypt.check_password_hash(admin_password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Zalogowałeś się', 'success')
            return redirect(next_page) if next_page else redirect(url_for('admin.panel'))
        else:
            flash('Logowanie nieudane. Sprawdź poprawność wpisanych danych', 'danger')
    return render_template('admin/login_admin.html', title='Zaloguj się jako administrator', form=form)


@admin.route('/panel', methods=['GET', 'POST'])
@login_required
def panel():
    if current_user.is_admin:
        groups = Group.query.filter_by(is_containing_sections=True).all()
        browser = request.user_agent.browser
        if browser != 'chrome' and browser != 'edge':
            flash('Panel administracyjny działa w pełni poprawnie tylko na przeglądarkach Chrome oraz Edge', 'warning')
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/panel.html', title='Panel administracyjny', groups=groups)


@admin.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if current_user.is_admin:
        form = AdminCreateGroup()
        if form.validate_on_submit():

            new_group = Group(name=form.name.data, is_containing_sections=True, subject=form.subject.data)
            db.session.add(new_group)
            db.session.commit()

            users_number = form.number.data
            add_users(users_number, new_group)

            flash('Grupa została utworzona', 'success')
            return redirect(url_for('admin.panel'))
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/create_group.html', title='Panel administracyjny', form=form)

# change url in manage_group.html if route changed
@admin.route('/delete_group/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        for section in group.users:
            if section.project:
                section_project = Project.query.filter_by(author=section).first()
                old_file = section_project.upload_file
                os.remove(os.path.join(app.root_path, 'static/projects', old_file))

            section_users_group = Group.query.filter_by(name=section.login).first()
            if section_users_group:
                for user in section_users_group.users:
                    db.session.delete(user)
                db.session.delete(section_users_group)

        db.session.delete(group)
        db.session.commit()
        flash('Grupa została usunięta', 'success')
        return redirect(url_for('admin.manage_groups'))
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))


@admin.route('/create_section_keys/<int:group_id>', methods=['GET', 'POST'])
@login_required
def create_section_keys(group_id):
    if current_user.is_admin:
        group = Group.query.filter_by(id=group_id).first()
        is_any_project = False
        for section in group.users:
            if section.project and not Group.query.filter_by(name=section.login).first():
                is_any_project = True
                users_num = section.project.creators_num
                new_group = Group(name=section.login, is_containing_sections=False)
                db.session.add(new_group)
                db.session.commit()

                add_users(users_num, new_group)

        if is_any_project:
            flash('Klucze zostały wygenerowane', 'success')
        else:
            flash('Nowe klucze mogą być wygenerowane (automatycznie) tylko dla sekcji które przesłały już projekt lub'
                  ' nie posiadają jeszcze użytkowników', 'warning')
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return redirect(url_for('admin.sections', group_id=group_id))


@admin.route('/add_user/<int:section_id>', methods=['GET', 'POST'])
@login_required
def add_user(section_id):
    if current_user.is_admin:
        section = User.query.get_or_404(section_id)
        users_group = Group.query.filter_by(name=section.login).first()
        if users_group:
            users_num = 1
            add_users(users_num, users_group)

            flash('Użytkownik został dodany', 'success')
        else:
            new_group = Group(name=section.login, is_containing_sections=False)
            db.session.add(new_group)
            db.session.commit()

            users_num = 1
            add_users(users_num, new_group)

            flash('Użytkownik został dodany', 'success')

    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return redirect(url_for('admin.sections', group_id=section.group_id))


@admin.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
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
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return redirect(url_for('admin.sections', group_id=user_section.group_id))


@admin.route('/add-section/<int:group_id>', methods=['GET', 'POST'])
@login_required
def add_section(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        users_num = 1
        add_users(users_num, group)
        flash('Sekcja została dodana', 'success')
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return redirect(url_for('admin.sections', group_id=group_id))


@admin.route('/delete-section/<int:section_id>', methods=['GET', 'POST'])
@login_required
def delete_section(section_id):
    if current_user.is_admin:
        section_to_delete = User.query.get_or_404(section_id)
        section_id = section_to_delete.group.id

        section_users_group = Group.query.filter_by(name=section_to_delete.login).first()
        if section_users_group:
            for user in section_users_group.users:
                db.session.delete(user)
            db.session.delete(section_users_group)

        if section_to_delete.project:
            section_project = Project.query.filter_by(author=section_to_delete).first()
            old_file = section_project.upload_file
            os.remove(os.path.join(app.root_path, 'static/projects', old_file))

        db.session.delete(section_to_delete)
        db.session.commit()
        flash('Sekcja została usunięta', 'success')
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return redirect(url_for('admin.sections', group_id=section_id))


@admin.route('/sections/<int:group_id>')
@login_required
def sections(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        user_groups = list()
        for section in group.users:
            user_groups.append(Group.query.filter_by(name=section.login).first())
        if not group.is_containing_sections:
            return redirect((url_for('admin.panel')))
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/sections.html', title='Sekcje', group=group, user_groups=user_groups)


@admin.route('/projects/<int:group_id>')
@login_required
def projects(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        if not group.is_containing_sections:
            abort(404)
        number_of_sections = len(group.users)
        projects = list()
        for section in group.users:
            project = Project.query.filter_by(author=section).first()
            if project:
                projects.append(project)
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/projects.html', title='Projekt', projects=projects, number_of_sections=number_of_sections)


@admin.route('/manage-groups', methods=['GET', 'POST'])
@login_required
def manage_groups():
    if current_user.is_admin:
        browser = request.user_agent.browser
        if browser != 'chrome' and browser != 'edge':
            flash('Panel administracyjny działa w pełni poprawnie tylko na przeglądarkach Chrome oraz Edge', 'warning')
        set_upload_time_form = SetUploadTimeForm()
        set_rating_form = SetRatingForm()
        group_name_form = EditGroupNameForm()
        groups = Group.query.filter_by(is_containing_sections=True).all()

        if set_upload_time_form.submitTime.data and set_upload_time_form.validate():
            group = Group.query.get_or_404(set_upload_time_form.selected_group_id.data)
            group.upload_time = set_upload_time_form.upload_time.data
            db.session.commit()
            flash('Czas na udostępnienie projektu został zaktualizowany', 'success')
            return redirect(url_for('admin.manage_groups'))
        else:
            for error in set_upload_time_form.upload_time.errors:
                flash(error, 'danger')

        if set_rating_form.submitRating.data and set_rating_form.validate():
            group = Group.query.get_or_404(set_rating_form.selected_group_id.data)
            group.rating_status = set_rating_form.rating_status.data
            group.points_per_user = set_rating_form.points.data
            db.session.commit()
            if set_rating_form.rating_status.data == 'enabled':
                flash('Ocenianie zostało włączone', 'success')
            elif set_rating_form.rating_status.data == 'disabled':
                flash('Ocenianie zostało wyłączone', 'success')
            else:
                flash('Ocenianie zostało zakończone', 'success')
            return redirect(url_for('admin.manage_groups'))
        else:
            for error in set_rating_form.points.errors:
                flash(error, 'danger')

        if group_name_form.submitName.data and group_name_form.validate():
            group = Group.query.get_or_404(group_name_form.selected_group_id.data)
            group.name = group_name_form.name.data
            group.subject = group_name_form.subject.data
            db.session.commit()
            flash('Nazwa grupy została zmieniona', 'success')
            return redirect(url_for('admin.manage_groups'))
        else:
            for error in group_name_form.name.errors:
                flash(error, 'danger')
            for error in group_name_form.subject.errors:
                flash(error, 'danger')

    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/manage_groups.html', title='Zarządzanie grupami', groups=groups,
                           set_upload_time_form=set_upload_time_form, set_rating_form=set_rating_form, group_name_form=group_name_form)


@admin.route('/generate-csv/<int:group_id>')
@login_required
def generate_csv(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)

        def generate():
            group = Group.query.get_or_404(group_id)
            group_name_with_subject = remove_accents(group.name) + ' (' + remove_accents(group.subject) + ')'
            header = ('Grupa:', group_name_with_subject)
            yield ",".join(header) + '\n'
            header = ("Sekcja", "Klucz dostepu")
            yield ",".join(header) + '\n\n'

            for n in range(len(group.users)):
                group_users = Group.query.filter_by(name=group.users[n].login).first()
                section = '\n' + 'Sekcja ' + str(n+1)
                if group_users:
                    row = (section, group.users[n].login, 'Uzytkownicy:')
                else:
                    row = (section, group.users[n].login)
                yield ','.join(row) + '\n'

                if group_users:
                    for user in group_users.users:
                        row = ('', '', user.login)
                        yield ','.join(row) + '\n'
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=" + remove_accents(group.subject) + '-' + remove_accents(group.name.replace(" ", "_")) + ".csv"})


@admin.route('/results-csv/<int:group_id>')
@login_required
def results_csv(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        def generate():
            group = Group.query.get_or_404(group_id)
            group_name_with_subject = remove_accents(group.name) + ' (' + remove_accents(group.subject) + ')'
            header = ('Grupa:', group_name_with_subject)
            yield ",".join(header) + '\n'
            header = ("Sekcja", "Wynik")
            yield ",".join(header) + '\n\n'

            for n, section in enumerate(group.users, 1):
                section_name = '\n' + 'Sekcja ' + str(n)
                section_score = (str(section.project.score) if section.project else '---')
                row = (section_name, section_score)
                yield ','.join(row) + '\n'
    else:
        flash('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony', 'warning')
        return redirect(url_for('main.home'))
    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=" + remove_accents(group.subject) + '-' + remove_accents(group.name.replace(" ", "_")) + '-wyniki' + ".csv"})
