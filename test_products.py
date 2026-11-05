"""Lab 7 tests: run with `python test_products.py`."""
from oop_inventory_manager import PhysicalProduct, DigitalProduct


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


if __name__ == "__main__":
    test_physical_product()
    test_digital_product()
