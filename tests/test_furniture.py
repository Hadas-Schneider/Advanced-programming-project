# import pytest
# import unittest
#
# from decimal import Decimal
# from furniture import DiscountStrategy
# from furniture import NoDiscount
# from furniture import HolidayDiscount
# from furniture import VIPDiscount
# from furniture import ClearanceDiscount
# from furniture import Furniture
# from furniture import Chair
# from furniture import Table
# from furniture import Sofa
# from furniture import Wardrobe
# from furniture import Bed
#
# from abc import ABC, abstractmethod
#
#
# # class MockDiscountStrategy(DiscountStrategy):
# #     def __init__(self, discount_percentage: float):
# #         self.discount_percentage = discount_percentage
# #
# #     def get_discount(self) -> float:
# #         """
# #         Implements the abstract method from DiscountStrategy
# #         """
# #         return self.discount_percentage
#
# @pytest.fixture()
# def chair_with_armrests():
#     return Chair("JtB4IU", "Zippy Chair", "A comfortable fabric chair without armrests.",
#                  "Fabric", "Silver", 1, 258, (291, 131, 73), "Sweden", 27, True)
#
# @pytest.fixture()
# def chair_without_armrests():
#     return Chair("a0BD7C", "Buddy Chair", "A comfortable plastic chair without armrests.",
#                  "Plastic", "Charcoal Gray", 2, 202, (97, 81, 139), "Italy", 92, False)
#
# @pytest.fixture()
# def table_not_extendable():
#     return Table("TwNXKF", "Cosy Table", "A sturdy glass table.",
#                  "Glass","Ivory White", 3, 811, (218, 133, 66), "USA",94,
#                  "rectangular", False)
#
#
# @pytest.fixture()
# def table_extendable():
#     return Table("xw1vKg", "Sturdy Table", "A modern fabric table extendable.",
#                  "Fabric","Walnut Brown", 1, 281, (180, 121, 149), "China",14,
#                  "circular", True)
#
#
# @pytest.fixture()
# def no_discount():
#     return NoDiscount()
#
#
# @pytest.fixture()
# def holiday_discount():
#     return HolidayDiscount()
#
#
# @pytest.fixture()
# def vip_discount():
#     return VIPDiscount()
#
#
# @pytest.fixture()
# def clearance_discount():
#     return ClearanceDiscount()
#
#
# @pytest.fixture(params=[NoDiscount, HolidayDiscount, VIPDiscount, ClearanceDiscount])
# def discount_strategy(request):
#     return request.param
#
#
# def test_apply_discount():
#     pass
#
#
# def test_set_discount_strategy():
#     pass
#
#
# def test_apply_tax():
#     pass
#
#
# def test_is_available():
#     pass
#
#
# ## Chair
# def test_chair_with_armrests_set_discount(chair_with_armrests, discount_strategy):
#     chair_with_armrests.set_discount_strategy(discount_strategy)
#     assert isinstance(chair_with_armrests.discount_strategy, type(discount_strategy))
#
#
# @pytest.mark.parametrizea
# def test_chair_with_armrests_apply_discount(chair_with_armrests, discount_strategy):
#     result = chair_with_armrests.apply_discount(discount_strategy)
#     assert result == Furniture.price_with_discount(chair_with_armrests.price,
#     chair_with_armrests.calculate_discount(discount_strategy))
#
# def test_chair_without_armrests_apply_discount(chair_without_armrests, no_discount):
#     result = chair_without_armrests.apply_discount(no_discount)
#     assert result == Furniture.price_with_discount(chair_without_armrests.price, chair_without_armrests.calculate_discount(no_discount))
#
# def test_chair_with_armrests_set_no_discount(chair_with_armrests, no_discount):
#     chair_with_armrests.set_discount_strategy(no_discount)
#     assert isinstance(chair_with_armrests.discount_strategy, NoDiscount)
#
#
# def test_chair_with_armrests_set_holiday_discount(chair_with_armrests, holiday_discount):
#     chair_with_armrests.set_discount_strategy(holiday_discount)
#     assert isinstance(chair_with_armrests.discount_strategy, HolidayDiscount)
#
#
# def test_chair_with_armrests_set_vip_discount(chair_with_armrests, vip_discount):
#     chair_with_armrests.set_discount_strategy(vip_discount)
#     assert isinstance(chair_with_armrests.discount_strategy, VIPDiscount)
#
# def test_chair_with_armrests_set_clearance_discount(chair_with_armrests, clearance_discount):
#     chair_with_armrests.set_discount_strategy(clearance_discount)
#     assert isinstance(chair_with_armrests.discount_strategy, ClearanceDiscount)
#
# def test_chair_with_armrests_info(chair_with_armrests):
#     assert chair_with_armrests.chair_info() == "Zippy Chair: Armrests - True, Material - Fabric"
#
# def test_chair_without_armrests_info(chair_without_armrests):
#     assert chair_without_armrests.chair_info() == "Buddy Chair: Armrests - False, Material - Plastic"
#
#
# ## Table
# def test_table_calculate_discount():
#     pass
#
#
# def test_table_info():
#     pass
#
#
# ## Sofa
# def test_sofa_calculate_discount():
#     pass
#
#
# def test_sofa_info():
#     pass
#
#
# ## Bed
# def test_bed_calculate_discount():
#     pass
#
#
# def test_bed_info():
#     pass
#
#
# ## Wardrobe
# def test_wardrobe_calculate_discount():
#     pass
#
#
# def test_wardrobe_info():
#     pass
#
#
# if __name__ == '__main__':
#     unittest.main()
