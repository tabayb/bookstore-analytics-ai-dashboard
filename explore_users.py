import pandas as pd
import re
from decimal import Decimal, ROUND_HALF_UP

#1.Load users
def load_users(store):
    users = pd.read_csv(f"{store}/users.csv")

    return users

#2.Getting Users Group
def get_user_groups(users):

    user_id_groups = users.groupby(["name", "phone", "email"], dropna=False)["id"].agg(list)
    phone_groups = users.groupby(["name", "address", "email"], dropna=False)["id"].agg(list)
    name_groups = users.groupby(["address", "phone", "email"], dropna=False)["id"].agg(list)
    email_groups = users.groupby(["name", "address", "phone"], dropna=False)["id"].agg(list)

    return user_id_groups, phone_groups, name_groups, email_groups

#3.Reconcile Users
def reconcile_users(users):
    user_id_groups, phone_groups, name_groups, email_groups = get_user_groups(users)

    parent = {}

    for user_id in users["id"]:
        parent[user_id] = user_id

    def find(user_id):
        while parent[user_id] != user_id:
            user_id = parent[user_id]
        return user_id

    def union(id1, id2):
        root1 = find(id1)
        root2 = find(id2)

        parent[root1] = root2

    for groups in [user_id_groups, phone_groups, name_groups, email_groups]:
        for ids in groups:
            first_id = ids[0]

            for user_id in ids[1:]:
                union(first_id, user_id)

    unique_roots = set()

    for user_id in users["id"]:
        unique_roots.add(find(user_id))

    users["real_users_id"] = users["id"].apply(find)

    return users

#4.Merge Users & Orders
def merge_users_orders(orders, users):
    orders_with_users = orders.merge(
        users[["id", "real_users_id"]],
        left_on="user_id",
        right_on="id",
        how="left",
        validate="many_to_one"
    )

    return orders_with_users

#5.Clean Prices
def clean_price(price):
    numbers = re.findall(r"\d+(?:\.\d+)?", price)

    if len(numbers) == 1:
        amount = Decimal(numbers[0])
    elif len(numbers) == 2:
        amount = Decimal(numbers[0]) + Decimal(numbers[1]) / Decimal("100")
    else:
        raise ValueError(f"Invalid Price: {price}")

    if "€" in price or "EUR" in price:
        amount = amount * Decimal("1.2")

    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return amount

#6.Calculate Best Buyers
def calculate_top_buyers(orders_with_users):
    buyers_totals = (
        orders_with_users.groupby("real_users_id")["paid_price"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    return buyers_totals

#7.Process Store
def process_store(store):
    users = load_users(store)
    users = reconcile_users(users)
    orders = pd.read_parquet(f"{store}/orders.parquet")
    orders_with_users = merge_users_orders(orders, users)
    orders_with_users["unit_price_usd"] = orders_with_users["unit_price"].apply(clean_price)
    orders_with_users["paid_price"] = orders_with_users["quantity"] * orders_with_users["unit_price_usd"]

    buyers_totals = calculate_top_buyers(orders_with_users)

    return users, orders, orders_with_users, buyers_totals

if __name__ == "__main__":
    stores = ["STORE1", "STORE2", "STORE3", "STORE4", "STORE5"]

    for store in stores:
        users_test, orders_test, joined_test, buyers_test = process_store(store)

        print("Store:", store)
        print("Total Users:", len(users_test))
        print("Real Unique Users:", users_test["real_users_id"].nunique())
        print("Orders:", len(orders_test))
        print("Missing Users:", joined_test["real_users_id"].isna().sum())
        print("Top 5 Buyers:")
        print(buyers_test)
        print("Unique Buyers:", joined_test["real_users_id"].nunique())
        print("------------------------")
