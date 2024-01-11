from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)

# database and migrations object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# create and initialize flask-login
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models
