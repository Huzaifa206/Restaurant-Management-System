import pyodbc

DB_CONFIG = {
    "server": r"DESKTOP-1GIK335\SQLEXPRESS",  
    "database": "RestaurantDatabase",
}

def get_connection():
    """Returns a live database connection using Windows Authentication.
    No username or password needed — uses your Windows PC login."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)


def execute_query(query, params=(), fetch=False):
    """
    Run any SQL query safely.
    - fetch=True  → returns list of rows (for SELECT)
    - fetch=False → commits changes (for INSERT/UPDATE/DELETE)
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] {e}")
        raise e
    finally:
        cursor.close()
        conn.close()


def test_connection():
    """Call this to verify your DB connection works."""
    try:
        conn = get_connection()
        conn.close()
        print("✅ Database connected successfully!")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def get_all_menu_items():
    return execute_query(
        "SELECT m.item_id, m.item_name, c.category_name, m.price, m.is_available "
        "FROM menu_items m JOIN categories c ON m.category_id = c.category_id "
        "WHERE m.is_available = 1",
        fetch=True
    )

def get_all_tables(branch_id=1):
    return execute_query(
        "SELECT * FROM restaurant_tables WHERE branch_id = ?",
        (branch_id,), fetch=True
    )

def get_pending_orders():
    return execute_query(
        "SELECT o.order_id, o.order_type, o.status, o.order_time, "
        "t.table_number, s.full_name as waiter "
        "FROM orders o "
        "LEFT JOIN restaurant_tables t ON o.table_id = t.table_id "
        "LEFT JOIN staff s ON o.staff_id = s.staff_id "
        "WHERE o.status IN ('Pending', 'In-Kitchen')"
        "ORDER BY o.order_time",
        fetch=True
    )

def get_low_stock_items(branch_id=1):
    return execute_query(
        "SELECT item_name, quantity_in_stock, reorder_level, unit "
        "FROM inventory "
        "WHERE branch_id = ? AND quantity_in_stock <= reorder_level",
        (branch_id,), fetch=True
    )

def authenticate_user(username, password):
    """Returns staff record if credentials match, else None."""
    results = execute_query(
        "SELECT staff_id, full_name, role, branch_id FROM staff "
        "WHERE username = ? AND password_hash = ? AND is_active = 1",
        (username, password), fetch=True
    )
    return results[0] if results else None