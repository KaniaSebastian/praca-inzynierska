from flaskapp import db
from flaskapp.models import User
import os
import shutil

if __name__ == '__main__':
    folder = 'flaskapp/static/projects'
    for filename in os.listdir(folder):
        if filename == '.gitignore':
            continue
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    db.drop_all()
    db.create_all()

    admin = User(login='admin', is_admin=True, password='$2b$12$y2NuF2eQtopJw72T0YiiDe5SponuGrVEJ/jl5OttikAKsd5M1M6aS')
    db.session.add(admin)

    db.session.commit()

    print(User.query.all())


'''
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()
print(bcrypt.generate_password_hash('').decode('utf-8'))
'''