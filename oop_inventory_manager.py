import json
import os
from abc import ABC, abstractmethod
from typing import NotRequired, TypedDict

FILE_NAME: str = "inventory.json"


# Typed dictionaries describing the JSON records used to save and load the inventory.
# Each key has its own type, so a type checker knows that "price" is a float, "stock" an int, etc.
class SupplierRecord(TypedDict):
    id: str
    name: str
    contact_email: str


class ProductRecord(TypedDict):
    id: str
    name: str
    price: float
    stock: int
    supplier: NotRequired[SupplierRecord]  # missing in records saved before Lab 8
    type: NotRequired[str]                 # missing in records saved before Lab 7
    weight: NotRequired[float]             # physical products only
    download_size: NotRequired[float]      # digital products only


class Supplier:
    """A company that supplies products.
    Association with Product: a Supplier is created on its own and can exist
    without any Product, and a Product is not a part of a Supplier (no ownership)."""

    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        self.__supplier_id: str = supplier_id
        self.__name: str = name
        self.__contact_email: str = contact_email

    def get_supplier_id(self) -> str:
        return self.__supplier_id

    def get_name(self) -> str:
        return self.__name

    def get_contact_email(self) -> str:
        return self.__contact_email

    def display_information(self) -> None:
        """Display this supplier's details on one line."""
        print(f"Supplier ID: {self.__supplier_id} | Name: {self.__name} | Email: {self.__contact_email}")

    def to_dict(self) -> SupplierRecord:
        """Convert the supplier to a dictionary so it can be saved as JSON."""
        return {
            "id": self.__supplier_id,
            "name": self.__name,
            "contact_email": self.__contact_email
        }


class Product(ABC):
    """Abstract base class for all products. Cannot be instantiated directly.

    Liskov Substitution Principle: code such as Inventory and Order only knows about
    Product, so every subclass must keep the expectations Product sets out:
      - update_stock() accepts any quantity >= 0, rejects negatives, and returns a bool.
      - get_fulfilment_info() always returns a str describing delivery.
      - display_information() and to_dict() may ADD details, but keep the common ones.
    """

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier) -> None:
        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        # Association: keep a reference to a Supplier that was created elsewhere.
        # The Product does not create or own the Supplier.
        self.__supplier: Supplier = supplier

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def update_stock(self, quantity: int) -> bool:
        """Set a new stock quantity. Returns True if the update was accepted.
        Expectation for every subclass: any quantity >= 0 is accepted and becomes the
        new stock; a negative quantity is rejected (False) and the stock is unchanged.
        For a DigitalProduct, stock means the number of licences available to sell."""
        if quantity < 0:
            print("Error: Stock quantity cannot be negative.")
            return False
        self.__stock = quantity
        return True

    def display_information(self) -> None:
        """Display this product's details on one line."""
        print(f"ID: {self.__product_id} | Name: {self.__name} | Price: ${self.__price:.2f} | "
              f"Stock: {self.__stock} | Supplier: {self.__supplier.get_name()}")

    def to_dict(self) -> ProductRecord:
        """Convert the product to a dictionary so it can be saved as JSON."""
        return {
            "id": self.__product_id,
            "name": self.__name,
            "price": self.__price,
            "stock": self.__stock,
            "supplier": self.__supplier.to_dict()
        }

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        """Return a message describing how this product is delivered to the customer."""
        pass


class CanBeShipped(ABC):
    """Interface: any class that signs this contract must be able to calculate a shipping cost."""

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        """Return the cost of shipping this object."""
        pass


class PhysicalProduct(Product, CanBeShipped):
    """A product that physically exists and has a weight (in kg).
    Inherits from Product (is-a) and implements the CanBeShipped interface."""

    BASE_SHIPPING_FEE: float = 5.00   # flat fee per shipment
    COST_PER_KG: float = 2.00         # extra charge for each kg

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self.__weight: float = weight

    def get_weight(self) -> float:
        return self.__weight

    def calculate_shipping_cost(self) -> float:
        """Shipping cost = flat fee + cost per kg * weight."""
        return self.BASE_SHIPPING_FEE + self.COST_PER_KG * self.__weight

    def get_fulfilment_info(self) -> str:
        return f"{self.get_name()} requires physical shipping ({self.__weight} kg)."

    def display_information(self) -> None:
        """Display the common product details (from Product), then the weight."""
        super().display_information()
        print(f"    Type: Physical | Weight: {self.__weight} kg")

    def to_dict(self) -> ProductRecord:
        """Reuse Product's dictionary, then add the type and weight."""
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self.__weight
        return data


class DigitalProduct(Product):
    """A product delivered digitally, with a download size (in MB)."""

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self.__download_size: float = download_size

    def get_download_size(self) -> float:
        return self.__download_size

    def get_fulfilment_info(self) -> str:
        return f"{self.get_name()} is delivered digitally via download link ({self.__download_size} MB)."

    def display_information(self) -> None:
        """Display the common product details (from Product), then the download size."""
        super().display_information()
        print(f"    Type: Digital | Download Size: {self.__download_size} MB")

    def to_dict(self) -> ProductRecord:
        """Reuse Product's dictionary, then add the type and download size."""
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self.__download_size
        return data


class Inventory:
    """Manages a collection of Product objects.
    Aggregation: the Inventory is a whole made up of Product parts, but it does not
    create or own them. Products exist before they are added, and removing a Product
    only removes the Inventory's reference to it - the Product itself is not destroyed."""

    def __init__(self) -> None:
        # Typed with the base class Product, so it can hold any kind of Product
        self.__products: list[Product] = []

    def add_product(self, product: Product) -> bool:
        """Add an existing Product object. Returns False if a product with the same ID already exists."""
        if self.find_product(product.get_product_id()) is not None:
            return False
        self.__products.append(product)
        return True

    def find_product(self, product_id: str) -> Product | None:
        """Return the product with the given ID, or None if not found."""
        for product in self.__products:
            if product.get_product_id().lower() == product_id.lower():
                return product
        return None

    def remove_product(self, product_id: str) -> Product | None:
        """Remove the matching Product reference from this inventory.
        The Product object is returned (not destroyed) so it can still be used,
        or None if no product with that ID is in the inventory."""
        product = self.find_product(product_id)
        if product is not None:
            self.__products.remove(product)
        return product

    def transfer_product(self, product_id: str, destination: "Inventory") -> bool:
        """Move the same Product object from this inventory to another inventory.
        Returns False if the product is not here or the destination already has that ID."""
        product = self.find_product(product_id)
        if product is None or destination.find_product(product_id) is not None:
            return False
        self.remove_product(product_id)
        destination.add_product(product)
        return True

    def clear(self) -> None:
        """Empty the inventory. Only the references are removed; the Products still exist."""
        self.__products.clear()

    def display_all_products(self) -> None:
        """Display all products in the inventory.
        Polymorphism: each Product displays itself, and the object's own class decides
        which display_information() runs - no checks for PhysicalProduct/DigitalProduct."""
        print("\nCurrent Inventory")
        if not self.__products:
            print("No products available.")
            return
        for product in self.__products:
            product.display_information()

    def get_products(self) -> list[Product]:
        """Return a copy of the product list, so callers can read it without changing the inventory."""
        return list(self.__products)

    def to_list(self) -> list[ProductRecord]:
        """Convert all products to a list of dictionaries for saving."""
        return [product.to_dict() for product in self.__products]


class OrderLine:
    """One product and the quantity of it requested in an Order.
    Composition: an OrderLine is created by, and belongs to, exactly one Order.
    Association: it refers to a Product, but does NOT own it - the Product
    exists on its own and may also be in an Inventory."""

    def __init__(self, product: Product, quantity: int) -> None:
        self.__product: Product = product
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        """Return the product price multiplied by the quantity."""
        return self.__product.get_price() * self.__quantity

    def display_information(self) -> None:
        """Display this order line on one line."""
        print(f"{self.__product.get_product_id()} | {self.__product.get_name()} | "
              f"${self.__product.get_price():.2f} x {self.__quantity} = ${self.calculate_subtotal():.2f}")


class Order:
    """A customer order made up of OrderLine objects.
    Composition: the Order creates and manages its own OrderLines. They are never
    created outside the Order or passed in, never transferred to another Order,
    and they are removed together with the Order when it is cancelled."""

    def __init__(self, order_id: str) -> None:
        self.__order_id: str = order_id
        self.__order_lines: list[OrderLine] = []

    def get_order_id(self) -> str:
        return self.__order_id

    def add_order_line(self, product: Product, quantity: int) -> bool:
        """Create a new OrderLine inside this Order for the given product and quantity.
        Returns False (and creates nothing) if the quantity is not a positive number."""
        if quantity <= 0:
            print("Error: Order quantity must be greater than zero.")
            return False
        order_line = OrderLine(product, quantity)  # the Order creates its own part
        self.__order_lines.append(order_line)
        return True

    def remove_order_line(self, product_id: str) -> bool:
        """Remove the order line for this product. The OrderLine is discarded (not returned),
        because it has no meaning outside this Order. Returns False if no line matches."""
        for order_line in self.__order_lines:
            if order_line.get_product().get_product_id().lower() == product_id.lower():
                self.__order_lines.remove(order_line)
                return True
        return False

    def get_order_lines(self) -> list[OrderLine]:
        """Return a copy of the order lines for reading only. Changes must go through the Order."""
        return list(self.__order_lines)

    def calculate_total(self) -> float:
        """Return the total value of the order by asking each OrderLine for its subtotal."""
        return sum(order_line.calculate_subtotal() for order_line in self.__order_lines)

    def cancel(self) -> None:
        """Cancel the order. Its OrderLines are removed with it (their lifecycle is tied to the Order)."""
        self.__order_lines.clear()

    def display_information(self) -> None:
        """Display the order ID, each order line and the order total."""
        print(f"\nOrder {self.__order_id}")
        if not self.__order_lines:
            print("No order lines.")
        for order_line in self.__order_lines:
            order_line.display_information()
        print(f"Order Total: ${self.calculate_total():.2f}")


def create_default_inventory() -> Inventory:
    """Create an inventory filled with the default sample products.
    Suppliers are created first, on their own, then passed to each Product (association)."""
    tech_supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.com")
    software_supplier = Supplier("S002", "SoftWorks Ltd", "orders@softworks.com")

    inventory = Inventory()
    inventory.add_product(PhysicalProduct("P001", "Laptop", 1200.00, 15, tech_supplier, 2.0))
    inventory.add_product(PhysicalProduct("P002", "Mouse", 25.50, 40, tech_supplier, 0.1))
    inventory.add_product(PhysicalProduct("P003", "Keyboard", 45.00, 25, tech_supplier, 0.8))
    inventory.add_product(DigitalProduct("D001", "Antivirus Software", 49.99, 100, software_supplier, 350))
    return inventory


# Used for records saved before Lab 8, which have no supplier information
UNKNOWN_SUPPLIER_DATA: SupplierRecord = {"id": "S000", "name": "Unknown Supplier", "contact_email": "n/a"}


def supplier_from_dict(data: SupplierRecord, suppliers: dict[str, Supplier]) -> Supplier:
    """Return the Supplier described by data. If a Supplier with the same ID was already
    loaded, reuse that object so products from the same supplier share one Supplier."""
    supplier_id = data["id"]
    if supplier_id not in suppliers:
        suppliers[supplier_id] = Supplier(supplier_id, data["name"], data["contact_email"])
    return suppliers[supplier_id]


def product_from_dict(item: ProductRecord, suppliers: dict[str, Supplier] | None = None) -> Product:
    """Create the correct Product subclass from a saved dictionary, using its "type" field.
    Records saved before Lab 7 have no type, so they are treated as physical products.
    Records saved before Lab 8 have no supplier, so they get the "Unknown Supplier"."""
    if suppliers is None:
        suppliers = {}
    supplier = supplier_from_dict(item.get("supplier", UNKNOWN_SUPPLIER_DATA), suppliers)

    product_type = item.get("type", "physical")
    if product_type == "physical":
        return PhysicalProduct(item["id"], item["name"], item["price"], item["stock"],
                               supplier, item.get("weight", 0.0))
    if product_type == "digital":
        return DigitalProduct(item["id"], item["name"], item["price"], item["stock"],
                              supplier, item.get("download_size", 0.0))
    raise ValueError(f"Unknown product type: {product_type}")


def load_inventory() -> Inventory:
    """Load inventory from JSON file if it exists; otherwise load default initial data."""
    if not os.path.exists(FILE_NAME):
        print(f"{FILE_NAME} not found. Starting with default inventory.")
        return create_default_inventory()

    print(f"{FILE_NAME} found.")
    try:
        with open(FILE_NAME, "r") as f:
            data: list[ProductRecord] = json.load(f)
    except json.JSONDecodeError:
        print("Error reading file. Starting with default inventory.")
        return create_default_inventory()

    inventory = Inventory()
    suppliers: dict[str, Supplier] = {}  # supplier ID -> Supplier, so each supplier is only created once
    for item in data:
        try:
            inventory.add_product(product_from_dict(item, suppliers))
        except (KeyError, ValueError) as error:
            print(f"Skipping invalid product record ({error}).")
    print("Inventory loaded successfully.")
    return inventory


def save_inventory(inventory: Inventory, show_message: bool = True) -> None:
    """Save the inventory to the JSON file (FILE_NAME)."""
    if show_message:
        print("Saving inventory...")
    with open(FILE_NAME, "w") as f:
        json.dump(inventory.to_list(), f, indent=4)
    print(f"Inventory saved successfully to {FILE_NAME}.")

# Main Program
def find_supplier(inventory: Inventory, supplier_id: str) -> Supplier | None:
    """Return an existing Supplier (used by a product in the inventory) with this ID, or None."""
    for product in inventory.get_products():
        supplier = product.get_supplier()
        if supplier.get_supplier_id().lower() == supplier_id.lower():
            return supplier
    return None


def choose_supplier_menu(inventory: Inventory) -> Supplier | None:
    """Ask for a supplier ID. Reuse the existing Supplier if one is known,
    otherwise create a new Supplier from the details the user enters."""
    supplier_id = input("Supplier ID: ").strip()
    if not supplier_id:
        print("Invalid input. Supplier ID cannot be empty.")
        return None

    supplier = find_supplier(inventory, supplier_id)
    if supplier is not None:
        print(f"Using existing supplier: {supplier.get_name()}")
        return supplier

    print("New supplier - please enter the supplier details.")
    name = input("Supplier Name: ").strip()
    email = input("Supplier Contact Email: ").strip()
    return Supplier(supplier_id, name, email)


def add_product_menu(inventory: Inventory) -> None:
    """Ask the user for new product details and add it to the inventory."""
    print("\nAdd New Product")
    prod_id = input("Product ID: ").strip()

    if inventory.find_product(prod_id) is not None:
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

    supplier = choose_supplier_menu(inventory)
    if supplier is None:
        return

    if type_choice == "1":
        product: Product = PhysicalProduct(prod_id, name, price, stock, supplier, extra)
    else:
        product = DigitalProduct(prod_id, name, price, stock, supplier, extra)

    inventory.add_product(product)
    print("Product added successfully!")


def update_stock_menu(inventory: Inventory) -> None:
    """Ask the user for a product ID and new stock quantity."""
    print("\nUpdate Stock")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.find_product(prod_id)
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


def search_product_menu(inventory: Inventory) -> None:
    """Ask the user for a product ID and display the matching product."""
    print("\nSearch Product")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.find_product(prod_id)
    if product is None:
        print("\nProduct not found.")
        return

    print("\nProduct Found")
    print("-" * 40)
    product.display_information()
    product.get_supplier().display_information()
    print(f"Fulfilment: {product.get_fulfilment_info()}")
    # Shipping is NOT part of the Product contract - it is the optional CanBeShipped interface,
    # so here we check for that interface rather than for a particular Product subclass.
    if isinstance(product, CanBeShipped):
        print(f"Shipping Cost: ${product.calculate_shipping_cost():.2f}")
    print("-" * 40)


def remove_product_menu(inventory: Inventory) -> None:
    """Ask the user for a product ID and remove that product from the inventory."""
    print("\nRemove Product")
    prod_id = input("Enter Product ID: ").strip()

    product = inventory.remove_product(prod_id)
    if product is None:
        print("Product not found.")
        return
    print(f"{product.get_name()} ({product.get_product_id()}) removed from the inventory.")


def create_order_menu(inventory: Inventory) -> None:
    """Build a customer Order from products in the inventory, then display it with its total.
    The Order creates its own OrderLines through add_order_line()."""
    print("\nCreate Order")
    order_id = input("Order ID: ").strip()
    if not order_id:
        print("Invalid input. Order ID cannot be empty.")
        return
    order = Order(order_id)

    while True:
        prod_id = input("Product ID to add (press Enter to finish): ").strip()
        if not prod_id:
            break
        product = inventory.find_product(prod_id)
        if product is None:
            print("Product not found.")
            continue
        try:
            quantity = int(input("Quantity: "))
        except ValueError:
            print("Invalid input. Quantity must be an integer.")
            continue
        if order.add_order_line(product, quantity):
            print(f"Added {quantity} x {product.get_name()}.")

    order.display_information()


def main() -> None:
    print("INVENTORY MANAGEMENT SYSTEM")
    inventory = load_inventory()

    while True:
        print("\nMENU")
        print("1. Display All Products")
        print("2. Add Product")
        print("3. Update Stock")
        print("4. Search Product")
        print("5. Remove Product")
        print("6. Create Order")
        print("7. Save Inventory")
        print("8. Exit")

        choice = input("Enter option: ").strip()

        if choice == "1":
            inventory.display_all_products()
        elif choice == "2":
            add_product_menu(inventory)
        elif choice == "3":
            update_stock_menu(inventory)
        elif choice == "4":
            search_product_menu(inventory)
        elif choice == "5":
            remove_product_menu(inventory)
        elif choice == "6":
            create_order_menu(inventory)
        elif choice == "7":
            save_inventory(inventory)
        elif choice == "8":
            print("\nSaving inventory before exit...")
            save_inventory(inventory, show_message=False)
            print("\nThank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid choice. Please select a valid option (1-8).")


if __name__ == "__main__":
    main()