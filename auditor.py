inventory = 0
stock = 0
user_quit = True

while user_quit:
    stock = input("Enter the stock Quantity: ")
    if stock != int or int(stock) < 0:
        print("Enter a valid number.")
    else:
        inventory += stock
        if stock > 500:
            print("ALERT! More than 500 stock.")
            break
    user_quit = input("Do you want to quit? (Yes or No): ")
    if user_quit == "Yes":
        user_quit = False
