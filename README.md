# expense-splitter

Expense-Splitting App:

This is a Flask-based web application for managing and splitting expenses among groups of users.


Prerequisites:

- Python 3.7+
- pip (Python package manager)
- SQLite3

## Setup

1. Clone the repository:

   git clone https://github.com/your-username/expense-splitting-app.git
   cd expense-splitting-app

2. Create a virtual environment:

   python -m venv venv


3. Activate the virtual environment:
   - On Windows:
     
     venv\Scripts\activate
     
   - On macOS and Linux:
     
     source venv/bin/activate
     

4. Install the required packages:
   
   pip install -r requirements.txt
   

## Configuration

1. Open `main.py` and replace the secret key:
   
   app.config['SECRET_KEY'] = 'your_secret_key_here'
   
   Replace 'your_secret_key_here' with a secure random string.

2. If you want to change the database name or location, update the `db_name` parameter in the `UserManagement`, `ExpenseManagement`, and `BalanceSheet` class initializations.

## Running the Application

1. Start the Flask development server:
   
   python main.py


2. Open a web browser and navigate to `http://localhost:5065` to access the application.

## API Endpoints

- POST `/login`: User login
- POST `/users`: Create a new user
- GET `/users/<user_id>`: Get user details
- GET `/users`: Get all users
- POST `/batches`: Create a new batch
- POST `/expenses`: Add a new expense
- GET `/expenses/user/<user_id>`: Get user expenses
- GET `/expenses/batch/<batch_id>`: Get batch expenses
- GET `/balance-sheet/user/<user_id>`: Get user balance sheet
- GET `/balance-sheet/batch/<batch_id>`: Get batch balance sheet
- GET `/balance-sheet/user/<user_id>/download`: Download user balance sheet



## Running Tests

To run the test suite:


python -m unittest discover tests



