from models import Clothing, Footwear
from cart import Cart
from order import place_order
from db import Database

db = Database("shop.db")

# seed the database only the first time
if db.is_empty():
    for p in [
        Clothing(1, "Denim Jacket", 2000, 5),
        Footwear(2, "Running Shoes", 3000, 2),
        Clothing(3, "Cotton T-Shirt", 800, 20),
    ]:
        db.save_product(p)

inv = db.load_inventory()
print("Stock at start:")
for p in inv.sorted_by_name():
    print(" ", p)

cart = Cart()
cart.add(inv.get_product(1), 1)
cart.add(inv.get_product(3), 2)

order = place_order(cart, inv)
db.save_order(order, inv)
print()
print(order)