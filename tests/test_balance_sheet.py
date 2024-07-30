#test_balance_sheet.py
import unittest
import sys
import os
import sqlite3

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from balance_sheet import BalanceSheet
from user_management import UserManagement
from expense_management import ExpenseManagement

class TestBalanceSheet(unittest.TestCase):
    def setUp(self):
        self.db_name = 'test_expenses.db'
        self.conn = sqlite3.connect(self.db_name)
        self.user_mgmt = UserManagement(self.db_name)
        self.expense_mgmt = ExpenseManagement(self.db_name)
        self.balance_sheet = BalanceSheet(self.db_name)

        self.user_mgmt.create_tables()
        self.expense_mgmt.create_tables()

        # Create test users
        self.user_mgmt.create_user('User1', 'user1@example.com', '1111111111', 'password1')
        self.user_mgmt.create_user('User2', 'user2@example.com', '2222222222', 'password2')

        # Create test batch
        self.expense_mgmt.create_batch('Test Batch', 'Test Description', [1, 2])

        # Add test expenses
        self.expense_mgmt.add_expense('Dinner', 100, 'equal', 1, 1, [])
        self.expense_mgmt.add_expense('Movie', 80, 'exact', 2, 1, [{'user_id': 1, 'amount': 30}, {'user_id': 2, 'amount': 50}])

    def test_get_user_balance_sheet(self):
        result = self.balance_sheet.get_user_balance_sheet(1)
        balance_sheet = result.get_json()
        
        self.assertEqual(balance_sheet['user_info']['name'], 'User1')
        self.assertEqual(len(balance_sheet['transactions']), 2)
        self.assertAlmostEqual(balance_sheet['summary']['total_owed'], 80)
        self.assertAlmostEqual(balance_sheet['summary']['total_paid'], 100)

    def test_get_batch_balance_sheet(self):
        result = self.balance_sheet.get_batch_balance_sheet(1)
        balance_sheet = result.get_json()
        
        self.assertEqual(balance_sheet['batch_info']['name'], 'Test Batch')
        self.assertEqual(len(balance_sheet['expenses']), 2)
        self.assertEqual(len(balance_sheet['member_balances']), 2)
        self.assertAlmostEqual(balance_sheet['summary']['total_expenses'], 180)

    def test_download_user_balance_sheet(self):
        result = self.balance_sheet.download_user_balance_sheet(1)
        self.assertEqual(result.mimetype, 'text/csv')
        self.assertTrue(result.headers['Content-Disposition'].startswith('attachment'))

    def tearDown(self):
        self.conn.close()
        os.remove(self.db_name)

if __name__ == '__main__':
    unittest.main()
