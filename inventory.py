import sqlite3
import os
from datetime import datetime

DB_FILE = 'inventory.db'

CREATE_PRODUCTS_TABLE = '''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0
);
'''

CREATE_IMAGES_TABLE = '''
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
'''

CREATE_TRANSACTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'sale' or 'purchase'
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
'''

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(CREATE_PRODUCTS_TABLE)
    cur.execute(CREATE_IMAGES_TABLE)
    cur.execute(CREATE_TRANSACTIONS_TABLE)
    conn.commit()
    conn.close()

# Product management

def add_product(code, name, description, price, quantity=0):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO products (code, name, description, price, quantity) VALUES (?, ?, ?, ?, ?)',
                    (code, name, description, price, quantity))
        conn.commit()
        print(f'Added product {name}')
    except sqlite3.IntegrityError:
        print('Error: Product code must be unique.')
    finally:
        conn.close()


def add_image(code, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM products WHERE code = ?', (code,))
    product = cur.fetchone()
    if not product:
        print('Product not found')
        conn.close()
        return
    cur.execute('INSERT INTO images (product_id, path) VALUES (?, ?)', (product['id'], image_path))
    conn.commit()
    conn.close()
    print('Image added to product')


def list_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products')
    rows = cur.fetchall()
    for row in rows:
        print(f"{row['code']} | {row['name']} | {row['description']} | Price: {row['price']} | Qty: {row['quantity']}")
    conn.close()


def show_product(code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE code = ?', (code,))
    product = cur.fetchone()
    if not product:
        print('Product not found')
        conn.close()
        return
    print(f"Code: {product['code']}")
    print(f"Name: {product['name']}")
    print(f"Description: {product['description']}")
    print(f"Price: {product['price']}")
    print(f"Quantity: {product['quantity']}")
    cur.execute('SELECT path FROM images WHERE product_id = ?', (product['id'],))
    images = cur.fetchall()
    print('Images:')
    for img in images:
        print(f" - {img['path']}")
    conn.close()

# Transactions

def record_transaction(code, t_type, quantity, price=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE code = ?', (code,))
    product = cur.fetchone()
    if not product:
        print('Product not found')
        conn.close()
        return
    price = price if price is not None else product['price']
    if t_type == 'sale' and product['quantity'] < quantity:
        print('Not enough inventory for sale')
        conn.close()
        return
    new_qty = product['quantity'] + quantity if t_type == 'purchase' else product['quantity'] - quantity
    cur.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_qty, product['id']))
    cur.execute('INSERT INTO transactions (product_id, type, quantity, price, timestamp) VALUES (?, ?, ?, ?, ?)',
                (product['id'], t_type, quantity, price, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    print('Transaction recorded')


def list_transactions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT t.id, p.code, p.name, t.type, t.quantity, t.price, t.timestamp
        FROM transactions t
        JOIN products p ON t.product_id = p.id
        ORDER BY t.timestamp DESC
    ''')
    rows = cur.fetchall()
    for row in rows:
        print(f"#{row['id']} | {row['timestamp']} | {row['type']} | {row['code']} {row['name']} | Qty: {row['quantity']} | Price: {row['price']}")
    conn.close()

# Command line interface

def print_help():
    print('Commands:')
    print(' init-db                             Initialize database')
    print(' add-product CODE NAME DESC PRICE QTY')
    print(' add-image CODE IMAGE_PATH')
    print(' list-products')
    print(' show-product CODE')
    print(' buy CODE QTY [PRICE]                Record purchase')
    print(' sell CODE QTY [PRICE]               Record sale')
    print(' list-transactions')
    print(' help')


def main(args):
    if not args:
        print_help()
        return
    cmd = args[0]
    if cmd == 'init-db':
        init_db()
        print('Database initialized')
    elif cmd == 'add-product' and len(args) >= 6:
        code = args[1]
        name = args[2]
        desc = args[3]
        price = float(args[4])
        qty = int(args[5])
        add_product(code, name, desc, price, qty)
    elif cmd == 'add-image' and len(args) >= 3:
        code = args[1]
        path = args[2]
        if not os.path.exists(path):
            print('Image file does not exist')
            return
        add_image(code, path)
    elif cmd == 'list-products':
        list_products()
    elif cmd == 'show-product' and len(args) >= 2:
        show_product(args[1])
    elif cmd == 'buy' and len(args) >= 3:
        code = args[1]
        qty = int(args[2])
        price = float(args[3]) if len(args) >= 4 else None
        record_transaction(code, 'purchase', qty, price)
    elif cmd == 'sell' and len(args) >= 3:
        code = args[1]
        qty = int(args[2])
        price = float(args[3]) if len(args) >= 4 else None
        record_transaction(code, 'sale', qty, price)
    elif cmd == 'list-transactions':
        list_transactions()
    else:
        print_help()

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
