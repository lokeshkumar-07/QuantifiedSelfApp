from pytz import timezone
from flaskApp import db
from datetime import datetime
from sqlalchemy.sql import func
import pytz


from flask_login import UserMixin

UTC = pytz.utc

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False) 
    trackers = db.relationship("Tracker", cascade='all, delete-orphan')
    logs = db.relationship("Logs", cascade= 'all, delete-orphan')


    def __repr__(self):
        return f"User('{self.username}')"
    
    def get_id(self):
           return (self.user_id)

class Tracker(db.Model):
    tracker_id = db.Column(db.Integer, primary_key = True)
    tracker_name = db.Column(db.String, nullable = False)
    tracker_description = db.Column(db.String, nullable = False)
    tracker_type = db.Column(db.String, nullable = False)
    choices = db.Column(db.String)
    last_reviewed = db.Column(db.String, nullable = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

class Logs(db.Model):
    log_id = db.Column(db.Integer, primary_key = True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    tracker_name = db.Column(db.String, db.ForeignKey('tracker.tracker_name'))
    when = db.Column(db.DateTime(timezone = True), nullable = False, default=func.now())
    value = db.Column(db.String, nullable = False)
    notes = db.Column(db.String, nullable = False)
    log_tracker_type = db.Column(db.String, db.ForeignKey('tracker.tracker_type'))