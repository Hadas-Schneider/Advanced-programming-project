import csv
import sys
import io
import unittest
import uuid
from unittest.mock import MagicMock, patch, mock_open
from order import Order


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.mock_user = MagicMock()
        self.mock_user.address = "123 Tel Aviv"
        self.mock_user.payment_method = "Credit card"
        self.mock_user.email = "test@example.com"

        class Furniture:
            def __init__(self, name, price):
                self.name = name
                self.price = price

        chair = Furniture("Chair", 20)
        table = Furniture("Table", 80)
        bed = Furniture("Bed", 100)

        self.items = [("Chair", 2, 20.00), ("Table", 1, 80.00), ("Bed", 1, 100.00)]
        self.total_price = 200

        # Set up Order
        self.order = Order(self.mock_user, self.items, self.total_price)
        self.order.order_id = "f47ac10b-58cc-4372-a567-0e02b2c3d479"

    def test_initialization(self):
        self.assertIsInstance(self.order.order_id, str)
        self.assertTrue(uuid.UUID(self.order.order_id))
        self.assertEqual(self.order.user, self.mock_user)
        self.assertEqual(self.order.items, self.items)
        self.assertEqual(self.order.total_price, self.total_price)
        self.assertEqual(self.order.status, "Pending")
        self.assertEqual(self.order.shipping_address, self.mock_user.address)
        self.assertEqual(self.order.payment_method, self.mock_user.payment_method)

    def test_complete_order(self):
        self.assertEqual(self.order.status, "Pending")
        self.order.complete_order()
        self.assertEqual(self.order.status, "Completed")

    def test_mark_as_delivered(self):
        self.order.status = "Completed"
        self.order.mark_as_delivered()
        self.assertEqual(self.order.status, "Delivered")

    def test_mark_as_not_delivered(self):
        self.order.status = "Pending"
        captured_output = io.StringIO()
        sys.stdout = captured_output
        self.order.mark_as_delivered()
        sys.stdout = sys.__stdout__
        self.assertEqual(self.order.status, "Pending")
        self.assertEqual(captured_output.getvalue().strip(),
                         "Order must be completed before marking as delivered.")

    def test_str(self):
        expected = (
            "Order f47ac10b-58cc-4372-a567-0e02b2c3d479: Chair x 2, Table x 1, Bed x 1 | "
            "Total: $200.00 | Status: Pending | "
            "Shipping to: 123 Tel Aviv | Payment method: Credit card"
        )
        self.assertEqual(str(self.order), expected)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_order_to_csv_new_file(self, mock_file, mock_exists):
        """
        Test `save_order_to_csv` when the file does not exist.
        """
        mock_exists.return_value = False  # Simulating a new file

        csv_output = io.StringIO()
        mock_file.return_value.__enter__.return_value = csv_output

        self.order.save_order_to_csv("test_orders.csv")

        # Verify that the file was opened in "append" mode
        mock_file.assert_called_once_with("test_orders.csv", mode="a", newline="")
        mock_exists.assert_called_once_with("test_orders.csv")

        csv_output.seek(0)
        csv_reader = csv.reader(csv_output)
        rows = list(csv_reader)

        # Validate header row
        self.assertEqual(rows[0], ["order_id", "user_email", "shipping_address", "payment_method",
                                   "items", "total_price", "status"])

        # Validate order details row
        items_str = "|".join(["Chair x 2 ($20.00)", "Table x 1 ($80.00)", "Bed x 1 ($100.00)"])
        expected_row = ["f47ac10b-58cc-4372-a567-0e02b2c3d479", "test@example.com", "123 Tel Aviv", "Credit card",
                        items_str, "$200.00", "Pending"]

        self.assertEqual(rows[1], expected_row)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_order_to_csv_existing_file(self, mock_file, mock_exists):
        """
        Test `save_order_to_csv` when the file already exists.
        """
        mock_exists.return_value = True  # Simulating an existing file

        csv_output = io.StringIO()
        mock_file.return_value.__enter__.return_value = csv_output

        self.order.save_order_to_csv("test_orders.csv")

        # Verify that the file was opened in "append" mode
        mock_file.assert_called_once_with("test_orders.csv", mode="a", newline="")

        csv_output.seek(0)
        csv_reader = csv.reader(csv_output)
        rows = list(csv_reader)

        # Ensure that the header is not duplicated
        if len(rows) > 1:
            self.assertEqual(rows[1][0], "order_id")

    @patch('builtins.open', new_callable=mock_open)
    def test_load_orders_from_csv(self, mock_file):
        # Create CSV data with proper formatting (no leading spaces)
        csv_data = """order_id,user_email,shipping_address,payment_method,items,total_price,status
    f47ac10b-58cc-4372-a567-0e02b2c3d479,test@example.com,123 Tel Aviv,Credit card,
    Chair x 2 ($20.00)|Table x 1 ($80.00)|Bed x 1 ($100.00),$200.00,Pending"""

        mock_file.return_value.__iter__.return_value = csv_data.splitlines()

        class MockReader:
            def __init__(self, data):
                self.data = data
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index >= len(self.data):
                    raise StopIteration
                row = self.data[self.index]
                self.index += 1
                return row

        reader_data = [
            ["order_id", "user_email", "shipping_address", "payment_method", "items", "total_price", "status"],
            ["f47ac10b-58cc-4372-a567-0e02b2c3d479", "test@example.com", "123 Tel Aviv", "Credit card",
             "Chair x 2 ($20.00)|Table x 1 ($80.00)|Bed x 1 ($100.00)", "$200.00", "Pending"]
        ]

        mock_reader = MockReader(reader_data)

        with patch('csv.reader', return_value=mock_reader):
            with patch('builtins.print') as mock_print:
                orders = Order.load_orders_from_csv("test_orders.csv")

                self.assertEqual(len(orders), 1)
                self.assertEqual(orders[0]["order_id"], "f47ac10b-58cc-4372-a567-0e02b2c3d479")
                self.assertEqual(orders[0]["user_email"], "test@example.com")
                self.assertEqual(orders[0]["status"], "Pending")
                self.assertEqual(orders[0]["items"], ["Chair x 2 ($20.00)", "Table x 1 ($80.00)", "Bed x 1 ($100.00)"])

                mock_print.assert_called_with("Orders loaded successfully from CSV.")

    @patch('builtins.open', new_callable=mock_open)
    def test_load_orders_from_csv_file_not_found(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        orders = Order.load_orders_from_csv("non_existing_file.csv")
        self.assertEqual(orders, [])

    @patch('builtins.open', new_callable=mock_open)
    def test_load_orders_from_csv_malformed_data(self, mock_file):
        csv_data = """order_id,user_email,shipping_address,payment_method,items,total_price
                     f47ac10b-58cc-4372-a567-0e02b2c3d479,test@example.com,123 Tel Aviv,Credit card,
                     Chair x 2 ($20.00)|Table x 1 ($80.00)|Bed x 1 ($100.00),$200.00"""

        mock_file.return_value.__iter__.return_value = csv_data.splitlines()

        # Create a properly formatted mock reader that behaves like an iterator
        class MockReader:
            def __init__(self, data):
                self.data = data
                self.index = 0

            def __iter__(self):
                return self

            def __next__(self):
                if self.index >= len(self.data):
                    raise StopIteration
                row = self.data[self.index]
                self.index += 1
                return row

        reader_data = [
            ["order_id", "user_email", "shipping_address", "payment_method", "items", "total_price"],
            ["f47ac10b-58cc-4372-a567-0e02b2c3d479", "test@example.com", "123 Tel Aviv", "Credit card",
             "Chair x 2 ($20.00)|Table x 1 ($80.00)|Bed x 1 ($100.00)", "$200.00"]
        ]

        mock_reader = MockReader(reader_data)

        with patch('csv.reader', return_value=mock_reader):
            with patch('builtins.print') as mock_print:
                orders = Order.load_orders_from_csv("test_orders.csv")
                self.assertEqual(len(orders), 0)
                mock_print.assert_called_with("Orders loaded successfully from CSV.")


if __name__ == '__main__':
    unittest.main()