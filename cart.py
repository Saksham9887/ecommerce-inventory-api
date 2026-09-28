class Cart:
    def __init__(self):
        self._items = {}  # product id -> (product, quantity)

    def add(self, product, qty=1):
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        current = self._items[product.id][1] if product.id in self._items else 0
        if current + qty > product.stock:
            raise ValueError(f"Only {product.stock} of {product.name} in stock")
        self._items[product.id] = (product, current + qty)

    def remove(self, product_id):
        if product_id not in self._items:
            raise ValueError(f"Product {product_id} is not in the cart")
        del self._items[product_id]

    def items(self):
        return list(self._items.values())

    def total(self):
        return sum(p.discounted_price() * qty for p, qty in self._items.values())

    def is_empty(self):
        return not self._items

    def clear(self):
        self._items.clear()