from flask import Flask
import os

from flask_sqlalchemy import SQLAlchemy
current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,  template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir,"database.sqlite3")
app.config['SECRET_KEY'] = "THISISMYSECRETKEY"

#databse instance
db =  SQLAlchemy(app)

from flaskApp import controllers