import json
import os
import secrets
from datetime import datetime
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo
from models import User

auth_bp = Blueprint('auth', __name__)

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('menu.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        data     = request.get_json() or {}
        email    = (data.get('email') or '').strip().lower()
        password = data.get('password')
        user_doc = mongo.db.users.find_one({'email': email})
        password_hash = user_doc.get('password') if user_doc else None
        if user_doc and password_hash and check_password_hash(password_hash, password):
            user = User(user_doc)
            login_user(user)
            return jsonify({'success': True, 'role': user.role})
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        data     = request.get_json() or {}
        name     = (data.get('name') or '').strip()
        email    = (data.get('email') or '').strip().lower()
        password = data.get('password')
        if not name or not email or not password:
            return jsonify({'success': False, 'message': 'Please fill in all fields'}), 400
        if mongo.db.users.find_one({'email': email}):
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        result = mongo.db.users.insert_one({
            'name':     name,
            'email':    email,
            'password': generate_password_hash(password),
            'role':     'student'
        })
        user_doc = mongo.db.users.find_one({'_id': result.inserted_id})
        login_user(User(user_doc))
        return jsonify({'success': True})
    return render_template('login.html')

@auth_bp.route('/login/google')
def google_login():
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    if not client_id or not os.getenv('GOOGLE_CLIENT_SECRET'):
        return redirect(url_for('auth.login', error='Google sign-in is not configured yet'))

    state = secrets.token_urlsafe(24)
    session['google_oauth_state'] = state
    params = {
        'client_id': client_id,
        'redirect_uri': url_for('auth.google_callback', _external=True),
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account'
    }
    return redirect(f'{GOOGLE_AUTH_URL}?{urlencode(params)}')

@auth_bp.route('/login/google/callback')
def google_callback():
    if request.args.get('state') != session.pop('google_oauth_state', None):
        return redirect(url_for('auth.login', error='Google sign-in could not be verified'))

    code = request.args.get('code')
    if not code:
        return redirect(url_for('auth.login', error='Google sign-in was cancelled'))

    token = exchange_google_code(code)
    if not token:
        return redirect(url_for('auth.login', error='Google sign-in failed'))

    profile = fetch_google_profile(token.get('access_token'))
    if not profile or not profile.get('email'):
        return redirect(url_for('auth.login', error='Google account email was not available'))
    if profile.get('email_verified') is False:
        return redirect(url_for('auth.login', error='Please verify your Google email before signing in'))

    email = profile['email'].strip().lower()
    user_doc = mongo.db.users.find_one({'email': email})
    if user_doc:
        mongo.db.users.update_one(
            {'_id': user_doc['_id']},
            {'$set': {
                'google_id': profile.get('sub'),
                'name': user_doc.get('name') or profile.get('name') or email.split('@')[0],
                'last_login_at': datetime.utcnow()
            }}
        )
        user_doc = mongo.db.users.find_one({'_id': user_doc['_id']})
    else:
        result = mongo.db.users.insert_one({
            'name': profile.get('name') or email.split('@')[0],
            'email': email,
            'password': '',
            'role': 'student',
            'google_id': profile.get('sub'),
            'created_at': datetime.utcnow(),
            'last_login_at': datetime.utcnow()
        })
        user_doc = mongo.db.users.find_one({'_id': result.inserted_id})

    login_user(User(user_doc))
    return redirect(url_for('menu.index'))

def exchange_google_code(code):
    payload = urlencode({
        'code': code,
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': url_for('auth.google_callback', _external=True),
        'grant_type': 'authorization_code'
    }).encode('utf-8')
    req = Request(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    try:
        with urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode('utf-8'))
    except (URLError, TimeoutError, json.JSONDecodeError):
        return None

def fetch_google_profile(access_token):
    if not access_token:
        return None
    req = Request(
        GOOGLE_USERINFO_URL,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    try:
        with urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode('utf-8'))
    except (URLError, TimeoutError, json.JSONDecodeError):
        return None

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
