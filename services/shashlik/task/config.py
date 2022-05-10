import os

app_dir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uhn7/K4sepyMIQlNxiVhC8EQQGj+cQqPfvba98d1Vgg='
    UPLOAD_FOLDER = os.path.join(app_dir, 'uploads/')
    ALLOWED_EXTENSIONS = ['png', 'gif', 'jpg', 'jpeg', 'bmp', 'svg']
    MAX_CONTENT_LENGTH = 8 * 1000 * 1000
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(app_dir, 'app.db')
