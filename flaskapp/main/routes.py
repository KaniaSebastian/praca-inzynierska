from flask import render_template, url_for, flash, redirect, request, Blueprint
from flaskapp.models import User, Project, Group
from flaskapp.main.forms import LoginForm
from flask_login import login_user, logout_user, current_user, login_required
from flask_babel import gettext
import sys

main = Blueprint('main', __name__)


@main.route('/')
def home():
    if not current_user.is_anonymous and not current_user.is_admin:
        if current_user.group.is_containing_sections:
            group = current_user.group
        elif not current_user.group.is_containing_sections:
            section = User.query.filter_by(login=current_user.group.name).first()
            group = section.group
    else:
        group = None
    return render_template('home.html', title=gettext('Strona główna'), group=group)


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
            remember_me_value = int(form.remember.data == True)
            return redirect(url_for('admin.admin_login', admin_name=form.login.data, remember=remember_me_value))
        if user:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(gettext('Zalogowałeś się'), 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(gettext('Logowanie nieudane. Sprawdź poprawność wpisanych danych'), 'danger')

    return render_template('login.html', title=gettext('Zaloguj się'), form=form)


@main.route('/logout')
def logout():
    logout_user()
    flash(gettext('Wylogowałeś się'), 'success')
    return redirect(url_for('main.home'))


@main.route('/project/view', defaults={'section_id': None})
@main.route('/project/view/<int:section_id>')
@login_required
def project_view(section_id):
    if not current_user.is_admin and current_user.group.is_containing_sections:
        project = current_user.project
    elif not current_user.is_admin and not current_user.group.is_containing_sections:
        user = User.query.filter_by(login=current_user.group.name).first()
        project = user.project
    elif current_user.is_admin:
        project = Project.query.filter_by(user_id=section_id).first()
    group = project.author.group
    section_keys = [section.login for section in group.users]
    raters_pool_per_project_num = User.query.filter_by(did_rate=True, rating_type='pool_per_project').join(Group, Group.id == User.group_id).filter(Group.name.in_(section_keys), Group.name != project.author.login).count()
    if raters_pool_per_project_num == 0:
        raters_pool_per_project_num = 1

    return render_template('project_view.html', title=gettext('Projekt'), project=project, group=group, raters_pool_per_project_num=raters_pool_per_project_num)


@main.route('/results', defaults={'group_id': None})
@main.route('/results/<int:group_id>')
@login_required
def results(group_id):
    if current_user.is_admin:
        group = Group.query.get_or_404(group_id)
        user_project = None
    else:
        if current_user.group.is_containing_sections:
            group = current_user.group
            if current_user.project:
                user_project = current_user.project
            else:
                user_project = None
        else:
            section = User.query.filter_by(login=current_user.group.name).first()
            group = section.group
            if section.project:
                user_project = section.project
            else:
                user_project = None

    group_projects = Project.query.join(User).filter(User.group == group).order_by(User.section_number.asc()).all()

    section_keys = [section.login for section in group.users]
    users_that_rated_num = User.query.filter_by(did_rate=True).join(Group, Group.id == User.group_id).filter(Group.name.in_(section_keys)).count()

    evaluators_nums = dict()
    evaluators_nums['points_pool_evaluators'] = User.query.filter_by(did_rate=True, rating_type='points_pool').join(Group, Group.id == User.group_id).filter(Group.name.in_(section_keys)).count()
    evaluators_nums['points_pool_shuffled_evaluators'] = User.query.filter_by(did_rate=True, rating_type='points_pool_shuffled').join(Group, Group.id == User.group_id).filter(Group.name.in_(section_keys)).count()
    evaluators_nums['pool_per_project_evaluators'] = User.query.filter_by(did_rate=True, rating_type='pool_per_project').join(Group, Group.id == User.group_id).filter(Group.name.in_(section_keys)).count()

    # numbers needed to calculate score for 3 method
    raters_pool_per_project_nums = dict()
    for project in group_projects:
        raters_num_temp = User.query.filter_by(did_rate=True, rating_type='pool_per_project').join(Group, Group.id == User.group_id).filter(Group.name.in_(section_keys), Group.name != project.author.login).count()
        if raters_num_temp == 0:
            raters_num_temp = 1
        raters_pool_per_project_nums[project] = raters_num_temp

    # sorting for method 3 results
    group_projects_sorted = sorted(group_projects, key=lambda project: project.score_pool_per_project/(raters_pool_per_project_nums.get(project)), reverse=True)

    return render_template('results.html', title=gettext('Wyniki'), group=group, group_projects=group_projects,
                           group_projects_sorted=group_projects_sorted, user_project=user_project,
                           users_that_rated_num=users_that_rated_num, raters_pool_per_project_nums=raters_pool_per_project_nums, evaluators_nums=evaluators_nums)
