from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.init_app(app)

db = SQLAlchemy(app)

from app import routes, models
