from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from extensions import mongo
from collections import defaultdict

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/menu')
@login_required
def index():
    return render_template('menu.html')

@menu_bp.route('/api/menu')
@login_required
def get_menu():
    items = mongo.db.menu_items.find()

    # Group by category (replaces the old Category table join)
    grouped = defaultdict(list)
    for item in items:
        grouped[item['category']].append({
            'id':          str(item['_id']),
            'name':        item['name'],
            'description': item.get('description', ''),
            'price':       item['price'],
            'available':   item.get('available', True)
        })

    # Return in a fixed category order
    order = ['Breakfast', 'Lunch', 'Snacks', 'Beverages', 'Desserts']
    result = []
    for cat in order:
        if cat in grouped:
            result.append({'category': cat, 'items': grouped[cat]})

    # Append any custom categories the admin may have added
    for cat in grouped:
        if cat not in order:
            result.append({'category': cat, 'items': grouped[cat]})

    return jsonify(result)
