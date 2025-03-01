import hashlib
import os
import csv
from abc import ABC, abstractmethod
from order import Order  # For updating the existent orders of users


class UserObserver(ABC):
    """
    Abstract base class for observing user changes.
    """
    @abstractmethod
    def update(self, user, change_type):
        pass


class ProfileUpdateNotifier(UserObserver):
    """
    Notifies when a user updates their profile.
    """
    def update(self, user, change_type):
        if change_type == "profile_updated":
            print(f" User {user.name} updated their profile.")


class User:
    """
    Represents a user in the furniture store.
    Handles user details, authentication, and order history.
    """

    def __init__(self, name: str, email: str, password: str, address: str, payment_method: str):
        """
        Initialize a User object.

        param name: Full name of the user.
        param email: Email address of the user (unique identifier).
        param password: Plaintext password for the user.
        param address: Shipping address for the user.
        param payment_method = Payment method that the user chooses.
        """
        if not self.validate_password(password):
            raise ValueError("Password must be at least 8 characters long and contain at least 1 special character")
        self.name = name
        self.email = email
        self.password = password
        self.salt = os.urandom(8).hex()  # Generate a random salt
        self.hashed_password = self.hash_password(password)  # Store hashed password and salt
        self.address = address
        self.payment_method = payment_method if payment_method else "Credit Card"  # Added default payment method
        self.order_history = []  # List of past orders
        self.wishlist = []  # We added a wish list here
        self.observers = []  # We Added observers for User changes

    def add_observer(self, observer: UserObserver):
        self.observers.append(observer)

    def remove_observer(self, observer: UserObserver):
        self.observers.remove(observer)

    def notify_observers(self, change_type):
        for observer in self.observers:
            observer.update(self, change_type)

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validate that the user's password meets security requirements.
        param password: The password the user chose.
        return: Boolean value if the password meets criteria.
        """
        if len(password) < 8:
            return False
        if not any(char in "@#$%^&*!" for char in password):
            return False
        return True

    def hash_password(self, password: str) -> str:
        """
        Hash a plaintext password using SHA-256 with a unique salt.

        param password: Plaintext password to hash.
        return: An hashed password.
        """
        salted_password = password + self.salt
        hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()[:16]
        return hashed_password

    def check_password(self, password: str) -> bool:
        """
        Rehash the input password with the stored salt and compare.

        param password: Plaintext password to verify.
        return: True if the password matches, False otherwise.
        """
        return self.hashed_password == self.hash_password(password)

    def update_profile(self, name: str = None, address: str = None):
        """
        Update the user's profile details.

        param name: New name for the user (optional).
        param address: New address for the user (optional).
        """
        if name:
            self.name = name
        if address:
            self.address = address
        self.notify_observers("profile_updated")  # Notify observers of profile updates

    def update_payment_method(self, payment_method: str):
        """
        Update the user's preferred payment method.
        param payment_method: A default value
        return: Selected payment method by the user.
        """
        self.payment_method = payment_method
        print(f"Payment method updated to: {payment_method}")

    def add_order_to_history(self, order):
        """
        Add an order to the user's order history.

        param order: Order object to add.
        """
        if isinstance(order, Order):
            self.order_history.append(order)
            self.notify_observers("order_added")
        else:
            print("Error: Trying to add a non-Order object to history")

    def view_order_history(self):
        """
        Display the user's past orders.
        """
        return [str(order) for order in self.order_history] if self.order_history else ["No past orders."]

    def add_to_wishlist(self, item):
        """
        Add an item to the user's wishlist.
        """
        self.wishlist.append(item)
        print(f"{item} added to wishlist.")

    def remove_from_wishlist(self, item):
        """
        Remove an item from the wishlist.
        """
        if item in self.wishlist:
            self.wishlist.remove(item)
            print(f" {item} removed from wishlist.")
        else:
            print(f"{item} is not in the wishlist.")

    def view_wishlist(self):
        """
        Display the user's wishlist. If it's empty, return a message.
        """
        return [item for item in self.wishlist] if self.wishlist else ["Wishlist is empty."]

    def save_to_csv(self, filename):
        # Read the existing data from the file
        updated = False
        rows = []

        try:
            with open(filename, mode="r", newline="") as file:
                reader = csv.reader(file)
                rows = list(reader)
        except FileNotFoundError:
            # If the file doesn't exist, it will be created when writing
            rows.append(
                ["name", "email", "password", "salt", "hashed_password", "address", "payment_method", "order_history",
                 "wishlist"])

        # Check if the user already exists in the CSV based on password and salt
        for i, row in enumerate(rows[1:], start=1):  # Skipping header
            if row[1] == self.email:  # Match by email instead of password and salt
                # User exists, update the row with new details
                rows[i] = [self.name, self.email, self.password, self.salt, self.hashed_password,
                           self.address, self.payment_method,
                           "|".join(self.format_order_history()) if self.order_history else None,
                           "|".join(self.wishlist) if self.wishlist else None]
                updated = True
                break

        # If the user was not found, add a new row
        if not updated:
            rows.append([self.name, self.email, self.password, self.salt, self.hashed_password,
                         self.address, self.payment_method,
                         "|".join(self.format_order_history()) if self.order_history else None,
                         "|".join(self.wishlist) if self.wishlist else None])

        # Write the updated rows to the CSV
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    def format_order_history(self):
        """Formats the order history into a string representation."""
        formatted_orders = []
        for order in self.order_history:
            # Ensure the order.items is formatted as "item_name x quantity"
            if isinstance(order.items, dict):
                formatted_items = ", ".join([f"{item} x {quantity}" for item, quantity in order.items.items()])
                formatted_orders.append(formatted_items)
        return formatted_orders

    @staticmethod
    def load_from_csv(filename, name, email, address):
        """
        Load user from CSV file based on name, email, and address
        """
        try:
            with open(filename, mode="r", newline="") as file:
                reader = csv.reader(file)

                for row in reader:
                    (csv_name, csv_email, password, salt, csv_hashed_password,
                     csv_address,payment_method, order_history, wishlist) = row

                    # Match user by name, email, and address
                    if csv_name == name and csv_email == email and csv_address == address:
                        # Reconstruct the user object from the row data
                        user = User(
                            name=csv_name,
                            email=csv_email,
                            password=password,
                            address=csv_address,
                            payment_method=payment_method
                        )
                        user.salt = salt  # Salt is stored as a string
                        user.hashed_password = csv_hashed_password  # Ensure we set the hashed password correctly
                        user.order_history = order_history.split("|") if order_history else []
                        user.wishlist = wishlist.split("|") if wishlist else []
                        return user  # Return the matched user

        except ValueError:
            print("User not found.")
        return None  # Return None if no match is found
    