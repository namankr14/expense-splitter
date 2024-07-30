import sqlite3
from flask import jsonify
from datetime import datetime

class ExpenseManagement:
    def __init__(self, db_name='expenses.db'):
        self.db_name = db_name

    def create_tables(self):
        """
        Create the necessary tables for expense management.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS expenses
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      description TEXT NOT NULL,
                      amount REAL NOT NULL,
                      split_method TEXT NOT NULL,
                      created_by INTEGER,
                      batch_id INTEGER,
                      created_at TIMESTAMP,
                      FOREIGN KEY (created_by) REFERENCES users (id),
                      FOREIGN KEY (batch_id) REFERENCES batches (id))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS expense_splits
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      expense_id INTEGER,
                      user_id INTEGER,
                      amount REAL,
                      percentage REAL,
                      FOREIGN KEY (expense_id) REFERENCES expenses (id),
                      FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS batches
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      description TEXT,
                      created_at TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS batch_members
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      batch_id INTEGER,
                      user_id INTEGER,
                      FOREIGN KEY (batch_id) REFERENCES batches (id),
                      FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        conn.commit()
        conn.close()
        print("Expense management tables created successfully")

    def create_batch(self, name, description, user_ids):
        """
        Create a new batch for expense splitting.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO batches (name, description, created_at) VALUES (?, ?, ?)",
                      (name, description, datetime.now()))
            batch_id = c.lastrowid
            
            for user_id in user_ids:
                c.execute("INSERT INTO batch_members (batch_id, user_id) VALUES (?, ?)",
                          (batch_id, user_id))
            
            conn.commit()
            return jsonify({"message": "Batch created successfully", "batch_id": batch_id}), 201
        except sqlite3.Error as e:
            return jsonify({"error": f"Failed to create batch: {str(e)}"}), 500
        finally:
            conn.close()

    def add_expense(self, description, amount, split_method, created_by, batch_id, splits):
        """
        Add a new expense and split it among batch members.
        """
        if split_method not in ['equal', 'exact', 'percentage']:
            return jsonify({"error": "Invalid split method"}), 400

        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO expenses 
                         (description, amount, split_method, created_by, batch_id, created_at) 
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (description, amount, split_method, created_by, batch_id, datetime.now()))
            expense_id = c.lastrowid

            if split_method == 'equal':
                c.execute("SELECT COUNT(*) FROM batch_members WHERE batch_id = ?", (batch_id,))
                member_count = c.fetchone()[0]
                split_amount = amount / member_count
                
                c.execute("SELECT user_id FROM batch_members WHERE batch_id = ?", (batch_id,))
                for (user_id,) in c.fetchall():
                    c.execute("INSERT INTO expense_splits (expense_id, user_id, amount) VALUES (?, ?, ?)",
                              (expense_id, user_id, split_amount))
            elif split_method == 'exact':
                for split in splits:
                    c.execute("INSERT INTO expense_splits (expense_id, user_id, amount) VALUES (?, ?, ?)",
                              (expense_id, split['user_id'], split['amount']))
            elif split_method == 'percentage':
                total_percentage = sum(split['percentage'] for split in splits)
                if abs(total_percentage - 100) > 0.01:  # Allow for small floating-point errors
                    raise ValueError("Percentage splits must add up to 100%")
                
                for split in splits:
                    split_amount = amount * (split['percentage'] / 100)
                    c.execute("INSERT INTO expense_splits (expense_id, user_id, amount, percentage) VALUES (?, ?, ?, ?)",
                              (expense_id, split['user_id'], split_amount, split['percentage']))

            conn.commit()
            return jsonify({"message": "Expense added successfully", "expense_id": expense_id}), 201
        except sqlite3.Error as e:
            return jsonify({"error": f"Failed to add expense: {str(e)}"}), 500
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        finally:
            conn.close()

    def get_user_expenses(self, user_id):
        """
        Retrieve expenses for a specific user.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            SELECT e.id, e.description, e.amount, e.split_method, es.amount as split_amount, 
                   e.created_at, b.name as batch_name
            FROM expenses e
            JOIN expense_splits es ON e.id = es.expense_id
            JOIN batches b ON e.batch_id = b.id
            WHERE es.user_id = ?
            ORDER BY e.created_at DESC
            LIMIT 100  -- Limit the number of results for better performance
        """, (user_id,))
        expenses = c.fetchall()
        conn.close()

        expense_list = [
            {
                "id": expense[0],
                "description": expense[1],
                "total_amount": expense[2],
                "split_method": expense[3],
                "user_amount": expense[4],
                "created_at": expense[5],
                "batch_name": expense[6]
            }
            for expense in expenses
        ]

        return jsonify(expense_list)

    def get_batch_expenses(self, batch_id):
        """
        Retrieve all expenses for a specific batch.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""
            SELECT e.id, e.description, e.amount, e.split_method, e.created_by, e.created_at,
                   u.name as created_by_name
            FROM expenses e
            JOIN users u ON e.created_by = u.id
            WHERE e.batch_id = ?
            ORDER BY e.created_at DESC
        """, (batch_id,))
        expenses = c.fetchall()
        conn.close()

        expense_list = [
            {
                "id": expense[0],
                "description": expense[1],
                "amount": expense[2],
                "split_method": expense[3],
                "created_by": expense[4],
                "created_by_name": expense[6],
                "created_at": expense[5]
            }
            for expense in expenses
        ]

        return jsonify(expense_list)