# Campus Canteen Management System

A web application for managing a campus canteen's menu, customer orders, and order progress. Students can browse the menu and place orders, while administrators can manage menu items and update order statuses.

## Features

### Student features

- Create an account or sign in with an existing account.
- Optional Google sign-in when Google OAuth credentials are configured.
- Browse menu items grouped by category.
- Add items to a cart and adjust quantities.
- Add order notes and choose a payment method.
- View personal order history and order status.

### Administrator features

- View dashboard statistics for orders, revenue, and students.
- View and filter incoming orders.
- Update order status: pending, preparing, ready, completed, or cancelled.
- Add, edit, enable or disable, and delete menu items.

## Technology

- Backend: Python, Flask, Flask-Login, Flask-PyMongo
- Database: MongoDB
- Authentication: session-based authentication with Werkzeug password hashing
- Frontend: HTML, CSS, and JavaScript

## Requirements

- Python 3
- MongoDB running locally, or a MongoDB connection URI

## Setup

1. Create and activate a virtual environment if desired.
2. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in a `.env` file. At minimum, set the MongoDB URI:

   ```env
   MONGO_URI=mongodb://localhost:27017/canteen
   SECRET_KEY=replace-with-a-secure-secret
   ```

   To enable Google sign-in, also configure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.

4. Start the application:

   ```bash
   python app.py
   ```

5. Open `http://localhost:5000` in a browser.

On its first run with an empty database, the application adds initial users and menu items.

## Default Accounts

| Role | Email | Password |
| --- | --- | --- |
| Administrator | krish.r2106@gmail.com | admin123 |
| Student | student@gmail.com | student123 |

Change these credentials before deploying the application outside a local development environment.

## Project Structure

```text
app.py                    Application factory, configuration, and initial data
extensions.py             Flask extension instances
models.py                 User model and login loader
mongo_helpers.py          MongoDB identifier helper
routes/
  auth.py                 Registration, login, logout, and Google OAuth
  menu.py                 Menu page and menu API
  orders.py               Order placement and order history APIs
  admin.py                Administration dashboard and management APIs
templates/                Application pages
Menu Items/               Menu item images
instance/                 MongoDB data exports
requirements.txt          Python dependencies
```

## Main Routes

| Route | Purpose |
| --- | --- |
| `/login` | Sign in page |
| `/register` | Student registration |
| `/menu` | Student menu and cart |
| `/orders` | Current user's orders |
| `/admin` | Administrator dashboard |

## Notes

- All menu, user, and order data is stored in MongoDB.
- The first application startup seeds data only when the `users` collection is empty.
- Administrative routes require a signed-in user with the `admin` role.
