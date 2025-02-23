import unittest

from furniture import FurnitureFactory
from furniture import Chair
from furniture import Table
from furniture import Bed
from furniture import Sofa
from furniture import Wardrobe
from furniture import NoDiscount


class TestFurnitureFactory(unittest.TestCase):
    def test_create_chair(self):
        chair = FurnitureFactory.create_furniture("Chair",name="Office Chair",has_armrests=True,
        )
        self.assertIsInstance(chair, Chair)
        self.assertEqual(chair.name, "Office Chair")
        self.assertEqual(chair.price, 100.0)
        self.assertEqual(chair.available_quantity, 0)
        self.assertIsInstance(chair.discount_strategy, NoDiscount)

    def test_create_table(self):
        table = FurnitureFactory.create_furniture("Table",
                 name="Cosy Table", shape="Rectangular", is_extendable=True)
        self.assertIsInstance(table, Table)
        self.assertEqual(table.name, "Cosy Table")
        #self.assertEqual()

    def test_create_sofa(self):
        sofa = FurnitureFactory.create_furniture("Sofa", name="Luxury Sofa", num_seats=4, has_recliner=True)
        self.assertIsInstance(sofa, Sofa)
        self.assertEqual(sofa.name, "Luxury Sofa")

    def test_create_bed(self):
        bed = FurnitureFactory.create_furniture("Bed", name="King Bed", bed_size="King", has_storage=False)
        self.assertIsInstance(bed, Bed)
        self.assertEqual(bed.name, "King Bed")
        self.assertEqual(bed.bed_size, "King")

    def test_create_wardrobe(self):
        wardrobe = FurnitureFactory.create_furniture("Wardrobe", name="Wooden Wardrobe", num_doors=3, has_mirror=True)
        self.assertIsInstance(wardrobe, Wardrobe)
        self.assertEqual(wardrobe.name, "Wooden Wardrobe")

    def test_invalid_furniture_type(self):
        with self.assertRaises(ValueError) as context:
            FurnitureFactory.create_furniture("Lamp", name="Table Lamp")
        self.assertEqual(str(context.exception), "Unknown furniture type: Lamp")

if __name__ == "__main__":
    unittest.main()
