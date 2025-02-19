from furniture import Furniture, DiscountStrategy, NoDiscount, FurnitureFactory
from order import Order
from inventory import Inventory
from abc import ABC, abstractmethod
import csv
import os


class CartObserver(ABC):
    """
    Abstract observer for monitoring cart changes.
    """
    @abstractmethod
    def update(self, cart, change_type, item=None):
        pass


class CartNotifier(CartObserver):
    """
    Notifies when an item is added or removed from the cart.
    """
    def update(self, cart, change_type, item=None):
        if change_type == "added":
            print(f"Item '{item.name}' added to cart. ")
        elif change_type == "removed":
            print(f"Item '{item.name}' removed from cart.")


class ShoppingCart:
    """
    Represents a shopping cart for a user.
    Handles adding/removing items, calculating totals, and applying discounts.
    """

    def __init__(self, user, inventory: Inventory):
        """
        Initialize a ShoppingCart object.

        param user: User object associated with the cart.
        """
        self.user = user
        self.inventory = inventory
        self.cart_items = {}  # {Furniture: quantity}
        self.observers = []

    def add_observer(self, observer: CartObserver):
        self.observers.append(observer)

    def notify_observers(self, change_type, item=None):
        for observer in self.observers:
            observer.update(self, change_type, item)

    def add_item(self, item: Furniture, quantity=1):
        """
        Add a furniture item to the cart or update its quantity.

        param item: Furniture object to add.
        param quantity: Quantity of the item to add (default: 1).
        """
        available_quantity = self.inventory.items_by_type.get(item.type, {}).get(item.name, item).available_quantity
        if available_quantity < quantity:
            print(f"Not enough stock units for {item.name}. Available only: {available_quantity}, Requested: {quantity}")
            return

        if item in self.cart_items:
            self.cart_items[item] += quantity
        else:
            self.cart_items[item] = quantity
        self.notify_observers("added", item)

    def remove_item(self, item: Furniture, quantity=1):
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
            self.notify_observers("removed", item)
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
        return sum(item.apply_discount() * quantity for item, quantity in self.cart_items.items())

    def checkout(self):
        """
        Perform the checkout process.
        return: Order object if successful, None if checkout fails.
        """
        print("\nStarting checkout process...")
        print(f"Shipping to: {self.user.address}")
        print(f"Payment method: {self.user.payment_method}")

        # Validate items against inventory
        for item, quantity in self.cart_items.items():
            available_quantity = inventory.items_by_type.get(type(item).__name__, {}).get(item.name,
                                                                                      item).available_quantity
            if available_quantity < quantity:
                print(f"Not enough stock for {item.name}. Available: {available_quantity}, Requested: {quantity}")
                return None

        # Apply discounts and calculate final total
        total_price = self.apply_discount()
        print(f"Total after discounts: ${total_price:.2f}")

        # Mock payment processing
        payment_successful = self.process_payment(total_price)
        if not payment_successful:
            print("Payment failed. Please try again.")
            return None

        # Deduct inventory and create order
        for item, quantity in self.cart_items.items():
            self.inventory.update_quantity(item.name, item.type, self.inventory.items_by_type[item.type][item.name]
                                           .available_quantity - quantity)

        # Create and complete order
        order = Order(user=self.user, items=self.cart_items, total_price=total_price)
        order.complete_order()
        order.save_order_to_csv()  # Saving the current order to the CSV file

        self.clear_cart_from_csv()  # Delete the user's current ordered cart from the carts' CSV file
        self.user.add_order_to_history(order)  # Save order to user's order history

        print("Checkout completed successfully!")
        print(order)

        self.cart_items = {}  # Clear the cart
        return order

    @staticmethod
    def process_payment(amount):
        """
        Mock payment processing.
        :param amount: Amount to process.
        :return: True if payment is successful, False otherwise.
        """
        print(f"Processing payment of ${amount:.2f} using {self.user.payment_method}...")
        return True  # Simulate a successful payment

    def save_cart_to_csv(self, filename="carts.csv"):
        """
        Save the shopping cart of the user to a CSV file.
        Each user's cart is saved separately using their email as an identifier.
        """
        rows = []

        if os.path.exists(filename):
            with open(filename, mode="r", newline="") as file:
                reader = csv.reader(file)
                rows = [row for row in reader if row and row[0] != self.user.email]

        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["user_email", "item_name", "quantity", "price"])

            # Save all carts excluding the current one
            writer.writerows(rows)

            # Save the current cart
            for item, quantity in self.cart_items.items():
                writer.writerow([self.user.email, item.name, quantity, item.price])
        print(f"Cart for {self.user.email} Saved to CSV.")

    def load_cart_from_csv(self, filename="carts.csv"):
        """
        Load the last shopping cart for the user from the CSV file.
        """
        if not os.path.exists(filename):
            print("No saved carts found.")
            return

        self.cart_items = {}
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the headlines row
            for row in reader:
                if row and row[0] == self.user.email:
                    item_name, quantity, price = row[1], int(row[2]), float(row[3])

                    # Create a Furniture instance
                    item = FurnitureFactory.create_furniture(furniture_type=item_name, name=item_name, price=price)
                    self.cart_items[item] = quantity
        print(f"Loaded previous cart for {self.user.email}.")

    def clear_cart_from_csv(self, filename="carts.csv"):
        """
        Remove the user's cart from the CSV after checkout.
        """
        if not os.path.exists(filename):
            return
        # Keeping only the other users' carts
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            rows = [row for row in reader if row and row[0] != self.user.email]

        # Saving back the remaining carts of other users
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["user_email", "item_name", "quantity", "price"])
            writer.writerows(rows)

        print(f" Cart for {self.user.email} cleared after checkout.")


