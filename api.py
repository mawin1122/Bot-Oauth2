from flask import Flask, redirect, request, session, url_for, render_template, jsonify  
import requests
import os
import logging
import json
import datetime
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=8)

CLIENT_ID = '111111111'
CLIENT_SECRET = 'asdasdasd'
REDIRECT_URI = 'http://localhost:5000/callback'
DISCORD_API_BASE_URL = 'https://discord.com/api'
RECAPTCHA_SECRET_KEY = '6LdmDFkkAAAAAAFYBGr37VPuRl-L1hfwraFwO5pW'
RECAPTCHA_SITE_KEY = '6LdmDFkkAAAAAEKni0zQPY4MEtv2nxLodGLEQvVO'
DISCORD_BOT_TOKEN = 'asdasd'
GUILD_ID = '111111111'


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('recaptcha'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    discord_authorize_url = (
        f'{DISCORD_API_BASE_URL}/oauth2/authorize'
        f'?client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&response_type=code'
        f'&scope=identify'
    )
    return redirect(discord_authorize_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return 'Error: No code provided'

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(f'{DISCORD_API_BASE_URL}/oauth2/token', data=data, headers=headers)
    if response.status_code != 200:
        logging.error(f'Error: {response.status_code}, {response.text}')
        return f'Error: {response.status_code}, {response.text}'
    
    token_info = response.json()
    access_token = token_info.get('access_token')
    if not access_token:
        return 'Error: No access token received'
    
    user_info = get_user_info(access_token)
    session['user'] = user_info
    session.permanent = True  # Set session as permanent to use the permanent session lifetime
    return redirect(url_for('recaptcha'))

def get_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{DISCORD_API_BASE_URL}/users/@me', headers=headers)
    response.raise_for_status()
    return response.json()

@app.route('/recaptcha')
def recaptcha():
    return render_template('recaptcha.html', site_key=RECAPTCHA_SITE_KEY)

@app.route('/verify', methods=['POST'])
def verify():
    recaptcha_response = request.form['g-recaptcha-response']
    payload = {'response': recaptcha_response, 'secret': RECAPTCHA_SECRET_KEY}
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    result = response.json()
    if result.get('success'):
        user = session.get('user')
        if user:
            user_id = user['id']
            assign_role(user_id)
            return redirect(url_for('success'))
        else:
            return 'User session not found. Please log in first.'
    else:
        return 'CAPTCHA verification failed!'

logging.basicConfig(level=logging.DEBUG)

def load_role_id():
    try:
        with open('./data/config.json', 'r') as f:
            config = json.load(f)
            return config.get('ROLE_ID')
    except FileNotFoundError:
        logging.error('config.json ไม่พบ กรุณาตรวจสอบไฟล์')
        return None
    except KeyError:
        logging.error('ไม่สามารถโหลด ROLE_ID จาก config.json ได้ กรุณาตรวจสอบโครงสร้างของไฟล์')
        return None

def assign_role(user_id):
    role_id = load_role_id()
    if not role_id:
        logging.error('ไม่สามารถโหลด ROLE_ID ได้')
        return
    
    url = f'https://discord.com/api/v9/guilds/{GUILD_ID}/members/{user_id}/roles/{role_id}'
    headers = {
        'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    logging.debug(f'กำลังจัดการสิทธิให้กับผู้ใช้ {user_id} ในกิลด์ {GUILD_ID}')
    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        logging.debug(f'จัดสิทธิให้กับผู้ใช้ {user_id} สำเร็จแล้ว')
    else:
        logging.error(f'ไม่สามารถจัดสิทธิได้: {response.status_code}, {response.text}')

@app.route('/success')
def success():
    if 'user' in session:
        username = session["user"]["username"]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if os.path.exists('./data/user_data.json'):
            with open('./data/user_data.json', 'r') as f:
                data = json.load(f)
        else:
            data = {"users": {}}

        if "users" in data and username in data["users"]:
            data["users"][username]["timestamp"] = timestamp
        else:
            data["users"][username] = {
                "timestamp": timestamp
            }

        with open('./data/user_data.json', 'w') as f:
            json.dump(data, f, indent=4)

        return '''
            <script>
                window.location.href = "https://discord.gg/GFtKxmAD";
            </script>
        '''
    else:
        return '''
            <div style="text-align:center;">
                <h2>User session not found. Please log in first.</h2>
            </div>
        '''

if __name__ == '__main__':
    app.run(debug=True)
