from abc import ABC, abstractmethod


class Product(ABC):
    def __init__(self, product_id, name, price, stock):
        self._id = product_id
        self._name = name
        self._price = price
        self._stock = stock

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def stock(self):
        return self._stock

    def reduce_stock(self, qty):
        if qty > self._stock:
            raise ValueError(f"Not enough stock for {self._name}")
        self._stock -= qty

    # each product type decides its own discount
    @abstractmethod
    def discounted_price(self):
        pass

    def __str__(self):
        return f"{self._id} | {self._name} | Rs.{self.discounted_price():.2f} | stock: {self._stock}"


class Clothing(Product):
    def discounted_price(self):
        return self._price * 0.90  # 10% off


class Footwear(Product):
    def discounted_price(self):
        return self._price * 0.85  # 15% off