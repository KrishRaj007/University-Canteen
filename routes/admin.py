from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from functools import wraps
from extensions import mongo
from mongo_helpers import id_filter
from datetime import datetime

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
    from routes.orders import serialize_order
    status = request.args.get('status', '')
    query  = {'status': status} if status else {}
    orders = mongo.db.orders.find(query).sort('created_at', -1).limit(100)
    return jsonify([serialize_order(o) for o in orders])

@admin_bp.route('/api/admin/orders/<order_id>/status', methods=['PUT'])
@login_required
@admin_required
def update_status(order_id):
    valid      = ['pending', 'preparing', 'ready', 'completed', 'cancelled']
    new_status = request.get_json().get('status')
    if new_status not in valid:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    mongo.db.orders.update_one(
        id_filter(order_id),
        {'$set': {'status': new_status}}
    )
    return jsonify({'success': True})

@admin_bp.route('/api/admin/menu', methods=['POST'])
@login_required
@admin_required
def add_item():
    data   = request.get_json()
    result = mongo.db.menu_items.insert_one({
        'name':        data['name'],
        'category':    data['category'],
        'price':       float(data['price']),
        'description': data.get('description', ''),
        'available':   True,
        'created_at':  datetime.utcnow()
    })
    return jsonify({'success': True, 'id': str(result.inserted_id)})

@admin_bp.route('/api/admin/menu/<item_id>', methods=['PUT'])
@login_required
@admin_required
def update_item(item_id):
    data    = request.get_json()
    updates = {}
    if 'name'        in data: updates['name']        = data['name']
    if 'price'       in data: updates['price']       = float(data['price'])
    if 'description' in data: updates['description'] = data['description']
    if 'available'   in data: updates['available']   = data['available']
    mongo.db.menu_items.update_one(
        id_filter(item_id),
        {'$set': updates}
    )
    return jsonify({'success': True})

@admin_bp.route('/api/admin/menu/<item_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_item(item_id):
    mongo.db.menu_items.delete_one(id_filter(item_id))
    return jsonify({'success': True})

@admin_bp.route('/api/admin/stats')
@login_required
@admin_required
def stats():
    total   = mongo.db.orders.count_documents({})
    pending = mongo.db.orders.count_documents({'status': 'pending'})
    prep    = mongo.db.orders.count_documents({'status': 'preparing'})
    ready   = mongo.db.orders.count_documents({'status': 'ready'})
    students= mongo.db.users.count_documents({'role': 'student'})

    # Sum revenue from completed orders
    pipeline = [
        {'$match':  {'status': 'completed'}},
        {'$group':  {'_id': None, 'total': {'$sum': '$total'}}}
    ]
    rev_result = list(mongo.db.orders.aggregate(pipeline))
    revenue    = rev_result[0]['total'] if rev_result else 0

    return jsonify({
        'total_orders': total,
        'pending':      pending,
        'preparing':    prep,
        'ready':        ready,
        'revenue':      revenue,
        'students':     students
    })
