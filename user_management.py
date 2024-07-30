import sqlite3
from flask import jsonify
import re
from werkzeug.security import generate_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserManagement:
    def __init__(self, db_name='expenses.db'):
        """
        Initialize the UserManagement class with a database name.
        
        :param db_name: Name of the SQLite database file
        """
        self.db_name = db_name
        logger.info(f"UserManagement initialized with database: {db_name}")

    def create_tables(self):
        """
        Create the necessary tables in the database for user management.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS users
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          email TEXT UNIQUE NOT NULL,
                          mobile TEXT NOT NULL,
                          password TEXT NOT NULL)''')
            conn.commit()
            logger.info("User tables created successfully")
        except sqlite3.Error as e:
            logger.error(f"Error creating user tables: {str(e)}")
        finally:
            conn.close()

    def validate_email(self, email):
        """
        Validate email format using a regular expression.
        
        :param email: Email address to validate
        :return: True if email is valid, False otherwise
        """
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(email_regex, email) is not None
        logger.debug(f"Email validation for {email}: {'Valid' if is_valid else 'Invalid'}")
        return is_valid

    def validate_mobile(self, mobile):
        """
        Validate mobile number format (assuming 10-digit number).
        
        :param mobile: Mobile number to validate
        :return: True if mobile number is valid, False otherwise
        """
        is_valid = mobile.isdigit() and len(mobile) == 10
        logger.debug(f"Mobile validation for {mobile}: {'Valid' if is_valid else 'Invalid'}")
        return is_valid

    def create_user(self, name, email, mobile, password):
        """
        Create a new user in the database.
        
        :param name: User's name
        :param email: User's email
        :param mobile: User's mobile number
        :param password: User's password
        :return: JSON response with creation status and user ID if successful
        """
        logger.info(f"Attempting to create user: {name}, {email}")
        if not all([name, email, mobile, password]):
            logger.warning("User creation failed: All fields are required")
            return jsonify({"error": "All fields are required"}), 400
        if not self.validate_email(email):
            logger.warning(f"User creation failed: Invalid email format - {email}")
            return jsonify({"error": "Invalid email format"}), 400
        if not self.validate_mobile(mobile):
            logger.warning(f"User creation failed: Invalid mobile number format - {mobile}")
            return jsonify({"error": "Invalid mobile number format"}), 400
        
        hashed_password = generate_password_hash(password)
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (name, email, mobile, password) VALUES (?, ?, ?, ?)",
                      (name, email, mobile, hashed_password))
            conn.commit()
            user_id = c.lastrowid
            logger.info(f"User created successfully: ID {user_id}, {name}, {email}")
            return jsonify({"message": "User created successfully", "user_id": user_id}), 201
        except sqlite3.IntegrityError:
            logger.error(f"User creation failed: Email already exists - {email}")
            return jsonify({"error": "Email already exists"}), 400
        except sqlite3.Error as e:
            logger.error(f"Database error during user creation: {str(e)}")
            return jsonify({"error": "Database error occurred"}), 500
        finally:
            conn.close()

    def get_user(self, user_id):
        """
        Retrieve user details by user ID.
        
        :param user_id: ID of the user to retrieve
        :return: JSON response with user details if found, error message otherwise
        """
        logger.info(f"Retrieving user details for ID: {user_id}")
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute("SELECT id, name, email, mobile FROM users WHERE id = ?", (user_id,))
            user = c.fetchone()
            if user:
                user_data = {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "mobile": user[3]
                }
                logger.info(f"User details retrieved successfully for ID: {user_id}")
                return jsonify(user_data)
            else:
                logger.warning(f"User not found for ID: {user_id}")
                return jsonify({"error": "User not found"}), 404
        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving user {user_id}: {str(e)}")
            return jsonify({"error": "Database error occurred"}), 500
        finally:
            conn.close()

    def get_user_by_email(self, email):
        """
        Retrieve user details by email.
        
        :param email: Email of the user to retrieve
        :return: Dictionary with user details if found, None otherwise
        """
        logger.info(f"Retrieving user details for email: {email}")
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = c.fetchone()
            if user:
                user_data = {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "mobile": user[3],
                    "password": user[4]
                }
                logger.info(f"User details retrieved successfully for email: {email}")
                return user_data
            else:
                logger.warning(f"User not found for email: {email}")
                return None
        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving user by email {email}: {str(e)}")
            return None
        finally:
            conn.close()

    def get_all_users(self):
        """
        Retrieve all users from the database.
        
        :return: JSON response with a list of all users
        """
        logger.info("Retrieving all users")
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute("SELECT id, name, email, mobile FROM users")
            users = c.fetchall()
            user_list = [
                {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "mobile": user[3]
                } for user in users
            ]
            logger.info(f"Retrieved {len(user_list)} users successfully")
            return jsonify(user_list)
        except sqlite3.Error as e:
            logger.error(f"Database error while retrieving all users: {str(e)}")
            return jsonify({"error": "Database error occurred"}), 500
        finally:
            conn.close()