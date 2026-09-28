import sqlite3
from flask import Flask, jsonify, request, g
from db import Database, CATEGORIES
from cart import Cart
from order import place_order

app = Flask(__name__)


def get_db():
    # one database connection per request
    if "db" not in g:
        g.db = Database("shop.db")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.conn.close()


def product_to_dict(p):
    return {
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "discounted_price": round(p.discounted_price(), 2),
        "stock": p.stock,
        "category": type(p).__name__.lower(),
    }


# any ValueError from our business logic becomes a clean 400 response
@app.errorhandler(ValueError)
def handle_value_error(e):
    return jsonify({"error": str(e)}), 400


@app.get("/products")
def list_products():
    inv = get_db().load_inventory()
    q = request.args.get("q")
    products = inv.search(q) if q else inv.sorted_by_name()
    if request.args.get("sort") == "price":
        products = sorted(products, key=lambda p: p.discounted_price())
    return jsonify([product_to_dict(p) for p in products])


@app.get("/products/<int:product_id>")
def get_product(product_id):
    inv = get_db().load_inventory()
    try:
        product = inv.get_product(product_id)
    except ValueError:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product_to_dict(product))


@app.post("/products")
def create_product():
    data = request.get_json(silent=True) or {}
    missing = [f for f in ("name", "price", "stock", "category") if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    category = str(data["category"]).lower()
    if category not in CATEGORIES:
        return jsonify({"error": f"category must be one of {list(CATEGORIES)}"}), 400

    try:
        price = float(data["price"])
        stock = int(data["stock"])
    except (TypeError, ValueError):
        return jsonify({"error": "price must be a number and stock an integer"}), 400
    if price <= 0 or stock < 0:
        return jsonify({"error": "price must be positive and stock non-negative"}), 400

    db = get_db()
    product = CATEGORIES[category](db.next_product_id(), data["name"], price, stock)
    db.save_product(product)
    return jsonify(product_to_dict(product)), 201


@app.delete("/products/<int:product_id>")
def delete_product(product_id):
    try:
        deleted = get_db().delete_product(product_id)
    except sqlite3.IntegrityError:
        return jsonify({"error": "Product has existing orders and cannot be deleted"}), 409
    if not deleted:
        return jsonify({"error": "Product not found"}), 404
    return "", 204


@app.post("/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    items = data.get("items")
    if not items or not isinstance(items, list):
        return jsonify({"error": "items must be a non-empty list"}), 400

    db = get_db()
    inv = db.load_inventory()
    cart = Cart()
    for item in items:
        try:
            pid = int(item["product_id"])
            qty = int(item["qty"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "each item needs an integer product_id and qty"}), 400
        cart.add(inv.get_product(pid), qty)

    order = place_order(cart, inv)
    db.save_order(order, inv)
    return jsonify({
        "order_id": order.order_id,
        "total": order.total,
        "items": [
            {"product_id": pid, "name": name, "qty": qty, "unit_price": price}
            for pid, name, qty, price in order.lines
        ],
    }), 201


if __name__ == "__main__":
    app.run(debug=True)