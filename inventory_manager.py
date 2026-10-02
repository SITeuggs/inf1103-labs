import json
import os

# Define default sample data to initialize if inventory.json does not exist
DEFAULT_INVENTORY = [
    {"id": "P001", "name": "Laptop", "price": 1200.00, "stock": 15},
    {"id": "P002", "name": "Mouse", "price": 25.50, "stock": 40},
    {"id": "P003", "name": "Keyboard", "price": 45.00, "stock": 25}
]

FILE_NAME = "inventory.json"


def load_inventory():
    """Load inventory from JSON file if it exists; otherwise load default initial data."""
    if os.path.exists(FILE_NAME):
        print(f"{FILE_NAME} found.")
        try:
            with open(FILE_NAME, "r") as f:
                inventory = json.load(f)
            print("Inventory loaded successfully.")
            return inventory
        except json.JSONDecodeError:
            print("Error reading file. Starting with default inventory.")
            return DEFAULT_INVENTORY.copy()
    else:
        print(f"{FILE_NAME} not found. Starting with default inventory.")
        return DEFAULT_INVENTORY.copy()


def save_inventory(inventory, show_message=True):
    """Save the inventory list to inventory.json."""
    if show_message:
        print("Saving inventory...")
    with open(FILE_NAME, "w") as f:
        json.dump(inventory, f, indent=4)
    print("Inventory saved successfully to inventory.json.")


def display_all(inventory):
    """Display all products in the inventory."""
    print("\nCurrent Inventory")
    if not inventory:
        print("No products available.")
        return
    for item in inventory:
        print(f"ID: {item['id']} | Name: {item['name']} | Price: ${item['price']:.2f} | Stock: {item['stock']}")


def add_product(inventory):
    """Add a new product to the inventory list."""
    print("\nAdd New Product")
    prod_id = input("Product ID: ").strip()
    
    # Check if product ID already exists
    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            print("Error: Product ID already exists.")
            return

    name = input("Product Name: ").strip()
    try:
        price = float(input("Price: "))
        stock = int(input("Stock Quantity: "))
    except ValueError:
        print("Invalid input. Price must be a number and stock must be an integer.")
        return

    new_product = {
        "id": prod_id,
        "name": name,
        "price": price,
        "stock": stock
    }
    inventory.append(new_product)
    print("Product added successfully!")


def update_stock(inventory):
    """Update stock quantity for an existing product."""
    print("\nUpdate Stock")
    prod_id = input("Enter Product ID: ").strip()

    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            print("\nProduct Found:")
            print(f"Name: {item['name']}")
            print(f"Current Stock: {item['stock']}\n")
            try:
                new_stock = int(input("New Stock Quantity: "))
                item["stock"] = new_stock
                print("\nStock updated successfully!")
                return
            except ValueError:
                print("Invalid input. Stock quantity must be an integer.")
                return

    print("Product not found.")


def search_product(inventory):
    """Search for a product by ID."""
    print("\nSearch Product")
    prod_id = input("Enter Product ID: ").strip()

    for item in inventory:
        if item["id"].lower() == prod_id.lower():
            print("\nProduct Found")
            print("-" * 40)
            print(f"ID: {item['id']}")
            print(f"Name: {item['name']}")
            print(f"Price: ${item['price']:.2f}")
            print(f"Stock: {item['stock']}")
            print("-" * 40)
            return

    print("\nProduct not found.")


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
            display_all(inventory)
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            search_product(inventory)
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