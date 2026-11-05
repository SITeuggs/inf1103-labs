"""Lab 7 tests: run with `python test_products.py`."""
from oop_inventory_manager import Product, PhysicalProduct, DigitalProduct


def test_physical_product():
    print("Step 1.2 - PhysicalProduct")
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, 3.5)
    guitar.display_information()
    print()


def test_digital_product():
    print("Step 1.3 - DigitalProduct")
    os_product = DigitalProduct("D100", "Operating System", 139.99, 100, 4500)
    os_product.display_information()
    print()


def test_method_overriding():
    print("Step 2.2 - Method overriding (parent info + child info)")
    products = [
        PhysicalProduct("P101", "Desk Lamp", 39.90, 12, 1.2),
        DigitalProduct("D101", "Photo Editor", 59.00, 50, 850),
    ]
    for product in products:
        product.display_information()
    print()


def test_fulfilment_info():
    print("Step 3.2 - get_fulfilment_info()")
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, 3.5)
    os_product = DigitalProduct("D100", "Operating System", 139.99, 100, 4500)
    print(guitar.get_fulfilment_info())
    print(os_product.get_fulfilment_info())
    print()


def test_abstract_product():
    print("Step 3.3 - Trying to create a Product directly")
    try:
        Product("X001", "Generic Thing", 10.00, 1)
        print("Unexpected: Product was created!")
    except TypeError as error:
        print(f"TypeError: {error}")
    print()


if __name__ == "__main__":
    test_physical_product()
    test_digital_product()
    test_method_overriding()
    test_fulfilment_info()
    test_abstract_product()
