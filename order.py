import uuid
import csv
import os
import sys


class Order:
    """
    Represents an order placed by a user.
    Storing details about the order, including items, total price, and status.
    """

    def __init__(self, user, items, total_price):
        """
        Initialize an Order object.

        param user: User who placed the order.
        param items: Dictionary of items in the order {Furniture: quantity}.
        param total_price: Total price of the order after discounts.
        """
        self.order_id = str(uuid.uuid4())  # Unique identifier for the order
        self.user = user
        self.items = items
        self.total_price = total_price
        self.status = "Pending"  # Default status is "Pending"
        self.shipping_address = user.address
        self.payment_method = user.payment_method

    def complete_order(self):
        """
        Mark the order as completed.
        """
        self.status = "Completed"

    def mark_as_delivered(self):
        """
        Mark the order as delivered if it's a completed order
        """
        if self.status == "Completed":
            self.status = "Delivered"
        else:
            print("Order must be completed before marking as delivered.")

    def __str__(self):
        """
        String representation of the order.
        """
        items_str = ", ".join([f"{name} x {quantity}" for name, quantity, price in self.items])
        return (f"Order {self.order_id}: {items_str} | Total: ${self.total_price:.2f} | Status: {self.status} | "
                f"Shipping to: {self.shipping_address} | Payment method: {self.payment_method}")

    def save_order_to_csv(self, filename=None):
        """
        Save Order details to a CSV file.
        """
        if filename is None:
            filename = "test_orders.csv" if "pytest" in sys.modules else "orders.csv"
        print(f"Saving order to {filename}")

        file_exists = os.path.exists(filename)
        with open(filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["order_id", "user_email", "shipping_address", "payment_method",
                                 "items", "total_price", "status"])

            items_str = "|".join([f"{name} x {quantity} (${price:.2f})"
                                  for name, quantity, price in self.items])

            writer.writerow([self.order_id, self.user.email, self.shipping_address, self.payment_method, items_str,
                            f"${self.total_price:.2f}", self.status])

        print(f"Order saved successfully to {filename}.")

    @staticmethod
    def load_orders_from_csv(filename="orders.csv"):
        """
        Load orders from a CSV file.
        """
        orders = []
        try:
            with open(filename, mode="r") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    if len(row) < 7:  # Check if there are enough columns
                        continue
                    order = {
                        "order_id": row[0],
                        "user_email": row[1],
                        "shipping_address": row[2],
                        "payment_method": row[3],
                        "items": row[4].split("|"),
                        "total_price": row[5],
                        "status": row[6]
                    }
                    orders.append(order)
            print("Orders loaded successfully from CSV.")
        except FileNotFoundError:
            print("Orders CSV file not found.")
        return orders
