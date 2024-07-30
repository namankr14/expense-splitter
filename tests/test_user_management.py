#test_user_management.py
import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_management import UserManagement

class TestUserManagement(unittest.TestCase):
    def setUp(self):
        self.user_mgmt = UserManagement('test_expenses.db')
        self.user_mgmt.create_tables()

    def test_create_user(self):
        result, status = self.user_mgmt.create_user('Test User', 'test@example.com', '1234567890', 'password123')
        self.assertEqual(status, 201)
        self.assertIn('User created successfully', result.get_json()['message'])

    def test_get_user(self):
        self.user_mgmt.create_user('Test User', 'test@example.com', '1234567890', 'password123')
        result = self.user_mgmt.get_user(1)
        self.assertIn('Test User', result.get_json()['name'])

    def test_get_user_by_email(self):
        self.user_mgmt.create_user('Test User', 'test@example.com', '1234567890', 'password123')
        user = self.user_mgmt.get_user_by_email('test@example.com')
        self.assertEqual(user['name'], 'Test User')

    def test_get_all_users(self):
        self.user_mgmt.create_user('User1', 'user1@example.com', '1111111111', 'password1')
        self.user_mgmt.create_user('User2', 'user2@example.com', '2222222222', 'password2')
        result = self.user_mgmt.get_all_users()
        self.assertEqual(len(result.get_json()), 2)

    def tearDown(self):
        os.remove('test_expenses.db')

if __name__ == '__main__':
    unittest.main()
