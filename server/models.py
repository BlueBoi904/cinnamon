from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256
# from flask_login import LoginManager

db = SQLAlchemy()


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())

    def set_password(self, password):
        pw_hash = pbkdf2_sha256.hash(password)
        print(pw_hash)
        self.password_hash = pw_hash

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)
