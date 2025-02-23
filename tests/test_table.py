import unittest
from furniture import NoDiscount
from furniture import HolidayDiscount
from furniture import VIPDiscount
from furniture import ClearanceDiscount
from furniture import Table


class TestTable(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.tables = {
            "With Extension": Table(
                u_id="sc5K8a", name="Cosy Table", description="A luxurious fabric table extendable.",
                material="Fabric", color="Silver", wp=1, price=248.0,
                dimensions=(222, 131, 100), country="Italy", available_quantity=31,
                shape="Rectangular", is_extendable=True
            ),
            "Without Extension": Table(
                u_id="fop7fI", name="Elegant Table", description="Simple fabric table",
                material="Plastic", color="Jet Black", wp=2, price=336.0,
                dimensions=(153, 135, 77), country="Poland", available_quantity=5,
                shape="Circular", is_extendable=False
            )
        }
        self.discounts = {
            "No Discount": NoDiscount(),
            "Holiday Discount": HolidayDiscount(),
            "VIP Discount": VIPDiscount(),
            "Clearance Discount": ClearanceDiscount()
        }

    def test_initialization(self):
        for table_type, table in self.tables.items():
            with self.subTest(table=table_type):
                self.assertIsInstance(table, Table)
                self.assertGreater(table.price, 0)
                self.assertIsInstance(table.shape, str)
                self.assertIsInstance(table.is_extendable, bool)

    def test_calculate_discount(self):
        expected_discounts = {
            "With Extension": {"No Discount": 10, "Holiday Discount": 25, "VIP Discount": 30, "Clearance Discount": 40},
            "Without Extension": {"No Discount": 0, "Holiday Discount": 15, "VIP Discount": 20, "Clearance Discount": 30}
        }

        for table_type, table in self.tables.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(table=table_type, discount=discount_type):
                    calculated_discount = table.calculate_discount(discount)
                    self.assertEqual(calculated_discount, expected_discounts[table_type][discount_type])

    def test_apply_discount(self):
        expected_prices = {
            "With Extension": {"No Discount": 223.2, "Holiday Discount": 186,
                               "VIP Discount": 173.6, "Clearance Discount": 148.8},
            "Without Extension": {"No Discount": 336, "Holiday Discount": 285.6,
                                  "VIP Discount": 268.8, "Clearance Discount": 235.2}
        }

        for table_type, table in self.tables.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(table=table_type, discount=discount_type):
                    discounted_price = table.apply_discount(discount)
                    self.assertAlmostEqual(discounted_price, expected_prices[table_type][discount_type])

    def test_apply_tax(self):
        tax_percentages = [5, 7, 45]  # List of different tax percentages

        for table_type, table in self.tables.items():
            for tax_percentage in tax_percentages:
                with self.subTest(table=table_type, tax_percentage=tax_percentage):
                    expected_price = table.price * (1 + tax_percentage / 100)
                    result = table.apply_tax(tax_percentage)
                    self.assertAlmostEqual(result, expected_price, places=2)

    def test_is_available(self):
        for table_type, table in self.tables.items():
            with self.subTest(table=table_type):
                self.assertTrue(table.is_available())

        # Set quantity to 0 and check again
        for table_type, table in self.tables.items():
            table.available_quantity = 0
            with self.subTest(table=table_type + " (Out of Stock)"):
                self.assertFalse(table.is_available())

    def test_table_info(self):
        expected_info = {
            "With Extension": "Cosy Table: Shape - Rectangular, Extendable - Yes, Material: Fabric",
            "Without Extension": "Elegant Table: Shape - Circular, Extendable - No, Material: Plastic"
        }

        for table_type, table in self.tables.items():
            with self.subTest(table=table_type):
                self.assertEqual(table.table_info(), expected_info[table_type])


if __name__ == '__main__':
    unittest.main()
