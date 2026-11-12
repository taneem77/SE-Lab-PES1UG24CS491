import math
from hypothesis import given, strategies as st
from processor import lookup_drink_code, calculate_average_shot_cost, parse_order_modifiers


@given(st.text() | st.none())
def test_lookup_drink_code_no_crash(s):
    try:
        result = lookup_drink_code(s)
    except Exception as e:
        assert False, f"lookup_drink_code crashed with: {type(e).__name__}: {e}"
    assert result is None or isinstance(result, float)


@given(st.text() | st.none())
def test_calculate_average_shot_cost_safe(s):
    try:
        result = calculate_average_shot_cost(s)
    except Exception as e:
        assert False, f"calculate_average_shot_cost crashed with: {type(e).__name__}: {e}"
    assert result is None or (isinstance(result, float) and math.isfinite(result) and result >= 0)


@given(st.text() | st.none())
def test_parse_order_modifiers_safe(s):
    try:
        result = parse_order_modifiers(s)
    except Exception as e:
        assert False, f"parse_order_modifiers crashed with: {type(e).__name__}: {e}"
    assert isinstance(result, dict)