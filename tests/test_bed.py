import unittest
from furniture import NoDiscount
from furniture import HolidayDiscount
from furniture import VIPDiscount
from furniture import ClearanceDiscount
from furniture import Bed


class TestBed(unittest.TestCase):
    def setUp(self):
        """Set up test cases"""
        self.beds = {
            "With Storage": Bed(
                u_id="S6GoqL", name="Cozy Bed", description="A compact plastic bed queen.",
                material="Plastic", color="Natural Oak", wp=2, price=129.0,
                dimensions=(189, 61, 171), country="China", available_quantity=94,
                bed_size="King", has_storage=True
            ),
            "Without Storage": Bed(
                u_id="cfJBBm", name="Lush Bed", description="An ergonomic metal bed double.",
                material="Metal", color="Ivory White", wp=10, price=669.0,
                dimensions=(237, 12, 65), country="Italy", available_quantity=45,
                bed_size="Single", has_storage=False
            )
        }
        self.discounts = {
            "No Discount": NoDiscount(),
            "Holiday Discount": HolidayDiscount(),
            "VIP Discount": VIPDiscount(),
            "Clearance Discount": ClearanceDiscount()
        }

    def test_initialization(self):
        for bed_type, bed in self.beds.items():
            with self.subTest(bed=bed_type):
                self.assertIsInstance(bed, Bed)
                self.assertGreater(bed.price, 0)
                self.assertIsInstance(bed.bed_size, str)
                self.assertIsInstance(bed.has_storage, bool)

    def test_calculate_discount(self):
        expected_discounts = {
            "With Storage": {"No Discount": 15, "Holiday Discount": 30, "VIP Discount": 35, "Clearance Discount": 45},
            "Without Storage": {"No Discount": 0, "Holiday Discount": 15, "VIP Discount": 20, "Clearance Discount": 30}
        }

        for bed_type, bed in self.beds.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(bed=bed_type, discount=discount_type):
                    calculated_discount = bed.calculate_discount(discount)
                    self.assertEqual(calculated_discount, expected_discounts[bed_type][discount_type])

    def test_apply_discount(self):
        expected_prices = {
            "With Storage": {"No Discount": 109.6, "Holiday Discount": 90.3,
                             "VIP Discount": 83.9, "Clearance Discount": 71.0},
            "Without Storage": {"No Discount": 669, "Holiday Discount": 568.6,
                                "VIP Discount": 535.2, "Clearance Discount": 468.3}
        }

        for bed_type, bed in self.beds.items():
            for discount_type, discount in self.discounts.items():
                with self.subTest(bed=bed_type, discount=discount_type):
                    discounted_price = bed.apply_discount(discount)
                    self.assertAlmostEqual(discounted_price, expected_prices[bed_type][discount_type])

    def test_apply_tax(self):
        tax_percentages = [2, 17, -5]  # List of different tax percentages

        for bed_type, bed in self.beds.items():
            for tax_percentage in tax_percentages:
                with self.subTest(bed=bed_type, tax_percentage=tax_percentage):
                    expected_price = bed.price * (1 + tax_percentage / 100)
                    result = bed.apply_tax(tax_percentage)
                    self.assertAlmostEqual(result, expected_price, places=2)

    def test_is_available(self):
        for bed_type, bed in self.beds.items():
            with self.subTest(bed=bed_type):
                self.assertTrue(bed.is_available())

        # Set quantity to 0 and check again
        for bed_type, bed in self.beds.items():
            bed.available_quantity = 0
            with self.subTest(bed=bed_type + " (Out of Stock)"):
                self.assertFalse(bed.is_available())

    def test_bed_info(self):
        expected_info = {
            "With Storage": "Cozy Bed: Size - King, Storage - True",
            "Without Storage": "Lush Bed: Size - Single, Storage - False"
        }

        for bed_type, bed in self.beds.items():
            with self.subTest(bed=bed_type):
                self.assertEqual(bed.bed_info(), expected_info[bed_type])


if __name__ == '__main__':
    unittest.main()
