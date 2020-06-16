from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, Response
from flaskapp import app, db, bcrypt
from flaskapp.models import User, Project, Group
from flaskapp.admin.forms import CreateGroupForm, AdminLoginForm, SetUploadTimeForm, SetRatingForm, EditGroupNameForm, \
    AddAdminForm, ChangePasswordForm
from flaskapp.admin.utils import add_users
from flask_login import login_user, current_user, login_required
import os
from werkzeug.urls import url_quote
from flask_babel import gettext

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
        if user and user.is_admin and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                flash(gettext('Zalogowałeś się'), 'success')
                return redirect(next_page)
            elif bcrypt.check_password_hash(current_user.password, 'admin'):
                flash(gettext('Zalogowałeś się. Ze względów bezpieczeństwa musisz ustawić nowe hasło.'), 'warning')
                return redirect(url_for('admin.change_password'))
            else:
                flash(gettext('Zalogowałeś się'), 'success')
                return redirect(url_for('admin.panel'))
        else:
            flash(gettext('Logowanie nieudane. Sprawdź poprawność wpisanych danych'), 'danger')
    return render_template('admin/login_admin.html', title=gettext('Zaloguj się jako administrator'), form=form)


@admin.route('/panel', methods=['GET', 'POST'])
@login_required
def panel():
    if current_user.is_admin:
        groups = current_user.admin_groups
        browser = request.user_agent.browser
        if browser != 'chrome' and browser != 'edge':
            flash(gettext('Panel administracyjny działa w pełni poprawnie tylko na przeglądarkach Chrome oraz Edge'), 'warning')
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/panel.html', title=gettext('Panel administracyjny'), groups=groups)


@admin.route('/create-group', methods=['GET', 'POST'])
@login_required
def create_group():
    if current_user.is_admin:
        form = CreateGroupForm()
        if form.validate_on_submit():
            new_group = Group(name=form.name.data, is_containing_sections=True, subject=form.subject.data, admin=current_user)
            db.session.add(new_group)
            db.session.commit()
            users_number = form.number.data
            add_users(users_number, new_group)
            flash(gettext('Grupa została utworzona'), 'success')
            return redirect(url_for('admin.panel'))
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/create_group.html', title=gettext('Panel administracyjny'), form=form)


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
        flash(gettext('Grupa została usunięta'), 'success')
        return redirect(url_for('admin.manage_groups'))
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))


@admin.route('/add_user/<int:section_id>', methods=['GET', 'POST'])
@login_required
def add_user(section_id):
    if current_user.is_admin:
        section = User.query.get_or_404(section_id)
        users_group = Group.query.filter_by(name=section.login).first()
        if users_group:
            users_num = 1
            add_users(users_num, users_group)

            flash(gettext('Użytkownik został dodany'), 'success')
        else:
            new_group = Group(name=section.login, is_containing_sections=False)
            db.session.add(new_group)
            db.session.commit()

            users_num = 1
            add_users(users_num, new_group)

            flash(gettext('Użytkownik został dodany'), 'success')

    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
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
        flash(gettext('Użytkownik został usunięty'), 'success')
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return redirect(url_for('admin.sections', group_id=user_section.group_id))


@admin.route('/add-section/<int:group_id>', methods=['GET', 'POST'])
@login_required
def add_section(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        users_num = 1
        add_users(users_num, group)
        flash(gettext('Sekcja została dodana'), 'success')
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
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
        flash(gettext('Sekcja została usunięta'), 'success')
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return redirect(url_for('admin.sections', group_id=section_id))


@admin.route('/sections/<int:group_id>')
@login_required
def sections(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        if current_user.id != group.admin_id:
            flash(gettext('Nie masz dostępu do tej grupy'), 'warning')
            return redirect(url_for('main.home'))
        user_groups = list()
        for section in group.users:
            user_groups.append(Group.query.filter_by(name=section.login).first())
        if not group.is_containing_sections:
            return redirect((url_for('admin.panel')))
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/sections.html', title=gettext('Sekcje'), group=group, user_groups=user_groups)


@admin.route('/projects/<int:group_id>')
@login_required
def projects(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        if not group.is_containing_sections:
            abort(404)
        if current_user.id != group.admin_id:
            flash(gettext('Nie masz dostępu do tej grupy'), 'warning')
            return redirect(url_for('main.home'))
        number_of_sections = len(group.users)
        projects = list()
        for section in group.users:
            project = Project.query.filter_by(author=section).first()
            if project:
                projects.append(project)
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/projects.html', title=gettext('Projekt'), projects=projects, number_of_sections=number_of_sections)


@admin.route('/manage-groups', methods=['GET', 'POST'])
@login_required
def manage_groups():
    if current_user.is_admin:
        browser = request.user_agent.browser
        if browser != 'chrome' and browser != 'edge':
            flash(gettext('Panel administracyjny działa w pełni poprawnie tylko na przeglądarkach Chrome oraz Edge'), 'warning')
        set_upload_time_form = SetUploadTimeForm()
        set_rating_form = SetRatingForm()
        group_name_form = EditGroupNameForm()
        groups = current_user.admin_groups

        if set_upload_time_form.submitTime.data and set_upload_time_form.validate():
            group = Group.query.get_or_404(set_upload_time_form.selected_group_id.data)
            group.upload_time = set_upload_time_form.upload_time.data
            db.session.commit()
            flash(gettext('Czas na udostępnienie projektu został zaktualizowany'), 'success')
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
                flash(gettext('Ocenianie zostało włączone'), 'success')
            elif set_rating_form.rating_status.data == 'disabled':
                flash(gettext('Ocenianie zostało wyłączone'), 'success')
            else:
                flash(gettext('Ocenianie zostało zakończone'), 'success')
            return redirect(url_for('admin.manage_groups'))
        else:
            for error in set_rating_form.points.errors:
                flash(error, 'danger')

        if group_name_form.submitName.data and group_name_form.validate():
            group = Group.query.get_or_404(group_name_form.selected_group_id.data)
            group.name = group_name_form.name.data
            group.subject = group_name_form.subject.data
            db.session.commit()
            flash(gettext('Nazwa grupy została zmieniona'), 'success')
            return redirect(url_for('admin.manage_groups'))
        else:
            for error in group_name_form.name.errors:
                flash(error, 'danger')
            for error in group_name_form.subject.errors:
                flash(error, 'danger')

    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/manage_groups.html', title=gettext('Zarządzanie grupami'), groups=groups,
                           set_upload_time_form=set_upload_time_form, set_rating_form=set_rating_form, group_name_form=group_name_form)


@admin.route('/generate-csv/<int:group_id>')
@login_required
def generate_csv(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)

        def generate():
            group = Group.query.get_or_404(group_id)
            group_name_with_subject = group.name + ' (' + group.subject + ')'
            header = (gettext('Grupa:'), group_name_with_subject)
            yield ",".join(header) + '\n'
            header = (gettext("Sekcja"), gettext("Klucz dostepu"))
            yield ",".join(header) + '\n\n'

            for n in range(len(group.users)):
                group_users = Group.query.filter_by(name=group.users[n].login).first()
                section = '\n' + gettext('Sekcja ') + str(group.users[n].section_number)
                if group_users:
                    row = (section, group.users[n].login, gettext('Uzytkownicy:'))
                else:
                    row = (section, group.users[n].login)
                yield ','.join(row) + '\n'

                if group_users:
                    for user in group_users.users:
                        row = ('', '', user.login)
                        yield ','.join(row) + '\n'
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    filename = group.subject + '-' + group.name.replace(" ", "_") + ".csv"
    filename = filename.encode('utf-8')
    filename = url_quote(filename)
    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=" + filename})


@admin.route('/results-csv/<int:group_id>')
@login_required
def results_csv(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)

        def generate():
            group = Group.query.get_or_404(group_id)
            group_name_with_subject = group.name + ' (' + group.subject + ')'
            header = (gettext('Grupa:'), group_name_with_subject)
            yield ",".join(header) + '\n'
            header = (gettext("Sekcja"), gettext("Wynik"))
            yield ",".join(header) + '\n\n'

            for section in group.users:
                section_name = '\n' + gettext('Sekcja ') + str(section.section_number)
                section_project_title = section.project.title if section.project else '---'
                section_score = (str(section.project.score) if section.project else '---')
                row = (section_name, section_project_title, section_score)
                yield ','.join(row) + '\n'
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    filename = group.subject + '-' + group.name.replace(" ", "_") + gettext('-wyniki') + ".csv"
    filename = filename.encode('utf-8')
    filename = url_quote(filename)
    return Response(generate(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=" + filename})


@admin.route('/add-admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if current_user.is_admin:
        form = AddAdminForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
            new_admin = User(login=form.login.data, is_admin=True, password=hashed_password)
            db.session.add(new_admin)
            db.session.commit()
            flash(gettext('Nowe konto administratora zostało utworzone'), 'success')
            return redirect(url_for('admin.panel'))
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/add_admin.html', title=gettext('Dodaj administratora'), form=form)


@admin.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if current_user.is_admin:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash(gettext('Hasło zostało zmienione'), 'success')
            return redirect(url_for('admin.panel'))
    else:
        flash(gettext('Musisz mieć uprawnienia administratora, aby uzyskać dostęp do tej strony'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('admin/change_password.html', title=gettext('Dodaj administratora'), form=form)


