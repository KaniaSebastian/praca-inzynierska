from flask import render_template, url_for, flash, redirect, request, Blueprint
from flaskapp import app, db
from flaskapp.models import User, Project, Group
from flaskapp.users.forms import CreateProjectForm, UpdateProjectForm, PointsForm
from flask_login import current_user, login_required
import os
from datetime import datetime
from flaskapp.users.utils import save_image
import sys

users = Blueprint('users', __name__)


@users.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    if not current_user.is_admin and current_user.group.is_section:
        if current_user.project:
            return redirect(url_for('main.project_view'))
        form = CreateProjectForm()
        if form.validate_on_submit():
            file = save_image(form.image.data)
            new_project = Project(title=form.title.data, description=form.description.data,
                                  image_file=file, creators_num=form.creators_num.data,
                                  author=current_user, optional_link=form.url.data)
            db.session.add(new_project)
            db.session.commit()
            flash('Projekt został dodany', 'success')
            return redirect(url_for('users.project'))
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
            user_project.date_posted = datetime.now()
            if form.image.data:
                old_file = user_project.image_file
                file = save_image(form.image.data)
                user_project.image_file = file
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


@users.route('/rating', methods=['GET', 'POST'])
@login_required
def rating():
    if not current_user.is_admin and not current_user.group.is_section:
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
        user_ratings = [{'points': None} for item in range(len(group_projects))]
        form = PointsForm(all_points=user_ratings, points_per_user=group.points_per_user)
        print(str(group.users), file=sys.stdout)
        if form.validate_on_submit():
            for i, single_project in enumerate(group_projects):
                single_project.score = single_project.score + form.all_points[i].data.get('points')
            current_user.did_rate = True
            db.session.commit()
            flash('Punkty zostały przydzielone. Tutaj pojawią się wyniki kiedy zakończy się ocenianie', 'success')
            return redirect(url_for('main.results'))
    else:
        flash('Dostęp do tej strony posiada tylko pojedynczy użytkownik sekcji', 'warning')
        return redirect(url_for('main.home'))
    return render_template('rating.html', title='Ocenianie prac', group=group, group_projects=group_projects, form=form)

