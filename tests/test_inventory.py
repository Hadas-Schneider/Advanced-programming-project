import unittest

from io import StringIO
from unittest.mock import Mock
from unittest.mock import patch
from furniture import Chair
from furniture import Table
from inventory import InventoryObserver
from inventory import Inventory


class Furniture:
    """Mock Furniture class for testing purposes"""

    def __init__(self, name, furniture_type, price, available_quantity):
        self.name = name
        self.type = furniture_type
        self.price = price
        self.available_quantity = available_quantity


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.inventory = Inventory()

        self.chair = Chair(
            u_id="123",
            name="Office Chair",
            description="Comfortable office chair",
            material="Leather",
            color="Black",
            wp=1,
            price=199.99,
            dimensions=(60, 60, 100),
            country="USA",
            available_quantity=10,
            has_armrests=True
        )

        self.chair2 = Chair(
            u_id="124",
            name="Office Chair",
            description="Comfortable office chair",
            material="Leather",
            color="Black",
            wp=1,
            price=99.99,
            dimensions=(20, 40, 90),
            country="USA",
            available_quantity=6,
            has_armrests=True
        )

        self.table = Table(
            u_id="125",
            name="Dining Table",
            description="Comfortable dining table",
            material="Leather",
            color="Black",
            wp=1,
            price=399.99,
            dimensions=(20, 40, 90),
            country="USA",
            available_quantity=5,
            shape="Circle",
            is_extendable=True
        )

        self.table2 = Table(
            u_id="126",
            name="Coffee Table",
            description="Comfortable coffee table",
            material="Leather",
            color="Black",
            wp=1,
            price=200.99,
            dimensions=(20, 40, 90),
            country="USA",
            available_quantity=2,
            shape="Circle",
            is_extendable=True
        )

        # Create mock observers
        self.observer1 = Mock(spec=InventoryObserver)
        self.observer2 = Mock(spec=InventoryObserver)

    def test_init(self):
        self.assertEqual({}, self.inventory.items_by_type)
        self.assertEqual([], self.inventory.observers)

    def test_add_observer(self):
        self.inventory.add_observer(self.observer1)
        self.assertEqual(1, len(self.inventory.observers))
        self.assertIn(self.observer1, self.inventory.observers)

        # Add another observer
        self.inventory.add_observer(self.observer2)
        self.assertEqual(2, len(self.inventory.observers))
        self.assertIn(self.observer2, self.inventory.observers)

    def test_remove_observer(self):
        self.inventory.add_observer(self.observer1)
        self.inventory.add_observer(self.observer2)
        self.assertEqual(2, len(self.inventory.observers))

        # Remove one observer
        self.inventory.remove_observer(self.observer1)
        self.assertEqual(1, len(self.inventory.observers))
        self.assertNotIn(self.observer1, self.inventory.observers)
        self.assertIn(self.observer2, self.inventory.observers)

        # Remove the other observer
        self.inventory.remove_observer(self.observer2)
        self.assertEqual(0, len(self.inventory.observers))

    def test_notify_observers(self):
        self.inventory.add_observer(self.observer1)
        self.inventory.add_observer(self.observer2)

        # Notify observers
        self.inventory.notify_observers(self.chair, "added")

        self.observer1.update.assert_called_once_with(self.chair, "added")
        self.observer2.update.assert_called_once_with(self.chair, "added")

        # Reset mocks and test with different item and change type
        self.observer1.reset_mock()
        self.observer2.reset_mock()

        self.inventory.notify_observers(self.table, "updated")
        self.observer1.update.assert_called_once_with(self.table, "updated")
        self.observer2.update.assert_called_once_with(self.table, "updated")

    def test_add_new_item(self):
        self.inventory.add_observer(self.observer1)
        self.inventory.add_item(self.chair)
        self.assertIn("Chair", self.inventory.items_by_type)
        self.assertIn("Office Chair", self.inventory.items_by_type["Chair"])
        self.observer1.update.assert_called_once_with(self.chair, "added")

        self.inventory.add_item(self.table)
        self.assertIn("Table", self.inventory.items_by_type)
        self.assertIn("Dining Table", self.inventory.items_by_type["Table"])

        expected_calls = [
            ((self.chair, "added"),),
            ((self.table, "added"),)
        ]
        self.observer1.update.assert_has_calls(expected_calls, any_order=True)

    def test_add_existed_item(self):
        """Test updating quantity when adding an existing item."""
        self.inventory.add_observer(self.observer1)
        self.inventory.add_item(self.chair)
        self.inventory.add_item(self.chair2)
        self.assertEqual(self.inventory.items_by_type["Chair"]["Office Chair"].available_quantity, 16)

        self.inventory.add_item(self.table)
        self.inventory.add_item(self.table2)
        self.assertEqual(self.inventory.items_by_type["Table"]["Dining Table"].available_quantity, 5)
        self.assertEqual(self.inventory.items_by_type["Table"]["Coffee Table"].available_quantity, 2)

        expected_calls = [
            ((self.chair, "added"),),
            ((self.chair2, "added"),),
            ((self.table, "added"),),
            ((self.table2, "added"),)
        ]
        self.observer1.update.assert_has_calls(expected_calls, any_order=True)

    def test_remove_item(self):
        self.inventory.add_observer(self.observer1)
        self.inventory.add_item(self.chair)
        self.inventory.remove_item(self.chair.name, self.chair.type)
        self.assertNotIn(self.chair.type, self.inventory.items_by_type.get(self.chair.type, {}))

        expected_calls = [
            ((self.chair, "added"),),
            ((self.chair, "removed"),)
        ]
        self.observer1.update.assert_has_calls(expected_calls, any_order=True)

    def test_remove_not_found_item(self):
        self.inventory.add_observer(self.observer1)
        self.inventory.add_item(self.table)

        # Case 1: The furniture type exists but the specific item name doesn't
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.inventory.remove_item("Coffee Table", "Table")
            self.assertIn("Item 'Coffee Table' of type 'Table' not found in inventory", fake_output.getvalue())

        # Case 2: The furniture type doesn't exist at all
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.inventory.remove_item("Dining Chair", "Chair")
            self.assertIn("Item 'Dining Chair' of type 'Chair' not found in inventory", fake_output.getvalue())

        # Verify the observer was never notified
        self.observer1.assert_not_called()

        # Verify the inventory state didn't change
        self.assertEqual(list(self.inventory.items_by_type.keys()), ["Table"])
        self.assertEqual(list(self.inventory.items_by_type["Table"].keys()), ["Dining Table"])

    def test_update_quantity_existing_item(self):
        self.inventory.add_observer(self.observer1)
        self.inventory.add_item(self.chair)
        self.inventory.update_quantity("Office Chair", "Chair", 20)
        self.assertEqual(self.inventory.items_by_type["Chair"]["Office Chair"].available_quantity, 20)
        expected_calls = [
            ((self.chair, "updated"),)
        ]
        self.observer1.update.assert_has_calls(expected_calls, any_order=True)

    def test_update_quantity_non_existing_item(self):
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.inventory.update_quantity("Gaming Chair", "Chair", 15)
            self.assertIn("Item 'Gaming Chair' of type 'Chair' not found in inventory.", fake_output.getvalue())
        self.observer1.assert_not_called()

    def test_test_search_existing_type(self):
        self.inventory.add_item(self.chair)
        self.inventory.add_item(self.table)
        self.inventory.add_item(self.table2)

        tables = self.inventory.search_by_type("Table")
        chairs = self.inventory.search_by_type("Chair")
        self.assertEqual(len(tables), 2)  # Expecting 2 tables
        self.assertEqual(tables[0].name, "Dining Table")
        self.assertEqual(tables[1].name, "Coffee Table")

        self.assertEqual(len(chairs), 1)  # Expecting 1 chair
        self.assertEqual(chairs[0].name, "Office Chair")

    def test_search_non_existing_type(self):
        result = self.inventory.search_by_type("Sofa")
        self.assertEqual(result, [])

    def test_search_by_name(self):
        self.inventory.add_item(self.chair)
        result = self.inventory.search(name="Office Chair")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Office Chair")

    def test_search_by_type(self):
        self.inventory.add_item(self.table)
        self.inventory.add_item(self.table2)
        result = self.inventory.search(type="Table")
        self.assertEqual(len(result), 2)

    def test_search_by_quantity(self):
        self.inventory.add_item(self.table)
        result = self.inventory.search(available_quantity=5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Dining Table")

    def test_search_with_multiple_filters(self):
        self.inventory.add_item(self.table2)
        result = self.inventory.search(name="Coffee Table", type="Table")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Coffee Table")

    def test_search_no_results(self):
        result = self.inventory.search(name="Nonexistent Item")
        self.assertEqual(result, [])

    def test_search_with_no_filters(self):
        self.inventory.add_item(self.chair)
        self.inventory.add_item(self.chair2)
        self.inventory.add_item(self.table)
        self.inventory.add_item(self.table2)
        result = self.inventory.search()
        self.assertEqual(len(result), 3)

    def test_get_all_items_empty_inventory(self):
        """Test get_all_items() when inventory is empty"""
        result = self.inventory.get_all_items()
        self.assertEqual(result, [], "Expected empty list for empty inventory")

    def test_get_all_items_item_attributes(self):
        """Comprehensive test to verify all item attributes are correctly mapped"""
        self.inventory.items_by_type = {
            "Chair": {self.chair.u_id: self.chair}
        }

        result = self.inventory.get_all_items()
        item = result[0]

        self.assertEqual(item['id'], "123")
        self.assertEqual(item['name'], "Office Chair")
        self.assertEqual(item['description'], "Comfortable office chair")
        self.assertEqual(item['material'], "Leather")
        self.assertEqual(item['color'], "Black")
        self.assertEqual(item['warranty_period'], 1)
        self.assertEqual(item['price'], 199.99)
        self.assertEqual(item['dimensions'], (60, 60, 100))
        self.assertEqual(item['country'], "USA")
        self.assertEqual(item['type'], "Chair")
        self.assertEqual(item['available_quantity'], 10)

    def test_get_all_items_multiple_types(self):
        """Test get_all_items() with multiple furniture types"""
        self.inventory.items_by_type = {
            "Chair": {self.chair.u_id: self.chair},
            "Table": {self.table.u_id: self.table}
        }

        result = self.inventory.get_all_items()

        self.assertEqual(len(result), 2, "Expected two items in result")

        ids = [item['id'] for item in result]
        self.assertIn(self.chair.u_id, ids)
        self.assertIn(self.table.u_id, ids)

    @patch("builtins.print")
    def test_view_inventory_non_empty(self, mock_print):
        self.inventory.add_item(self.chair)
        self.inventory.add_item(self.table)
        self.inventory.add_item(self.table2)
        self.inventory.view_inventory()

        # Check that the print statements are called as expected
        mock_print.assert_any_call("Current Inventory:")
        mock_print.assert_any_call("Type: Chair")
        mock_print.assert_any_call("  - Office Chair: 10 in stock, Price: $199.99")
        mock_print.assert_any_call("Type: Table")
        mock_print.assert_any_call("  - Dining Table: 5 in stock, Price: $399.99")
        mock_print.assert_any_call("  - Coffee Table: 2 in stock, Price: $200.99")

    @patch("builtins.print")
    def test_view_inventory_empty(self, mock_print):
        self.inventory.items_by_type = {}
        self.inventory.view_inventory()
        mock_print.assert_called_with("The inventory is empty.")

    def test_check_low_stock(self):
        self.inventory.add_item(self.chair)
        self.inventory.add_item(self.table)
        self.inventory.add_item(self.table2)
        low_stock_items = self.inventory.check_low_stock()

        # Verify that we only get items with stock <= 5
        low_stock_names = [item.name for item in low_stock_items]
        self.assertNotIn("Office Chair", low_stock_names)
        self.assertIn("Dining Table", low_stock_names)
        self.assertIn("Coffee Table", low_stock_names)

    def test_check_low_stock_with_custom_threshold(self):
        self.inventory.add_item(self.chair)
        self.inventory.add_item(self.table)
        self.inventory.add_item(self.table2)
        low_stock_items = self.inventory.check_low_stock(threshold=4)

        # Verify that we only get items with stock <= 4
        low_stock_names = [item.name for item in low_stock_items]
        self.assertNotIn("Office Chair", low_stock_names)
        self.assertNotIn("Dining Table", low_stock_names)
        self.assertIn("Coffee Table", low_stock_names)


if __name__ == '__main__':
    unittest.main()
