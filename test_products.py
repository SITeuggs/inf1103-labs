"""Lab 7 tests: run with `python test_products.py`.

Each test matches one item from the Lab 7 "Testing and review" checklist (section 7).
Tests print their output so you can see the behaviour, and use assert so a failure is reported.
"""
import json
import os
import tempfile

import oop_inventory_manager as manager
from oop_inventory_manager import (
    Product, PhysicalProduct, DigitalProduct, CanBeShipped, Inventory,
    product_from_dict, load_inventory, save_inventory,
)


def make_guitar():
    return PhysicalProduct("P100", "Guitar", 350.00, 5, 3.5)


def make_os():
    return DigitalProduct("D100", "Operating System", 139.99, 100, 4500)


# 1. Physical products store and display their weights
def test_physical_weight():
    guitar = make_guitar()
    guitar.display_information()
    assert guitar.get_weight() == 3.5
    # Inherited from Product
    assert guitar.get_name() == "Guitar" and guitar.get_stock() == 5


# 2. Digital products store and display their download sizes
def test_digital_download_size():
    os_product = make_os()
    os_product.display_information()
    assert os_product.get_download_size() == 4500
    assert os_product.get_price() == 139.99


# 3. Both subclasses implement get_fulfilment_info()
def test_fulfilment_info():
    guitar, os_product = make_guitar(), make_os()
    print(guitar.get_fulfilment_info())
    print(os_product.get_fulfilment_info())
    assert "physical shipping" in guitar.get_fulfilment_info()
    assert "delivered digitally" in os_product.get_fulfilment_info()


# 4. The abstract Product class cannot be instantiated directly
def test_product_is_abstract():
    try:
        Product("X001", "Generic Thing", 10.00, 1)
    except TypeError as error:
        print(f"TypeError (expected): {error}")
    else:
        raise AssertionError("Product should not be instantiable")


# 5. Physical products can calculate shipping costs (rule: $5.00 + $2.00 per kg)
def test_shipping_cost():
    for weight, expected in [(0.05, 5.10), (3.5, 12.00), (15.0, 35.00)]:
        product = PhysicalProduct("P1", "Item", 10.0, 1, weight)
        cost = product.calculate_shipping_cost()
        print(f"{weight} kg -> ${cost:.2f}")
        assert abs(cost - expected) < 0.001
    assert isinstance(make_guitar(), CanBeShipped)


# 6. Digital products are not required to implement shipping behaviour
def test_digital_not_shippable():
    os_product = make_os()
    assert not isinstance(os_product, CanBeShipped)
    assert not hasattr(os_product, "calculate_shipping_cost")
    print("DigitalProduct does not implement CanBeShipped")


# 7. Inventory operations continue to work
def test_inventory_operations():
    inventory = Inventory()
    assert inventory.add_product(make_guitar())
    assert inventory.add_product(make_os())
    assert not inventory.add_product(make_guitar()), "duplicate ID should be rejected"

    found = inventory.search_product("p100")  # search is case-insensitive
    assert found is not None and found.get_name() == "Guitar"
    assert inventory.search_product("NOPE") is None

    assert found.update_stock(20) and found.get_stock() == 20
    assert not found.update_stock(-1) and found.get_stock() == 20

    inventory.display_all()
    assert len(inventory.to_list()) == 2


# 8. JSON saving and loading preserve the correct product types
def test_json_round_trip():
    inventory = Inventory()
    inventory.add_product(make_guitar())
    inventory.add_product(make_os())

    original_file = manager.FILE_NAME
    with tempfile.TemporaryDirectory() as folder:
        manager.FILE_NAME = os.path.join(folder, "test_inventory.json")  # never touch the real file
        try:
            save_inventory(inventory, show_message=False)
            with open(manager.FILE_NAME) as f:
                saved = json.load(f)
            print(json.dumps(saved, indent=2))
            assert saved[0]["type"] == "physical" and saved[0]["weight"] == 3.5
            assert saved[1]["type"] == "digital" and saved[1]["download_size"] == 4500

            reloaded = load_inventory()  # simulates restarting the program
        finally:
            manager.FILE_NAME = original_file

    guitar = reloaded.search_product("P100")
    os_product = reloaded.search_product("D100")
    assert type(guitar) is PhysicalProduct and guitar.get_weight() == 3.5
    assert type(os_product) is DigitalProduct and os_product.get_download_size() == 4500


# Extra: records saved before Lab 7 (no "type") still load, as physical products
def test_old_json_record_loads():
    product = product_from_dict({"id": "P001", "name": "Laptop", "price": 1200.0, "stock": 15})
    assert isinstance(product, PhysicalProduct) and product.get_weight() == 0.0
    print("Old-format record loaded as PhysicalProduct")


TESTS = [
    ("Physical products store and display their weights", test_physical_weight),
    ("Digital products store and display their download sizes", test_digital_download_size),
    ("Both subclasses implement get_fulfilment_info()", test_fulfilment_info),
    ("Abstract Product cannot be instantiated", test_product_is_abstract),
    ("Physical products calculate shipping costs", test_shipping_cost),
    ("Digital products do not implement shipping", test_digital_not_shippable),
    ("Inventory operations continue to work", test_inventory_operations),
    ("JSON save/load preserves product types", test_json_round_trip),
    ("Old JSON records (no type) still load", test_old_json_record_loads),
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
