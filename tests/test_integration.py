#test_integration.py
import unittest
from flask import Flask
from user_management import UserManagement
from expense_management import ExpenseManagement
from balance_sheet import BalanceSheet

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        self.user_mgmt = UserManagement('test_expenses.db')
        self.expense_mgmt = ExpenseManagement('test_expenses.db')
        self.balance_sheet = BalanceSheet('test_expenses.db')

        self.user_mgmt.create_tables()
        self.expense_mgmt.create_tables()

    def test_user_creation_and_expense_addition(self):
        # Create a user
        user_response = self.client.post('/users', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'mobile': '1234567890',
            'password': 'password123'
        })
        self.assertEqual(user_response.status_code, 201)
        user_id = user_response.get_json()['user_id']

        # Create a batch
        batch_response = self.client.post('/batches', json={
            'name': 'Test Batch',
            'description': 'Test Description',
            'user_ids': [user_id]
        })
        self.assertEqual(batch_response.status_code, 201)
        batch_id = batch_response.get_json()['batch_id']

        # Add an expense
        expense_response = self.client.post('/expenses', json={
            'description': 'Test Expense',
            'amount': 100,
            'split_method': 'equal',
            'created_by': user_id,
            'batch_id': batch_id,
            'splits': []
        })
        self.assertEqual(expense_response.status_code, 201)

        # Get user balance sheet
        balance_sheet_response = self.client.get(f'/balance-sheet/user/{user_id}')
        self.assertEqual(balance_sheet_response.status_code, 200)
        balance_sheet = balance_sheet_response.get_json()
        self.assertEqual(balance_sheet['summary']['total_paid'], 100)

    def tearDown(self):
        import os
        os.remove('test_expenses.db')

if __name__ == '__main__':
    unittest.main()
