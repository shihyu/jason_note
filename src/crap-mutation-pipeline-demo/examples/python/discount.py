def calculate_discount(price: float, is_member: bool) -> float:
    if price < 0:
        raise ValueError("price must not be negative")
    if is_member:
        return price * 0.8
    return price
