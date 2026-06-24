from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from models import Order, MenuItem, Category, User

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    return render_template('admin.html')

@admin_bp.route('/api/admin/orders')
@login_required
@admin_required
def all_orders():
    status = request.args.get('status', '')
    query = Order.query.order_by(Order.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    from routes.orders import serialize_order
    return jsonify([serialize_order(o) for o in query.limit(100).all()])

@admin_bp.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
@login_required
@admin_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json()
    valid = ['pending', 'preparing', 'ready', 'completed', 'cancelled']
    new_status = data.get('status')
    if new_status not in valid:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    order.status = new_status
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/api/admin/menu', methods=['POST'])
@login_required
@admin_required
def add_item():
    data = request.get_json()
    cat = Category.query.filter_by(name=data['category']).first()
    if not cat:
        cat = Category(name=data['category'])
        db.session.add(cat)
        db.session.flush()
    item = MenuItem(name=data['name'], description=data.get('description', ''),
                    price=float(data['price']), category_id=cat.id, available=True)
    db.session.add(item)
    db.session.commit()
    return jsonify({'success': True, 'id': item.id})

@admin_bp.route('/api/admin/menu/<int:item_id>', methods=['PUT'])
@login_required
@admin_required
def update_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    data = request.get_json()
    if 'name' in data: item.name = data['name']
    if 'price' in data: item.price = float(data['price'])
    if 'description' in data: item.description = data['description']
    if 'available' in data: item.available = data['available']
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/api/admin/menu/<int:item_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/api/admin/stats')
@login_required
@admin_required
def stats():
    from sqlalchemy import func
    total_orders = Order.query.count()
    pending = Order.query.filter_by(status='pending').count()
    preparing = Order.query.filter_by(status='preparing').count()
    ready = Order.query.filter_by(status='ready').count()
    revenue = db.session.query(func.sum(Order.total)).filter(Order.status == 'completed').scalar() or 0
    return jsonify({
        'total_orders': total_orders,
        'pending': pending,
        'preparing': preparing,
        'ready': ready,
        'revenue': revenue,
        'students': User.query.filter_by(role='student').count()
    })
