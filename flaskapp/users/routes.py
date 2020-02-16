from flask import render_template, url_for, flash, redirect, request, Blueprint
from flaskapp import app, db
from flaskapp.models import User, Project, Group
from flaskapp.users.forms import CreateProjectForm, UpdateProjectForm, PointsForm
from flask_login import current_user, login_required
import os
from datetime import datetime
from flaskapp.users.utils import save_file, create_users_keys
import pytz

users = Blueprint('users', __name__)


@users.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    if not current_user.is_admin and current_user.group.is_containing_sections:
        if current_user.project:
            return redirect(url_for('main.project_view'))
        form = CreateProjectForm()
        if form.validate_on_submit():
            new_file = save_file(form.file.data)

            ip = request.environ.get('HTTP_X_FORWARDED_FOR')
            if ip is None:
                ip = request.remote_addr

            if ip:
                user_ip = ip
            else:
                user_ip = None

            new_project = Project(title=form.title.data, description=form.description.data,
                                  upload_file=new_file, creators_num=form.creators_num.data,
                                  author=current_user, optional_link=form.url.data, last_editor=user_ip,
                                  date_posted=datetime.now(pytz.timezone('Poland')))
            db.session.add(new_project)
            db.session.commit()
            create_users_keys(current_user.login, form.creators_num.data)
            flash('Projekt został dodany', 'success')
            return redirect(url_for('users.access_keys'))
    else:
        flash('Dostęp do tej strony posiada tylko sekcja', 'warning')
        return redirect(url_for('main.home'))
    return render_template('project.html', title='Projekt', form=form, legend='Dodaj projekt')


@users.route('/project/update', methods=['GET', 'POST'])
@login_required
def update_project():
    if not current_user.is_admin:
        if not current_user.project:
            return redirect(url_for('users.project'))
        form = UpdateProjectForm()
        user_project = Project.query.filter_by(author=current_user).first()
        if form.validate_on_submit():
            user_project.title = form.title.data
            user_project.description = form.description.data
            user_project.optional_link = form.url.data
            user_project.date_posted = datetime.now(pytz.timezone('Poland'))

            ip = request.environ.get('HTTP_X_FORWARDED_FOR')
            if ip is None:
                ip = request.remote_addr

            if ip:
                user_ip = ip
            else:
                user_ip = None

            user_project.last_editor = user_ip

            if form.file.data:
                old_file = user_project.upload_file
                new_file = save_file(form.file.data)
                user_project.upload_file = new_file
                os.remove(os.path.join(app.root_path, 'static/projects', old_file))
            db.session.commit()
            flash('Projekt został edytowany', 'success')
            return redirect(url_for('main.project_view'))
        elif request.method == 'GET':
            form.title.data = user_project.title
            form.description.data = user_project.description
            form.url.data = user_project.optional_link
    else:
        flash('Dostęp do tej strony posiada tylko sekcja', 'warning')
        return redirect(url_for('admin.panel'))
    return render_template('project.html', title='Edytuj projekt', form=form, legend='Edytuj projekt')


@users.route('/keys')
@login_required
def access_keys():
    if not current_user.is_admin and current_user.group.is_containing_sections:
        users_group = Group.query.filter_by(name=current_user.login).first()
        if users_group:
            keys = [user.login for user in users_group.users]
        else:
            keys = None
    else:
        flash('Dostęp do tej strony posiada tylko sekcja', 'warning')
        return redirect(url_for('main.home'))
    return render_template('keys.html', title='Klucze dostępu', keys=keys)


@users.route('/rating', methods=['GET', 'POST'])
@login_required
def rating():
    if not current_user.is_admin and not current_user.group.is_containing_sections:
        section = User.query.filter_by(login=current_user.group.name).first()
        group = Group.query.get_or_404(section.group.id)

        group_projects = list()
        for section in group.users:
            section_project = Project.query.filter_by(author=section).first()
            if section_project and section_project.author.login != current_user.group.name:
                group_projects.append(section_project)
        if len(group_projects) == 0:
            flash('Za mało udostępnionych projektów, aby przeprowadzić ocenianie', 'warning')
            return redirect(url_for('main.project_view'))
        user_ratings = [{'points': 0} for item in range(len(group_projects))]
        form = PointsForm(all_points=user_ratings, points_per_user=group.points_per_user)

        if form.validate_on_submit():
            for i, single_project in enumerate(group_projects):
                single_project.score = single_project.score + form.all_points[i].data.get('points')
            current_user.did_rate = True
            db.session.commit()
            flash('Punkty zostały przydzielone', 'success')
            return redirect(url_for('users.rating'))
    else:
        flash('Dostęp do tej strony posiada tylko pojedynczy użytkownik sekcji', 'warning')
        return redirect(url_for('main.home'))
    return render_template('rating.html', title='Ocenianie prac', group=group, group_projects=group_projects, form=form)

