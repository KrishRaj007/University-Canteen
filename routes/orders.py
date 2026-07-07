from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from extensions import mongo
from mongo_helpers import id_filter
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
@login_required
def index():
    return render_template('orders.html')

@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def place_order():
    data    = request.get_json()
    items   = data.get('items', [])
    notes   = data.get('notes', '')
    payment = data.get('payment_method', 'cash')

    if not items:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    total       = 0
    order_items = []

    for item_data in items:
        menu_item = mongo.db.menu_items.find_one(id_filter(item_data['id']))
        if not menu_item or not menu_item.get('available', True):
            name = menu_item['name'] if menu_item else 'Item'
            return jsonify({'success': False, 'message': f'{name} is unavailable'}), 400
        qty    = item_data['quantity']
        price  = menu_item['price']
        total += price * qty
        order_items.append({
            'menu_item_id':   str(menu_item['_id']),
            'name':           menu_item['name'],
            'menu_item_name': menu_item['name'],
            'quantity':       qty,
            'price':          price,
            'subtotal':       price * qty
        })

    result = mongo.db.orders.insert_one({
        'user_id':        current_user.id,
        'user_name':      current_user.name,
        'total':          total,
        'status':         'pending',
        'payment_method': payment,
        'notes':          notes,
        'items':          order_items,
        'created_at':     datetime.utcnow()
    })

    return jsonify({
        'success':  True,
        'order_id': str(result.inserted_id),
        'total':    total
    })

@orders_bp.route('/api/orders/my')
@login_required
def my_orders():
    orders = mongo.db.orders.find(
        {'user_id': current_user.id}
    ).sort('created_at', -1)
    return jsonify([serialize_order(o) for o in orders])

@orders_bp.route('/api/orders/<order_id>')
@login_required
def get_order(order_id):
    order = mongo.db.orders.find_one(id_filter(order_id))
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    if order['user_id'] != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(serialize_order(order))

def serialize_order(order):
    created_at = order.get('created_at')
    if hasattr(created_at, 'strftime'):
        created_at = created_at.strftime('%d %b %Y, %I:%M %p')

    return {
        'id':             str(order['_id']),
        'status':         order['status'],
        'total':          order['total'],
        'payment_method': order['payment_method'],
        'notes':          order.get('notes', ''),
        'created_at':     created_at or '',
        'user_name':      order.get('user_name', ''),
        'items':          order.get('items', [])
    }
