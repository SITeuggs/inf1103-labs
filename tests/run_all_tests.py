"""Run every test file in this folder: `python tests/run_all_tests.py` (from the project folder).

Each test file is run on its own, and a short summary is printed at the end.
"""
import os
import subprocess
import sys

TESTS_FOLDER = os.path.dirname(os.path.abspath(__file__))
TEST_FILES: list[str] = [
    "test_products.py",          # Lab 7: inheritance, abstract classes, interfaces, JSON
    "test_relationships.py",     # Lab 8: association, aggregation, composition
    "test_lsp_polymorphism.py",  # Lab 8: Liskov Substitution Principle and polymorphism
]


def main() -> None:
    results: list[tuple[str, bool]] = []
    for file_name in TEST_FILES:
        print("\n" + "#" * 70)
        print(f"# Running {file_name}")
        print("#" * 70)
        completed = subprocess.run([sys.executable, os.path.join(TESTS_FOLDER, file_name)])
        results.append((file_name, completed.returncode == 0))

    print("\n" + "=" * 70)
    print("ALL TEST FILES")
    print("=" * 70)
    for file_name, passed in results:
        print(f"[{'PASS' if passed else 'FAIL'}] {file_name}")
    if not all(passed for _, passed in results):
        raise SystemExit(1)
    print("\nAll test files passed.")


if __name__ == "__main__":
    main()
