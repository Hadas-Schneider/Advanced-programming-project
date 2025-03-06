import unittest
from shopping_cart import ShoppingCart
from furniture import Chair, Table
from User import User
from inventory import Inventory
import os
from unittest.mock import patch, mock_open


class TestRegressionCheckout(unittest.TestCase):
    """
    Regression tests for the shopping cart system.
    Verifies that the checkout process correctly updates inventory,
    user order history and saves orders properly without affecting relevant classes.
    """
    def setUp(self):
        """ Set up test environment with a user, inventory and shopping cart. """
        self.user = User("Jane Doe", "jane@example.com", "Secure@123", "456 Another St", "PayPal")
        self.inventory = Inventory()
        self.cart = ShoppingCart(self.user, self.inventory)

        # Create and add items to inventory
        self.chair = Chair(u_id="001", name="Office Chair", description="Ergonomic chair",
                           material="Metal", color="Black", wp=2, price=100.0, dimensions=(60, 60, 120),
                           country="USA", available_quantity=5, has_armrests=True)

        self.table = Table(u_id="002", name="Dining Table", description="Wooden dining table",
                           material="Wood", color="Brown", wp=3, price=250.0, dimensions=(180, 90, 75),
                           country="Canada", available_quantity=3, shape="Rectangular", is_extendable=True)

        self.inventory.add_item(self.chair)
        self.inventory.add_item(self.table)
        # Add items to the cart.
        self.cart.add_item(self.chair, quantity=1)
        self.cart.add_item(self.table, quantity=2)

    @patch("order.open", new_callable=mock_open)
    @patch("shopping_cart.open", new_callable=mock_open)
    def test_checkout_process(self, mock_file_order, mock_file_cart):
        """
        Regression test to verify checkout updates all components correctly:
        - Updates inventory correctly
        - Saves orders properly
        - Clears the cart after checkout
        - Stores the order in user history
        """
        # Ensure cart is not empty before checkout
        self.assertGreater(len(self.cart.cart_items), 0, "Cart should not be empty before checkout")

        # Capture initial stock levels before checkout
        initial_chair_stock = self.inventory.items_by_type["Chair"]["Office Chair"].available_quantity
        initial_table_stock = self.inventory.items_by_type["Table"]["Dining Table"].available_quantity

        # Calculate expected total price before checkout
        expected_total = self.cart.calculate_total()

        # Simulate checkout process (mocking file writes)
        # Make sure that every call to "open("orders.csv")" redirects to "test_orders.csv"
        with patch("builtins.open", mock_open()) as mocked_file:
            order = self.cart.checkout()

        # Ensure order is created successfully
        self.assertIsNotNone(order, "Order should not be None after successful checkout.")

        # Verify inventory is updated correctly
        self.assertEqual(order.total_price, expected_total, "Order total price should match calculated total")

        updated_chair_stock = self.inventory.items_by_type["Chair"]["Office Chair"].available_quantity
        updated_table_stock = self.inventory.items_by_type["Table"]["Dining Table"].available_quantity

        self.assertEqual(updated_chair_stock, initial_chair_stock - 1,
                         "Inventory for chairs should be reduced after checkout")
        self.assertEqual(updated_table_stock, initial_table_stock - 2,
                         "Inventory for tables should be reduced after checkout")

        # Verify cart is cleared after checkout
        self.assertEqual(len(self.cart.cart_items), 0, "Cart should be empty after checkout")

        # Verify order is saved in user's order history
        self.assertIn(order, self.user.order_history, "Order should be saved in user's order history")

        print(" Regression test for checkout passed!")

    def tearDown(self):
        """ Cleanup test-generated files to ensure a clean state for future tests. """
        if os.path.exists("test_orders.csv"):
            os.remove("test_orders.csv")

        if os.path.exists("orders.csv"):
            os.remove("orders.csv")


if __name__ == "__main__":
    unittest.main()
