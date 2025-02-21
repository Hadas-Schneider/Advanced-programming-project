import unittest

import pytest

from furniture import NoDiscount
from furniture import HolidayDiscount
from furniture import VIPDiscount
from furniture import ClearanceDiscount

@pytest.mark.parametrize("price", [2,-5,444])
def test_no_discount_calculate_discount(price):
    f = NoDiscount()
    result = f.calculate_discount(price)
    assert result == 0

@pytest.mark.parametrize("price, expected", [(2,0.3),(-5,-0.75),(445,66.75)])
def test_holiday_discount_calculate_discount(price, expected):
    f = HolidayDiscount()
    assert expected == f.calculate_discount(price)

@pytest.mark.parametrize("price, expected", [(2,0.4),(-5,-1),(445,89)])
def test_vip_discount_calculate_discount(price, expected):
    f = VIPDiscount ()
    assert expected == f.calculate_discount(price)

@pytest.mark.parametrize("price, expected", [(2,0.6),(-5,-1.5),(445,133.5)])
def test_clearance_discount_calculate_discount(price, expected):
    f = ClearanceDiscount ()
    assert expected == f.calculate_discount(price)

@pytest.mark.parametrize("price, expected", [(2,0.9),(-5,-1.5),(445,133.5)])
def test_clearance_discount_calculate_discount_failer(price, expected):
    f = ClearanceDiscount ()
    assert expected == f.calculate_discount(price)

if __name__ == "__main__":
    unittest.main()
