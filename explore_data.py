import pandas as pd
import re
from decimal import Decimal, ROUND_HALF_UP
from dateutil import parser
from datetime import date

#1.Load orders:
def load_orders(store):
    orders = pd.read_parquet(f"{store}/orders.parquet")
    return orders

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

def clean_timestamp(timestamp):
    normalized = timestamp.replace(",", " ")
    normalized = normalized.replace(";", " ")
    normalized = normalized.replace("A.M.", "AM")
    normalized = normalized.replace("P.M.", "PM")

    is_european = bool(re.search(r"\b\d{1,2}\.\d{1,2}\.\d{4}\b", normalized))
    parsed = parser.parse(normalized, dayfirst=is_european)

    return parsed

def calculate_daily_revenue(orders):
    daily_revenue = orders.groupby("date")["paid_price"].sum()

    top_5_days = daily_revenue.sort_values(ascending=False).head(5)

    return daily_revenue, top_5_days

def process_store(store):
    orders = load_orders(store)

    orders["unit_price_usd"] = orders["unit_price"].apply(clean_price)
    orders["paid_price"] = orders["quantity"] * orders["unit_price_usd"]
    orders["parsed_timestamp"] = orders["timestamp"].apply(clean_timestamp)
    orders["date"] = orders["parsed_timestamp"].apply(lambda ts: ts.date())

    daily_revenue, top_5_days = calculate_daily_revenue(orders)

    return orders, daily_revenue, top_5_days

if __name__ == "__main__":
    stores = ["STORE1", "STORE2", "STORE3", "STORE4", "STORE5"]

    for store in stores:
        orders_test, daily_test, top_test = process_store(store)

        future_orders = orders_test[orders_test["date"] > date.today()]

        print("Store:", store)
        print("Total Orders:", len(orders_test))
        print("Future Orders:", len(future_orders))
        print("Top 5 Days:")
        print(top_test)

        print("Min Date:", orders_test["date"].min())
        print("Max Date:", orders_test["date"].max())

        print("Last 7 Dates Revenue:")
        print(daily_test.sort_index().tail(7))

        print("------------------------")
