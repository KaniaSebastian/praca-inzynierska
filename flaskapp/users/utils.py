from flaskapp import app
from flaskapp.models import Project
import secrets
import os


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
