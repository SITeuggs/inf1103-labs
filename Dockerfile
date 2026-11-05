FROM python:3.11-slim

WORKDIR /app

# Lab 7: OOP Inventory Management System, its tests and sample data
COPY oop_inventory_manager.py test_products.py inventory.json ./

# Default: run the interactive program (use `docker run -it ...`)
# To run the tests instead: docker run --rm inventory-lab7 python test_products.py
CMD ["python", "oop_inventory_manager.py"]
