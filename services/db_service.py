import sqlite3
import os

DB_FOLDER = "database"
DB_NAME = "database/receipts.db"
F_STORE = "store"
F_INVOICE = "invoice_number"
F_DATE = "date"
F_AMOUNT = "amount"
F_UPLOADER = "uploader_id"
F_SOURCE = "source"
F_CAT = "category"
F_TIME = "created_at"

os.makedirs(DB_FOLDER, exist_ok=True)

def init_db():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {F_STORE} TEXT,
        {F_INVOICE} TEXT,
        {F_DATE} TEXT,
        {F_AMOUNT} REAL,
        {F_UPLOADER} TEXT,
        {F_SOURCE} TEXT,
        {F_CAT} TEXT,
        {F_TIME} TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_receipt(data):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
# (store, invoice_number, date, amount, uploader_id, source, category)

    cursor.execute(f"""
    INSERT INTO receipts
    ({F_STORE}, {F_INVOICE}, {F_DATE}, {F_AMOUNT}, {F_UPLOADER}, {F_SOURCE}, {F_CAT})
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    (
        data.get(F_STORE),
        data.get(F_INVOICE),
        data.get(F_DATE),
        data.get(F_AMOUNT),
        data.get(F_UPLOADER),
        data.get(F_SOURCE),
        data.get(F_CAT)
    ) )

    conn.commit()
    conn.close()

def find_duplicate(invoice):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM receipts WHERE {F_INVOICE} = ?", (invoice,))
    rows = cursor.fetchall()
    count = len(rows)

    conn.close()
    return count > 0
 
def query_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM receipts")
    rows = cursor.fetchall()

    conn.close()
    return rows

#
def query_db_weekly():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(f"""
                    SELECT {F_UPLOADER}, COUNT(*) as total_receipts,
                    SUM({F_AMOUNT}) as total_amount
                    FROM receipts
                    WHERE {F_TIME} >= date('now', '-7 days')
                    GROUP BY {F_UPLOADER} 
                """)
    rows = cursor.fetchall()

    conn.close()
    return rows





