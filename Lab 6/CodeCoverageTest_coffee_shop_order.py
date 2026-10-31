"""Lab 6 - Code (line) coverage tests for coffee_shop_order.py

Run:
    coverage run -m pytest CodeCoverageTest_coffee_shop_order.py
    coverage report -m
"""
import pytest
from coffee_shop_order import process_order_batch, check_espresso_machine


# ---------------- process_order_batch ----------------
def test_invalid_orders_type_raises():
    with pytest.raises(ValueError):
        process_order_batch("not a list", 0.1)


def test_negative_tax_raises():
    with pytest.raises(ValueError):
        process_order_batch([], -0.05)


def test_unpaid_order_is_skipped():
    result = process_order_batch([{"paid": False, "size": "small"}], 0.1)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_all_sizes_priced_correctly():
    orders = [
        {"paid": True, "size": "small"},
        {"paid": True, "size": "medium"},
        {"paid": True, "size": "large"},
    ]
    result = process_order_batch(orders, 0.0)
    assert result == {"total": 13.5, "status": "COMPLETED"}


def test_invalid_size_is_rejected():
    result = process_order_batch([{"paid": True, "size": "huge"}], 0.1)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_syrup_cost_is_capped_at_1_50():
    order = {
        "paid": True,
        "size": "medium",
        "customizations": [
            {"type": "syrup", "cost": 1.0},   # under cap -> full cost
            {"type": "syrup", "cost": 2.0},   # over cap  -> capped to 1.5
        ],
    }
    result = process_order_batch([order], 0.0)
    assert result["total"] == pytest.approx(7.0)


def test_other_customization_adds_full_cost():
    order = {
        "paid": True,
        "size": "medium",
        "customizations": [{"type": "oat_milk", "cost": 0.5}],
    }
    result = process_order_batch([order], 0.0)
    assert result["total"] == pytest.approx(5.0)


def test_negative_cost_customization_is_rejected():
    order = {
        "paid": True,
        "size": "small",
        "customizations": [{"type": "syrup", "cost": -1.0}],
    }
    result = process_order_batch([order], 0.0)
    assert result == {"total": 3.0, "status": "COMPLETED"}


def test_strict_allergy_zeroes_the_order():
    order = {
        "paid": True,
        "size": "medium",
        "strict_allergy": True,
        "customizations": [
            {"type": "allergen_alert", "cost": 0.0},
            {"type": "syrup", "cost": 1.0},
        ],
    }
    result = process_order_batch([order], 0.1)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_member_discount_applied():
    result = process_order_batch([{"paid": True, "size": "medium", "is_member": True}], 0.0)
    assert result["total"] == pytest.approx(4.05)
    assert result["status"] == "COMPLETED"


def test_audit_rejected_when_more_than_4_rejections():
    orders = [{"paid": True, "size": "huge"}] * 5 + [{"paid": True, "size": "medium"}]
    result = process_order_batch(orders, 0.0)
    assert result == {"total": 4.5, "status": "AUDIT_REJECTED"}


# ---------------- check_espresso_machine ----------------
def test_machine_no_data():
    assert check_espresso_machine([]) == "NO_DATA"


def test_machine_shutdown_on_two_consecutive_overheats():
    assert check_espresso_machine([[90.0, 97.0, 98.0]]) == "SHUTDOWN"


def test_machine_optimal():
    assert check_espresso_machine([[90.0, 95.0, 96.0]]) == "OPTIMAL"
