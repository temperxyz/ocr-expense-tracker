import sqlite3

DB_PATH="expenses.db"
def getconnection():
    #return connection object to the sqlite db
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row # makes row behave like dictionary
    return conn
def get_all_expenses():
    """Return all expenses, most recent first"""
    conn=getconnection()
    cursor=conn.cursor()
    cursor.execute("""SELECT* FROM expense ORDER BY created_at DESC""")
    rows = cursor.fetchall()   #gets ALL matching rows as a list
    conn.close()
    return rows

def init_db():
    #creating an expense table if it doesnt exists.
    conn=getconnection()
    cursor=conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS expense(expense_id INTEGER PRIMARY KEY,
                                     merchant TEXT,
                                     date TEXT,
                                     total REAL,
                                     category TEXT NOT NULL,
                                     raw_text TEXT NOT NULL,
                                     image_path TEXT NOT NULL UNIQUE,
                                     created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()
def get_expenses_by_category(category):
    """Returning all expenses matching a category."""
    conn=getconnection()
    cursor=conn.cursor()
    cursor.execute("""SELECT* FROM expense WHERE category =?""",(category,))
    rows=cursor.fetchall()
    conn.close()
    return rows
def insert_expense(merchant, date, total, category, raw_text, image_path):
    conn = getconnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO expense(merchant,date,total,category,raw_text,image_path)
            VALUES (?,?,?,?,?,?)
        """, (merchant, date, total, category, raw_text, image_path))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Insert failed likely duplicate image_path: {e}")
        return False
    finally:
        conn.close() 
def get_expenses_by_date_range(start_date, end_date):
    """Returns expenses with date between start_date and end_date (inclusive)."""
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute("""SELECT* FROM expense WHERE date BETWEEN ? AND ?""",(start_date,end_date,))
    rows = cursor.fetchall()
    conn.close()
    return rows
def delete_expense(expense_id):
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM expense WHERE expense_id=?""",(expense_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount
def update_expense(expense_id, merchant, date, total, category, raw_text, image_path):
    conn = getconnection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE expense
        SET merchant = ?, date = ?, total = ?, category = ?, raw_text = ?, image_path = ?
        WHERE expense_id = ?
    """, (merchant, date, total, category, raw_text, image_path, expense_id))
    
    conn.commit()
    conn.close()
    return cursor.rowcount
