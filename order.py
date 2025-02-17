import uuid


class Order:
    """
    Represents an order placed by a user.
    Stores details about the order, including items, total price, and status.
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

    def complete_order(self):
        """
        Mark the order as completed.
        """
        self.status = "Completed"

    def __str__(self):
        """
        String representation of the order.
        """
        items_str = ", ".join([f"{item.name} x {quantity}" for item, quantity in self.items.items()])
        return f"Order {self.order_id}: {items_str} | Total: ${self.total_price:.2f} | Status: {self.status}"
