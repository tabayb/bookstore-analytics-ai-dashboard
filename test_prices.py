import re
from decimal import Decimal, ROUND_HALF_UP

def clean_price(price):
    numbers = re.findall(r"\d+(?:\.\d+)?", price)
    if len(numbers) ==   1:
        amount = Decimal(numbers[0])

    elif len(numbers) == 2:
        amount = Decimal(numbers[0]) + Decimal(numbers[1]) / Decimal("100")

    else:
        raise ValueError(f"Invalid Price: {price}")

    if "€" in price or "EUR" in price:
        amount = amount * Decimal("1.2")
        amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return amount

print(clean_price("$42¢25"))
print(clean_price("USD 22.75"))
print(clean_price("29€50¢"))
print(clean_price("€5.99"))