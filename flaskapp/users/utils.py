from flaskapp import app, db
from flaskapp.models import Project, Group
from flaskapp.admin.utils import add_users
import secrets
import os


def save_file(file):
    _, extension = os.path.splitext(file.filename)
    upload_file_name = secrets.token_hex(5) + extension
    while True:
        if Project.query.filter_by(upload_file=upload_file_name).first():
            continue
        else:
            break
    file_path = os.path.join(app.root_path, 'static/projects', upload_file_name)
    file.save(file_path)
    return upload_file_name


def create_users_keys(section_login, number_of_users):
    if not Group.query.filter_by(name=section_login).first():
        new_group = Group(name=section_login, is_containing_sections=False)
        db.session.add(new_group)
        db.session.commit()
        add_users(number_of_users, new_group)
        return True
    else:
        return False
