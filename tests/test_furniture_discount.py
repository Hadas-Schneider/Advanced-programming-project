import unittest

import pytest

from furniture import DiscountStrategy
from furniture import NoDiscount
from furniture import HolidayDiscount
from furniture import VIPDiscount
from furniture import ClearanceDiscount


def test_discount_strategy_is_abstract():
    with pytest.raises(TypeError):
        DiscountStrategy()


def test_no_discount():
    strategy = NoDiscount()
    assert strategy.get_discount() == 0, "NoDiscount should always return 0"


def test_holiday_discount():
    strategy = HolidayDiscount()
    assert strategy.get_discount() == 15, "HolidayDiscount should return 15"


def test_vip_discount():
    strategy = VIPDiscount()
    assert strategy.get_discount() == 20, "VIPDiscount should return 20"


def test_clearance_discount():
    strategy = ClearanceDiscount()
    assert strategy.get_discount() == 30, "ClearanceDiscount should return 30"


if __name__ == '__main__':
    unittest.main()
