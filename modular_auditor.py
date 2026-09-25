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
    new_total = current_total + new_value
    return new_total

# Function to calculate tax
def calculate_tax(amount):
    tax = amount * 0.10
    return tax

# Function to print out the current report
def generate_report(stock, tax, inventory):
    print(f"Added {stock} units.")
    print(f"Tax on this delivery: ${tax:.2f}")
    print(f"Current Total: {inventory}")

# Function to generate the final summary
def generate_report_summary(total_units):
    print("\n===== FINAL REPORT =====")
    print(f"Total inventory units: {total_units}")
    print("========================")

# Initialize variables
inventory = 0

while True:
    stock = get_valid_input()

    # Check if user wants to quit
    if stock == "quit":
        break

    # Calculate tax for this specific delivery
    tax = calculate_tax(stock)

    # Add delivery to inventory
    inventory = process_delivery(inventory, stock)

    # Generates the current report
    generate_report(stock, tax, inventory)

    # Check inventory limit
    if inventory > 500:
        print("ALERT! Inventory limit exceeded 500 units.")
        break

# Generate final report
generate_report_summary(inventory)
