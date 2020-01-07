from flaskapp import app
from flaskapp.models import Project
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
