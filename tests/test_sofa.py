import unittest
from furniture import NoDiscount
from furniture import HolidayDiscount
from furniture import VIPDiscount
from furniture import ClearanceDiscount
from furniture import Sofa


class TestSofa(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.sofas = {
            "With Recliner": Sofa(
                    u_id="VWudm2", name="Cozy Sofa", description="A comfortable fabric sofa without recliner.",
                    material="Fabric", color="Charcoal Gray", wp=1, price=215.0,
                    dimensions=(228, 41, 76), country="Usa", available_quantity=38,
                    num_seats=2, has_recliner=True
            ),
            "Without Recliner": Sofa(
                u_id="yJPKkl", name="Relax Sofa", description="A comfortable fabric sofa without recliner.",
                material="Plastic", color="Charcoal Gray", wp=3, price=553.0,
                dimensions=(128, 52, 172), country="Sweden", available_quantity=91,
                num_seats=3, has_recliner=False
            )
        }
        self.discounts = {
            "No Discount": NoDiscount(),
            "Holiday Discount": HolidayDiscount(),
            "VIP Discount": VIPDiscount(),
            "Clearance Discount": ClearanceDiscount()
        }

    def test_initialization(self):
        for sofa_type, sofa in self.sofas.items():
            with self.subTest(sofa=sofa_type):
                self.assertIsInstance(sofa, Sofa)
                self.assertGreater(sofa.price, 0)
                self.assertIsInstance(sofa.num_seats, int)
                self.assertIsInstance(sofa.has_recliner, bool)

    def test_calculate_discount(self):
        expected_discounts = {
            "With Recliner": {"No Discount": 4, "Holiday Discount": 19, "VIP Discount": 24, "Clearance Discount": 34},
            "Without Recliner": {"No Discount": 6, "Holiday Discount": 21, "VIP Discount": 26, "Clearance Discount": 36}
        }

        for sofa_type, sofa in self.sofas.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(sofa=sofa_type, discount=discount_type):
                    calculated_discount = sofa.calculate_discount(discount)
                    self.assertEqual(calculated_discount, expected_discounts[sofa_type][discount_type])

    def test_apply_discount(self):
        expected_prices = {
            "With Recliner": {"No Discount": 206.4, "Holiday Discount": 174.2,
                              "VIP Discount": 163.4, "Clearance Discount": 141.9},
            "Without Recliner": {"No Discount": 519.8, "Holiday Discount": 436.9,
                                 "VIP Discount": 409.2, "Clearance Discount": 353.9}
        }

        for sofa_type, sofa in self.sofas.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(sofa=sofa_type, discount=discount_type):
                    discounted_price = sofa.apply_discount(discount)
                    self.assertAlmostEqual(discounted_price, expected_prices[sofa_type][discount_type])

    def test_apply_tax(self):
        tax_percentages = [2, 14, -25]  # List of different tax percentages

        for sofa_type, sofa in self.sofas.items():
            for tax_percentage in tax_percentages:
                with self.subTest(sofa=sofa_type, tax_percentage=tax_percentage):
                    expected_price = sofa.price * (1 + tax_percentage / 100)
                    result = sofa.apply_tax(tax_percentage)
                    self.assertAlmostEqual(result, expected_price, places=2)

    def test_is_available(self):
        for sofa_type, sofa in self.sofas.items():
            with self.subTest(sofa=sofa_type):
                self.assertTrue(sofa.is_available())

        # Set quantity to 0 and check again
        for sofa_type, sofa in self.sofas.items():
            sofa.available_quantity = 0
            with self.subTest(sofa=sofa_type + " (Out of Stock)"):
                self.assertFalse(sofa.is_available())

    def test_bed_info(self):
        expected_info = {
            "With Recliner": "Cozy Sofa: Seats - 2, Recliner - True",
            "Without Recliner": "Relax Sofa: Seats - 3, Recliner - False"
        }

        for sofa_type, sofa in self.sofas.items():
            with self.subTest(sofa=sofa):
                self.assertEqual(sofa.sofa_info(), expected_info[sofa_type])


if __name__ == '__main__':
    unittest.main()
