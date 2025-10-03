import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA
from dotenv import load_dotenv
import os

# ----------------------------
# Database connection
# ----------------------------
load_dotenv()  # load variables from .env

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

# ----------------------------
# Load transactions with products & stores
# ----------------------------
df = pd.read_sql("""    SELECT t.date, t.total_price, t.location, t.weather, t.promotion_applied,
           p.product_name, s.store_name
    FROM transactions t
    JOIN products p ON t.product_name = p.product_name
    JOIN stores s ON t.location = s.store_name;
""", engine)

df['date'] = pd.to_datetime(df['date'])

footfall = pd.read_sql("SELECT date, location, customer_count FROM footfall;", engine)
footfall['date'] = pd.to_datetime(footfall['date'])
daily_footfall = footfall.copy()

# ----------------------------
# Streamlit UI: Filters
# ----------------------------
st.title("📈 Predictions Dashboard")

# Store filter
stores = ["All"] + sorted(df["store_name"].dropna().unique().tolist())
selected_store = st.selectbox("Select Store", stores)

# Product filter
products = ["All"] + sorted(df["product_name"].dropna().unique().tolist())
selected_product = st.selectbox("Select Product", products)

# Forecast horizon input
n_days = st.slider("Forecast Days", min_value=7, max_value=60, value=14, step=1)

# ----------------------------
# Apply filters
# ----------------------------
filtered_df = df.copy()
if selected_store != "All":
    filtered_df = filtered_df[filtered_df["store_name"] == selected_store]
if selected_product != "All":
    filtered_df = filtered_df[filtered_df["product_name"] == selected_product]

# ----------------------------
# Aggregate daily revenue
# ----------------------------
daily_revenue = (
    filtered_df.groupby("date")["total_price"]
    .sum()
    .reset_index()
    .rename(columns={"total_price": "revenue"})
)

# Safety check
if daily_revenue.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ----------------------------
# Forecast with ARIMA
# ----------------------------
try:
    model = ARIMA(daily_revenue["revenue"], order=(5, 1, 0))
    model_fit = model.fit()

    # Forecast future
    forecast = model_fit.forecast(steps=n_days)
    forecast_dates = pd.date_range(start=daily_revenue["date"].max() + pd.Timedelta(days=1), periods=n_days)
    forecast_df = pd.DataFrame({"date": forecast_dates, "forecast_revenue": forecast})

    # ----------------------------
    # Plot
    # ----------------------------
    fig = px.line(daily_revenue, x="date", y="revenue", title="Revenue Forecast")
    fig.add_scatter(x=forecast_df["date"], y=forecast_df["forecast_revenue"], mode="lines", name="Forecast")

    st.plotly_chart(fig, use_container_width=True)

    # Show forecast table
    st.subheader("📊 Forecast Data")
    st.dataframe(forecast_df)

except Exception as e:
    st.error(f"Error fitting ARIMA model: {e}")


# ----------------------------
# Download Button
# ----------------------------
csv = forecast_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Forecast (CSV)",
    data=csv,
    file_name="forecast.csv",
    mime="text/csv",
)


# if not daily_footfall.empty and len(daily_footfall) > 30:  # need enough data
#     footfall_model = ARIMA(daily_footfall["customer_count"], order=(5,1,0))
#     footfall_fit = footfall_model.fit()
#     footfall_forecast = footfall_fit.forecast(steps=n_days)  # use slider
#     footfall_dates = pd.date_range(
#         start=daily_footfall["date"].max() + pd.Timedelta(days=1),
#         periods=n_days
#     )
#     footfall_forecast_df = pd.DataFrame({
#         "date": footfall_dates,
#         "forecast_footfall": footfall_forecast
#     })
#
#     # Plot footfall forecast
#     st.subheader("🚶 Footfall Forecast")
#     fig2 = px.line(daily_footfall, x="date", y="customer_count", title="Footfall Forecast")
#     fig2.add_scatter(x=footfall_forecast_df["date"], y=footfall_forecast_df["forecast_footfall"],
#                      mode="lines", name="Forecast")
#     st.plotly_chart(fig2, use_container_width=True)
#
#     # Download button
#     csv2 = footfall_forecast_df.to_csv(index=False).encode("utf-8")
#     st.download_button(
#         label="⬇️ Download Footfall Forecast (CSV)",
#         data=csv2,
#         file_name="footfall_forecast.csv",
#         mime="text/csv",
#     )
# else:
#     st.warning("Not enough footfall data for this store to forecast.")
