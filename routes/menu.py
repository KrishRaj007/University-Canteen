from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import MenuItem, Category

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu')
@login_required
def index():
    return render_template('menu.html')

@menu_bp.route('/api/menu')
@login_required
def get_menu():
    categories = Category.query.all()
    result = []
    for cat in categories:
        items = [{
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'price': item.price,
            'available': item.available
        } for item in cat.items]
        if items:
            result.append({'category': cat.name, 'items': items})
    return jsonify(result)
