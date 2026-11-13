"""Lab 8 tests: run from the project folder with `python tests/test_relationships.py`.

These tests demonstrate the object relationships from Lab 8:
  - Association: Supplier <-> Product (section 2)
Tests print their output so you can see the behaviour, and use assert so a failure is reported.
"""
import os
import sys

# Let this file (inside tests/) import modules from the project folder above it
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oop_inventory_manager import Supplier, PhysicalProduct, DigitalProduct


def make_supplier() -> Supplier:
    return Supplier("S100", "Acme Supplies", "sales@acme.com")


# ---------------------------------------------------------------------------
# Section 2: Association - Supplier and Product
# ---------------------------------------------------------------------------

# 2a. A Supplier is created on its own, then given to each Product when the Product is created
def test_supplier_association() -> None:
    supplier = make_supplier()
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, supplier, 3.5)
    os_product = DigitalProduct("D100", "Operating System", 139.99, 100, supplier, 4500)

    print("Supplier information through the PhysicalProduct:")
    guitar.get_supplier().display_information()
    print("Supplier information through the DigitalProduct:")
    os_product.get_supplier().display_information()

    # Both products refer to the SAME Supplier object (a reference, not a copy)
    assert guitar.get_supplier() is supplier
    assert os_product.get_supplier() is supplier
    # The Supplier and the Products are separate objects
    assert guitar is not supplier and os_product is not supplier
    print(f"id(supplier)={id(supplier)}, id(guitar)={id(guitar)}, id(os_product)={id(os_product)}")


# 2b. Predict first: what happens after `del supplier`?
#     `del` only removes the variable NAME. The products still hold a reference to the
#     Supplier object, so it is not destroyed and the products can still display it.
def test_products_keep_supplier_after_del() -> None:
    supplier = make_supplier()
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, supplier, 3.5)
    os_product = DigitalProduct("D100", "Operating System", 139.99, 100, supplier, 4500)
    supplier_id_before = id(supplier)

    del supplier
    print("After `del supplier`:")
    guitar.get_supplier().display_information()
    os_product.get_supplier().display_information()

    assert id(guitar.get_supplier()) == supplier_id_before
    assert guitar.get_supplier() is os_product.get_supplier()


# 2c. A Supplier can exist before any Product, and after its Products are gone
def test_supplier_exists_independently() -> None:
    supplier = make_supplier()
    print("Supplier exists before any product is created:")
    supplier.display_information()

    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, supplier, 3.5)
    guitar.display_information()
    del guitar

    print("Supplier still exists after the product is deleted:")
    supplier.display_information()
    assert supplier.get_name() == "Acme Supplies"


TESTS = [
    ("Association: products refer to a shared Supplier", test_supplier_association),
    ("Association: products keep their Supplier after `del supplier`", test_products_keep_supplier_after_del),
    ("Association: Supplier exists independently of Products", test_supplier_exists_independently),
]


if __name__ == "__main__":
    results = []
    for number, (description, test) in enumerate(TESTS, start=1):
        print(f"\n=== Test {number}: {description} ===")
        try:
            test()
            results.append((description, "PASS"))
        except AssertionError as error:
            print(f"FAILED: {error}")
            results.append((description, "FAIL"))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for description, result in results:
        print(f"[{result}] {description}")
    passed = sum(1 for _, result in results if result == "PASS")
    print(f"\n{passed}/{len(results)} tests passed.")
    if passed != len(results):
        raise SystemExit(1)
