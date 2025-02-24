import unittest
from shopping_cart import ShoppingCart
from furniture import Chair, Table, VIPDiscount
from User import User
from inventory import Inventory
import os


class TestRegressionCheckout(unittest.TestCase):
    """
    Regression tests for the shopping cart system
    """
    def setUp(self):
        """ Set up test environment with a user, inventory and shopping cart. """
        self.user = User("Jane Doe", "jane@example.com", "Secure@123", "456 Another St", "PayPal")
        self.inventory = Inventory()
        self.cart = ShoppingCart(self.user, self.inventory)

        # Add items to inventory
        self.chair = Chair(u_id="001", name="Office Chair", description="Ergonomic chair",
                           material="Metal", color="Black", wp=2, price=100.0, dimensions=(60, 60, 120),
                           country="USA", available_quantity=5, has_armrests=True)

        self.table = Table(u_id="002", name="Dining Table", description="Wooden dining table",
                           material="Wood", color="Brown", wp=3, price=250.0, dimensions=(180, 90, 75),
                           country="Canada", available_quantity=3, shape="Rectangular", is_extendable=True)

        self.cart.add_item(self.chair, quantity=1)
        self.cart.add_item(self.table, quantity=2)

    def test_checkout_process(self):
        """
        Regression test to verify checkout updates all components correctly.
        """
        self.assertGreater(len(self.cart.cart_items), 0, "Cart should not be empty before checkout")
        initial_chair_stock = self.inventory.items_by_type["Chair"]["Office Chair"].available_quantity
        initial_table_stock = self.inventory.items_by_type["Table"]["Dining Table"].available_quantity

        order = self.cart.checkout()
        self.assertIsNotNone(order, "Order should not be None after successful checkout.")
        expected_total = self.cart.calculate_total()
        self.assertEqual(order.total_price, expected_total, "Order total price should match calculated total")

        self.assertEqual(self.inventory.items_by_type["Chair"]["Office Chair"].available_quantity,
                         initial_chair_stock - 1, "Inventory for chairs should be reduced after checkout")

        self.assertEqual(self.inventory.items_by_type["Table"]["Dining Table"].available_quantity,
                         initial_table_stock - 1,
                         "Inventory for tables should be reduced after checkout")
        self.assertEqual(len(self.cart.cart_items), 0, "Cart should be empty after checkout")
        print("✅ Regression test for checkout passed!")

    def tearDown(self):
        """ Cleanup CSV after test to prevent affecting future tests. """
        self.assertTrue(os.path.exists("orders.csv"), "Order file should be created after checkout. ")
        if os.path.exists("orders.csv"):
            os.remove("orders.csv")


if __name__ == "__main__":
    unittest.main()
