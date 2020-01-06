from flaskapp import db, app
from flaskapp.models import User, Project
import os

for project in Project.query.all():
    old_file = project.image_file
    os.remove(os.path.join(app.root_path, 'static/projects', old_file))
db.drop_all()
db.create_all()

# admin_group = Group(name='admin_group')
# admin = User(login='admin', is_admin=True, group=admin_group)
admin = User(login='admin', is_admin=True)
db.session.add(admin)

db.session.commit()

print(User.query.all())

'''
from flaskapp import db
from flaskapp.models import User
User.query.all()
'''

'''
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
bcrypt.generate_password_hash('').decode('utf-8')
'''