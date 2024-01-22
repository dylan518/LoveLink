from flask import Flask, request, jsonify
from flask import Flask, render_template
import json
import os
from google.oauth2 import id_token
from google.auth.transport import requests


app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
# Path to your data.json file
DATA_FILE_PATH = 'data.json'

# Your Google Client ID
CLIENT_ID = '1038325471078-255fgp3191kfd7sfrsbqqcbiim4vonq1.apps.googleusercontent.com'

# Read data from the data.json file
def read_data():
    if not os.path.exists(DATA_FILE_PATH):
        return {}
    with open(DATA_FILE_PATH, 'r') as file:
        return json.load(file)

# Write data to the data.json file
def write_data(data):
    with open(DATA_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)


# Route for token sign-in
@app.route('/token-signin', methods=['POST'])
def token_signin():
    token = request.json.get('idtoken')
    try:
        # Verify the token using Google's verifier
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        
        # ID token is valid. Get the user's Google ID, Name and Email
        userid = idinfo['sub']
        useremail = idinfo.get('email', '')
        username = idinfo.get('name', '')

        # Read existing users data
        users_data = read_data()

        # Check if user already exists; if not, add to your data storage
        if userid not in users_data:
            users_data[userid] = {
                'name': username,
                'email': useremail,
                'interests': []  # You can store additional data as needed
            }
            write_data(users_data)
        
        return jsonify({'status': 'success', 'message': 'User authenticated', 'userid': userid, 'name': username, 'email': useremail})
    except ValueError:
        # Invalid token
        return jsonify({'status': 'failure', 'message': 'Invalid token'}), 401


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
