from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from functools import wraps
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

from user_management import UserManagement
from expense_management import ExpenseManagement
from balance_sheet import BalanceSheet

# Initialize Flask app
app = Flask(__name__)

# Configure CORS replace '*' with your frontend's domain
CORS(app, resources={r"/*": {"origins": "*"}})

# Secret key for JWT randomly generated key stored securely
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize our management classes
user_mgmt = UserManagement()
expense_mgmt = ExpenseManagement()
balance_sheet = BalanceSheet()

# Initialize database tables
user_mgmt.create_tables()
expense_mgmt.create_tables()

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = user_mgmt.get_user(data['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Login route
@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"message": "Login required"}), 401
    
    user = user_mgmt.get_user_by_email(auth.username)
    if user and check_password_hash(user['password'], auth.password):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    
    return jsonify({"message": "Invalid credentials"}), 401

# User creation route - this doesn't require authentication
@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    return user_mgmt.create_user(data['name'], data['email'], data['mobile'], data['password'])

# Get user details route - requires authentication
@app.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    # Check if the requested user_id matches the authenticated user's id
    if current_user['id'] != user_id:
        return jsonify({"message": "Unauthorized"}), 403
    return user_mgmt.get_user(user_id)

# Get all users route - typically this would be an admin-only function
@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    # Here you might want to check if the current_user has admin privileges
    return user_mgmt.get_all_users()

# Create a new batch route
@app.route('/batches', methods=['POST'])
@token_required
def create_batch(current_user):
    data = request.json
    return expense_mgmt.create_batch(data['name'], data['description'], data['user_ids'])

# Add a new expense route
@app.route('/expenses', methods=['POST'])
@token_required
def add_expense(current_user):
    data = request.json
    # Ensure the current user is the one creating the expense
    if current_user['id'] != data['created_by']:
        return jsonify({"message": "Unauthorized"}), 403
    return expense_mgmt.add_expense(data['description'], data['amount'], data['split_method'],
                                    data['created_by'], data['batch_id'], data['splits'])

# Get user expenses route
@app.route('/expenses/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_expenses(current_user, user_id):
    # Ensure the current user is requesting their own expenses
    if current_user['id'] != user_id:
        return jsonify({"message": "Unauthorized"}), 403
    return expense_mgmt.get_user_expenses(user_id)

# Get batch expenses route
@app.route('/expenses/batch/<int:batch_id>', methods=['GET'])
@token_required
def get_batch_expenses(current_user, batch_id):
    # Here you might want to check if the current_user is part of this batch
    return expense_mgmt.get_batch_expenses(batch_id)

# Get user balance sheet route
@app.route('/balance-sheet/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_balance_sheet(current_user, user_id):
    # Ensure the current user is requesting their own balance sheet
    if current_user['id'] != user_id:
        return jsonify({"message": "Unauthorized"}), 403
    return balance_sheet.get_user_balance_sheet(user_id)

# Get batch balance sheet route
@app.route('/balance-sheet/batch/<int:batch_id>', methods=['GET'])
@token_required
def get_batch_balance_sheet(current_user, batch_id):
    # Here you might want to check if the current_user is part of this batch
    return balance_sheet.get_batch_balance_sheet(batch_id)

# Download user balance sheet route
@app.route('/balance-sheet/user/<int:user_id>/download', methods=['GET'])
@token_required
def download_user_balance_sheet(current_user, user_id):
    # Ensure the current user is downloading their own balance sheet
    if current_user['id'] != user_id:
        return jsonify({"message": "Unauthorized"}), 403
    return balance_sheet.download_user_balance_sheet(user_id)

# Serve the main page
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# Run the Flask app
if __name__ == '__main__':
    # proper WSGI server and configure HTTPS
    app.run(debug=True, port=5065)