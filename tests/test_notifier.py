import unittest
from io import StringIO

from unittest.mock import patch, MagicMock
from inventory import InventoryObserver
from inventory import LowStockNotifier

class TestLowStockNotifier(unittest.TestCase):
    def test_abstract_class_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            InventoryObserver()

    def setUp(self):
        self.default_notifier = LowStockNotifier()
        self.custom_notifier = LowStockNotifier(threshold=10)
        self.mock_item = MagicMock()
        self.mock_item.name = "Test Item"

    def test_initialization(self):
        self.assertEqual(self.default_notifier.threshold, 5)
        self.assertEqual(self.custom_notifier.threshold, 10)

    @patch('sys.stdout', new_callable=StringIO)
    def test_update_low_stock_added(self, mock_stdout):
        self.mock_item.available_quantity = 3
        self.default_notifier.update(self.mock_item, "added")
        self.assertIn(f"Warning: Low stock for Test Item! Only 3 left.", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_update_low_stock_updated(self, mock_stdout):
        self.mock_item.available_quantity = 2
        self.default_notifier.update(self.mock_item, "updated")
        self.assertIn(f"Warning: Low stock for Test Item! Only 2 left.", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_update_sufficient_stock(self, mock_stdout):
        self.mock_item.available_quantity = 10
        self.default_notifier.update(self.mock_item, "added")
        self.assertEqual(mock_stdout.getvalue(), "")

    @patch('sys.stdout', new_callable=StringIO)
    def test_update_different_change_type(self, mock_stdout):
        self.mock_item.available_quantity = 2
        self.default_notifier.update(self.mock_item, "removed")
        self.assertEqual(mock_stdout.getvalue(), "")

    @patch('sys.stdout', new_callable=StringIO)
    def test_custom_threshold(self, mock_stdout):
        self.mock_item.available_quantity = 8
        # This should trigger a warning with the custom threshold (10)
        self.custom_notifier.update(self.mock_item, "updated")
        self.assertIn(f"Warning: Low stock for Test Item! Only 8 left.", mock_stdout.getvalue())

        # Clear the mock
        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        # But it should not trigger a warning with the default threshold (5)
        self.default_notifier.update(self.mock_item, "updated")
        self.assertEqual(mock_stdout.getvalue(), "")


if __name__ == '__main__':
    unittest.main()


