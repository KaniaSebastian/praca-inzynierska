from flask import render_template, url_for, flash, redirect, request, Blueprint
from flaskapp.models import User, Project, Group
from flaskapp.main.forms import LoginForm
from flask_login import login_user, logout_user, current_user, login_required

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('home.html', title='Strona główna')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and user.is_admin:
            return redirect(url_for('admin.admin_login', admin_name=form.login.data))
        if user:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Zalogowałeś się', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Logowanie nieudane. Sprawdź poprawność wpisanych danych', 'danger')

    return render_template('login.html', title='Zaloguj się', form=form)


@main.route('/logout')
def logout():
    logout_user()
    flash('Wylogowałeś się', 'success')
    return redirect(url_for('main.home'))


@main.route('/project/view', defaults={'section_id': None})
@main.route('/project/view/<int:section_id>')
@login_required
def project_view(section_id):
    if not current_user.is_admin and current_user.group.is_section:
        project = current_user.project[0]
    elif not current_user.is_admin and not current_user.group.is_section:
        user = User.query.filter_by(login=current_user.group.name).first()
        project = user.project[0]
    elif current_user.is_admin:
        project = Project.query.filter_by(user_id=section_id).first()
    return render_template('project_view.html', title='Projekt', project=project)


@main.route('/results', defaults={'group_id': None})
@main.route('/results/<int:group_id>')
@login_required
def results(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        user_project = None
    else:
        if current_user.group.is_section:
            group = current_user.group
            user_project = current_user.project[0]
        else:
            section = User.query.filter_by(login=current_user.group.name).first()
            group = section.group
            user_project = section.project[0]

    group_projects = dict()
    for counter, section in enumerate(group.users, 1):
        section_project = Project.query.filter_by(author=section).first()
        if section_project:
            group_projects[counter] = section_project
    group_projects_sorted = {k: v for k, v in sorted(group_projects.items(), key=lambda item: item[1].score, reverse=True)}  # sorting by score

    users_that_rated_num = 0
    for section in group.users:
        section_group = Group.query.filter_by(name=section.login).first()
        if section_group:
            for user in section_group.users:
                if user.did_rate:
                    users_that_rated_num = users_that_rated_num + 1

    return render_template('results.html', title='Wyniki', group=group, group_projects=group_projects,
                           group_projects_sorted=group_projects_sorted, user_project=user_project,
                           users_that_rated_num=users_that_rated_num)