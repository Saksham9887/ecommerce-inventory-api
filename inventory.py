class Inventory:
    def __init__(self):
        self._products = {}  # product id -> Product object

    def add_product(self, product):
        if product.id in self._products:
            raise ValueError(f"Product id {product.id} already exists")
        self._products[product.id] = product

    def get_product(self, product_id):
        product = self._products.get(product_id)
        if product is None:
            raise ValueError(f"No product with id {product_id}")
        return product

    def remove_product(self, product_id):
        if product_id not in self._products:
            raise ValueError(f"No product with id {product_id}")
        del self._products[product_id]

    def search(self, keyword):
        keyword = keyword.lower()
        return [p for p in self._products.values() if keyword in p.name.lower()]

    def sorted_by_price(self, descending=False):
        return sorted(
            self._products.values(),
            key=lambda p: p.discounted_price(),
            reverse=descending,
        )

    def sorted_by_name(self):
        return sorted(self._products.values(), key=lambda p: p.name.lower())

    def low_stock(self, threshold=3):
        return [p for p in self._products.values() if p.stock <= threshold]