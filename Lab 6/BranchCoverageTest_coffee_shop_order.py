"""Lab 6 - Branch coverage tests for coffee_shop_order.py

Run:
    coverage run --branch -m pytest BranchCoverageTest_coffee_shop_order.py
    coverage report -m
"""
import pytest
from coffee_shop_order import process_order_batch, check_espresso_machine


# ======================= process_order_batch =======================

# ---- input validation ----
def test_orders_not_a_list_raises():
    with pytest.raises(ValueError):
        process_order_batch("not a list", 0.1)


def test_orders_dict_raises():
    with pytest.raises(ValueError):
        process_order_batch({"paid": True}, 0.1)


def test_negative_tax_raises():
    with pytest.raises(ValueError):
        process_order_batch([], -0.05)


def test_zero_tax_is_valid():
    assert process_order_batch([], 0.0) == {"total": 0.0, "status": "NO_SALE"}


# ---- loop over orders ----
def test_empty_orders_list_is_no_sale():
    assert process_order_batch([], 0.1) == {"total": 0.0, "status": "NO_SALE"}


def test_unpaid_order_skipped():
    result = process_order_batch([{"paid": False, "size": "small"}], 0.1)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_missing_paid_key_treated_as_unpaid():
    assert process_order_batch([{"size": "large"}], 0.1) == {"total": 0.0, "status": "NO_SALE"}


# ---- size branches ----
def test_size_small():
    assert process_order_batch([{"paid": True, "size": "small"}], 0.0)["total"] == 3.0


def test_size_medium():
    assert process_order_batch([{"paid": True, "size": "medium"}], 0.0)["total"] == 4.5


def test_size_large():
    assert process_order_batch([{"paid": True, "size": "large"}], 0.0)["total"] == 6.0


def test_size_missing_defaults_to_medium():
    assert process_order_batch([{"paid": True}], 0.0)["total"] == 4.5


def test_invalid_size_rejected():
    result = process_order_batch([{"paid": True, "size": "huge"}], 0.1)
    assert result == {"total": 0.0, "status": "NO_SALE"}


# ---- customization branches ----
def test_no_customizations():
    result = process_order_batch([{"paid": True, "size": "small", "customizations": []}], 0.0)
    assert result["total"] == 3.0


def test_syrup_below_cap():
    order = {"paid": True, "size": "small", "customizations": [{"type": "syrup", "cost": 1.0}]}
    assert process_order_batch([order], 0.0)["total"] == pytest.approx(4.0)


def test_syrup_exactly_at_cap():
    order = {"paid": True, "size": "small", "customizations": [{"type": "syrup", "cost": 1.5}]}
    assert process_order_batch([order], 0.0)["total"] == pytest.approx(4.5)


def test_syrup_above_cap_is_capped():
    order = {"paid": True, "size": "medium", "customizations": [{"type": "syrup", "cost": 2.0}]}
    assert process_order_batch([order], 0.0)["total"] == pytest.approx(6.0)


def test_other_customization_full_cost():
    order = {"paid": True, "size": "medium", "customizations": [{"type": "oat_milk", "cost": 0.5}]}
    assert process_order_batch([order], 0.0)["total"] == pytest.approx(5.0)


def test_customization_with_missing_keys_adds_zero():
    order = {"paid": True, "size": "medium", "customizations": [{}]}
    assert process_order_batch([order], 0.0)["total"] == pytest.approx(4.5)


def test_negative_cost_rejected_and_skipped():
    order = {"paid": True, "size": "small", "customizations": [{"type": "syrup", "cost": -1.0}]}
    assert process_order_batch([order], 0.0) == {"total": 3.0, "status": "COMPLETED"}


def test_negative_cost_then_valid_mod_continues_loop():
    order = {
        "paid": True, "size": "small",
        "customizations": [{"type": "oat_milk", "cost": -0.5}, {"type": "oat_milk", "cost": 0.5}],
    }
    assert process_order_batch([order], 0.0)["total"] == pytest.approx(3.5)


# ---- allergen branches ----
def test_allergen_non_strict_rejected_but_order_continues():
    order = {
        "paid": True, "size": "medium",
        "customizations": [
            {"type": "allergen_alert", "cost": 0.0},
            {"type": "syrup", "cost": 1.0},
        ],
    }
    result = process_order_batch([order], 0.0)
    assert result == {"total": 5.5, "status": "COMPLETED"}


def test_allergen_strict_breaks_and_zeroes_order():
    order = {
        "paid": True, "size": "medium", "strict_allergy": True,
        "customizations": [
            {"type": "allergen_alert", "cost": 0.0},
            {"type": "syrup", "cost": 1.0},
        ],
    }
    assert process_order_batch([order], 0.1) == {"total": 0.0, "status": "NO_SALE"}


def test_strict_allergy_order_zeroed_but_other_orders_still_count():
    strict = {
        "paid": True, "size": "large", "strict_allergy": True,
        "customizations": [{"type": "allergen_alert", "cost": 0.0}],
    }
    normal = {"paid": True, "size": "small"}
    result = process_order_batch([strict, normal], 0.0)
    assert result == {"total": 3.0, "status": "COMPLETED"}


# ---- membership ----
def test_member_gets_10_percent_off():
    result = process_order_batch([{"paid": True, "size": "large", "is_member": True}], 0.0)
    assert result["total"] == pytest.approx(5.4)


def test_non_member_pays_full_price():
    result = process_order_batch([{"paid": True, "size": "large", "is_member": False}], 0.0)
    assert result["total"] == pytest.approx(6.0)


# ---- tax + final status branches ----
def test_tax_is_applied():
    assert process_order_batch([{"paid": True, "size": "small"}], 0.10)["total"] == pytest.approx(3.3)


def test_mixed_batch_with_tax():
    orders = [
        {"paid": True, "size": "small"},
        {"paid": True, "size": "large", "is_member": True},
    ]
    result = process_order_batch(orders, 0.08)
    assert result["status"] == "COMPLETED"
    assert result["total"] == pytest.approx(9.07)


def test_exactly_4_rejections_is_not_audit():
    orders = [{"paid": True, "size": "huge"}] * 4 + [{"paid": True, "size": "medium"}]
    assert process_order_batch(orders, 0.0) == {"total": 4.5, "status": "COMPLETED"}


def test_5_rejections_triggers_audit():
    orders = [{"paid": True, "size": "huge"}] * 5 + [{"paid": True, "size": "medium"}]
    assert process_order_batch(orders, 0.0) == {"total": 4.5, "status": "AUDIT_REJECTED"}


def test_audit_rejected_even_when_total_is_zero():
    orders = [{"paid": True, "size": "huge"}] * 5
    assert process_order_batch(orders, 0.1) == {"total": 0.0, "status": "AUDIT_REJECTED"}


def test_negative_cost_mods_count_toward_audit():
    order = {
        "paid": True, "size": "small",
        "customizations": [{"type": "syrup", "cost": -1.0}] * 5,
    }
    assert process_order_batch([order], 0.0) == {"total": 3.0, "status": "AUDIT_REJECTED"}


# ======================= check_espresso_machine =======================
def test_machine_empty_list_no_data():
    assert check_espresso_machine([]) == "NO_DATA"


def test_machine_none_no_data():
    assert check_espresso_machine(None) == "NO_DATA"


def test_machine_all_normal_optimal():
    assert check_espresso_machine([[90.0, 92.0, 95.0]]) == "OPTIMAL"


def test_machine_exactly_96_is_not_overheating():
    assert check_espresso_machine([[96.0, 96.0, 96.0]]) == "OPTIMAL"


def test_machine_two_consecutive_overheats_shutdown():
    assert check_espresso_machine([[90.0, 97.0, 98.0]]) == "SHUTDOWN"


def test_machine_three_consecutive_overheats_shutdown():
    assert check_espresso_machine([[97.0, 98.0, 99.0]]) == "SHUTDOWN"


def test_machine_single_overheat_then_cooldown_resets_streak():
    assert check_espresso_machine([[97.0, 90.0, 97.0]]) == "OPTIMAL"


def test_machine_streak_resets_between_cycles():
    assert check_espresso_machine([[97.0], [97.0]]) == "OPTIMAL"


def test_machine_empty_cycle_is_optimal():
    assert check_espresso_machine([[]]) == "OPTIMAL"


def test_machine_shutdown_in_later_cycle():
    assert check_espresso_machine([[90.0, 91.0], [97.0, 99.0]]) == "SHUTDOWN"
