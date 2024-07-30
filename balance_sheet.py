
import sqlite3
import csv
import io
from flask import jsonify, send_file

class BalanceSheet:
    def __init__(self, db_name='expenses.db'):
        # Initialize the BalanceSheet class with a database name
        self.conn = db_name

    def get_user_balance_sheet(self, user_id):
        # Generate a balance sheet for a specific user
        conn = sqlite3.connect(self.dbname)
        c = conn.cursor()

        # Get user details
        c.execute("SELECT name, email, mobile FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if not user:
            print(f"Error: User with ID {user_id} not found")
            return jsonify({"error": "User not found"}), 404

        # Get user's expenses and payments
        c.execute("""
            SELECT b.name AS batch_name, e.description, e.amount AS total_amount, 
                   es.amount AS user_amount, e.created_by, e.created_at
            FROM expenses e
            JOIN expense_splits es ON e.id = es.expense_id
            JOIN batches b ON e.batch_id = b.id
            WHERE es.user_id = ?
            ORDER BY e.created_at DESC
        """, (user_id,))
        transactions = c.fetchall()

        # Calculate total owed and total paid
        total_owed = sum(t[3] for t in transactions if t[4] != user_id)
        total_paid = sum(t[2] for t in transactions if t[4] == user_id)

        balance_sheet = {
            "user_info": {
                "name": user[0],
                "email": user[1],
                "mobile": user[2]
            },
            "transactions": [
                {
                    "batch_name": t[0],
                    "description": t[1],
                    "total_amount": t[2],
                    "user_amount": t[3],
                    "is_payment": t[4] == user_id,
                    "date": t[5]
                } for t in transactions
            ],
            "summary": {
                "total_owed": total_owed,
                "total_paid": total_paid,
                "net_balance": total_paid - total_owed
            }
        }

        conn.close()
        print(f"Generated balance sheet for user {user_id}")
        return jsonify(balance_sheet)

    def get_batch_balance_sheet(self, batch_id):
        # Generate a balance sheet for a specific batch
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Get batch details
        c.execute("SELECT name, description FROM batches WHERE id = ?", (batch_id,))
        batch = c.fetchone()
        if not batch:
            print(f"Error: Batch with ID {batch_id} not found")
            return jsonify({"error": "Batch not found"}), 404

        # Get batch expenses
        c.execute("""
            SELECT e.id, e.description, e.amount, e.split_method, e.created_by, u.name AS created_by_name, e.created_at
            FROM expenses e
            JOIN users u ON e.created_by = u.id
            WHERE e.batch_id = ?
            ORDER BY e.created_at DESC
        """, (batch_id,))
        expenses = c.fetchall()

        # Get batch members and their balances
        c.execute("""
            SELECT u.id, u.name, u.email,
                   SUM(CASE WHEN e.created_by = u.id THEN e.amount ELSE 0 END) AS total_paid,
                   SUM(es.amount) AS total_owed
            FROM users u
            JOIN batch_members bm ON u.id = bm.user_id
            LEFT JOIN expenses e ON e.batch_id = bm.batch_id AND e.created_by = u.id
            LEFT JOIN expense_splits es ON es.expense_id = e.id AND es.user_id = u.id
            WHERE bm.batch_id = ?
            GROUP BY u.id
        """, (batch_id,))
        members = c.fetchall()

        balance_sheet = {
            "batch_info": {
                "name": batch[0],
                "description": batch[1]
            },
            "expenses": [
                {
                    "id": e[0],
                    "description": e[1],
                    "amount": e[2],
                    "split_method": e[3],
                    "created_by": e[4],
                    "created_by_name": e[5],
                    "created_at": e[6]
                } for e in expenses
            ],
            "member_balances": [
                {
                    "id": m[0],
                    "name": m[1],
                    "email": m[2],
                    "total_paid": m[3],
                    "total_owed": m[4],
                    "net_balance": m[3] - m[4]
                } for m in members
            ],
            "summary": {
                "total_expenses": sum(e[2] for e in expenses),
                "member_count": len(members)
            }
        }

        conn.close()
        print(f"Generated balance sheet for batch {batch_id}")
        return jsonify(balance_sheet)

    def download_user_balance_sheet(self, user_id):
        # Generate a downloadable CSV balance sheet for a specific user
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Get user details
        c.execute("SELECT name, email, mobile FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if not user:
            print(f"Error: User with ID {user_id} not found")
            return jsonify({"error": "User not found"}), 404

        # Get user's expenses and payments
        c.execute("""
            SELECT b.name AS batch_name, e.description, e.amount AS total_amount, 
                   es.amount AS user_amount, e.created_by, e.created_at
            FROM expenses e
            JOIN expense_splits es ON e.id = es.expense_id
            JOIN batches b ON e.batch_id = b.id
            WHERE es.user_id = ?
            ORDER BY e.created_at DESC
        """, (user_id,))
        transactions = c.fetchall()

        # Calculate total owed and total paid
        total_owed = sum(t[3] for t in transactions if t[4] != user_id)
        total_paid = sum(t[2] for t in transactions if t[4] == user_id)

        # Create CSV file
        output = io.StringIO()
        writer = csv.writer(output)

        # Write user info
        writer.writerow(["User Balance Sheet"])
        writer.writerow(["Name", "Email", "Mobile"])
        writer.writerow([user[0], user[1], user[2]])
        writer.writerow([])

        # Write transactions
        writer.writerow(["Batch", "Description", "Total Amount", "User Amount", "Type", "Date"])
        for t in transactions:
            writer.writerow([
                t[0], t[1], t[2], t[3],
                "Payment" if t[4] == user_id else "Expense",
                t[5]
            ])

        # Write summary
        writer.writerow([])
        writer.writerow(["Summary"])
        writer.writerow(["Total Owed", total_owed])
        writer.writerow(["Total Paid", total_paid])
        writer.writerow(["Net Balance", total_paid - total_owed])

        conn.close()
        
        # Prepare the CSV file for download
        output.seek(0)
        print(f"Generated downloadable balance sheet for user {user_id}")
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            attachment_filename=f'user_{user_id}_balance_sheet.csv'
        )