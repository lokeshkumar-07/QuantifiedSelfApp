from flask import redirect, render_template, request, url_for, flash
from flaskApp import app
from flaskApp.models import User, Tracker, Logs
from flaskApp.forms import RegistrationForm, LoginForm

from flaskApp import db

from flask_bcrypt import Bcrypt 

from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from matplotlib import pyplot as plt


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#Forms Classes

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
@login_required
def home():
    trackers = Tracker
    return render_template('home.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Your are now able to login', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title = 'Register', form = form )

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by( username = form.username.data ).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember= form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessfull. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('welcome'))

@app.route('/trackers/<int:user_id>')
@login_required
def user_trackers(user_id):
    trackers = Tracker.query.filter_by(user_id = user_id).all()
    logs = Logs.query.filter_by(user_id = user_id).all()

    return render_template('view_tracker.html', trackers = trackers, title="Your Trackers", logs= logs)

@app.route('/addTracker/<int:user_id>', methods = ['GET', 'POST'])
@login_required
def add_tracker(user_id):
    if request.method == 'POST':
        
        tracker_name = request.form.get('t_name')
        tracker_description = request.form.get('t_desp')
        tracker_type = request.form.get('t_type')
        tracker_choices = request.form.get('t_choices')

        tracker = Tracker.query.filter_by(tracker_name = tracker_name, user_id = user_id).first()
        if tracker :
            message = "Tracker already exists!"
            return render_template('add_tracker.html', title="Add tracker", msg = message )
        else:
            tracker = Tracker(tracker_name = tracker_name, tracker_description = tracker_description, tracker_type = tracker_type, choices = tracker_choices, user_id = user_id )
            db.session.add(tracker)
            db.session.commit()

            return redirect(url_for('user_trackers', user_id = user_id))
    return render_template('add_tracker.html', title="Add tracker")

@app.route('/deletetracker/<tracker_name>/<int:user_id>')
@login_required
def delate_tracker(tracker_name, user_id):
    tracker = Tracker.query.filter_by(tracker_name = tracker_name, user_id = user_id).first()
    db.session.delete(tracker)
    log = Logs.query.filter_by(tracker_name = tracker_name, user_id = user_id).all()
    for i in log:
        db.session.delete(i)
    db.session.commit()
    return redirect(url_for('user_trackers', user_id = user_id))

@app.route('/viewlogs/<tracker_name>/<int:user_id>')
@login_required
def view_logs(tracker_name, user_id):
    logs = Logs.query.filter_by(tracker_name = tracker_name, user_id = user_id).all()

    dev_x = []
    dev_y = []
    log_type = ""
    for log in logs:
        if log.log_tracker_type == 'Numeric':
            dev_x.append(log.when.strftime("%d-%m-%y %a %H:%M:%S"))
            dev_y.append(int(log.value))
            log_type = "Numeric"
    

    if len(dev_x) != 0:
        plt.cla()
        plt.plot(dev_x,dev_y)
        plt.xlabel("Time")
        plt.ylabel("Values")
        plt.savefig('flaskApp/static/graph.png')
        
    return render_template('view_logs.html', tracker_name = tracker_name , title="Your Logs", logs = logs, log_type = log_type)

@app.route('/addlogs/<tracker_name>/<int:user_id>' , methods = ['GET', 'POST'])
@login_required
def add_logs(tracker_name, user_id):
    tracker = Tracker.query.filter_by(tracker_name = tracker_name, user_id = user_id).first()
    if request.method == 'POST':
        value = request.form.get('value')
        notes = request.form.get('notes')

        log = Logs(user_id = user_id, value = value, notes = notes, log_tracker_type = tracker.tracker_type, tracker_name = tracker_name)
        
        db.session.add(log)
        db.session.commit()

        log1 = Logs.query.filter_by(user_id = user_id , tracker_name = tracker_name).all()

        tracker = Tracker.query.filter_by(user_id = user_id, tracker_name = tracker_name).first()
        tracker.last_reviewed = log1[-1].when.strftime("%d-%m-%y %a %H:%M:%S")
        db.session.commit()

        return redirect(url_for('user_trackers', user_id = user_id))   

    multiple_choice_list = []
    if tracker.tracker_type == 'Multiple Choice':
        multiple_choice_list = tracker.choices.split(",")
        
    return render_template('add_logs.html', tracker = tracker, multiple_choice_list = multiple_choice_list)


@app.route('/editlogs/<int:user_id>/<tracker_name>/<int:log_id>', methods = ['GET', 'POST'])
@login_required
def update_logs(user_id, tracker_name, log_id):
    log = Logs.query.filter_by(user_id = user_id, tracker_name = tracker_name, log_id = log_id).first()
    tracker = Tracker.query.filter_by(user_id = user_id, tracker_name = tracker_name).first()

    if request.method == "POST":
        value = request.form.get('value')
        notes = request.form.get('notes')
        log = Logs.query.filter_by(user_id = user_id, tracker_name = tracker_name, log_id = log_id).first()

        log.value = value
        log.notes = notes
        db.session.commit()

        return redirect(url_for('view_logs',tracker_name = tracker_name , user_id = user_id))

    multiple_choice_list = []
    if tracker.tracker_type == "Multiple Choice":
        multiple_choice_list = tracker.choices.split(",")
    return render_template('update_logs.html', title="Edit Log",tracker = tracker, log = log, multiple_choice_list = multiple_choice_list)

@app.route('/deletelogs/<int:user_id>/<tracker_name>/<int:log_id>')
@login_required
def delete_log(user_id, tracker_name, log_id):
    log = Logs.query.filter_by(user_id = user_id, tracker_name = tracker_name, log_id = log_id).first()
    db.session.delete(log)
    db.session.commit()

    return redirect(url_for('view_logs',tracker_name = tracker_name , user_id = user_id))
