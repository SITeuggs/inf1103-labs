FROM python:3.11-slim

WORKDIR /app

# OOP Inventory Management System (Lab 8), its tests and sample data
COPY oop_inventory_manager.py inventory.json ./
COPY tests/ ./tests/

# Build:            docker build -t inventory-lab8 .
# Run the program:  docker run -it --rm inventory-lab8
# Run all tests:    docker run --rm inventory-lab8 python tests/run_all_tests.py
CMD ["python", "oop_inventory_manager.py"]
