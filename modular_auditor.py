# Initialize variables
inventory = 0

# Function to get user input and check its validity
def get_valid_input():
    while True:
        # Get user input
        user_input = input("Enter a stock quantity (or 'quit' to exit): ").strip()

        # Check for quit command
        if user_input.lower() == "quit":
            return "quit"

        # Check if input is a positive whole number
        if not user_input.isdigit():
            print("Error: Invalid input. Please enter a positive whole number.")
            continue

        stock = int(user_input)

        # Return the valid integer
        return stock

# Function to calculate the new total and return it
def process_delivery(current_total, new_value):
    """Adds the new delivery to the current inventory total."""
    new_total = current_total + new_value
    return new_total

# Function to calculate tax
def calculate_tax(amount):
    """Calculates 10% tax on a delivery amount."""
    tax = amount * 0.10
    return tax

