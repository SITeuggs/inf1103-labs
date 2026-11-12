FROM python:3.11-slim

WORKDIR /app

# OOP Inventory Management System, its tests and sample data
COPY oop_inventory_manager.py inventory.json ./
COPY tests/ ./tests/

# Default: run the interactive program (use `docker run -it ...`)
# To run the tests instead: docker run --rm inventory-lab9 python tests/test_products.py
CMD ["python", "oop_inventory_manager.py"]
