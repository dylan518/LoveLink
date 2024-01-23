from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

database_url = os.environ.get('DATABASE_URL')
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    raise RuntimeError("DATABASE_URL not set")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Your Google Client ID
CLIENT_ID = '1038325471078-255fgp3191kfd7sfrsbqqcbiim4vonq1.apps.googleusercontent.com'
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    interests = db.relationship('Interest', backref='user', lazy=True)  # Relationship to Interest

class Interest(db.Model):
    __tablename__ = 'interests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.String(), db.ForeignKey('users.id'), nullable=False) 

@app.route('/')
def index():
    user_count = User.query.count()
    release_date = datetime(2024, 2, 28)
    days_until_release = (release_date - datetime.now()).days
    return render_template('login.html', user_count=user_count, days_until_release=days_until_release)

@app.route('/user-count')
def user_count():
    count = User.query.count()
    return jsonify({'user_count': count})

@app.route('/token-signin', methods=['POST'])
def token_signin():
    token = request.json.get('idToken')
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID, clock_skew_in_seconds=300)
        userid = idinfo['sub']

        user = User.query.get(userid)
        if not user:
            user = User(id=userid, name=idinfo.get('name', ''), email=idinfo.get('email', ''))
            db.session.add(user)
        else:
            user.name = idinfo.get('name', '')
            user.email = idinfo.get('email', '')
        db.session.commit()

        session['user_id'] = userid
        session['name'] = user.name
        session['email'] = user.email

        return jsonify({'status': 'success', 'userid': userid, 'name': user.name, 'email': user.email})
    except ValueError as e:
        return jsonify({'status': 'failure', 'message': str(e)}), 401

@app.route('/add-interest', methods=['POST'])
def add_interest():
    if 'user_id' not in session:
        return jsonify({'status': 'failure', 'message': 'User not logged in'}), 401

    interest_name = request.json.get('name')
    if not interest_name:
        return jsonify({'status': 'failure', 'message': 'Missing interest name'}), 400

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user:
        new_interest = Interest(name=interest_name, user=user)
        db.session.add(new_interest)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Added interest {interest_name}'})
    else:
        return jsonify({'status': 'failure', 'message': 'User not found'}), 404

@app.route('/interests')
def interests():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user = User.query.get(session['user_id'])
    if user:
        interests = [interest.name for interest in user.interests]
    else:
        interests = []
    return render_template('interests.html', name=user.name, email=user.email, interests=interests)

@app.route('/remove-interest', methods=['POST'])
def remove_interest():
    if 'user_id' not in session:
        return jsonify({'status': 'failure', 'message': 'User not logged in'}), 401

    interest_name = request.json.get('name')
    user_id = session['user_id']
    interest = Interest.query.filter_by(name=interest_name, user_id=user_id).first()
    if interest:
        db.session.delete(interest)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Removed interest {interest_name}'})
    else:
        return jsonify({'status': 'failure', 'message': 'Interest not found'}), 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
