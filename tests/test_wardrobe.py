import unittest
from furniture import NoDiscount
from furniture import HolidayDiscount
from furniture import VIPDiscount
from furniture import ClearanceDiscount
from furniture import Wardrobe


class TestSofa(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.wardrobes = {
        "With Mirror": Wardrobe(
            u_id="KMWpQl", name="Smart Wardrobe", description="A luxurious glass wardrobe.",
            material="Glass", color="Charcoal Gray", wp=3, price=631.0,
            dimensions=(110, 136, 56), country="Italy", available_quantity=52,
            num_doors=2, has_mirror=True

        ),
            "Without Mirror": Wardrobe(
                u_id="QMqFqc", name="Chic Wardrobe", description="An elegant glass wardrobe with mirror.",
                material="Glass", color="Charcoal Gray", wp=3, price=652.0,
                dimensions=(85, 112, 185), country="Poland", available_quantity=63,
                num_doors=1, has_mirror=False
            )
        }
        self.discounts = {
            "No Discount": NoDiscount(),
            "Holiday Discount": HolidayDiscount(),
            "VIP Discount": VIPDiscount(),
            "Clearance Discount": ClearanceDiscount()
        }

    def test_initialization(self):
        for wardrobe_type, wardrobe in self.wardrobes.items():
            with self.subTest(wardrobe=wardrobe_type):
                self.assertIsInstance(wardrobe, Wardrobe)
                self.assertGreater(wardrobe.price, 0)
                self.assertIsInstance(wardrobe.num_doors, int)
                self.assertIsInstance(wardrobe.has_mirror, bool)

    def test_calculate_discount(self):
        expected_discounts = {
            "With Mirror": {"No Discount": 6, "Holiday Discount": 21, "VIP Discount": 26, "Clearance Discount": 36},
            "Without Mirror": {"No Discount": 3, "Holiday Discount": 18, "VIP Discount": 23, "Clearance Discount": 33}
        }

        for wardrobe_type, wardrobe in self.wardrobes.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(wardrobe=wardrobe_type, discount=discount_type):
                    calculated_discount = wardrobe.calculate_discount(discount)
                    self.assertEqual(calculated_discount, expected_discounts[wardrobe_type][discount_type])

    def test_apply_discount(self):
        expected_prices = {
            "With Mirror": {"No Discount": 593.1, "Holiday Discount": 498.5, "VIP Discount": 466.9, "Clearance Discount": 403.8},
            "Without Mirror": {"No Discount": 632.4, "Holiday Discount": 534.6, "VIP Discount": 502.0, "Clearance Discount": 436.8}
        }

        for wardrobe_type, wardrobe in self.wardrobes.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(wardrobe=wardrobe_type, discount=discount_type):
                    discounted_price = wardrobe.apply_discount(discount)
                    self.assertAlmostEqual(discounted_price, expected_prices[wardrobe_type][discount_type])

    def test_apply_tax(self):
        tax_percentages = [12, -14, 34]  # List of different tax percentages

        for wardrobe_type, wardrobe in self.wardrobes.items():
            for tax_percentage in tax_percentages:
                with self.subTest(wardrobe=wardrobe_type, tax_percentage=tax_percentage):
                    expected_price = wardrobe.price * (1 + tax_percentage / 100)
                    result = wardrobe.apply_tax(tax_percentage)
                    self.assertAlmostEqual(result, expected_price, places=2)

    def test_is_available(self):
        for wardrobe_type, wardrobe in self.wardrobes.items():
            with self.subTest(wardrobe=wardrobe_type):
                self.assertTrue(wardrobe.is_available())

        # Set quantity to 0 and check again
        for wardrobe_type, wardrobe in self.wardrobes.items():
            wardrobe.available_quantity = 0
            with self.subTest(wardrobe=wardrobe_type + " (Out of Stock)"):
                self.assertFalse(wardrobe.is_available())

    def test_wardrobe_info(self):
        expected_info = {
            "With Mirror": "Smart Wardrobe: Doors - 2, Mirror - True",
            "Without Mirror": "Chic Wardrobe: Doors - 1, Mirror - False"
        }

        for wardrobe_type, wardrobe in self.wardrobes.items():
            with self.subTest(wardrobe=wardrobe):
                self.assertEqual(wardrobe.wardrobe_info(), expected_info[wardrobe_type])


if __name__ == '__main__':
    unittest.main()
