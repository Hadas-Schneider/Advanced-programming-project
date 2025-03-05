from io import StringIO
import unittest
from unittest.mock import mock_open, patch, call, MagicMock
from shopping_cart import ShoppingCart
from furniture import Furniture, Chair, Table, VIPDiscount
from User import User
from inventory import Inventory
import os


def mock_inventory():
    inventory = Inventory()
    inventory.add_item(Furniture("FG4rKJp", "Chair", "Office Chair", "Plastic", "Black", 3, 100.8, (250, 112, 88),
                                 "Germany", 2))
    return inventory


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
        fake_item = Chair(u_id="999", name="Fake Chair", description="Does not exist",
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
        with patch('shopping_cart.ShoppingCart.process_payment', return_value=True) as mocked_payment:
            order = self.cart.checkout()
            self.assertIsNotNone(order, "Checkout should return an order.")
            self.assertTrue(mocked_payment.called, "Payment process should be called.")

    def test_calculate_total(self):
        """Test calculating the total cost of items in the cart."""
        self.cart.add_item(self.chair, 2)
        self.cart.add_item(self.table, 1)
        mock_chair_price = self.chair.apply_discount(self.chair.discount_strategy)
        mock_table_price = self.table.apply_discount(self.table.discount_strategy)

        expected_subtotal = (mock_chair_price * 2) + (mock_table_price * 1)
        expected_total_after_discount = Furniture.price_with_discount(
            expected_subtotal, self.cart.discount_strategy.get_discount()
        )

        expected_final_total = expected_total_after_discount * (1 + (18 / 100))
        calculated_total = self.cart.calculate_total(tax_percentage=18)

        self.assertAlmostEqual(calculated_total, round(expected_final_total, 2), places=2,
                               msg="Calculated total does not match expected total.")

    def test_checkout_insufficient_stock(self):
        """
        Test checkout failure due to insufficient stock.
        """
        with self.assertRaises(ValueError):
            self.cart.add_item(self.chair, quantity=15)

    def test_save_cart_to_csv(self):
        """Test that the shopping cart is saved in the CSV."""
        mock_data = "user_email,item_name,quantity,price\r\njohn@example.com,Office Chair,1,100\r\n"
        m = mock_open(read_data=mock_data)

        with patch('builtins.open', m):
            self.cart.add_item(self.chair, 1)
            self.cart.save_cart_to_csv("test_carts.csv")
            m.assert_called_once_with("test_carts.csv", mode='w', newline='')

            handle = m()
            print("Actual write calls:", handle.write.call_args_list)
            expected_calls = [
                call('user_email,item_name,quantity,price\n'),
                call('john@example.com,Office Chair,1,100.0\n')
            ]
            written_data = [call.args[0].replace("\r\n", "\n") for call in handle.write.call_args_list]
            expected_data = [c.args[0] for c in expected_calls]
            assert expected_data == written_data, f"Expected: {expected_data}, Got: {written_data}"

    def test_load_cart_from_csv(self):
        """ Testing the reloading of the data in the CSV file."""
        mock_data = "user_email,item_name,quantity,price\njohn@example.com,Office Chair,1,100\n"
        # Creating the mock to open the CSV file
        file_like_object = StringIO(mock_data)
        with patch('builtins.open', return_value=file_like_object), patch('os.path.exists', return_value=True):
            self.cart.load_cart_from_csv("test_carts.csv")

    def test_update_existing_cart_in_csv(self):
        """Testing the existent user's cart updates in the file """
        initial_data = "user_email,item_name,quantity,price\njohn@example.com,Office Chair,2,200\n"
        m = mock_open(read_data=initial_data)

        with patch('builtins.open', m) as mocked_file, patch('csv.writer', autospec=True) as mock_writer:
            handle = mock_writer.return_value
            handle.writerow.side_effect = lambda x: None

            # First save to simulate the initial write
            self.cart.add_item(self.chair, quantity=2)
            self.cart.save_cart_to_csv("test_carts.csv")

            expected_data_first_save = [
                ['john@example.com', 'Office Chair', 2, 100.0]
            ]
            # Check the data sent to writerows before asserting
            print("Data sent to writerows after first save:", handle.writerows.call_args_list)
            handle.writerows.assert_has_calls([call(expected_data_first_save)], any_order=False)

            # Update the cart and save again to simulate the update
            self.cart.add_item(self.chair, quantity=3)
            self.cart.save_cart_to_csv("test_carts.csv")
            updated_data = [
                ['john@example.com', 'Office Chair', 5, 100.0]
            ]
            print("Updated save data:", updated_data)
            handle.writerows.assert_has_calls([call(updated_data)], any_order=False)

            expected_calls = [
                call("test_carts.csv", mode='w', newline=''),  # Check the file was opened correctly
                call("test_carts.csv", mode='w', newline='')   # Check the file was opened again for the second write
            ]
            mocked_file.assert_has_calls(expected_calls, any_order=True)

    def tearDown(self):
        """
        Cleanup after each test.
        """
        self.cart.cart_items.clear()
        self.inventory.items_by_type.clear()

        if os.path.exists("test_carts.csv"):
            os.remove("test_carts.csv")

    if __name__ == "__main__":
        unittest.main()
