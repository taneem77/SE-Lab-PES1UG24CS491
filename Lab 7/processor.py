import math

MENU_PRICES = {
    "LAT": 4.50,
    "CAP": 4.00,
    "ESP": 3.00,
    "AME": 3.50,
    "MOC": 5.00,   # fixed: was "MOc" (lowercase c) so it could never match .upper()
}


def lookup_drink_code(code_string):
    """Return price for a drink code prefix, or None if input is invalid/unknown."""
    if not isinstance(code_string, str):      # None, int, etc.
        return None
    code_prefix = code_string.strip().upper()[:3]
    return MENU_PRICES.get(code_prefix)       # no KeyError on unknown/empty


def calculate_average_shot_cost(pricing_csv):
    """Return average of comma-separated prices, or None if input is invalid."""
    if not isinstance(pricing_csv, str):
        return None
    prices = []
    for p in pricing_csv.split(','):
        p = p.strip()
        if not p:                             # skip empty elements like "1,,3"
            continue
        try:
            value = float(p)
        except ValueError:
            return None                       # non-numeric -> invalid
        if not math.isfinite(value) or value < 0:   # nan, inf, negatives
            return None
        prices.append(value)
    if not prices:                            # avoids ZeroDivisionError
        return None
    avg = sum(prices) / len(prices)
    return avg if math.isfinite(avg) else None


def parse_order_modifiers(order_spec):
    """Parse 'key:value;key:value' into a dict. Malformed pairs are skipped."""
    modifier_dict = {}
    if not isinstance(order_spec, str):
        return modifier_dict
    for item in order_spec.split(';'):
        if ':' not in item:                   # no colon -> skip
            continue
        key, value = item.split(':', 1)       # maxsplit=1 handles "a:b:c"
        key, value = key.strip(), value.strip()
        if key:                               # skip empty keys
            modifier_dict[key] = value
    return modifier_dict


def main():
    print("==== Running lookup_drink_code ====")
    drink_input = input("Enter drink code prefix (e.g. LAT, CAP, ESP): ")
    price = lookup_drink_code(drink_input)
    print("Base Price: $", price if price is not None else "Invalid drink code")

    print("\n==== Running calculate_average_shot_cost ====")
    shots_input = input("Enter CSV of shot prices (e.g. 1.0, 1.5, 2.0): ")
    avg_price = calculate_average_shot_cost(shots_input)
    print("Average Shot Price: $", avg_price if avg_price is not None else "Invalid input")

    print("\n==== Running parse_order_modifiers ====")
    spec_input = input("Enter modifiers (e.g. milk:oat;syrup:vanilla): ")
    mods = parse_order_modifiers(spec_input)
    print("Parsed Modifiers:", mods)


if __name__ == "__main__":
    main()