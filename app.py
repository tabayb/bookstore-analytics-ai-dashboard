import streamlit as st
import pandas as pd

from explore_data import process_store as process_revenue
from explore_users import process_store as process_users
from explore_books import process_store as process_books

from google import genai
from ai_tools import answer_with_tools

from datetime import date
from pydantic import BaseModel
from google.genai import types

@st.cache_data(show_spinner="Loading store data...")
def load_dashboard_data(store):
    revenue_data = process_revenue(store)
    users_data = process_users(store)
    books_data = process_books(store)

    return revenue_data, users_data, books_data

class AIDateRange(BaseModel):
    start_date: str | None
    end_date: str | None

#1.Page Configuration
st.set_page_config(
    page_title="Book Stores Dashboard",
    layout="wide"
)

st.title("Book Stores Analytics")

# AI-controlled dashboard filters
if "ai_date_from" not in st.session_state:
    st.session_state.ai_date_from = None

if "ai_date_to" not in st.session_state:
    st.session_state.ai_date_to = None


#2.Store Selection and Data Loading

stores = ["STORE1", "STORE2", "STORE3", "STORE4", "STORE5"]

selected_store = st.selectbox("Choose a store:", stores)


revenue_data, users_data, books_data = load_dashboard_data(selected_store)

orders, daily_revenue, top_5_days = revenue_data

users, user_orders, orders_with_users, top_buyers = users_data

books, book_orders, orders_with_books, popular_authors, individual_authors = books_data

#3.KPI metrics

total_orders = len(orders)
total_revenue = orders["paid_price"].sum()
unique_buyers = orders_with_users["real_users_id"].nunique()
real_unique_users = users["real_users_id"].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Orders", f"{total_orders:,}")

with col2:
    st.metric("Total Revenue (USD)", f"${total_revenue:,.2f}")

with col3:
    st.metric("Unique Buyers", f"{unique_buyers:,}")

with col4:
    st.metric("Real Unique Users", f"{real_unique_users:,}")

#4. Dashboard Tabs

tab_revenue, tab_customers, tab_books = st.tabs(["Revenue", "Customers", "Books"])

#5. Revenue Analytics

with tab_revenue:
    #5.1 Top 5 Revenue Days
    st.subheader("Top 5 Days by Revenue")

    top_days_df = top_5_days.reset_index()
    top_days_df.columns = ["Date", "Revenue (USD)"]

    # Format dates as YYYY-MM-DD
    top_days_df["Date"] = pd.to_datetime(top_days_df["Date"]).dt.strftime("%Y-%m-%d")

     # Format revenue
    top_days_df["Revenue (USD)"] = (top_days_df["Revenue (USD)"].astype(float).round(2))

    st.dataframe(top_days_df, hide_index=True, width="stretch")

    #5.2 Daily Revenue
    st.subheader("Daily Revenue Trend")

    chart_df = daily_revenue.sort_index().reset_index()
    chart_df.columns = ["Date", "Revenue (USD)"]

    chart_df["Date"] = pd.to_datetime(chart_df["Date"])
    chart_df["Revenue (USD)"] = chart_df["Revenue (USD)"].astype(float)

    # Apply AI date filters
    if st.session_state.ai_date_from is not None:
        chart_df = chart_df[
            chart_df["Date"] >= pd.to_datetime(st.session_state.ai_date_from)
        ]

    if st.session_state.ai_date_to is not None:
        chart_df = chart_df[
            chart_df["Date"] <= pd.to_datetime(st.session_state.ai_date_to)
        ]

    # Display filtered chart
    if not chart_df.empty:
        st.line_chart(
            chart_df,
            x="Date",
            y="Revenue (USD)"
        )
    else:
        st.warning("No revenue data for the selected period.")

#6. Customer Analytics

with tab_customers:

    #6.1 Best Buyer
    st.subheader("Best Buyer")

    best_buyer_id = top_buyers.index[0]
    best_buyer_total = top_buyers.iloc[0]

    best_buyer_records = users[users["real_users_id"] == best_buyer_id]

    st.metric("Best Buyer Total (USD)", f"${best_buyer_total:,.2f}")

    st.write("Name:", ", ".join(best_buyer_records["name"].dropna().unique()))

    associated_ids = best_buyer_records["id"].astype(int).tolist()

    st.write("Associated User IDs:")

    st.json(associated_ids)

    st.write("Linked Accounts:", len(associated_ids))

    #6.2 Top 5 Buyers

    st.subheader("Top 5 Buyers")

    top_buyers_df = top_buyers.reset_index()

    top_buyers_df.columns = ["Real User ID", "Total Spent (USD)"]

    st.dataframe(top_buyers_df, hide_index=True, use_container_width=True)

# 7. Books Analytics

with tab_books:

    # 7.1 Unique Author Sets
    unique_author_sets = books["author_set"].nunique()

    st.metric(
        "Unique Sets of Authors",
        unique_author_sets
    )

    # 7.2 Top 5 Author Sets
    st.subheader("Top 5 Author Sets")

    authors_df = popular_authors.reset_index()

    authors_df.columns = ["Author Set", "Books Sold"]

    authors_df["Author Set"] = authors_df["Author Set"].apply(lambda authors: ", ".join(authors))

    st.dataframe(authors_df, hide_index=True, width="stretch")

    #7.3 Most Popular Author(s)

    st.subheader("Most Popular Author(s)")

    max_books_sold = individual_authors.max()

    most_popular_authors = individual_authors[individual_authors == max_books_sold].index.tolist()

    st.write(", ".join(map(str, most_popular_authors)))

    st.metric("Books Sold", int(max_books_sold))

    # 7.4 Top 5 Individual Authors
    st.subheader("Top 5 Individual Authors")

    individual_df = individual_authors.reset_index()
    individual_df.columns = ["Author", "Books Sold"]

    st.dataframe(individual_df, hide_index=True, width="stretch")


# 8. AI ASSISTANT — Chat Interface


# 8. AI ASSISTANT

st.divider()
st.subheader("AI Data Assistant")

# Initialize chat history
if st.session_state.get("chat_store") != selected_store:
    st.session_state.chat_store = selected_store
    st.session_state.chat_history = []

# Clear chat history
if st.button("🗑️ Clear Chat", key="clear_ai_chat"):
    st.session_state.chat_history = []
    st.rerun()

# Scrollable chat window
chat_box = st.container(height=450, border=True)

# Display previous messages
with chat_box:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Input remains below the chat window
with st.container():
    question = st.chat_input(
        "Ask a question about the selected store...",
        key="analytics_chat"
    )

if question:

    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })

    with chat_box:

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            try:
                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                with st.spinner("Gemini is analyzing data..."):
                    answer = answer_with_tools(
                        client=client,
                        model="gemini-3.5-flash-lite",
                        question=question,
                        store=selected_store,
                        orders=orders,
                        books=books,
                        orders_with_books=orders_with_books,
                        users=users,
                        top_buyers=top_buyers,
                        top_5_days=top_5_days,
                        popular_authors=popular_authors,
                        individual_authors=individual_authors
                    )

                st.markdown(answer)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:
                st.error(f"Gemini API error: {error}")

# 9. AI DASHBOARD FILTERS


# 9. AI DASHBOARD FILTERS

st.divider()
st.subheader("AI Dashboard Filters")

# Initialize filter chat history
if "filter_chat_history" not in st.session_state:
    st.session_state.filter_chat_history = []

# Scrollable chat window
filter_box = st.container(height=300, border=True)

# Display previous commands and responses
with filter_box:
    for message in st.session_state.filter_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Filter chat input
with st.container():
    filter_command = st.chat_input(
        "e.g. Show revenue for March 2026",
        key="dashboard_filter_chat"
    )

if filter_command:

    st.session_state.filter_chat_history.append({
        "role": "user",
        "content": filter_command
    })

    try:
        client = genai.Client(
            api_key=st.secrets["GEMINI_API_KEY"]
        )

        with st.spinner("Gemini is selecting the period..."):

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=f"""
                Extract a date range from this dashboard command.

                Rules:
                - Return dates in YYYY-MM-DD format.
                - For a month, use its first and last calendar day.
                - Both dates are inclusive.
                - If the period is unclear, return null values.
                - Do not invent dates.

                Command: {filter_command}
                """,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIDateRange,
                    temperature=0
                )
            )

        result = AIDateRange.model_validate_json(response.text)

        if not result.start_date or not result.end_date:
            confirmation = (
                "I couldn't identify a date range. "
                "Please specify a month or start and end dates."
            )

        else:
            start = date.fromisoformat(result.start_date)
            end = date.fromisoformat(result.end_date)

            if start > end:
                confirmation = "Invalid date range: start is after end."

            else:
                st.session_state.ai_date_from = start.isoformat()
                st.session_state.ai_date_to = end.isoformat()

                confirmation = (
                    f"Date filter applied: "
                    f"**{start.isoformat()} → {end.isoformat()}**\n\n"
                    "Open the Revenue tab to see the filtered chart."
                )

    except Exception as error:
        confirmation = f"Could not apply filter: {error}"

    # Save AI response
    st.session_state.filter_chat_history.append({
        "role": "assistant",
        "content": confirmation
    })

    # Refresh chart and chat history
    st.rerun()
