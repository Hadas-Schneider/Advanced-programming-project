import unittest
from shopping_cart import ShoppingCart
from furniture import Chair, Table, VIPDiscount, NoDiscount
from User import User
from inventory import Inventory


class TestShoppingCart(unittest.TestCase):

    def setUp(self):
        """
        Set up a user, inventory and shopping cart for testing.
        """
        self.user = User("John Doe", "john@example.com", "Secure@123", "123 Main St", "Credit Card")
        self.inventory = Inventory()
        self.cart = ShoppingCart(self.user, self.inventory)

        # Add furniture items to inventory
        self.chair = Chair(u_id="001", name="Office Chair", description="Ergonomic office chair",
                           material="Metal", color="Black", wp=2, price=100.0, dimensions=(60, 60, 120),
                           country="USA", available_quantity=10, has_armrests=True)

        self.table = Table(u_id="002", name="Dining Table", description="Wooden dining table",
                           material="Wood", color="Brown", wp=3, price=250.0, dimensions=(180, 90, 75),
                           country="Canada", available_quantity=5, shape="Rectangular", is_extendable=True)

        self.inventory.add_item(self.chair)
        self.inventory.add_item(self.table)

    def test_add_invalid_quantity(self):
        """ Test adding invalid quantity types. """
        with self.assertRaises(ValueError):
            self.cart.add_item(self.chair, quantity=-2)  # Negative quantity
        with self.assertRaises(ValueError):
            self.cart.add_item(self.chair, quantity="five")  # String instead of int

    def test_add_nonexistent_item(self):
        """ Test adding a non-existent item. """
        fake_item = Chair(u_id="999", name="Fake Chair",description="Does not exist",
                          material="Plastic", color="Red", wp=1, price=50.0, dimensions=(50, 50, 100),
                          country="Unknown", available_quantity=0, has_armrests=False)
        with self.assertRaises(KeyError):
            self.cart.add_item(fake_item, quantity=1)

    def test_exceed_inventory_limit(self):
        """ Test adding more than available stock."""
        with self.assertRaises(ValueError):
            self.cart.add_item(self.chair, quantity=999)

    def test_remove_nonexistent_item(self):
        """ Test removing an item that does not exist in the cart """
        with self.assertRaises(KeyError):
            self.cart.remove_item(self.chair, quantity=1)

    def test_add_and_remove_large_quantity(self):
        """ Test adding and removing a large quantity of items """
        self.cart.add_item(self.table, quantity=5)
        self.assertEqual(self.cart.cart_items[self.table], 5)

        self.cart.remove_item(self.table, quantity=3)
        self.assertEqual(self.cart.cart_items[self.table], 2)

        self.cart.remove_item(self.table, quantity=2)
        self.assertNotIn(self.table, self.cart.cart_items)  # Ensure it's removed completely

    def test_add_zero_quantity(self):
        """ Test adding zero quantity should not change the cart """
        with self.assertRaises(ValueError):
            self.cart.add_item(self.chair, quantity=0)

    def test_add_duplicate_items(self):
        """ Test adding the same item twice should increase quantity """
        self.cart.add_item(self.chair, quantity=1)
        self.cart.add_item(self.chair, quantity=2)
        self.assertEqual(self.cart.cart_items[self.chair], 3)

    def test_add_item(self):
        """
        Test adding an item to the cart.
        """
        self.cart.add_item(self.chair, quantity=2)
        self.assertIn(self.chair, self.cart.cart_items)
        self.assertEqual(self.cart.cart_items[self.chair], 2)

    def test_remove_item(self):
        """
        Test removing an item from the cart.
        """
        self.cart.add_item(self.chair, quantity=3)
        self.cart.remove_item(self.chair, quantity=1)
        self.assertEqual(self.cart.cart_items[self.chair], 2)

        self.cart.remove_item(self.chair, quantity=2)
        self.assertNotIn(self.chair, self.cart.cart_items)

    def test_calculate_total_no_discount(self):
        """
        Test calculating total price without discounts.
        """
        self.cart.add_item(self.chair, quantity=1)
        self.cart.add_item(self.table, quantity=2)

        chair_price_after_discount = self.chair.apply_discount(self.chair.discount_strategy)
        table_price_after_discount = self.table.apply_discount(self.table.discount_strategy)

        subtotal = (chair_price_after_discount * 1) + (table_price_after_discount * 2)
        expected_total = subtotal * 1.18
        self.assertEqual(self.cart.calculate_total(tax_percentage=18), expected_total)

    def test_calculate_total_with_discount(self):
        """
        Test calculating total price with a cart-wide discount.
        """
        self.cart.add_item(self.chair, quantity=1)
        self.cart.add_item(self.table, quantity=2)

        self.cart.discount_strategy = VIPDiscount()

        chair_price_after_discount = self.chair.apply_discount(self.chair.discount_strategy)
        table_price_after_discount = self.table.apply_discount(self.table.discount_strategy)

        subtotal = (chair_price_after_discount * 1) + (table_price_after_discount * 2)
        total_after_cart_discount = subtotal * (1 - VIPDiscount().get_discount() / 100)
        expected_total = total_after_cart_discount * 1.18
        self.assertEqual(self.cart.calculate_total(tax_percentage=18), expected_total)

    def test_checkout_success(self):
        """
        Test successful checkout.
        """
        self.cart.add_item(self.chair, quantity=2)
        self.cart.add_item(self.table, quantity=1)

        expected_total = self.cart.calculate_total()
        order = self.cart.checkout()

        print(f" Cart content before checkout: {self.cart.cart_items}")
        print(f"Re-calculate the price: {self.cart.calculate_total()}")

        self.assertIsNotNone(order)
        self.assertEqual(order.total_price, expected_total)

    def test_checkout_insufficient_stock(self):
        """
        Test checkout failure due to insufficient stock.
        """
        with self.assertRaises(ValueError):
            self.cart.add_item(self.chair, quantity=15)

    def tearDown(self):
        """
        Cleanup after each test.
        """
        self.cart.cart_items.clear()
        self.inventory.items_by_type.clear()

    if __name__ == "__main__":
        unittest.main()
