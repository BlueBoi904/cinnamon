from enum import unique
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String())
    admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        pw_hash = pbkdf2_sha256.hash(password)
        self.password = pw_hash

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)


def clearTable():
    try:
        db.session.query(User).delete()
        db.session.commit()
    except:
        db.session.rollback()
