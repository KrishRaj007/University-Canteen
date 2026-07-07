from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo
from models import User

auth_bp = Blueprint('auth', __name__)

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
        data     = request.get_json()
        email    = data.get('email')
        password = data.get('password')
        user_doc = mongo.db.users.find_one({'email': email})
        if user_doc and check_password_hash(user_doc['password'], password):
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
        data     = request.get_json()
        name     = data.get('name')
        email    = data.get('email')
        password = data.get('password')
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

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
