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

while True:
    stock = get_valid_input()

    #Checks if user wants to quit
    if stock == "quit":
        break

    total_stock = total_stock + stock
    print(total_stock)

