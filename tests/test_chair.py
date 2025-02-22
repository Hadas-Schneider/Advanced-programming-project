import unittest
from furniture import NoDiscount
from furniture import HolidayDiscount
from furniture import VIPDiscount
from furniture import ClearanceDiscount
from furniture import Chair


class TestChair(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.chairs = {
            "With Armrests": Chair(
                u_id="C001", name="Office Chair", description="Ergonomic office chair",
                material="Leather", color="Black", wp=5, price=200.0,
                dimensions=(50, 50, 120), country="USA", available_quantity=10,
                has_armrests=True
            ),
            "Without Armrests": Chair(
                u_id="C002", name="Basic Chair", description="Simple plastic chair",
                material="Plastic", color="Red", wp=2, price=100.0,
                dimensions=(40, 40, 90), country="China", available_quantity=5,
                has_armrests=False
            )
        }
        self.discounts = {
            "No Discount": NoDiscount(),
            "Holiday Discount": HolidayDiscount(),
            "VIP Discount": VIPDiscount(),
            "Clearance Discount": ClearanceDiscount()
        }

    def test_initialization(self):
        """Test Chair object initialization for both chairs"""
        for chair_type, chair in self.chairs.items():
            with self.subTest(chair=chair_type):
                self.assertIsInstance(chair, Chair)
                self.assertGreater(chair.price, 0)
                self.assertIsInstance(chair.has_armrests, bool)

    def test_calculate_discount(self):
        """Test discount calculation for both chairs with different discount types"""
        expected_discounts = {
            "With Armrests": {"No Discount": 5, "Holiday Discount": 20, "VIP Discount": 25, "Clearance Discount": 35},
            "Without Armrests": {"No Discount": 0, "Holiday Discount": 15, "VIP Discount": 20, "Clearance Discount": 30}
        }

        for chair_type, chair in self.chairs.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(chair=chair_type, discount=discount_type):
                    calculated_discount = chair.calculate_discount(discount)
                    self.assertEqual(calculated_discount, expected_discounts[chair_type][discount_type])

    def test_apply_discount(self):
        """Test applying discount for both chairs"""
        expected_prices = {
            "With Armrests": {"No Discount": 190, "Holiday Discount": 160, "VIP Discount": 150, "Clearance Discount": 130},
            "Without Armrests": {"No Discount": 100, "Holiday Discount": 85, "VIP Discount": 80, "Clearance Discount": 70}
        }

        for chair_type, chair in self.chairs.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(chair=chair_type, discount=discount_type):
                    discounted_price = chair.apply_discount(discount)
                    self.assertAlmostEqual(discounted_price, expected_prices[chair_type][discount_type])

    def test_apply_tax(self):
        """Test apply_tax function with different tax percentages"""
        tax_percentages = [5, 10, 15]  # List of different tax percentages

        for chair_type, chair in self.chairs.items():
            for tax_percentage in tax_percentages:
                with self.subTest(chair=chair_type, tax_percentage=tax_percentage):
                    expected_price = chair.price * (1 + tax_percentage / 100)
                    result = chair.apply_tax(tax_percentage)
                    self.assertAlmostEqual(result, expected_price, places=2)

    def test_is_available(self):
        """Test is_available method for both chairs"""
        for chair_type, chair in self.chairs.items():
            with self.subTest(chair=chair_type):
                self.assertTrue(chair.is_available())

        # Set quantity to 0 and check again
        for chair_type, chair in self.chairs.items():
            chair.available_quantity = 0
            with self.subTest(chair=chair_type + " (Out of Stock)"):
                self.assertFalse(chair.is_available())



if __name__ == '__main__':
    unittest.main()
