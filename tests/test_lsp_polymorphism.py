"""Lab 8 tests: run from the project folder with `python tests/test_lsp_polymorphism.py`.

These tests demonstrate:
  - The Liskov Substitution Principle (section 6)
  - Polymorphism through the common Product type (section 7)
None of the code under test checks whether a product is a PhysicalProduct or a
DigitalProduct - it only uses what Product promises.
Tests print their output so you can see the behaviour, and use assert so a failure is reported.
"""
import contextlib
import io
import os
import sys

# Let this file (inside tests/) import modules from the project folder above it
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oop_inventory_manager import Supplier, Product, PhysicalProduct, DigitalProduct, Inventory


def make_products() -> list[Product]:
    """One PhysicalProduct and one DigitalProduct, both typed simply as Product."""
    supplier = Supplier("S100", "Acme Supplies", "sales@acme.com")
    return [
        PhysicalProduct("P100", "Guitar", 350.00, 5, supplier, 3.5),
        DigitalProduct("D100", "Operating System", 139.99, 100, supplier, 4500),
    ]


def capture_output(product: Product) -> str:
    """Run show_product_details() and return what it printed (and print it too)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        show_product_details(product)
    print(buffer.getvalue(), end="")
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Section 6: Liskov Substitution Principle
# ---------------------------------------------------------------------------

def show_product_details(product: Product) -> None:
    """Section 6.2: accepts ANY Product and only uses behaviour every Product supports."""
    product.display_information()
    print(product.get_fulfilment_info())


# 6a. show_product_details works with both subclasses, without changing the function
def test_show_product_details_substitutable() -> None:
    physical, digital = make_products()
    physical_output = capture_output(physical)
    digital_output = capture_output(digital)

    assert "Type: Physical" in physical_output and "physical shipping" in physical_output
    assert "Type: Digital" in digital_output and "delivered digitally" in digital_output


# 6b. Both product types can be added to an Inventory and used by its normal operations
def test_both_types_work_in_inventory() -> None:
    inventory = Inventory()
    for product in make_products():
        assert inventory.add_product(product)

    inventory.display_all_products()
    for product_id in ("P100", "D100"):
        found = inventory.find_product(product_id)
        assert found is not None
        assert found.update_stock(42) and found.get_stock() == 42

    assert len(inventory.to_list()) == 2
    assert inventory.remove_product("D100") is not None
    assert inventory.remove_product("P100") is not None
    assert inventory.get_products() == []
    print("add, find, update_stock, to_list and remove work for both product types")


# 6c. Section 6.3: the update_stock() expectation set by Product is kept by BOTH subclasses
def test_update_stock_expectation_preserved() -> None:
    for product in make_products():
        name = type(product).__name__
        # Valid inputs the parent accepts must also be accepted by the subclass
        assert product.update_stock(0) is True and product.get_stock() == 0
        assert product.update_stock(50) is True and product.get_stock() == 50
        # Invalid input is rejected the same way, and the stock is unchanged
        assert product.update_stock(-1) is False and product.get_stock() == 50
        print(f"{name}: accepts 0 and 50, rejects -1, always returns a bool")


# 6d. Other expectations: return types and the common dictionary keys are preserved
def test_other_expectations_preserved() -> None:
    for product in make_products():
        info = product.get_fulfilment_info()
        assert isinstance(info, str) and info != ""
        record = product.to_dict()
        for key in ("id", "name", "price", "stock", "supplier"):
            assert key in record, f"{type(product).__name__}.to_dict() is missing {key}"
        print(f"{type(product).__name__}: fulfilment info is a str, to_dict keeps the Product keys")


# 6e. Diagnose: the teammate's proposed DigitalProduct breaks code written for Product
class BrokenDigitalProduct(DigitalProduct):
    """The teammate's proposal from section 6.3 - NOT used in the real program."""

    def update_stock(self, quantity: int) -> bool:
        raise NotImplementedError("Digital products have no stock")


def restock_all(products: list[Product], quantity: int) -> None:
    """Code written only against Product, like Inventory would be."""
    for product in products:
        product.update_stock(quantity)


def test_teammate_proposal_violates_lsp() -> None:
    supplier = Supplier("S100", "Acme Supplies", "sales@acme.com")
    good: list[Product] = make_products()
    restock_all(good, 10)  # works for the real subclasses
    print("restock_all works with the real PhysicalProduct and DigitalProduct")

    broken: list[Product] = good + [BrokenDigitalProduct("D200", "E-book", 9.99, 1, supplier, 5)]
    try:
        restock_all(broken, 10)
    except NotImplementedError as error:
        print(f"BrokenDigitalProduct crashes code that expects a Product: {error}")
    else:
        raise AssertionError("BrokenDigitalProduct should have broken restock_all")


# ---------------------------------------------------------------------------
# Section 7: Polymorphism through the common Product type
# ---------------------------------------------------------------------------

# 7a. Predict first: the Guitar prints that it "requires physical shipping (3.5 kg)", and the
#     Operating System prints that it "is delivered digitally via download link (4500 MB)".
#     ONE loop over the Inventory, no isinstance(), no separate loops per type.
def test_polymorphism_single_loop() -> None:
    inventory = Inventory()
    for product in make_products():
        inventory.add_product(product)

    outputs: list[str] = []
    for product in inventory.get_products():
        outputs.append(capture_output(product))  # display_information() + get_fulfilment_info()

    assert "Type: Physical | Weight: 3.5 kg" in outputs[0]
    assert "Guitar requires physical shipping (3.5 kg)." in outputs[0]
    assert "Type: Digital | Download Size: 4500 MB" in outputs[1]
    assert "Operating System is delivered digitally via download link (4500 MB)." in outputs[1]


# 7b. The same method call runs a different implementation depending on the object
def test_same_call_different_behaviour() -> None:
    physical, digital = make_products()
    for product in (physical, digital):
        method_owner = type(product).get_fulfilment_info.__qualname__
        print(f"{product.get_name()}: get_fulfilment_info() runs {method_owner}")
    assert physical.get_fulfilment_info() != digital.get_fulfilment_info()
    assert type(physical).get_fulfilment_info is not type(digital).get_fulfilment_info


TESTS = [
    ("LSP: show_product_details works with both subclasses", test_show_product_details_substitutable),
    ("LSP: both product types work with Inventory operations", test_both_types_work_in_inventory),
    ("LSP: update_stock() expectation preserved by both subclasses", test_update_stock_expectation_preserved),
    ("LSP: return types and common keys preserved", test_other_expectations_preserved),
    ("LSP: teammate's DigitalProduct.update_stock violates LSP", test_teammate_proposal_violates_lsp),
    ("Polymorphism: one loop, correct specialised behaviour", test_polymorphism_single_loop),
    ("Polymorphism: same call, different implementation", test_same_call_different_behaviour),
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
