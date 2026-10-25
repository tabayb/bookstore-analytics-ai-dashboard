
from datetime import date
from google.genai import types


def answer_with_tools(
    client, model, question, store,
    orders, books, orders_with_books,
    users, top_buyers, top_5_days,
    popular_authors, individual_authors
):

    # 1. Most expensive sold book
    def get_most_expensive_book() -> dict:
        """Find the book with the highest actual unit selling price in USD."""

        if orders.empty:
            return {"error": "No orders found"}

        row = orders.loc[
            orders["unit_price_usd"].astype(float).idxmax()
        ]

        matching_books = books[
            books["id"] == row["book_id"]
        ]

        if matching_books.empty:
            return {"error": "Book not found"}

        return {
            "title": str(matching_books.iloc[0]["title"]),
            "unit_price_usd": str(row["unit_price_usd"])
        }

    # 2. Top selling books
    def get_top_books(limit: int = 5) -> dict:
        """Find the most sold book titles by total quantity."""

        if not 1 <= limit <= 10:
            return {"error": "Limit must be between 1 and 10"}

        ranking = (
            orders_with_books.groupby(["book_id", "title"])["quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(limit)
        )

        return {
            "books": [
                {"title": str(title), "quantity": int(quantity)}
                for (_, title), quantity in ranking.items()
            ]
        }

    # 3. Revenue for a date range
    def get_revenue_between(start_date: str, end_date: str) -> dict:
        """Calculate revenue and order count between two ISO dates YYYY-MM-DD."""

        try:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)
        except ValueError:
            return {"error": "Dates must use YYYY-MM-DD"}

        if start > end:
            return {"error": "Start date must not exceed end date"}

        filtered = orders[
            (orders["date"] >= start) &
            (orders["date"] <= end)
        ]

        return {
            "start_date": start_date,
            "end_date": end_date,
            "orders": int(len(filtered)),
            "revenue_usd": str(filtered["paid_price"].sum())
        }

    # 4. Best buyer
    def get_best_buyer() -> dict:
        """Find the highest spending buyer and associated user IDs."""

        if top_buyers.empty:
            return {"error": "No buyers found"}

        buyer_id = top_buyers.index[0]

        records = users[
            users["real_users_id"] == buyer_id
        ]

        return {
            "name": records["name"].dropna().unique().tolist(),
            "user_ids": records["id"].tolist(),
            "spent_usd": str(top_buyers.iloc[0])
        }

    # 5. Author rankings
    def get_top_authors(kind: str = "individual") -> dict:
        """Return top authors by quantity. Kind: individual or sets."""

        if kind == "individual":
            ranking = individual_authors
        elif kind == "sets":
            ranking = popular_authors
        else:
            return {"error": "Kind must be individual or sets"}

        return {
            "authors": [
                {
                    "author": ", ".join(name) if isinstance(name, tuple) else str(name),
                    "quantity": int(quantity)
                }
                for name, quantity in ranking.items()
            ]
        }

    # Small overview always available
    overview = {
        "store": store,
        "total_orders": len(orders),
        "total_revenue_usd": str(orders["paid_price"].sum()),
        "real_unique_users": int(users["real_users_id"].nunique()),
        "unique_buyers": int(users[
            users["real_users_id"].isin(orders["user_id"])
        ]["real_users_id"].nunique()) if False else None,
        "top_revenue_days": [
            {"date": str(day), "revenue_usd": str(amount)}
            for day, amount in top_5_days.items()
        ]
    }

    # Use the actual order-to-user mapping for unique buyers
    overview.pop("unique_buyers")

    response = client.models.generate_content(
        model=model,
        contents=(
            "You are a bookstore data analyst. "
            "Use only the supplied overview and available tools. "
            "Call a tool when additional information is required. "
            "Never invent data. "
            "Only analyze the selected store. "
            "Answer in the language of the user's question.\n\n"
            f"Store overview: {overview}\n"
            f"Question: {question}"
        ),
        config=types.GenerateContentConfig(
            temperature=0,
            tools=[
                get_most_expensive_book,
                get_top_books,
                get_revenue_between,
                get_best_buyer,
                get_top_authors
            ],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=5
            )
        )
    )

    return response.text or "No answer returned."
