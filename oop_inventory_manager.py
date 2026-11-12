import json
import os
from abc import ABC, abstractmethod

FILE_NAME = "inventory.json"


class Product(ABC):
    """Abstract base class for all products. Cannot be instantiated directly."""

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

    @abstractmethod
    def get_fulfilment_info(self):
        """Return a message describing how this product is delivered to the customer."""
        pass


class CanBeShipped(ABC):
    """Interface: any class that signs this contract must be able to calculate a shipping cost."""

    @abstractmethod
    def calculate_shipping_cost(self):
        """Return the cost of shipping this object."""
        pass


class PhysicalProduct(Product, CanBeShipped):
    """A product that physically exists and has a weight (in kg).
    Inherits from Product (is-a) and implements the CanBeShipped interface."""

    BASE_SHIPPING_FEE = 5.00   # flat fee per shipment
    COST_PER_KG = 2.00         # extra charge for each kg

    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)
        self.__weight = weight

    def get_weight(self):
        return self.__weight

    def calculate_shipping_cost(self):
        """Shipping cost = flat fee + cost per kg * weight."""
        return self.BASE_SHIPPING_FEE + self.COST_PER_KG * self.__weight

    def get_fulfilment_info(self):
        return f"{self.get_name()} requires physical shipping ({self.__weight} kg)."

    def display_information(self):
        """Display the common product details (from Product), then the weight."""
        super().display_information()
        print(f"    Type: Physical | Weight: {self.__weight} kg")

    def to_dict(self):
        """Reuse Product's dictionary, then add the type and weight."""
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self.__weight
        return data


class DigitalProduct(Product):
    """A product delivered digitally, with a download size (in MB)."""

    def __init__(self, product_id, name, price, stock, download_size):
        super().__init__(product_id, name, price, stock)
        self.__download_size = download_size

    def get_download_size(self):
        return self.__download_size

    def get_fulfilment_info(self):
        return f"{self.get_name()} is delivered digitally via download link ({self.__download_size} MB)."

    def display_information(self):
        """Display the common product details (from Product), then the download size."""
        super().display_information()
        print(f"    Type: Digital | Download Size: {self.__download_size} MB")

    def to_dict(self):
        """Reuse Product's dictionary, then add the type and download size."""
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self.__download_size
        return data


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
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.00, 15, 2.0))
    inventory.add_product(PhysicalProduct("P002", "Mouse", 25.50, 40, 0.1))
    inventory.add_product(PhysicalProduct("P003", "Keyboard", 45.00, 25, 0.8))
    inventory.add_product(DigitalProduct("D001", "Antivirus Software", 49.99, 100, 350))
    return inventory


def product_from_dict(item):
    """Create the correct Product subclass from a saved dictionary, using its "type" field.
    Records saved before Lab 7 have no type, so they are treated as physical products."""
    product_type = item.get("type", "physical")
    if product_type == "physical":
        return PhysicalProduct(item["id"], item["name"], item["price"], item["stock"],
                               item.get("weight", 0.0))
    if product_type == "digital":
        return DigitalProduct(item["id"], item["name"], item["price"], item["stock"],
                              item.get("download_size", 0.0))
    raise ValueError(f"Unknown product type: {product_type}")


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
        try:
            inventory.add_product(product_from_dict(item))
        except (KeyError, ValueError) as error:
            print(f"Skipping invalid product record ({error}).")
    print("Inventory loaded successfully.")
    return inventory


def save_inventory(inventory, show_message=True):
    """Save the inventory to the JSON file (FILE_NAME)."""
    if show_message:
        print("Saving inventory...")
    with open(FILE_NAME, "w") as f:
        json.dump(inventory.to_list(), f, indent=4)
    print(f"Inventory saved successfully to {FILE_NAME}.")

# Main Program
def add_product_menu(inventory):
    """Ask the user for new product details and add it to the inventory."""
    print("\nAdd New Product")
    prod_id = input("Product ID: ").strip()

    if inventory.search_product(prod_id) is not None:
        print("Error: Product ID already exists.")
        return

    print("Product Type:")
    print("1. Physical Product")
    print("2. Digital Product")
    type_choice = input("Choose type (1-2): ").strip()
    if type_choice not in ("1", "2"):
        print("Invalid product type.")
        return

    name = input("Product Name: ").strip()
    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
        if type_choice == "1":
            extra = float(input("Weight (kg): "))
        else:
            extra = float(input("Download Size (MB): "))
    except ValueError:
        print("Invalid input. Price, weight and download size must be numbers, and stock must be an integer.")
        return

    if price < 0 or stock < 0 or extra < 0:
        print("Invalid input. Values cannot be negative.")
        return

    if type_choice == "1":
        product = PhysicalProduct(prod_id, name, price, stock, extra)
    else:
        product = DigitalProduct(prod_id, name, price, stock, extra)

    inventory.add_product(product)
    print("Product added successfully!")


def update_stock_menu(inventory):
    """Ask the user for a product ID and new stock quantity."""
    print("\nUpdate Stock")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.search_product(prod_id)
    if product is None:
        print("Product not found.")
        return

    print("\nProduct Found:")
    print(f"Name: {product.get_name()}")
    print(f"Current Stock: {product.get_stock()}\n")
    try:
        new_stock = int(input("New Stock Quantity: "))
    except ValueError:
        print("Invalid input. Stock quantity must be an integer.")
        return

    if product.update_stock(new_stock):
        print("\nStock updated successfully!")


def search_product_menu(inventory):
    """Ask the user for a product ID and display the matching product."""
    print("\nSearch Product")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.search_product(prod_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("-" * 40)
    product.display_information()
    print(f"Fulfilment: {product.get_fulfilment_info()}")
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")
    print("-" * 40)


def main():
    print("INVENTORY MANAGEMENT SYSTEM")
    inventory = load_inventory()

    while True:
        print("\nMENU")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Save Inventory")
        print("6. Exit")

        choice = input("Enter option: ").strip()

        if choice == "1":
            inventory.display_all()
        elif choice == "2":
            add_product_menu(inventory)
        elif choice == "3":
            update_stock_menu(inventory)
        elif choice == "4":
            search_product_menu(inventory)
        elif choice == "5":
            save_inventory(inventory)
        elif choice == "6":
            print("\nSaving inventory before exit...")
            save_inventory(inventory, show_message=False)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid choice. Please select a valid option (1-6).")


if __name__ == "__main__":
    main()