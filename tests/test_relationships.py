"""Lab 8 tests: run from the project folder with `python tests/test_relationships.py`.

These tests demonstrate the object relationships from Lab 8:
  - Association: Supplier <-> Product (section 2)
  - Aggregation: Inventory <>-- Product (section 3)
  - Composition: Order <#>-- OrderLine, with OrderLine --> Product (section 4)
Tests print their output so you can see the behaviour, and use assert so a failure is reported.
"""
import os
import sys

# Let this file (inside tests/) import modules from the project folder above it
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oop_inventory_manager import (
    Supplier, PhysicalProduct, DigitalProduct, Inventory, OrderLine, Order,
)


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


# ---------------------------------------------------------------------------
# Section 3: Aggregation - Inventory and Product
# ---------------------------------------------------------------------------

# 3a. Inventory supports add_product, find_product and remove_product
def test_inventory_add_find_remove() -> None:
    supplier = make_supplier()
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, supplier, 3.5)
    inventory = Inventory()

    assert inventory.add_product(guitar)
    assert inventory.find_product("P100") is guitar  # the same object, not a copy
    assert inventory.find_product("NOPE") is None

    removed = inventory.remove_product("P100")
    assert removed is guitar
    assert inventory.find_product("P100") is None
    assert inventory.remove_product("P100") is None  # nothing left to remove
    print("add_product, find_product and remove_product work")


# 3b. Test aggregation (steps 1-5 from the lab)
#     Predict first (before step 3): the Product still works after it is removed from
#     Inventory A, because remove_product only removes the Inventory's reference.
def test_aggregation_product_moves_between_inventories() -> None:
    supplier = make_supplier()

    # Step 1: create the Product BEFORE any Inventory exists
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, supplier, 3.5)
    print("Product created before any inventory:")
    guitar.display_information()

    # Step 2: add it to Inventory A
    inventory_a = Inventory()
    inventory_b = Inventory()
    inventory_a.add_product(guitar)
    inventory_a.display_all_products()

    # Step 3: remove it from Inventory A - the Product object can still be used
    inventory_a.remove_product("P100")
    print("After removing from Inventory A, the product still works:")
    guitar.display_information()
    assert guitar.update_stock(8) and guitar.get_stock() == 8

    # Step 4: add the SAME Product object to Inventory B
    inventory_b.add_product(guitar)
    inventory_b.display_all_products()

    # Step 5: removing it from an inventory did not destroy it
    assert inventory_a.find_product("P100") is None
    found = inventory_b.find_product("P100")
    assert found is guitar
    assert found.get_stock() == 8  # keeps the change made in step 3


# 3c. transfer_product moves the same object from one inventory to another
def test_transfer_product() -> None:
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, make_supplier(), 3.5)
    inventory_a, inventory_b = Inventory(), Inventory()
    inventory_a.add_product(guitar)

    assert inventory_a.transfer_product("P100", inventory_b)
    assert inventory_a.find_product("P100") is None
    assert inventory_b.find_product("P100") is guitar
    assert not inventory_a.transfer_product("P100", inventory_b)  # no longer in A
    print("Guitar transferred from Inventory A to Inventory B")


# 3d. Emptying an inventory does not destroy its products
def test_emptied_inventory_keeps_products() -> None:
    supplier = make_supplier()
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, supplier, 3.5)
    os_product = DigitalProduct("D100", "Operating System", 139.99, 100, supplier, 4500)
    inventory = Inventory()
    inventory.add_product(guitar)
    inventory.add_product(os_product)

    inventory.clear()
    inventory.display_all_products()
    assert inventory.get_products() == []

    print("Products still exist after the inventory is emptied:")
    guitar.display_information()
    os_product.display_information()
    assert guitar.get_name() == "Guitar" and os_product.get_name() == "Operating System"


# ---------------------------------------------------------------------------
# Section 4: Composition - Order and OrderLine
# ---------------------------------------------------------------------------

def make_products() -> tuple[PhysicalProduct, DigitalProduct]:
    supplier = make_supplier()
    guitar = PhysicalProduct("P100", "Guitar", 350.00, 5, supplier, 3.5)
    os_product = DigitalProduct("D100", "Operating System", 139.99, 100, supplier, 4500)
    return guitar, os_product


# 4a. OrderLine.calculate_subtotal() returns price * quantity
def test_order_line_subtotal() -> None:
    guitar, _ = make_products()
    line = OrderLine(guitar, 2)
    line.display_information()
    assert abs(line.calculate_subtotal() - 700.00) < 0.001
    assert isinstance(line.calculate_subtotal(), float)


# 4b. The Order creates its own OrderLines and calculates its total from them
def test_order_creates_lines_and_total() -> None:
    guitar, os_product = make_products()
    order = Order("O001")
    assert order.add_order_line(guitar, 2)       # 2 x 350.00 = 700.00
    assert order.add_order_line(os_product, 3)   # 3 x 139.99 = 419.97
    order.display_information()

    lines = order.get_order_lines()
    assert len(lines) == 2
    assert all(isinstance(line, OrderLine) for line in lines)  # created inside the Order
    assert abs(order.calculate_total() - 1119.97) < 0.001

    # An invalid quantity is rejected and no OrderLine is created
    assert not order.add_order_line(guitar, 0)
    assert len(order.get_order_lines()) == 2


# 4c. Predict first: the same Product added to two different Orders gives
#     2 OrderLine objects (one per Order) but still only 1 Product object.
def test_same_product_in_two_orders() -> None:
    guitar, _ = make_products()
    order_1 = Order("O001")
    order_2 = Order("O002")
    order_1.add_order_line(guitar, 1)
    order_2.add_order_line(guitar, 4)

    line_1 = order_1.get_order_lines()[0]
    line_2 = order_2.get_order_lines()[0]
    print(f"OrderLine ids: {id(line_1)} and {id(line_2)}")
    print(f"Product ids:   {id(line_1.get_product())} and {id(line_2.get_product())}")

    assert line_1 is not line_2                                   # 2 separate OrderLines
    assert line_1.get_product() is line_2.get_product() is guitar  # 1 shared Product


# 4d. Order lines are removed through the Order, and cancelling the Order removes them all
def test_remove_line_and_cancel_order() -> None:
    guitar, os_product = make_products()
    order = Order("O001")
    order.add_order_line(guitar, 2)
    order.add_order_line(os_product, 1)

    assert order.remove_order_line("P100")
    assert not order.remove_order_line("P100")  # already removed
    order.display_information()
    assert len(order.get_order_lines()) == 1

    order.cancel()
    order.display_information()
    assert order.get_order_lines() == [] and order.calculate_total() == 0

    # The Products were only referred to by the OrderLines, so they still exist
    guitar.display_information()
    os_product.display_information()


# 4e. OrderLine refers to a Product but does not own it - the Product can be in an Inventory too
def test_order_line_does_not_own_product() -> None:
    guitar, _ = make_products()
    inventory = Inventory()
    inventory.add_product(guitar)

    product = inventory.find_product("P100")
    assert product is not None  # find_product returns Product | None
    order = Order("O001")
    order.add_order_line(product, 1)
    del order  # the Order and its OrderLine are gone...

    print("Product is still in the inventory after the order is deleted:")
    inventory.display_all_products()
    assert inventory.find_product("P100") is guitar  # ...but the Product is not


TESTS = [
    ("Association: products refer to a shared Supplier", test_supplier_association),
    ("Association: products keep their Supplier after `del supplier`", test_products_keep_supplier_after_del),
    ("Association: Supplier exists independently of Products", test_supplier_exists_independently),
    ("Aggregation: Inventory add/find/remove", test_inventory_add_find_remove),
    ("Aggregation: Product moves from Inventory A to B without being destroyed",
     test_aggregation_product_moves_between_inventories),
    ("Aggregation: transfer_product moves the same object", test_transfer_product),
    ("Aggregation: emptied Inventory does not destroy Products", test_emptied_inventory_keeps_products),
    ("Composition: OrderLine calculates its subtotal", test_order_line_subtotal),
    ("Composition: Order creates its OrderLines and calculates its total", test_order_creates_lines_and_total),
    ("Composition: same Product in two Orders -> 2 OrderLines, 1 Product", test_same_product_in_two_orders),
    ("Composition: remove an order line / cancel the Order", test_remove_line_and_cancel_order),
    ("Composition: OrderLine refers to Product but does not own it", test_order_line_does_not_own_product),
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
