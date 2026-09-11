# Initialize state tracking variables
inventory = 0

while True:
    user_input = input("Enter a stock quantity (or 'quit' to exit): ").strip()

    # Check for quit command (case-insensitive)
    if user_input.lower() == "quit":
        break

    # Validate if input consists only of digits (handles non-integers and negative signs)
    if not user_input.isdigit():
        print("Error: Invalid input. Please enter a positive whole number.")
        continue

    # Convert valid input string to an integer
    stock = int(user_input)

    # Business rule validation and state updating
    if stock < 0:
        print("Error: Negative numbers are not allowed.")
    else:
        inventory += stock
        print(f"Added {stock} units. Current Total: {inventory}")

        # Trigger alert and break if inventory exceeds 500
        if inventory > 500:
            print("ALERT! Inventory limit exceeded 500 units.")
            break

