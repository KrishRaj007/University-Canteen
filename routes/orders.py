from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from models import Order, OrderItem, MenuItem
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
@login_required
def index():
    return render_template('orders.html')

@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def place_order():
    data = request.get_json()
    items = data.get('items', [])
    notes = data.get('notes', '')
    payment = data.get('payment_method', 'cash')

    if not items:
        return jsonify({'success': False, 'message': 'Cart is empty'}), 400

    total = 0
    order_items = []
    for item_data in items:
        menu_item = MenuItem.query.get(item_data['id'])
        if not menu_item or not menu_item.available:
            return jsonify({'success': False, 'message': f'{menu_item.name if menu_item else "Item"} is unavailable'}), 400
        qty = item_data['quantity']
        total += menu_item.price * qty
        order_items.append(OrderItem(menu_item_id=menu_item.id, quantity=qty, price=menu_item.price))

    order = Order(user_id=current_user.id, total=total,
                  notes=notes, payment_method=payment)
    db.session.add(order)
    db.session.flush()
    for oi in order_items:
        oi.order_id = order.id
        db.session.add(oi)
    db.session.commit()
    return jsonify({'success': True, 'order_id': order.id, 'total': total})

@orders_bp.route('/api/orders/my')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([serialize_order(o) for o in orders])

@orders_bp.route('/api/orders/<int:order_id>')
@login_required
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(serialize_order(order))

def serialize_order(order):
    return {
        'id': order.id,
        'status': order.status,
        'total': order.total,
        'payment_method': order.payment_method,
        'notes': order.notes,
        'created_at': order.created_at.strftime('%d %b %Y, %I:%M %p'),
        'user_name': order.user.name,
        'items': [{
            'name': oi.menu_item.name,
            'quantity': oi.quantity,
            'price': oi.price
        } for oi in order.items]
    }
