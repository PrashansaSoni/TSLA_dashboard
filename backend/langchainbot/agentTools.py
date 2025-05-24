from langchain.tools import tool
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
import ast

df = pd.read_csv("TSLA_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

df["Support"] = df["Support"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
df["Resistance"] = df["Resistance"].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])
df["Bullish"] = (df["close"] > df["open"]).astype(int)

# Define tools
@tool
def count_bullish_days(year: int):
    """Count days where close > open for a given year."""
    filtered = df[df["timestamp"].dt.year == year]
    return filtered["Bullish"].sum()

# Should correct this import llm issuse, since it is used here
@tool
def search_context(query: str):
    """Use GroqAPI to retrieve relevant information based on a query."""
    prompt = ChatPromptTemplate([
        ("system", "you are a financial advisor who will answer the questions"),
        ("user", "this is the {query}")
    ])
    response = prompt | llm
    ai_response = response.invoke({"query": query}).content
    return ai_response

@tool
def max_closing_price(year: int) -> float:
    """Get the highest closing price in a given year."""
    filtered = df[df["timestamp"].dt.year == year]
    if filtered.empty:
        return float('nan')
    return filtered["close"].max()

@tool
def min_opening_price(year: int, month: int) -> float:
    """Get the lowest opening price in a given month and year."""
    filtered = df[(df["timestamp"].dt.year == year) & (df["timestamp"].dt.month == month)]
    if filtered.empty:
        return float('nan')
    return filtered["open"].min()

@tool
def average_closing_price(start_date: str, end_date: str) -> float:
    """Calculate the average closing price between two dates (format: YYYY-MM-DD)."""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    filtered = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]
    if filtered.empty:
        return float('nan')
    return filtered["close"].mean()

@tool
def total_volume(year: int) -> float:
    """Calculate the total trading volume for a given year."""
    filtered = df[df["timestamp"].dt.year == year]
    if filtered.empty:
        return 0.0
    return filtered["volume"].sum()

@tool
def percentage_change(start_date: str, end_date: str) -> float:
    """Calculate the percentage change in closing price between two dates (format: YYYY-MM-DD)."""
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    start_close = df[df["timestamp"] == start]["close"]
    end_close = df[df["timestamp"] == end]["close"]
    if start_close.empty or end_close.empty:
        return float('nan')
    return ((end_close.values[0] - start_close.values[0]) / start_close.values[0]) * 100

@tool
def top_volume_days(n: int, year: int) -> str:
    """Get the top N days with the highest trading volume in a given year."""
    filtered = df[df["timestamp"].dt.year == year]
    if filtered.empty:
        return "No data available for that year."
    top_days = filtered.nlargest(n, "volume")
    result = "\n".join([f"{row['timestamp'].date()}: {row['volume']}" for _, row in top_days.iterrows()])
    return result

# Define tools list
tools = [
    count_bullish_days,
    search_context,
    max_closing_price,
    min_opening_price,
    average_closing_price,
    total_volume,
    percentage_change,
    top_volume_days
]
