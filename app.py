import os

from flask import Flask, send_from_directory
from datetime import datetime
from dotenv import load_dotenv
from extensions import mongo, login_manager

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'canteen-secret-key-2024')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/canteen')

    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from routes.auth import auth_bp
    from routes.menu import menu_bp
    from routes.orders import orders_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    @app.route('/menu-items/<path:filename>')
    def menu_item_image(filename):
        return send_from_directory(os.path.join(app.root_path, 'Menu Items'), filename)

    with app.app_context():
        seed_data()

    return app


def seed_data():
    from werkzeug.security import generate_password_hash

    if mongo.db.users.count_documents({}) > 0:
        return

    mongo.db.users.insert_many([
        {
            'name':       'Admin',
            'email':      'krish.r2106@gmail.com',
            'password':   generate_password_hash('admin123'),
            'role':       'admin',
            'created_at': datetime.utcnow()
        },
        {
            'name':       'Rahul Sharma',
            'email':      'student@gmail.com',
            'password':   generate_password_hash('student123'),
            'role':       'student',
            'created_at': datetime.utcnow()
        }
    ])

    items = [
        ('Aloo Paratha',    'Breakfast', 40,  'Crispy stuffed paratha with butter'),
        ('Poha',            'Breakfast', 30,  'Light flattened rice with spices'),
        ('Idli Sambar',     'Breakfast', 35,  'Soft idlis with hot sambar & chutney'),
        ('Dal Rice',        'Lunch',     60,  'Comfort dal with steamed rice'),
        ('Rajma Chawal',    'Lunch',     70,  'Kidney beans curry with rice'),
        ('Veg Thali',       'Lunch',     90,  'Full thali: rice, dal, sabzi, roti, salad'),
        ('Chicken Biryani', 'Lunch',     120, 'Aromatic basmati rice with tender chicken'),
        ('Samosa (2 pcs)',  'Snacks',    20,  'Crispy fried pastry with potato filling'),
        ('Bread Pakora',    'Snacks',    25,  'Golden fried bread with spiced filling'),
        ('Maggi Noodles',   'Snacks',    30,  'Classic masala noodles'),
        ('Masala Chai',     'Beverages', 15,  'Spiced milk tea'),
        ('Cold Coffee',     'Beverages', 45,  'Chilled blended coffee with ice cream'),
        ('Lassi',           'Beverages', 35,  'Sweet or salted yogurt drink'),
        ('Gulab Jamun',     'Desserts',  30,  '2 pieces in warm sugar syrup'),
        ('Ice Cream',       'Desserts',  40,  'Vanilla / Chocolate / Strawberry'),
    ]

    mongo.db.menu_items.insert_many([
        {
            'name':        name,
            'category':    cat,
            'price':       price,
            'description': desc,
            'available':   True,
            'created_at':  datetime.utcnow()
        }
        for name, cat, price, desc in items
    ])


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
