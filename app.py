from flask import Flask
from extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'canteen-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canteen.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
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

    with app.app_context():
        db.create_all()
        seed_data()

    return app

def seed_data():
    from models import User, MenuItem, Category
    from werkzeug.security import generate_password_hash

    if User.query.first():
        return

    # Create admin
    admin = User(name='Admin', email='admin@canteen.com',
                 password=generate_password_hash('admin123'), role='admin')
    # Create student
    student = User(name='Rahul Sharma', email='student@canteen.com',
                   password=generate_password_hash('student123'), role='student')
    db.session.add_all([admin, student])

    # Categories
    cats = {}
    for name in ['Breakfast', 'Lunch', 'Snacks', 'Beverages', 'Desserts']:
        c = Category(name=name)
        db.session.add(c)
        cats[name] = c
    db.session.flush()

    items = [
        ('Aloo Paratha', 'Breakfast', 40, 'Crispy stuffed paratha with butter', True),
        ('Poha', 'Breakfast', 30, 'Light flattened rice with spices', True),
        ('Idli Sambar', 'Breakfast', 35, 'Soft idlis with hot sambar & chutney', True),
        ('Dal Rice', 'Lunch', 60, 'Comfort dal with steamed rice', True),
        ('Rajma Chawal', 'Lunch', 70, 'Kidney beans curry with rice', True),
        ('Veg Thali', 'Lunch', 90, 'Full thali: rice, dal, sabzi, roti, salad', True),
        ('Chicken Biryani', 'Lunch', 120, 'Aromatic basmati rice with tender chicken', True),
        ('Samosa (2 pcs)', 'Snacks', 20, 'Crispy fried pastry with potato filling', True),
        ('Bread Pakora', 'Snacks', 25, 'Golden fried bread with spiced filling', True),
        ('Maggi Noodles', 'Snacks', 30, 'Classic masala noodles', True),
        ('Masala Chai', 'Beverages', 15, 'Spiced milk tea', True),
        ('Cold Coffee', 'Beverages', 45, 'Chilled blended coffee with ice cream', True),
        ('Lassi', 'Beverages', 35, 'Sweet or salted yogurt drink', True),
        ('Gulab Jamun', 'Desserts', 30, '2 pieces in warm sugar syrup', True),
        ('Ice Cream', 'Desserts', 40, 'Vanilla / Chocolate / Strawberry', True),
    ]

    for name, cat, price, desc, avail in items:
        item = MenuItem(name=name, category_id=cats[cat].id,
                        price=price, description=desc, available=avail)
        db.session.add(item)

    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
