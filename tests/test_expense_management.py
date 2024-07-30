#test_expense_management
import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expense_management import ExpenseManagement
from user_management import UserManagement

class TestExpenseManagement(unittest.TestCase):
    def setUp(self):
        self.expense_mgmt = ExpenseManagement('test_expenses.db')
        self.user_mgmt = UserManagement('test_expenses.db')
        self.expense_mgmt.create_tables()
        self.user_mgmt.create_tables()

        # Create test users
        self.user_mgmt.create_user('User1', 'user1@example.com', '1111111111', 'password1')
        self.user_mgmt.create_user('User2', 'user2@example.com', '2222222222', 'password2')

    def test_create_batch(self):
        result, status = self.expense_mgmt.create_batch('Test Batch', 'Test Description', [1, 2])
        self.assertEqual(status, 201)
        self.assertIn('Batch created successfully', result.get_json()['message'])

    def test_add_expense_equal_split(self):
        self.expense_mgmt.create_batch('Test Batch', 'Test Description', [1, 2])
        result, status = self.expense_mgmt.add_expense('Dinner', 100, 'equal', 1, 1, [])
        self.assertEqual(status, 201)
        self.assertIn('Expense added successfully', result.get_json()['message'])

    def test_add_expense_exact_split(self):
        self.expense_mgmt.create_batch('Test Batch', 'Test Description', [1, 2])
        splits = [{'user_id': 1, 'amount': 60}, {'user_id': 2, 'amount': 40}]
        result, status = self.expense_mgmt.add_expense('Movie', 100, 'exact', 1, 1, splits)
        self.assertEqual(status, 201)
        self.assertIn('Expense added successfully', result.get_json()['message'])

    def test_get_user_expenses(self):
        self.expense_mgmt.create_batch('Test Batch', 'Test Description', [1, 2])
        self.expense_mgmt.add_expense('Dinner', 100, 'equal', 1, 1, [])
        result = self.expense_mgmt.get_user_expenses(1)
        self.assertEqual(len(result.get_json()), 1)

    def test_get_batch_expenses(self):
        self.expense_mgmt.create_batch('Test Batch', 'Test Description', [1, 2])
        self.expense_mgmt.add_expense('Dinner', 100, 'equal', 1, 1, [])
        self.expense_mgmt.add_expense('Movie', 80, 'equal', 2, 1, [])
        result = self.expense_mgmt.get_batch_expenses(1)
        self.assertEqual(len(result.get_json()), 2)

    def tearDown(self):
        os.remove('test_expenses.db')

if __name__ == '__main__':
    unittest.main()
