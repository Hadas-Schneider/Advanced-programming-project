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
        self.password, self.salt = self.hash_password(password)  # Store hashed password and salt
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
        :param password: the password the user chose.
        :return: boolean value if the password meets criteria.
        """
        if len(password) < 8:
            return False
        if not any(char in "@#$%^&*!" for char in password):
            return False
        return True

    @staticmethod
    def hash_password(password: str) -> (str, str):
        """
        Hash a plaintext password using SHA-256 with a unique salt.

        param password: Plaintext password to hash.
        return: A tuple of (hashed_password, salt).
        """
        salt = os.urandom(16).hex()  # Generate a random salt
        salted_password = password + salt
        hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        return hashed_password, salt

    def check_password(self, password: str) -> bool:
        """
        Verify if a plaintext password matches the stored hashed password.

        param password: Plaintext password to verify.
        return: True if the password matches, False otherwise.
        """
        salted_password = password + self.salt
        hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        return hashed_password == self.password

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
        param payment_method: a default value
        return: selected payment method by the user.
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
        print(f"{item.name} added to wishlist.")

    def remove_from_wishlist(self, item):
        """
        Remove an item from the wishlist.
        """
        if item in self.wishlist:
            self.wishlist.remove(item)
            print(f" {item.name} removed from wishlist.")
        else:
            print(f"{item.name} is not in the wishlist.")

    def view_wishlist(self):
        """
        Display the user's wishlist. If it's empty, return a message.
        """
        return [item.name for item in self.wishlist] if self.wishlist else ["Wishlist is empty."]

    def save_to_csv(self, filename="users.csv"):
        """
        Save user details to a CSV file.
        """
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["name", "email", "password", "salt", "address", "payment_method", "order_history",
                            "wishlist"])
            writer.writerow([
                self.name, self.email, self.password, self.salt, self.address, self.payment_method,
                "|".join(self.order_history) if self.order_history else "No orders",
                "|".join(self.wishlist) if self.wishlist else "Wishlist is empty"
            ])
        print("User data saved successfully to CSV.")

    @staticmethod
    def load_from_csv(filename="users.csv"):
        """
        Load user details from a CSV file.
        """
        try:
            with open(filename, mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    user = User(row["name"], row["email"], row["password"], row["address"],
                                row.get("payment_method", "Credit Card")
                                )
                    user.order_history = row["order_history"].split("|") if row["order_history"] != "No orders" else []
                    user.wishlist = row["wishlist"].split("|") if row["wishlist"] != "Wishlist is empty" else []
                    print(" User data loaded successfully from CSV.")
                    return user
        except FileNotFoundError:
            print(" User CSV file not found.")
        return None
