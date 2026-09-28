import itertools


class Order:
    _counter = itertools.count(1)  # shared by all orders, gives unique ids

    def __init__(self, lines, total):
        self.order_id = next(Order._counter)
        self.lines = lines  # list of (product_id, name, qty, unit_price)
        self.total = total

    def __str__(self):
        out = [f"Order #{self.order_id}"]
        for _, name, qty, price in self.lines:
            out.append(f"  {name} x{qty} @ Rs.{price:.2f}")
        out.append(f"  Total: Rs.{self.total:.2f}")
        return "\n".join(out)


def place_order(cart, inventory):
    if cart.is_empty():
        raise ValueError("Cart is empty")

    # check everything first, so a failure leaves stock untouched
    for product, qty in cart.items():
        if qty > inventory.get_product(product.id).stock:
            raise ValueError(f"Not enough stock for {product.name}")

    lines = []
    for product, qty in cart.items():
        inventory.get_product(product.id).reduce_stock(qty)
        lines.append((product.id, product.name, qty, product.discounted_price()))

    order = Order(lines, cart.total())
    cart.clear()
    return order