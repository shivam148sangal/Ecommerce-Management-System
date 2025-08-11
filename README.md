# E-commerce Product Management System

A Python-based E-commerce Product Management System with MySQL integration.  
It supports **category, product, customer, and order management**, along with **stock updates, CSV exports, and invoice generation**.  
The system uses a **simple command-line menu** for easy inventory and order handling.

---

## 🚀 Features
- **Category Management** – Add and list product categories.
- **Product Management** – Add, list, search, and update stock.
- **Customer Management** – Add and list customers.
- **Order Management** – Create orders, view details, update status.
- **Data Export** – Export products and orders to CSV.
- **Invoice Generation** – Generate text invoices for orders.
- **MySQL Integration** – All data stored in MySQL database.

---

## 📦 Requirements
- Python 
- MySQL server
- `mysql-connector-python` library

Install the required library:

pip install mysql-connector-python


## ⚙️ Setup

1. Make sure MySQL server is running.
2. Enter your MySQL username and password" in `E-Commerce.py`:

   ```python
   DB_HOST = "localhost"
   DB_USER = "root"
   DB_PASS = "your_password"
   DB_NAME = "ecommerce_db"
   ```

## 📋 Menu Options

The main menu includes:

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
15. Exit

---

## 📂 Outputs

* **CSV files** – Products and orders can be exported as ".csv" files.
* **Invoices** – Orders generate ".txt." invoices in the current directory.

