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


# ---------- File Handling ----------

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


# ---------- Main Program (menu and user input) ----------

def add_product_menu(inventory):
    """Ask the user for new product details and add it to the inventory."""
    print("\nAdd New Product")
    prod_id = input("Product ID: ").strip()

    if inventory.search_product(prod_id) is not None:
        print("Error: Product ID already exists.")
        return

    name = input("Product Name: ").strip()
    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
    except ValueError:
        print("Invalid input. Price must be a number and stock must be an integer.")
        return

    if price < 0 or stock < 0:
        print("Invalid input. Price and stock cannot be negative.")
        return

    inventory.add_product(Product(prod_id, name, price, stock))
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
    print(f"ID: {product.get_product_id()}")
    print(f"Name: {product.get_name()}")
    print(f"Price: ${product.get_price():.2f}")
    print(f"Stock: {product.get_stock()}")
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
