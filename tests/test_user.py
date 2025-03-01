import unittest
import csv
import io
from unittest.mock import patch
from User import User, ProfileUpdateNotifier
from order import Order  # Assuming Order is a valid class with necessary attributes


class TestUser(unittest.TestCase):

    def setUp(self):
        """Create a test user"""
        self.user = User(name="Avi Cohen", email="avicohen@example.com",
                         password="Strong@123",
                         address="123 Main St",
                         payment_method="PayPal")
        self.test_filename = "users_database.csv"

    def test_user_creation(self):
        """Test user initialization with valid inputs"""
        self.assertEqual(self.user.name, "Avi Cohen")
        self.assertEqual(self.user.email, "avicohen@example.com")
        self.assertEqual(self.user.address, "123 Main St")
        self.assertEqual(self.user.payment_method, "PayPal")
        self.assertIsInstance(self.user.order_history, list)
        self.assertIsInstance(self.user.wishlist, list)

    def test_password_validation(self):
        """Test password validation rules"""
        self.assertTrue(self.user.validate_password("Strong@123")) # Password is legal
        self.assertFalse(User.validate_password("Strong"))  # Password is too short
        self.assertFalse(User.validate_password("Strong123"))  # Password doesn't contain special character

    def test_password_hashing_and_verification(self):
        """Ensure password hashing and verification works correctly"""
        self.assertTrue(self.user.check_password("Strong@123"))  # Correct password
        self.assertFalse(self.user.check_password("Strong@1234"))  # Incorrect password

    def test_profile_update(self):
        """Ensure profile updates work properly"""
        self.user.update_profile(name="Avi Cohen 2", address="456 Elm St")
        self.assertEqual(self.user.name, "Avi Cohen 2")
        self.assertEqual(self.user.address, "456 Elm St")

    def test_order_history(self):
        """Ensure orders are added and retrieved correctly"""
        order = Order(user=self.user, items={"Table": 1, "Chair": 1}, total_price=200)
        self.user.add_order_to_history(order)
        self.assertEqual(len(self.user.order_history), 1)
        self.assertIn(order, self.user.order_history)

    def test_view_wishlist(self):
        """Test wishlist functionalities"""

        class MockItem:
            def __init__(self, name):
                self.name = name

        # Ensure wishlist starts empty
        self.assertEqual(self.user.view_wishlist(), ["Wishlist is empty."])

        item1 = MockItem("Buddy Table")
        item2 = MockItem("Zippy Chair")

        # Add items to wishlist
        self.user.add_to_wishlist(item1)
        self.user.add_to_wishlist(item2)

        # Check that view_wishlist() returns the correct list
        self.assertEqual(self.user.view_wishlist(), [item1, item2])

        # Remove items from wishlist
        self.user.remove_from_wishlist(item1)
        self.assertNotIn(item1, self.user.wishlist)
        self.user.remove_from_wishlist(item2)

        # Check that wishlist is empty again
        self.assertEqual(self.user.view_wishlist(), ["Wishlist is empty."])

    def test_update_payment_method(self):
        """Ensure payment method updates correctly"""
        self.user.update_payment_method("Credit Card")
        self.assertEqual(self.user.payment_method, "Credit Card")

    def test_observer_notifications(self):
        """Ensure observers are notified when user profile changes"""
        observer = ProfileUpdateNotifier()
        self.user.add_observer(observer)

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            self.user.update_profile(name="Observer Test")
            output = mock_stdout.getvalue().strip()

        self.assertIn("User Observer Test updated their profile.", output)

    def test_save_new_to_csv(self):
        """Test that the user is correctly saved to the CSV file."""
        # Ensure the user instance is saved to the file
        self.user.save_to_csv(self.test_filename)

        # Read the last row of the file
        with open(self.test_filename, mode="r") as file:
            reader = csv.reader(file)
            rows = list(reader)

        expected_data = [
            self.user.name,
            self.user.email,
            self.user.password,
            self.user.salt,
            self.user.hashed_password,
            self.user.address,
            self.user.payment_method,
            "",
            ""
        ]

        self.assertEqual(rows[-1], expected_data)  # Check last row matches user data

    def test_load_from_csv(self):
        """Test that the user is correctly loaded from the CSV file."""
        loaded_user = User.load_from_csv(self.test_filename, "Avi Cohen", "avicohen@example.com",
                                         "123 Main St")

        self.assertEqual(loaded_user.name, self.user.name)
        self.assertEqual(loaded_user.email, self.user.email)
        self.assertEqual(loaded_user.address, self.user.address)
        self.assertEqual(loaded_user.payment_method, self.user.payment_method)
        self.assertEqual(loaded_user.order_history, self.user.order_history)  # Assuming empty at start
        self.assertEqual(loaded_user.wishlist, self.user.wishlist)  # Assuming empty at start

    def test_save_exists_to_csv(self):
        """Test that existing user is correctly saved to the CSV file after changes."""
        # Ensure the user instance is saved to the file
        existing_user = User.load_from_csv(self.test_filename, "Avi Cohen", "avicohen@example.com",
                                         "123 Main St")
        existing_user.update_profile(address="456 Elm St")
        order = Order(user=existing_user, items={"Table": 1, "Chair": 1}, total_price=200)
        existing_user.add_order_to_history(order)
        existing_user.save_to_csv(self.test_filename)

        # Read the relevant row in the file
        with open(self.test_filename, mode="r") as file:
            reader = csv.reader(file)
            rows = list(reader)

        expected_data = [
            existing_user.name,
            existing_user.email,
            existing_user.password,
            existing_user.salt,
            existing_user.hashed_password,
            existing_user.address,
            existing_user.payment_method,
            "Table x 1, Chair x 1",
            ""
        ]

        # Find the row that contains the user's email
        user_row = None
        for row in rows:
            if row[1] == existing_user.email:  # Assuming email is at index 1
                user_row = row
                break  # Stop once we find the correct row

        # Ensure we found a matching row
        self.assertIsNotNone(user_row, "User record not found in CSV file.")

        # Compare the expected data with the found row
        self.assertEqual(user_row, expected_data)

if __name__ == '__main__':
    unittest.main()
