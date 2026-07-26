COUPONS = {"SAVE10": 0.10, "SAVE20": 0.20}


def calculate_total_cents(unit_price_cents: int, quantity: int, coupon: str | None) -> int:
    total = unit_price_cents * quantity
    discount = COUPONS.get(coupon, 0)
    return round(total * (1 - discount))