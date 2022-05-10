from app import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Date, index=True, default=datetime.date(datetime.utcnow()))
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic', passive_deletes=True)
    threads = db.relationship('Thread', backref='author', lazy='dynamic', passive_deletes=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(4096))
    timestamp = db.Column(db.Date, index=True, default=datetime.date(datetime.utcnow()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    tred_id = db.Column(db.Integer, db.ForeignKey('thread.id', ondelete='CASCADE'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    body = db.Column(db.String(4096))
    is_private = db.Column(db.Boolean, default=False, nullable=False)
    timestamp = db.Column(db.Date, index=True, default=datetime.date(datetime.utcnow()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    file_path = db.Column(db.String(512))
    posts = db.relationship('Post', backref="main", lazy="dynamic", passive_deletes=True)

    def __repr__(self):
        return '<Thread {}>'.format(self.body)

