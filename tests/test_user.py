import unittest
import csv
import io
from io import StringIO
from unittest.mock import patch, MagicMock
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
        self.assertTrue(self.user.validate_password("Strong@123"))  # Password is legal
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

    @patch('builtins.open')
    def test_save_to_csv_new_file(self, mock_open_func):
        """Test saving user to a new CSV file that doesn't exist yet"""
        # Mock the file not existing
        mock_open_func.side_effect = [
            FileNotFoundError,  # First open() call raises FileNotFoundError
            MagicMock()  # Second open() call for writing returns a file-like object
        ]

        # Set up the mock for CSV writer
        mock_writer = MagicMock()
        csv.writer = MagicMock(return_value=mock_writer)

        # Call the method
        self.user.save_to_csv(self.test_filename)

        # Verify the correct data was written
        expected_rows = [
            ["name", "email", "password", "salt", "hashed_password", "address", "payment_method", "order_history",
                 "wishlist"],
            ["Avi Cohen", "avicohen@example.com", "Strong@123", self.user.salt, self.user.hashed_password,
             "123 Main St", "PayPal", None, None]
        ]
        mock_writer.writerows.assert_called_once_with(expected_rows)

    @patch('builtins.open')
    def test_save_to_csv_update_existing_user(self, mock_open_func):
        """Test updating an existing user in the CSV file"""
        # Create a mock file with existing data
        existing_data = (
            "name,email,password,salt,hashed_password,address,payment_method,order_history,wishlist\n"
            "Avi Cohen,avicohen@example.com,old_password,old_salt,old_hash,old_address,old_payment,OldOrder,OldItem\n"
        )
        mock_file = StringIO(existing_data)

        # First open is for reading, returns our StringIO with data
        # Second open is for writing, returns a MagicMock
        mock_open_context = [
            mock_file,
            MagicMock()
        ]

        # Configure mock_open to return different file handles
        mock_open_func.side_effect = lambda filename, mode, newline="": mock_open_context.pop(0)

        # Set up the mock for CSV writer
        mock_writer = MagicMock()
        csv.writer = MagicMock(return_value=mock_writer)

        # Call the method
        self.user.save_to_csv(self.test_filename)

        # Verify the correct data was written
        expected_rows = [
            ["name", "email", "password", "salt", "hashed_password", "address", "payment_method", "order_history",
             "wishlist"],
            ["Avi Cohen", "avicohen@example.com", "Strong@123", self.user.salt, self.user.hashed_password,
             "123 Main St", "PayPal", None, None]
        ]
        mock_writer.writerows.assert_called_once_with(expected_rows)

    @patch('builtins.open')
    def test_save_to_csv_add_new_user(self, mock_open_func):
        """Test adding a new user to an existing CSV file with other users"""
        # Create a mock file with existing data (different user)
        existing_data = (
            "name,email,password,salt,hashed_password,address,payment_method,order_history,wishlist\n"
            "Jane Smith,jane@example.com,pwd,salt,hash,address,payment,Order,Item\n"
        )
        mock_file = StringIO(existing_data)

        # Configure mock_open
        mock_open_context = [
            mock_file,
            MagicMock()
        ]
        mock_open_func.side_effect = lambda filename, mode, newline="": mock_open_context.pop(0)

        # Set up the mock for CSV writer
        mock_writer = MagicMock()
        csv.writer = MagicMock(return_value=mock_writer)

        # Call the method
        self.user.save_to_csv(self.test_filename)

        # Verify the correct data was written
        expected_rows = [
            ["name", "email", "password", "salt", "hashed_password", "address", "payment_method", "order_history",
             "wishlist"],
            ["Jane Smith", "jane@example.com", "pwd", "salt", "hash", "address", "payment", "Order", "Item"],
            ["Avi Cohen", "avicohen@example.com", "Strong@123", self.user.salt, self.user.hashed_password,
             "123 Main St", "PayPal", None, None]
        ]
        mock_writer.writerows.assert_called_once_with(expected_rows)

    @patch('builtins.open')
    def test_file_permission_error(self, mock_open_func):
        """Test handling of permission errors during file operations"""
        mock_open_func.side_effect = PermissionError("Permission denied")

        with self.assertRaises(PermissionError):
            self.user.save_to_csv(self.test_filename)

    @patch('csv.reader')
    @patch('csv.writer')
    @patch('builtins.open')
    def test_csv_processing_error(self, mock_open_func, mock_writer, mock_reader):
        """Test handling of CSV processing errors"""
        # Create a mock file object that will be returned when open() is called
        mock_file = MagicMock()
        # Configure the mock_open_func to return the mock_file when used in a with statement
        mock_open_func.return_value.__enter__.return_value = mock_file

        # Configure the csv.reader mock to raise a csv.Error when called
        # This simulates a CSV processing failure
        mock_reader.side_effect = csv.Error("CSV processing error")

        # Assert that a csv.Error exception is raised when the save_to_csv method is called
        # This verifies that the exception from csv.reader is properly propagated
        with self.assertRaises(csv.Error):
            self.user.save_to_csv(self.test_filename)

    @patch('builtins.open')
    def test_load_from_csv_user_found(self, mock_open_func):
        """Test loading a user that exists in the CSV file"""
        # Create mock CSV data with the user we want to find
        mock_csv_data = (
            "Avi Cohen,avicohen@example.com,Strong@123,salt123,hashed_pwd_123,123 Main St,PayPal,Order1|Order2,Item1|Item2\n"
        )
        mock_file = StringIO(mock_csv_data)
        mock_open_func.return_value.__enter__.return_value = mock_file

        # Call the method
        user = User.load_from_csv(self.test_filename, self.user.name, self.user.email, self.user.address)

        # Verify the returned user has the correct attributes
        self.assertIsNotNone(user)
        self.assertEqual(user.name, self.user.name)
        self.assertEqual(user.email, self.user.email)
        self.assertEqual(user.password, "Strong@123")
        self.assertEqual(user.salt, "salt123")
        self.assertEqual(user.hashed_password, "hashed_pwd_123")
        self.assertEqual(user.address, self.user.address)
        self.assertEqual(user.payment_method, "PayPal")
        self.assertEqual(user.order_history, ["Order1", "Order2"])
        self.assertEqual(user.wishlist, ["Item1", "Item2"])

    @patch('builtins.open')
    def test_load_from_csv_user_not_found(self, mock_open_func):
        """Test loading a user that doesn't exist in the CSV file"""
        # Create mock CSV data without the user we're looking for
        mock_csv_data = (
            "Jane Smith,jane@example.com,pwd123,salt456,hashed_pwd_456,456 Oak St,CreditCard,Order3,Item3\n"
        )
        mock_file = StringIO(mock_csv_data)
        mock_open_func.return_value.__enter__.return_value = mock_file

        # Call the method
        user = User.load_from_csv(self.test_filename, self.user.name, self.user.email, self.user.address)

        # Verify no user was returned
        self.assertIsNone(user)

    @patch('builtins.open')
    def test_load_from_csv_empty_file(self, mock_open_func):
        """Test loading from an empty CSV file"""
        # Create an empty mock CSV file
        mock_file = StringIO("")
        mock_open_func.return_value.__enter__.return_value = mock_file

        # Call the method
        user = User.load_from_csv(self.test_filename, self.user.name, self.user.email, self.user.address)

        # Verify no user was returned
        self.assertIsNone(user)

    @patch('builtins.open')
    def test_load_from_csv_missing_fields(self, mock_open_func):
        """Test loading a user with missing fields (fewer than expected columns)"""
        # Create mock CSV data with missing fields
        mock_csv_data = (
            "Avi Cohen,avicohen@example.com,Strong@123\n"  # Missing several fields
        )
        mock_file = StringIO(mock_csv_data)
        mock_open_func.return_value.__enter__.return_value = mock_file

        # Mock print to capture the error message
        with patch('builtins.print') as mock_print:
            # Call the method
            user = User.load_from_csv(self.test_filename, self.user.name, self.user.email, self.user.address)

            # Verify the error was printed and no user was returned
            mock_print.assert_called_with("User not found.")
            self.assertIsNone(user)

    @patch('builtins.open')
    def test_load_from_csv_empty_collections(self, mock_open_func):
        """Test loading a user with empty order history and wishlist"""
        # Create mock CSV data with empty collections
        mock_csv_data = (
            "Avi Cohen,avicohen@example.com,Strong@123,salt123,hashed_pwd_123,123 Main St,PayPal,,\n"
        )
        mock_file = StringIO(mock_csv_data)
        mock_open_func.return_value.__enter__.return_value = mock_file

        # Call the method
        user = User.load_from_csv(self.test_filename, self.user.name, self.user.email, self.user.address)

        # Verify the user has empty lists for the collections
        self.assertIsNotNone(user)
        self.assertEqual(user.order_history, [])
        self.assertEqual(user.wishlist, [])

    @patch('builtins.open')
    def test_load_from_csv_file_not_found(self, mock_open_func):
        """Test handling of file not found error"""
        # Mock a file not found error
        mock_open_func.side_effect = FileNotFoundError("File not found")

        # Call the method
        user = User.load_from_csv(self.test_filename, self.user.name, self.user.email, self.user.address)

        # Verify no user was returned
        self.assertIsNone(user)

    @patch('builtins.open')
    @patch('builtins.print')
    def test_load_from_csv_csv_error(self, mock_print, mock_open_func):
        """Test handling of CSV parsing error"""
        # Create a mock file that will cause a ValueError when unpacked
        # This simulates a CSV row with incorrect number of fields
        mock_csv_data = (
            "Avi Cohen,avicohen@example.com\n"  # Not enough fields to unpack
        )
        mock_file = StringIO(mock_csv_data)
        mock_open_func.return_value.__enter__.return_value = mock_file

        # Call the method
        user = User.load_from_csv(self.test_filename, self.user.name, self.user.email, self.user.address)

        # Verify error was printed and no user was returned
        mock_print.assert_called_with("User not found.")
        self.assertIsNone(user)

    @patch('builtins.open')
    def test_load_from_csv_permission_error(self, mock_open_func):
        """Test handling of permission error"""
        # Mock a permission error
        mock_open_func.side_effect = PermissionError("Permission denied")

        # Call the method
        user = User.load_from_csv(self.test_filename, self.user.name, self.user.email, self.user.address)

        # Verify no user was returned
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()
