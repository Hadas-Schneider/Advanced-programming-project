from typing import Dict, List, Optional
import csv
import os
import sys
from User import User
from furniture import Furniture, DiscountStrategy, NoDiscount
from order import Order
from inventory import Inventory
from abc import ABC, abstractmethod
import builtins

original_open = builtins.open


def debug_open(*args, **kwargs):
    print(f"Opening file: {args[0]} | Mode: {kwargs.get('mode', 'r')}")
    return original_open(*args, **kwargs)


builtins.open = debug_open


class CartObserver(ABC):
    """
    Abstract observer for monitoring cart changes.
    """
    @abstractmethod
    def update(self, cart: 'ShoppingCart', change_type: str, item: Optional[Furniture] = None) -> None:
        pass


class CartNotifier(CartObserver):
    """
    Notifies when an item is added or removed from the cart.
    """
    def update(self, cart: 'ShoppingCart', change_type: str, item: Optional[Furniture] = None) -> None:
        if change_type == "added":
            print(f"Item '{item.name}' added to cart. ")
        elif change_type == "removed":
            print(f"Item '{item.name}' removed from cart.")


class ShoppingCart:
    """
    Represents a shopping cart for a user.
    Handles adding/removing items, calculating totals, and applying discounts.
    """

    def __init__(self, user: User, inventory: Inventory, discount_strategy: DiscountStrategy = NoDiscount()) -> None:
        """
        Initialize a ShoppingCart object (representing a shopping cart for a user).

        param user: User object associated with the cart.
        param inventory : Inventory object to check the items' stock levels
        param discount_strategy : Discount strategy to apply to the entire cart (The default is No Discount).
        """
        self.user: User = user
        self.inventory: Inventory = inventory
        self.cart_items: Dict[Furniture, int] = {}  # {Furniture: quantity}
        self.discount_strategy: DiscountStrategy = discount_strategy  # We assume no discount to start with
        self.observers: List[CartObserver] = []

    def add_observer(self, observer: CartObserver) -> None:
        self.observers.append(observer)

    def notify_observers(self, change_type: str, item: Optional[Furniture] = None) -> None:
        for observer in self.observers:
            observer.update(self, change_type, item)

    def set_cart_discount_strategy(self, discount_strategy: DiscountStrategy) -> None:
        """
        Set a discount strategy for the entire cart.This will be used as the last step in the checkout.
        """
        self.discount_strategy: DiscountStrategy = discount_strategy

    def add_item(self, item: Furniture, quantity: int = 1) -> None:
        """
        Add a furniture item to the cart or update its quantity.

        param item: Furniture object to add.
        param quantity: Quantity of the item to add (default: 1).
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        if item.name not in self.inventory.items_by_type.get(item.type, {}):
            raise KeyError(f"Item {item.name} does not exist in inventory.")

        available_quantity = self.inventory.items_by_type.get(item.type, {}).get(item.name, item).available_quantity
        if available_quantity < quantity:
            raise ValueError(f"Not enough stock units for {item.name}. Available only: {available_quantity}"
                  f", Requested: {quantity}")

        if item in self.cart_items:
            self.cart_items[item] += quantity
        else:
            self.cart_items[item] = quantity

        self.notify_observers("added", item)

    def remove_item(self, item: Furniture, quantity: int = 1) -> None:
        """
        Remove a furniture item or reduce its quantity in the cart.

        param item: Furniture object to remove.
        param quantity: Quantity to remove (default: 1).
        """
        if item is None:
            raise KeyError("Item not found in inventory.")
        if item not in self.cart_items:
            raise KeyError(f"Item '{item.name}' is not in the cart.")

        if self.cart_items[item] <= quantity:
            del self.cart_items[item]
        else:
            self.cart_items[item] -= quantity

        self.notify_observers("removed", item)

    def view_cart(self) -> None:
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

    def calculate_total(self, tax_percentage: float = 18) -> float:
        """
        Calculate the total price of all items in the cart after applying individual and cart-wide discounts.
        Args:
        tax_percentage (float): The tax rate to apply to the total after discounts.

        returns: float: Total price as a float including discounts and tax.
        """
        total = sum(item.apply_discount(item.discount_strategy) * quantity
                    for item, quantity in self.cart_items.items())
        cart_discount = self.discount_strategy.get_discount()
        total_after_discount = Furniture.price_with_discount(total, cart_discount)
        total_with_tax = total_after_discount * (1 + tax_percentage / 100)

        return round(total_with_tax, 2)

    def checkout(self) -> Optional[Order]:
        """
        Perform the checkout process.
        return: Order object if successful, None if checkout fails.
        """
        print("\nStarting checkout process...")
        print(f"Shipping to: {self.user.address}")
        print(f"Payment method: {self.user.payment_method}")
        print(f"Current inventory before update: {self.inventory.items_by_type}")

        # Validate items against inventory
        for item, quantity in self.cart_items.items():
            available_quantity = self.inventory.items_by_type.get(type(item).__name__, {}).get(item.name, item)\
                .available_quantity

            if available_quantity < quantity:
                print(f"Not enough stock for {item.name}. Available: {available_quantity}, Requested: {quantity}")
                return None

        if not self.cart_items:
            print("Checkout failed: Cart is empty.")
            return None

        # Apply discounts and calculate final total
        total_price = self.calculate_total()

        if total_price == 0:
            print("Checkout failed: Total price is 0.")
            return None
        print(f"Total after discounts: ${total_price:.2f}")

        # Mock payment processing
        payment_successful = self.process_payment(self.user, total_price)
        if not payment_successful:
            print("Payment failed. Please try again.")
            return None

        # Deduct inventory and create order
        for item, quantity in self.cart_items.items():
            new_quantity = self.inventory.items_by_type[item.type][item.name].available_quantity - quantity
            success = self.inventory.update_quantity(item.name, item.type, new_quantity)
            if success:
                print(f" {quantity} units of '{item.name}' have been deducted from inventory.")
            else:
                print(f" Warning: Could not update stock for '{item.name}'.")
        # Create and complete order
        order = Order(
            user=self.user,
            items=[(item.name, quantity, item.price) for item, quantity in self.cart_items.items()],
            total_price=total_price
        )
        order.complete_order()
        print(f" Cart content before checkout: {self.cart_items}")

        order.save_order_to_csv()  # Saving the current order to the CSV file

        cart_filename = "test_carts.csv" if "pytest" in sys.modules else "carts.csv"
        print(f"🛒 Calling clear_cart_from_csv with filename: {cart_filename}")
        self.clear_cart_from_csv(filename=cart_filename)
        self.user.add_order_to_history(order)  # Save order to user's order history
        print("Checkout completed successfully!")
        print(order)

        self.cart_items = {}  # Clear the cart
        return order

    @staticmethod
    def process_payment(user: User, amount: float) -> bool:
        """
        Mock payment processing.
        Args:
            user (User): The user object which includes payment details.
            amount (float): The amount to process for payment.
        Returns:
        True (bool) if payment is successful, False otherwise.
        """
        print(f"Processing payment of ${amount:.2f} using {user.payment_method}...")
        return True  # Simulate a successful payment

    def save_cart_to_csv(self, filename: str = "cart_data.csv") -> None:
        """
        Save the shopping cart of the user to a CSV file.
        If the user already exists in the file, update their entry.
        """
        expected_header = ["user_email", "item_name", "quantity", "price"]
        temp_data = []
        user_exists = False

        # Reading the current data
        if os.path.exists(filename) and os.stat(filename).st_size > 0:
            with open(filename, mode='r', newline='') as file:
                reader = csv.reader(file)
                headers = next(reader, None)

                if headers != expected_header:
                    print("Incorrect CSV header detected! Overwriting file.")
                    temp_data.append(expected_header)
                else:
                    temp_data.append(headers)

                for row in reader:
                    if row and row[0] == self.user.email:
                        user_exists = True
                        continue
                    temp_data.append(row)
        else:
            print("File does not exist or is empty. Adding header.")
            temp_data.append(expected_header)

        # Checking if user already exists to decide if to add or just update his data
        action = "Updating existing" if user_exists else "Adding new"
        print(f"{action} cart for {self.user.email} to CSV.")

        # Add new user's data
        for item, quantity in self.cart_items.items():
            temp_data.append([self.user.email, item.name, quantity, item.price])
        print(f"Final data before writing: {temp_data}")

        print("Writing data to CSV:", temp_data)

        # Writing the new data
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file, lineterminator="\n")
            writer.writerows(temp_data)

            print(f"Data written successfully to {filename}")
        print(f"Cart for {self.user.email} {'Updated' if user_exists else 'Saved'} to CSV.")

    def load_cart_from_csv(self, filename: str = "cart_data.csv") -> None:
        """
        Load the last shopping cart for the user from the CSV file.
        """
        print("Checking if file exists...")
        if not os.path.exists(filename):
            print("File does not exist.")
            return

        print("File exists, loading data...")
        self.cart_items = {}
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)

            # Read headers first
            headers = next(reader, None)
            print("Headers:", headers)

            expected_header = ["user_email", "item_name", "quantity", "price"]
            if headers != expected_header:
                print(f"Incorrect CSV header detected while loading. Expected {expected_header}, but got {headers}.")
                return

            # Process data rows
            for row in reader:
                print("Reading row:", row)
                if row and row[0] == self.user.email:
                    item_name, quantity = row[1], int(row[2])
                    furniture_type = self.inventory.get_furniture_type(item_name)

                    if furniture_type:
                        item = self.inventory.items_by_type[furniture_type].get(item_name)
                        if item:
                            self.cart_items[item] = quantity
                        else:
                            print(f"Warning: Item {item_name} not found in inventory.")
                    else:
                        print(f"Warning! Could not determine furniture type for '{item_name}'")
        print(f"Loaded previous cart for {self.user.email}. Cart items: {self.cart_items}")

    def clear_cart_from_csv(self, filename: str = "carts.csv") -> None:
        """
        Remove the user's cart from the CSV after checkout.
        """
        if not os.path.exists(filename):
            return
        # Keeping only the other users' carts
        with open(filename, mode="r", newline="") as file:
            reader = csv.reader(file)
            rows = [row for row in reader if row and row[0] != self.user.email]
        if rows:
            # Saving back the remaining carts of other users
            with open(filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["user_email", "item_name", "quantity", "price"])
                writer.writerows(rows)
                print(f" Cart for {self.user.email} cleared after checkout.")
        else:
            os.remove(filename)
