from flask import render_template, url_for, flash, redirect, request, Blueprint
from flaskapp import app, db
from flaskapp.models import User, Project, Group, Comments
from flaskapp.users.forms import CreateProjectForm, UpdateProjectForm, PointsForm
from flaskapp.main.forms import PointsPoolPerProjectForm
from flask_login import current_user, login_required
import os
from datetime import datetime
from flaskapp.users.utils import save_file, create_users_keys
import pytz
from flask_babel import gettext
from random import shuffle, choice

users = Blueprint('users', __name__)


@users.route('/project', methods=['GET', 'POST'])
@login_required
def project():
    if not current_user.is_admin and current_user.group.is_containing_sections:
        if not current_user.project and current_user.group.rating_status == 'disabled_improvement':
            flash(gettext('Teraz trwa poprawa projektów. Nie możesz poprawić projektu jeśli go wcześniej nie udostępniłeś.'), 'warning')
            return redirect(url_for('main.home'))
        if current_user.project:
            return redirect(url_for('main.project_view'))
        form = CreateProjectForm()
        group = current_user.group
        if form.validate_on_submit():
            if current_user.group.rating_status != 'disabled' and current_user.group.rating_status != 'disabled_improvement':
                return redirect(url_for('main.home'))
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
            flash(gettext('Projekt został dodany'), 'success')
            return redirect(url_for('users.access_keys'))
    else:
        flash(gettext('Dostęp do tej strony posiada tylko sekcja'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('project.html', title=gettext('Projekt'), form=form, legend=gettext('Dodaj projekt'), group=group)


@users.route('/project/update', methods=['GET', 'POST'])
@login_required
def update_project():
    if not current_user.is_admin:
        if not current_user.project and current_user.group.rating_status == 'disabled_improvement':
            flash(gettext('Teraz trwa poprawa projektów. Nie możesz poprawić projektu jeśli go wcześniej nie udostępniłeś.'), 'warning')
            return redirect(url_for('main.home'))
        if not current_user.project:
            return redirect(url_for('users.project'))
        form = UpdateProjectForm()
        user_project = Project.query.filter_by(author=current_user).first()
        group = user_project.author.group
        section_keys = [section.login for section in group.users]
        raters_pool_per_project_num = User.query.filter_by(did_rate=True, rating_type='pool_per_project').join(Group, Group.id == User.group_id).filter(Group.name.in_(section_keys), Group.name != user_project.author.login).count()
        if raters_pool_per_project_num == 0:
            raters_pool_per_project_num = 1

        if form.validate_on_submit():
            if current_user.group.rating_status != 'disabled' and current_user.group.rating_status != 'disabled_improvement':
                return redirect(url_for('main.home'))
            #####
            if group.rating_status == 'disabled':
                user_project.title = form.title.data
                user_project.description = form.description.data
                user_project.optional_link = form.url.data
                user_project.date_posted = datetime.now(pytz.timezone('Poland'))
            else:
                user_project.title_improvement = form.title.data
                user_project.description_improvement = form.description.data
                user_project.optional_link_improvement = form.url.data
                user_project.date_posted_improvement = datetime.now(pytz.timezone('Poland'))
            #####

            # get user IP
            ip = request.environ.get('HTTP_X_FORWARDED_FOR')
            if ip is None:
                ip = request.remote_addr

            if ip:
                user_ip = ip
            else:
                user_ip = None

            user_project.last_editor = user_ip

            if form.file.data:
                if group.rating_status == 'disabled':
                    old_file = user_project.upload_file
                    new_file = save_file(form.file.data)
                    user_project.upload_file = new_file
                    os.remove(os.path.join(app.root_path, 'static/projects', old_file))
                else:
                    old_file = user_project.upload_file_improvement
                    new_file = save_file(form.file.data)
                    user_project.upload_file_improvement = new_file
                    if old_file:
                        os.remove(os.path.join(app.root_path, 'static/projects', old_file))

            db.session.commit()
            flash(gettext('Projekt został edytowany'), 'success')
            return redirect(url_for('main.project_view'))
        elif request.method == 'GET':
            if user_project.upload_file_improvement and (group.rating_status == 'disabled_improvement' or group.rating_status == 'enabled_improvement' or group.rating_status == 'ended_improvement'):
                form.title.data = user_project.title_improvement
                form.description.data = user_project.description_improvement
                form.url.data = user_project.optional_link_improvement
            else:
                form.title.data = user_project.title
                form.description.data = user_project.description
                form.url.data = user_project.optional_link
    else:
        flash(gettext('Dostęp do tej strony posiada tylko sekcja'), 'warning')
        return redirect(url_for('admin.panel'))
    return render_template('project.html', title=gettext('Edytuj projekt'), form=form, legend=gettext('Edytuj projekt'),
                           group=group, project=user_project, raters_pool_per_project_num=raters_pool_per_project_num)


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
        flash(gettext('Dostęp do tej strony posiada tylko sekcja'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('keys.html', title=gettext('Klucze dostępu'), keys=keys)


@users.route('/rating', methods=['GET', 'POST'])
@login_required
def rating():
    if not current_user.is_admin and not current_user.group.is_containing_sections:
        # choose random rating type for user
        if not current_user.rating_type:
            current_user.rating_type = choice(['points_pool', 'points_pool_shuffled', 'pool_per_project'])
            db.session.commit()

        section = User.query.filter_by(login=current_user.group.name).first()
        group = Group.query.get_or_404(section.group.id)

        group_projects = list()
        for section in group.users:
            section_project = Project.query.filter_by(author=section).first()
            if section_project and section_project.author.login != current_user.group.name:
                group_projects.append(section_project)
        if len(group_projects) == 0:
            flash(gettext('Za mało udostępnionych projektów, aby przeprowadzić ocenianie'), 'warning')
            return redirect(url_for('main.project_view'))
        user_ratings = [{'points': 0} for item in range(len(group_projects))]

        # for rating_type='pool_per_project' different form is created
        if current_user.rating_type == 'pool_per_project':
            form = PointsPoolPerProjectForm(all_points=user_ratings, points_per_project=group.points_per_project)
        else:
            form = PointsForm(all_points=user_ratings, points_per_user=group.points_per_user)

        # if rating_type for user is "points_pool_shuffled" then shuffle projects for rating
        if current_user.rating_type == "points_pool_shuffled":
            to_shuffle = list(zip(group_projects, form.all_points))
            shuffle(to_shuffle)
            group_projects, form.all_points = zip(*to_shuffle)

        # from validation
        if form.validate_on_submit():
            if current_user.did_rate or group.rating_status != 'enabled':
                return redirect(url_for('main.home'))

            if current_user.rating_type == "points_pool":
                for i, single_project in enumerate(group_projects):
                    single_project.score_points_pool = single_project.score_points_pool + form.all_points[i].data.get('points')
            elif current_user.rating_type == "points_pool_shuffled":
                for i, single_project in enumerate(group_projects):
                    single_project.score_points_pool_shuffled = single_project.score_points_pool_shuffled + form.all_points[i].data.get('points')
            else:
                for i, single_project in enumerate(group_projects):
                    single_project.score_pool_per_project += form.all_points[i].data.get('points')
                    distinction = int(form.all_points[i].data.get('distinction'))
                    single_project.user_distinctions += distinction

            for i, single_project in enumerate(group_projects):
                new_comments = Comments(comment_star_1=form.all_points[i].data.get('comment_star_1'),
                                        comment_star_2=form.all_points[i].data.get('comment_star_2'),
                                        comment_wish=form.all_points[i].data.get('comment_wish'),
                                        author=current_user, project=single_project)
                db.session.add(new_comments)

            current_user.did_rate = True
            db.session.commit()
            flash(gettext('Punkty zostały przydzielone'), 'success')
            return redirect(url_for('users.rating'))
    else:
        flash(gettext('Dostęp do tej strony posiada tylko pojedynczy użytkownik sekcji'), 'warning')
        return redirect(url_for('main.home'))
    return render_template('rating.html', title=gettext('Ocenianie prac'), group=group, group_projects=group_projects, form=form)

