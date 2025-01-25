import hashlib
import os


class User:
    """
    Represents a user in the furniture store.
    Handles user details, authentication, and order history.
    """

    def __init__(self, name: str, email: str, password: str, address: str):
        """
        Initialize a User object.

        :param name: Full name of the user.
        :param email: Email address of the user (unique identifier).
        :param password: Plaintext password for the user.
        :param address: Shipping address for the user.
        """
        self.name = name
        self.email = email
        self.password, self.salt = self.hash_password(password)  # Store hashed password and salt
        self.address = address
        self.order_history = []  # List of past orders
        # we can add a wish list here

    @staticmethod
    def hash_password(password: str) -> (str, str):
        """
        Hash a plaintext password using SHA-256 with a unique salt.

        :param password: Plaintext password to hash.
        :return: A tuple of (hashed_password, salt).
        """
        salt = os.urandom(16).hex()  # Generate a random salt
        salted_password = password + salt
        hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        return hashed_password, salt

    def check_password(self, password: str) -> bool:
        """
        Verify if a plaintext password matches the stored hashed password.

        :param password: Plaintext password to verify.
        :return: True if the password matches, False otherwise.
        """
        salted_password = password + self.salt
        hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        return hashed_password == self.password

    def update_profile(self, name: str = None, address: str = None):
        """
        Update the user's profile details.

        :param name: New name for the user (optional).
        :param address: New address for the user (optional).
        """
        if name:
            self.name = name
        if address:
            self.address = address

    def add_order_to_history(self, order):
        """
        Add an order to the user's order history.

        :param order: Order object to add.
        """
        self.order_history.append(order)

    def view_order_history(self):
        """
        Display the user's past orders.
        """
        if not self.order_history:
            print(f"{self.name} has no past orders.")
        else:
            print(f"Order History for {self.name}:")
            for order in self.order_history:
                print(f"- {order}")
