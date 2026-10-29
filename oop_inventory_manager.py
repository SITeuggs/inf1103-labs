import json
import os

FILE_NAME = "inventory.json"


class Product:
    """Represents and manages a single product."""

    def __init__(self, product_id, name, price, stock):
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    def update_stock(self, quantity):
        """Set a new stock quantity. Returns True if the update was accepted."""
        if quantity < 0:
            print("Error: Stock quantity cannot be negative.")
            return False
        self.__stock = quantity
        return True

    def display_information(self):
        """Display this product's details on one line."""
        print(f"ID: {self.__product_id} | Name: {self.__name} | Price: ${self.__price:.2f} | Stock: {self.__stock}")

    def to_dict(self):
        """Convert the product to a dictionary so it can be saved as JSON."""
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock
        }

class Inventory:
    """Manages a collection of Product objects."""

    def __init__(self):
        self.__products = []

    def add_product(self, product):
        """Add a product. Returns False if a product with the same ID already exists."""
        if self.search_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def search_product(self, product_id):
        """Return the product with the given ID, or None if not found."""
        for product in self.__products:
            if product.get_product_id().lower() == product_id.lower():
                return product
        return None

    def display_all(self):
        """Display all products in the inventory."""
        print("\nCurrent Inventory")
        if not self.__products:
            print("No products available.")
            return
        for product in self.__products:
            product.display_information()

    def to_list(self):
        """Convert all products to a list of dictionaries for saving."""
        return [product.to_dict() for product in self.__products]

def create_default_inventory():
    """Create an inventory filled with the default sample products."""
    inventory = Inventory()
    inventory.add_product(Product("P001", "Laptop", 1200.00, 15))
    inventory.add_product(Product("P002", "Mouse", 25.50, 40))
    inventory.add_product(Product("P003", "Keyboard", 45.00, 25))
    return inventory


def load_inventory():
    """Load inventory from JSON file if it exists; otherwise load default initial data."""
    if not os.path.exists(FILE_NAME):
        print(f"{FILE_NAME} not found. Starting with default inventory.")
        return create_default_inventory()

    print(f"{FILE_NAME} found.")
    try:
        with open(FILE_NAME, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Error reading file. Starting with default inventory.")
        return create_default_inventory()

    inventory = Inventory()
    for item in data:
        inventory.add_product(Product(item["id"], item["name"], item["price"], item["stock"]))
    print("Inventory loaded successfully.")
    return inventory


def save_inventory(inventory, show_message=True):
    """Save the inventory to inventory.json."""
    if show_message:
        print("Saving inventory...")
    with open(FILE_NAME, "w") as f:
        json.dump(inventory.to_list(), f, indent=4)
    print("Inventory saved successfully to inventory.json.")
