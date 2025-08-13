"""
E-commerce Product Management System (Self-contained, auto-creates DB & tables)
Requires: mysql-connector-python
Install: pip install mysql-connector-python
Change DB_USER and DB_PASS below to match your MySQL credentials.
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
import csv
import os
import decimal

DB_HOST = "localhost"
DB_USER = "root"        # <-- change this
DB_PASS = "@Shivam94102"   # <-- change this
DB_NAME = "eco"

# ---------------------------
# 1) Connect to MySQL server and create database if needed
# ---------------------------
try:
    root_conn = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS)
    root_cursor = root_conn.cursor()
    root_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    root_conn.commit()
    root_cursor.close()
    root_conn.close()
except Error as e:
    print("Error connecting to MySQL server:", e)
    raise SystemExit(1)

# ---------------------------
# 2) Connect to the created database
# ---------------------------
try:
    mydb = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
    cursor = mydb.cursor(buffered=True)
except Error as e:
    print("Error connecting to database:", e)
    raise SystemExit(1)

# ---------------------------
# 3) Create tables (if not exists)
# ---------------------------
TABLES = {}

TABLES['categories'] = """
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255)
) ENGINE=InnoDB;
"""

TABLES['products'] = """
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0,
    category_id INT,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
) ENGINE=InnoDB;
"""

TABLES['customers'] = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(30),
    address VARCHAR(255),
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""

TABLES['orders'] = """
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) DEFAULT 'Pending', -- Pending, Processing, Shipped, Delivered, Cancelled
    total_amount DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
) ENGINE=InnoDB;
"""

TABLES['order_items'] = """
CREATE TABLE IF NOT EXISTS order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    line_total DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL
) ENGINE=InnoDB;
"""

for name, ddl in TABLES.items():
    cursor.execute(ddl)
mydb.commit()

# ---------------------------
# 4) Seed sample categories & products (only if empty)
# ---------------------------
def seed_data():
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ("Electronics", "Phones, laptops, accessories"),
            ("Clothing", "Men and Women apparel"),
            ("Home", "Home and kitchen"),
        ]
        cursor.executemany("INSERT INTO categories (name, description) VALUES (%s,%s)", categories)
        mydb.commit()

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        # Get a valid category id for Electronics
        cursor.execute("SELECT category_id FROM categories WHERE name=%s", ("Electronics",))
        cat = cursor.fetchone()
        electronics_id = cat[0] if cat else None

        products = [
            ("SKU-APPLE-IP12", "iPhone 12", "Apple iPhone 12, 64GB", 39999.00, 10, electronics_id),
            ("SKU-GALAXY-S21", "Samsung Galaxy S21", "Samsung S21, 128GB", 34999.00, 8, electronics_id),
            ("SKU-TSHIRT-BLUE", "Blue T-Shirt", "Cotton T-Shirt (Blue)", 399.00, 50, None),
        ]
        cursor.executemany(
            "INSERT INTO products (sku, name, description, price, stock, category_id) VALUES (%s,%s,%s,%s,%s,%s)",
            products
        )
        mydb.commit()

seed_data()

# ---------------------------
# 5) Helper utilities
# ---------------------------
def to_decimal(x):
    if isinstance(x, decimal.Decimal):
        return float(x)
    return x

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ---------------------------
# 6) Product & Category management
# ---------------------------
def list_categories():
    cursor.execute("SELECT category_id, name, description FROM categories")
    rows = cursor.fetchall()
    print("\nCategories:")
    for r in rows:
        print(f"{r[0]} - {r[1]}: {r[2]}")
    if not rows:
        print("No categories found.")

def add_category():
    name = input("Category name: ").strip()
    desc = input("Description: ").strip()
    try:
        cursor.execute("INSERT INTO categories (name, description) VALUES (%s,%s)", (name, desc))
        mydb.commit()
        print("Category added.")
    except Error as e:
        print("Error adding category:", e)

def list_products(show_all=True):
    q = """SELECT p.product_id, p.sku, p.name, p.price, p.stock, c.name
           FROM products p LEFT JOIN categories c ON p.category_id = c.category_id
           ORDER BY p.created_on DESC"""
    cursor.execute(q)
    rows = cursor.fetchall()
    print("\nProducts:")
    for r in rows:
        print(f"ID:{r[0]} | SKU:{r[1]} | {r[2]} | ₹{to_decimal(r[3])} | Stock:{r[4]} | Category:{r[5]}")
    if not rows:
        print("No products found.")

def add_product():
    sku = input("SKU (unique): ").strip()
    name = input("Product name: ").strip()
    desc = input("Description: ").strip()
    price = float(input("Price: ").strip())
    stock = int(input("Stock quantity: ").strip())
    list_categories()
    cat_in = input("Enter Category ID (or blank): ").strip()
    cat_id = int(cat_in) if cat_in else None
    try:
        cursor.execute(
            "INSERT INTO products (sku, name, description, price, stock, category_id) VALUES (%s,%s,%s,%s,%s,%s)",
            (sku, name, desc, price, stock, cat_id)
        )
        mydb.commit()
        print("Product added.")
    except Error as e:
        print("Error adding product:", e)

def update_stock():
    list_products()
    pid = int(input("Enter product ID to update stock: ").strip())
    delta = int(input("Enter stock change (positive to add, negative to reduce): ").strip())
    cursor.execute("SELECT stock FROM products WHERE product_id=%s", (pid,))
    r = cursor.fetchone()
    if not r:
        print("Product not found.")
        return
    new_stock = r[0] + delta
    if new_stock < 0:
        print("Error: resulting stock would be negative.")
        return
    cursor.execute("UPDATE products SET stock=%s WHERE product_id=%s", (new_stock, pid))
    mydb.commit()
    print("Stock updated.")

def search_products():
    key = input("Search keyword (name or sku): ").strip()
    cursor.execute("""
        SELECT product_id, sku, name, price, stock FROM products
        WHERE name LIKE %s OR sku LIKE %s
    """, ('%'+key+'%', '%'+key+'%'))
    rows = cursor.fetchall()
    print("\nSearch Results:")
    for r in rows:
        print(f"ID:{r[0]} | SKU:{r[1]} | {r[2]} | ₹{to_decimal(r[3])} | Stock:{r[4]}")
    if not rows:
        print("No products matched.")

# ---------------------------
# 7) Customer management
# ---------------------------
def add_customer():
    name = input("Customer name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    address = input("Address: ").strip()
    try:
        cursor.execute("INSERT INTO customers (name, email, phone, address) VALUES (%s,%s,%s,%s)",
                       (name, email, phone, address))
        mydb.commit()
        print("Customer added.")
    except Error as e:
        print("Error adding customer:", e)

def list_customers():
    cursor.execute("SELECT customer_id, name, email, phone FROM customers")
    rows = cursor.fetchall()
    print("\nCustomers:")
    for r in rows:
        print(f"ID:{r[0]} | {r[1]} | {r[2]} | {r[3]}")
    if not rows:
        print("No customers yet.")

# ---------------------------
# 8) Orders: create, view, update status
# ---------------------------
def create_order():
    # Select or create customer
    list_customers()
    cust_in = input("Enter Customer ID (or 'n' to add new customer): ").strip()
    if cust_in.lower() == 'n':
        add_customer()
        cursor.execute("SELECT LAST_INSERT_ID()")
        cust_id = cursor.fetchone()[0]
    else:
        cust_id = int(cust_in)

    # Build order items
    items = []
    while True:
        list_products()
        pid = int(input("Enter product ID to add to order (0 to finish): ").strip())
        if pid == 0:
            break
        qty = int(input("Quantity: ").strip())
        # check stock
        cursor.execute("SELECT price, stock, name FROM products WHERE product_id=%s", (pid,))
        rec = cursor.fetchone()
        if not rec:
            print("Invalid product ID.")
            continue
        price, stock, pname = rec
        if stock < qty:
            print(f"Not enough stock for {pname}. Available: {stock}")
            continue
        line_total = float(price) * qty
        items.append((pid, qty, float(price), line_total))
        print(f"Added {qty} x {pname}")

    if not items:
        print("No items in order. Aborting.")
        return

    # Insert order and items within transaction
    try:
        mydb.start_transaction()
        cursor.execute("INSERT INTO orders (customer_id, status, total_amount) VALUES (%s,%s,%s)",
                       (cust_id, 'Processing', 0))
        cursor.execute("SELECT LAST_INSERT_ID()")
        order_id = cursor.fetchone()[0]

        total_amount = 0
        for pid, qty, unit_price, line_total in items:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total) VALUES (%s,%s,%s,%s,%s)",
                (order_id, pid, qty, unit_price, line_total)
            )
            # reduce stock
            cursor.execute("UPDATE products SET stock = stock - %s WHERE product_id=%s", (qty, pid))
            total_amount += line_total

        cursor.execute("UPDATE orders SET total_amount=%s WHERE order_id=%s", (total_amount, order_id))
        mydb.commit()
        print(f"Order {order_id} created successfully. Total: ₹{round(total_amount,2)}")
        generate_invoice(order_id)
    except Error as e:
        mydb.rollback()
        print("Failed to create order:", e)

def list_orders():
    cursor.execute("""
        SELECT o.order_id, o.order_date, c.name, o.status, o.total_amount
        FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
    """)
    rows = cursor.fetchall()
    print("\nOrders:")
    for r in rows:
        print(f"OrderID:{r[0]} | Date:{r[1]} | Customer:{r[2]} | Status:{r[3]} | Total:₹{to_decimal(r[4])}")
    if not rows:
        print("No orders found.")

def view_order_details():
    oid = int(input("Enter Order ID: ").strip())
    cursor.execute("""
        SELECT o.order_id, o.order_date, c.name, c.email, o.status, o.total_amount
        FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id=%s
    """, (oid,))
    order = cursor.fetchone()
    if not order:
        print("Order not found.")
        return
    print(f"\nOrder {order[0]} | Date: {order[1]} | Customer: {order[2]} | Email: {order[3]} | Status: {order[4]} | Total: ₹{to_decimal(order[5])}")
    cursor.execute("""
        SELECT oi.item_id, p.sku, p.name, oi.quantity, oi.unit_price, oi.line_total
        FROM order_items oi LEFT JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id=%s
    """, (oid,))
    items = cursor.fetchall()
    print("\nItems:")
    for it in items:
        print(f"{it[0]} | SKU:{it[1]} | {it[2]} | Qty:{it[3]} | Unit:₹{to_decimal(it[4])} | Line:₹{to_decimal(it[5])}")

def update_order_status():
    list_orders()
    oid = int(input("Enter Order ID to update: ").strip())
    new_status = input("Enter new status (Pending/Processing/Shipped/Delivered/Cancelled): ").strip().capitalize()
    if new_status not in ('Pending','Processing','Shipped','Delivered','Cancelled'):
        print("Invalid status.")
        return
    cursor.execute("UPDATE orders SET status=%s WHERE order_id=%s", (new_status, oid))
    mydb.commit()
    print("Order status updated.")

# ---------------------------
# 9) Exports & invoices
# ---------------------------
def export_products_csv():
    cursor.execute("SELECT product_id, sku, name, price, stock FROM products")
    rows = cursor.fetchall()
    with open("products_export.csv", "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["product_id", "sku", "name", "price", "stock"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], to_decimal(r[3]), r[4]])
    print("Products exported to products_export.csv")

def export_orders_csv():
    cursor.execute("""
        SELECT o.order_id, o.order_date, c.name, o.status, o.total_amount
        FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id
    """)
    rows = cursor.fetchall()
    with open("orders_export.csv", "w", newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(["order_id", "order_date", "customer", "status", "total_amount"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], r[3], to_decimal(r[4])])
    print("Orders exported to orders_export.csv")

def generate_invoice(order_id):
    # create a simple text invoice
    cursor.execute("""
        SELECT o.order_id, o.order_date, c.name, c.email, c.phone, o.status, o.total_amount
        FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id=%s
    """, (order_id,))
    order = cursor.fetchone()
    if not order:
        print("Cannot generate invoice: order not found.")
        return
    cursor.execute("""
        SELECT p.sku, p.name, oi.quantity, oi.unit_price, oi.line_total
        FROM order_items oi LEFT JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id=%s
    """, (order_id,))
    items = cursor.fetchall()
    filename = f"Invoice_{order_id}.txt"
    with open(filename, "w", encoding='utf-8') as f:
        f.write("----- Invoice -----\n")
        f.write(f"Order ID: {order[0]}\nDate: {order[1]}\nCustomer: {order[2]}\nEmail: {order[3]}\nPhone: {order[4]}\nStatus: {order[5]}\n\n")
        f.write("Items:\n")
        for it in items:
            f.write(f"{it[0]} | {it[1]} | Qty:{it[2]} | Unit:₹{to_decimal(it[3])} | Line:₹{to_decimal(it[4])}\n")
        f.write(f"\nTotal: ₹{to_decimal(order[6])}\n")
    print(f"Invoice generated: {filename}")

# ---------------------------
# 10) Main menu
# ---------------------------
def main_menu():
    while True:
        print("""
=== E-commerce Product Management ===
1. List Categories
2. Add Category
3. List Products
4. Add Product
5. Update Product Stock
6. Search Products
7. List Customers
8. Add Customer
9. Create Order
10. List Orders
11. View Order Details
12. Update Order Status
13. Export Products CSV
14. Export Orders CSV
0. Exit
""")
        ch = input("Enter choice: ").strip()
        if ch == "1":
            list_categories()
        elif ch == "2":
            add_category()
        elif ch == "3":
            list_products()
        elif ch == "4":
            add_product()
        elif ch == "5":
            update_stock()
        elif ch == "6":
            search_products()
        elif ch == "7":
            list_customers()
        elif ch == "8":
            add_customer()
        elif ch == "9":
            create_order()
        elif ch == "10":
            list_orders()
        elif ch == "11":
            view_order_details()
        elif ch == "12":
            update_order_status()
        elif ch == "13":
            export_products_csv()
        elif ch == "14":
            export_orders_csv()
        elif ch == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    try:
        main_menu()
    finally:
        cursor.close()
        mydb.close()
