from flask_sqlalchemy import SQLAlchemy
from passlib.hash import pbkdf2_sha256

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String())
    admin = db.Column(db.Boolean, default=False)
    watchlists = db.relationship('WatchList', backref='user', lazy=True)

    def __init__(self, username, admin=False, watchlists=[]):
        self.username = username
        self.admin = admin
        self.watchlists = watchlists

    def set_password(self, password):
        pw_hash = pbkdf2_sha256.hash(password)
        self.password = pw_hash

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)


class WatchList(db.Model):
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)
    watchlist = db.Column(db.ARRAY(db.String), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)

    def __init__(self, watchlist, user_id):
        self.watchlist = watchlist
        self.user_id = user_id


def clearTable(tableName):
    try:
        db.session.query(tableName).delete()
        db.session.commit()
    except:
        db.session.rollback()
