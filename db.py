import sqlite3
from models import Clothing, Footwear
from inventory import Inventory

CATEGORIES = {"clothing": Clothing, "footwear": Footwear}


class Database:
    def __init__(self, path="shop.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def next_product_id(self):
        row = self.conn.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM products"
        ).fetchone()
        return row[0]

    def delete_product(self, product_id):
        with self.conn:
            cur = self.conn.execute(
                "DELETE FROM products WHERE id = ?", (product_id,)
            )
        return cur.rowcount > 0

    def _create_tables(self):
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL CHECK (stock >= 0),
                    category TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS order_items (
                    order_id INTEGER NOT NULL REFERENCES orders(id),
                    product_id INTEGER NOT NULL REFERENCES products(id),
                    qty INTEGER NOT NULL,
                    unit_price REAL NOT NULL
                );
            """)

    def is_empty(self):
        return self.conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0

    def save_product(self, product):
        category = type(product).__name__.lower()
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO products (id, name, price, stock, category) "
                "VALUES (?, ?, ?, ?, ?)",
                (product.id, product.name, product.price, product.stock, category),
            )

    def load_inventory(self):
        inv = Inventory()
        rows = self.conn.execute(
            "SELECT id, name, price, stock, category FROM products"
        ).fetchall()
        for pid, name, price, stock, category in rows:
            inv.add_product(CATEGORIES[category](pid, name, price, stock))
        return inv

    def save_order(self, order, inventory):
        with self.conn:  # one transaction: everything saves, or nothing does
            cur = self.conn.execute(
                "INSERT INTO orders (total) VALUES (?)", (order.total,)
            )
            order.order_id = cur.lastrowid
            for product_id, name, qty, unit_price in order.lines:
                self.conn.execute(
                    "INSERT INTO order_items (order_id, product_id, qty, unit_price) "
                    "VALUES (?, ?, ?, ?)",
                    (order.order_id, product_id, qty, unit_price),
                )
                self.conn.execute(
                    "UPDATE products SET stock = ? WHERE id = ?",
                    (inventory.get_product(product_id).stock, product_id),
                )
        return order