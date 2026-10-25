import yaml
import pandas as pd

#1. Load books
def load_books(store):
    with open (f"{store}/books.yaml", "r", encoding="utf-8") as file:
        books = yaml.safe_load(file)

    books_df = pd.DataFrame(books)
    books_df.columns = books_df.columns.str.lstrip(":")

    return books_df

#2. Load orders
def load_orders(store):
    orders = pd.read_parquet(f"{store}/orders.parquet")
    return orders

#3. Normalize authors
def normalize_authors(authors):
    splitted = authors.split(",")

    cleaned_authors = []

    for author in splitted:
        cleaned_authors.append(author.strip())

    sorted_authors = sorted(cleaned_authors)

    return tuple(sorted_authors)

#4. merge_books_orders
def merge_books_orders(orders, books_df):
    orders_with_books = orders.merge(
        books_df[["id", "title", "author_set"]],
        left_on="book_id",
        right_on="id",
        how="left",
        validate="many_to_one"
    )

    return orders_with_books


#5. Clculate 5 top authors and individual authors
def calculate_authors_metrics(orders_with_books):
    popular_authors = (
        orders_with_books.groupby("author_set")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    authors_exploded = orders_with_books.explode("author_set")

    individual_authors = (
        authors_exploded.groupby("author_set")["quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    return popular_authors, individual_authors

#6.Process Store
def process_store(store):
    books_df = load_books(store)
    orders = load_orders(store)

    books_df["author_set"] = books_df["author"].apply(normalize_authors)

    orders_with_books = merge_books_orders(orders, books_df)

    popular_authors, individual_authors = calculate_authors_metrics(orders_with_books)

    return books_df, orders, orders_with_books, popular_authors, individual_authors


if __name__ == "__main__":
    stores = ["STORE1", "STORE2", "STORE3", "STORE4", "STORE5"]
    for store in stores:
        books_test, orders_test, joined_test, popular_test, individual_test = process_store(store)

        print("Store:", store)
        print("Unique Author Sets:", books_test["author_set"].nunique())

        print("Orders before JOIN:", len(orders_test))
        print("Orders after JOIN:", len(joined_test))
        print("Missing authors:", joined_test["author_set"].isna().sum())

        print("Top 5 Author Sets:")
        print(popular_test)

        print("Top 5 Individual Authors:")
        print(individual_test)

        print("------------------------")
