# 🍽️ Campus Canteen — Online Food Ordering System

A full-stack canteen management system built with Flask + HTML/CSS/JS.

## Features

### Student Panel
- 🔐 Register / Login
- 🍛 Browse menu by category
- 🛒 Add items to cart, adjust quantities
- 📝 Place orders with notes & payment method
- 📋 Track orders with live status updates

### Admin Panel
- 📊 Live dashboard with stats (orders, revenue, student count)
- 👨‍🍳 Manage incoming orders (Pending → Preparing → Ready → Completed)
- 🍽️ Full menu management (Add, Enable/Disable, Delete items)

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

## Demo Accounts

| Role    | Email                  | Password   |
|---------|------------------------|------------|
| Student | student@canteen.com    | student123 |
| Admin   | admin@canteen.com      | admin123   |

## Project Structure

```
canteen/
├── app.py              # Main Flask app + DB seeding
├── models.py           # SQLAlchemy models
├── requirements.txt    # Python dependencies
├── routes/
│   ├── auth.py         # Login / Register / Logout
│   ├── menu.py         # Menu API
│   ├── orders.py       # Order placement & tracking
│   └── admin.py        # Admin CRUD + stats
└── templates/
    ├── login.html      # Login & Register UI
    ├── menu.html       # Student menu + cart
    ├── orders.html     # My Orders page
    └── admin.html      # Admin dashboard
```

## Tech Stack

- **Backend**: Python / Flask / SQLAlchemy / Flask-Login
- **Database**: SQLite (auto-created on first run)
- **Frontend**: Vanilla HTML + CSS + JavaScript (no frameworks)
- **Auth**: Session-based with Werkzeug password hashing
