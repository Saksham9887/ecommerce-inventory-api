# E-commerce Inventory & Order API

A small backend for an online store, built in Python with Flask and SQLite.
It manages a product catalog, validates stock, and places orders atomically.

## Features
- Product hierarchy using OOP: abstract `Product` with `Clothing` and `Footwear`
  subclasses, each with its own discount rule (polymorphism)
- In-memory `Inventory` with O(1) lookup by id (dict), keyword search, and sorting
- `Cart` and all-or-nothing order placement: stock is validated for every item
  before any is deducted
- SQLite persistence with foreign keys, a `CHECK (stock >= 0)` constraint, and
  transactions so an order and its stock update save together or not at all
- REST API with input validation and meaningful status codes (201, 204, 400, 404, 409)

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | /products | List products (`?q=shirt` to search, `?sort=price`) |
| GET | /products/<id> | Get one product |
| POST | /products | Create a product |
| DELETE | /products/<id> | Delete a product (409 if it has orders) |
| POST | /orders | Place an order |

## Run it
    pip install flask
    python app.py

Example order:

    POST /orders
    {"items": [{"product_id": 1, "qty": 2}]}

## Known limitations
- No authentication
- The stock check happens in Python before the database write, so simultaneous
  buyers of the last item could collide. The fix is an atomic
  `UPDATE ... WHERE stock >= ?` inside the transaction.
