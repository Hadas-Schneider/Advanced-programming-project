from order import Order


class ShoppingCart:
    """
    Represents a shopping cart for a user.
    Handles adding/removing items, calculating totals, and applying discounts.
    """

    def __init__(self, user):
        """
        Initialize a ShoppingCart object.

        param user: User object associated with the cart.
        """
        self.user = user
        self.cart_items = {}  # {Furniture: quantity}

    def add_item(self, item, quantity=1):
        """
        Add a furniture item to the cart or update its quantity.

        param item: Furniture object to add.
        param quantity: Quantity of the item to add (default: 1).
        """
        if item in self.cart_items:
            self.cart_items[item] += quantity
        else:
            self.cart_items[item] = quantity

    def remove_item(self, item, quantity=1):
        """
        Remove a furniture item or reduce its quantity in the cart.

        param item: Furniture object to remove.
        param quantity: Quantity to remove (default: 1).
        """
        if item in self.cart_items:
            if self.cart_items[item] <= quantity:
                del self.cart_items[item]
            else:
                self.cart_items[item] -= quantity
        else:
            print(f"Item '{item.name}' is not in the cart.")

    def view_cart(self):
        """
        Display all items in the cart, their quantities, and prices.
        """
        if not self.cart_items:
            print("Your cart is empty.")
            return

        print(f"Shopping Cart for {self.user.name}:")
        for item, quantity in self.cart_items.items():
            print(f"- {item.name}: {quantity} x ${item.price:.2f} = ${item.price * quantity:.2f}")
        print(f"Total: ${self.calculate_total():.2f}")

    def calculate_total(self):
        """
        Calculate the total price of all items in the cart.

        return: Total price as a float.
        """
        return sum(item.price * quantity for item, quantity in self.cart_items.items())

    def apply_discount(self):
        """
        Apply type-specific discounts to each item and a cart-wide discount if conditions are met.

        return: Final total price after discounts.
        """
        total = 0

        for item, quantity in self.cart_items.items():
            # Apply type-specific discounts
            discounted_price = item.calculate_discount(0)  # 0 indicates no additional discount
            total_item_price = discounted_price * quantity
            print(f"- {item.name}: {quantity} x ${discounted_price:.2f} = ${total_item_price:.2f}")
            total += total_item_price

        # Apply cart-wide discount if specific conditions are met
        cart_discount = 0
        if self.calculate_total() > 500:  # Example condition: total price > $500
            cart_discount = total * 0.1  # 10% cart-wide discount

        final_total = total - cart_discount
        print(f"Total after discounts: ${final_total:.2f}")
        return final_total

    def checkout(self, inventory):
        """
        Perform the checkout process.

        param inventory: Inventory object to validate and deduct items from.
        return: Order object if successful, None if checkout fails.
        """
        print("\nStarting checkout process...")

        # Step 1: Validate items against inventory
        for item, quantity in self.cart_items.items():
            #available_quantity = inventory.items_by_type[type(item).__name__].get(item.name, item).available_quantity
            available_quantity = inventory.items_by_type.get(type(item).__name__, {}).get(item.name,
                                                                                          item).available_quantity
            if available_quantity < quantity:
                print(f"Insufficient stock for {item.name}. Available: {available_quantity}, Requested: {quantity}")
                return None

        # Step 2: Calculate final total
        total_price = self.apply_discount()

        # Step 3: Mock payment processing
        payment_successful = self.process_payment(total_price)
        if not payment_successful:
            print("Payment failed. Please try again.")
            return None

        # Step 4: Deduct inventory and create order
        for item, quantity in self.cart_items.items():
            inventory.update_quantity(item.name, type(item).__name__, inventory.items_by_type[type(item).__name__][
                item.name].available_quantity - quantity)

        order = Order(user=self.user, items=self.cart_items, total_price=total_price)
        order.complete_order()

        # Step 5: Save order to user history
        self.user.add_order_to_history(order)

        print("Checkout completed successfully!")
        print(order)

        # Clear the cart
        self.cart_items = {}

        return order

    @staticmethod
    def process_payment(amount):
        """
        Mock payment processing.

        :param amount: Amount to process.
        :return: True if payment is successful, False otherwise.
        """
        print(f"Processing payment of ${amount:.2f}...")
        return True  # Simulate a successful payment
