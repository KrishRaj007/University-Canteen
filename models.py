from flask_login import UserMixin
from extensions import mongo, login_manager
from mongo_helpers import id_filter

@login_manager.user_loader
def load_user(user_id):
    user = mongo.db.users.find_one(id_filter(user_id))
    if not user:
        return None
    return User(user)

class User(UserMixin):
    def __init__(self, user_doc):
        self.id       = str(user_doc['_id'])
        self.name     = user_doc['name']
        self.email    = user_doc['email']
        self.password = user_doc['password']
        self.role     = user_doc.get('role', 'student')
