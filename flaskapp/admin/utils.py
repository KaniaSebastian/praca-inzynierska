from flaskapp import db
from flaskapp.models import User
from sqlalchemy import func
import string
import secrets


def add_users(number_of_users, group):
    while number_of_users > 0:
        alphabet = string.ascii_letters + string.digits
        random_key = ''.join(secrets.choice(alphabet) for i in range(5))
        if User.query.filter_by(login=random_key).first():
            continue
        new_user = User(login=random_key, group=group)
        db.session.add(new_user)
        number_of_users = number_of_users - 1
    db.session.commit()

    if group.is_containing_sections:
        max_number = db.session.query(func.max(User.section_number)).filter_by(group=group).scalar()
        if max_number:
            new_user.section_number = max_number + 1
        else:
            for i, user in enumerate(group.users, 1):
                user.section_number = i
    db.session.commit()
