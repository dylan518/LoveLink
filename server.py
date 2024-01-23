from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import json
import os
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for secure sessions

# Your Google Client ID
CLIENT_ID = '1038325471078-255fgp3191kfd7sfrsbqqcbiim4vonq1.apps.googleusercontent.com'
DATA_FILE_PATH = 'data.json'

@app.route('/user-count')
def user_count():
    users_data = read_data()
    count = len(users_data)
    return jsonify({'user_count': count})
def read_data():
    if not os.path.exists(DATA_FILE_PATH):
        return {}
    with open(DATA_FILE_PATH, 'r') as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)

from datetime import datetime

from datetime import datetime

@app.route('/')
def index():
    users_data = read_data()
    user_count = len(users_data)
    # Assuming you have a datetime object for the release date
    release_date = datetime(2024, 2, 28)
    days_until_release = (release_date - datetime.now()).days
    return render_template('login.html', user_count=user_count, days_until_release=days_until_release)


@app.route('/token-signin', methods=['POST'])
def token_signin():
    token = request.json.get('idToken')
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID, clock_skew_in_seconds=300)
        userid = idinfo['sub']

        users_data = read_data()

        # Update user's information or create a new entry if it doesn't exist
        if userid not in users_data:
            users_data[userid] = {
                'name': idinfo.get('name', ''),
                'email': idinfo.get('email', ''),
                'interests': []
            }
        else:
            # Update email and name in case it's changed
            users_data[userid]['email'] = idinfo.get('email', '')
            users_data[userid]['name'] = idinfo.get('name', '')

        write_data(users_data)

        # Store the user ID in the session
        session['user_id'] = userid
        session['name'] = users_data[userid]['name']
        session['email'] = users_data[userid]['email']

        return jsonify({'status': 'success', 'userid': userid, 'name': users_data[userid]['name'], 'email': users_data[userid]['email']})
    except ValueError as e:
        # The token is invalid
        return jsonify({'status': 'failure', 'message': str(e)}), 401

@app.route('/add-interest', methods=['POST'])
def add_interest():
    if 'user_id' not in session:
        return jsonify({'status': 'failure', 'message': 'User not logged in'}), 401

    # If you're sending the data as JSON, use request.json.get
    interest_name = request.json.get('name')
    if not interest_name:
        return jsonify({'status': 'failure', 'message': 'Missing interest name'}), 400

    user_id = session['user_id']
    users_data = read_data()

    if user_id in users_data:
        users_data[user_id].setdefault('interests', []).append(interest_name)
        write_data(users_data)
        return jsonify({'status': 'success', 'message': f'Added interest {interest_name}'}), 200
    else:
        return jsonify({'status': 'failure', 'message': 'User data not found'}), 404
@app.route('/interests')
def interests():
    if 'user_id' not in session:
        # If the user is not logged in, redirect to the login page
        return redirect(url_for('index'))

    user_data = read_data().get(session['user_id'], {})
    return render_template('interests.html', 
                           name=user_data.get('name'), 
                           email=user_data.get('email'), 
                           interests=user_data.get('interests', []))


@app.route('/remove-interest', methods=['POST'])
def remove_interest():
    if 'user_id' not in session:
        return jsonify({'status': 'failure', 'message': 'User not logged in'}), 401

    # If you're sending the data as JSON, use request.json.get
    interest_name = request.json.get('name')
    if not interest_name:
        return jsonify({'status': 'failure', 'message': 'Missing interest name'}), 400

    user_id = session['user_id']
    users_data = read_data()

    if user_id in users_data:
        # Check if the interest exists in the user's list and remove it
        if interest_name in users_data[user_id].get('interests', []):
            users_data[user_id]['interests'].remove(interest_name)
            write_data(users_data)
            return jsonify({'status': 'success', 'message': f'Removed interest {interest_name}'}), 200
        else:
            return jsonify({'status': 'failure', 'message': f'Interest {interest_name} not found'}), 404
    else:
        return jsonify({'status': 'failure', 'message': 'User data not found'}), 404
@app.route('/logout')
def logout():
    # Clear the sessionind
    session.clear()
    # Redirect to the login page
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)
