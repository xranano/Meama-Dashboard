import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from dotenv import load_dotenv
import os
# ---------------------------
# DATABASE CONFIG
# ---------------------------
load_dotenv()  # load variables from .env

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

# ---------------------------
# LOAD DATA FUNCTIONS
# ---------------------------
@st.cache_data
def load_transactions():
    query = """
    SELECT t.transaction_id,
           t.datetime,
           t.date,
           s.store_name AS store,
           p.product_name AS product,
           p.category AS category,
           t.quantity AS units_sold,
           t.unit_price AS price,
           t.total_price AS revenue,
           t.payment_method,
           t.promotion_applied,
           t.weather,
           t.event_holiday
    FROM transactions t
    JOIN products p ON t.product_name = p.product_name
    JOIN stores s ON t.location = s.store_name
    ORDER BY t.date;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_footfall():
    query = """
    SELECT f.date,
           s.store_name AS store,
           f.customer_count AS visitors
    FROM footfall f
    JOIN stores s ON f.location = s.store_name
    ORDER BY f.date;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_inventory():
    query = """
    SELECT i.date,
           s.store_name AS store,
           i.product_name AS product,
           i.stock_level AS stock_level
    FROM inventory i
    JOIN stores s ON i.location = s.store_name
    ORDER BY i.date;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_staffing():
    query = """
    SELECT st.date,
           s.store_name AS store,
           st.shift,
           st.staff_count AS staff_count
    FROM staffing st
    JOIN stores s ON st.location = s.store_name
    ORDER BY st.date;
    """
    return pd.read_sql(query, engine)

# ---------------------------
# MAIN
# ---------------------------
st.set_page_config(page_title="Meama Analytics Dashboard", page_icon=":bar_chart:", layout="wide")
st.title("Meama Analytics Dashboard")

# Load data
df_sales = load_transactions()
df_footfall = load_footfall()
df_inventory = load_inventory()
df_staffing = load_staffing()

# Convert dates
for df in [df_sales, df_footfall, df_inventory, df_staffing]:
    df["date"] = pd.to_datetime(df["date"])

# ---------------------------
# FILTERS
# ---------------------------
date_range = st.date_input(
    "Select Date Range",
    value=(df_sales["date"].min(), df_sales["date"].max()),
    min_value=df_sales["date"].min(),
    max_value=df_sales["date"].max()
)

selected_store = st.selectbox("Select Store", ["All"] + df_sales["store"].unique().tolist())
selected_category = st.selectbox("Select Category", ["All"] + df_sales["category"].unique().tolist())

mask = (df_sales["date"] >= pd.to_datetime(date_range[0])) & (df_sales["date"] <= pd.to_datetime(date_range[1]))
if selected_store != "All":
    mask &= (df_sales["store"] == selected_store)
if selected_category != "All":
    mask &= (df_sales["category"] == selected_category)

df_filtered = df_sales.loc[mask]

# Footfall filtering
mask_footfall = (df_footfall["date"] >= pd.to_datetime(date_range[0])) & (df_footfall["date"] <= pd.to_datetime(date_range[1]))
if selected_store != "All":
    mask_footfall &= (df_footfall["store"] == selected_store)
df_footfall_filtered = df_footfall.loc[mask_footfall]

# ---------------------------
# KPIs
# ---------------------------
total_sales = df_filtered["revenue"].sum()
total_units = df_filtered["units_sold"].sum()
total_visitors = df_footfall_filtered["visitors"].sum()
conversion_rate = (total_units / total_visitors * 100) if total_visitors > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"{total_sales:,.2f} ₾")
col2.metric("Units Sold", total_units)
col3.metric("Visitors", total_visitors)
col4.metric("Conversion Rate", f"{conversion_rate:.2f}%")
st.markdown("---")

# ---------------------------
# TABS
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Sales Over Time",
    "🥤 Sales by Product",
    "🏬 Revenue vs Footfall",
    "🚶 Footfall Analytics"
])

# 1️⃣ Sales Over Time
with tab1:
    sales_time = df_filtered.groupby("date")["revenue"].sum().reset_index()
    fig = px.line(sales_time, x="date", y="revenue", title="Revenue Over Time", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# 2️⃣ Sales by Product
with tab2:
    sales_product = df_filtered.groupby("product")["units_sold"].sum().reset_index()
    fig = px.pie(sales_product, names="product", values="units_sold", title="Units Sold by Product")
    st.plotly_chart(fig, use_container_width=True)

# 3️⃣ Revenue vs Footfall
with tab3:
    merged = df_filtered.groupby("date")["revenue"].sum().reset_index().merge(
        df_footfall_filtered.groupby("date")["visitors"].sum().reset_index(),
        on="date",
        how="left"
    )
    fig = px.line(merged, x="date", y=["revenue", "visitors"], title="Revenue vs Footfall")
    st.plotly_chart(fig, use_container_width=True)

# 4️⃣ Footfall Analytics
with tab4:
    footfall_time = df_footfall_filtered.groupby("date")["visitors"].sum().reset_index()
    fig1 = px.line(footfall_time, x="date", y="visitors", title="Visitors Over Time", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    store_visitors = df_footfall_filtered.groupby("store")["visitors"].sum().reset_index()
    fig2 = px.bar(store_visitors, x="store", y="visitors", title="Visitors by Store", color="store")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# Top 5 Products by Revenue
# ---------------------------
top_products = df_filtered.groupby("product")["revenue"].sum().reset_index().sort_values(by="revenue", ascending=False).head(5)
fig_top = px.bar(top_products, x="product", y="revenue", title="Top 5 Products by Revenue", text_auto=True)
st.plotly_chart(fig_top, use_container_width=True)
st.dataframe(top_products)


# Sales grouped by weather
sales_weather = df_filtered.groupby("weather")["revenue"].sum().reset_index()
fig_weather = px.bar(
    sales_weather,
    x="weather",
    y="revenue",
    title="Revenue by Weather",
    color="weather",
    text_auto=True
)
st.plotly_chart(fig_weather, use_container_width=True)

merged_weather = df_filtered.groupby(["date", "weather"])["revenue"].sum().reset_index().merge(
    df_footfall_filtered.groupby("date")["visitors"].sum().reset_index(),
    on="date",
    how="left"
)


