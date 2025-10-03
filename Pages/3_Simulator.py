import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
st.title("🧪 Promotion & Discount Simulator")

# ----------------------------
# Inputs
# ----------------------------
load_dotenv()  # load variables from .env

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

@st.cache_data
def load_stores():
    query = """
    SELECT DISTINCT s.store_name
    FROM stores s
    ORDER BY s.store_name;
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_products():
    query = """
    SELECT DISTINCT i.product_name
    FROM inventory i
    ORDER BY i.product_name;
    """
    return pd.read_sql(query, engine)

# ----------------------------
# Use them in Streamlit
# ----------------------------
stores_df = load_stores()
products_df = load_products()

# Convert DataFrames to list for multiple selection
stores = stores_df["store_name"].tolist()
products = products_df["product_name"].tolist()



selected_stores = st.multiselect("Select Stores", stores, default=stores[:1])
selected_products = st.multiselect("Select Products", products, default=products[:1])

# Horizonს
n_days = st.slider("Simulation Horizon (days)", min_value=7, max_value=90, value=30, step=1)

# External factors
external_factor = st.selectbox("External Factor", ["None", "Holiday/Event", "Bad Weather"])

# Advanced: seasonality, randomness
randomness = st.checkbox("Add Random Noise", value=True)
seasonality = st.selectbox("Seasonality", ["None", "Weekly", "Monthly"])

# ----------------------------
# Dynamic Promotions
# ----------------------------
if "promotions" not in st.session_state:
    st.session_state.promotions = []  # store all promotions

def add_promotion():
    st.session_state.promotions.append({
        "promo_type": "None",
        "discount": 10,
        "price_elasticity": -1.2
    })

st.button("➕ Add Promotion", on_click=add_promotion)

# Render each promotion block
for i, promo in enumerate(st.session_state.promotions):
    st.markdown(f"### Promotion {i+1}")
    st.session_state.promotions[i]["promo_type"] = st.selectbox(
        f"Promotion Type (#{i+1})", ["None", "Flat Discount", "Bundle Offer", "Buy X Get Y"],
        key=f"promo_type_{i}"
    )
    st.session_state.promotions[i]["discount"] = st.slider(
        f"Discount % (#{i+1})", min_value=0, max_value=50, value=promo["discount"], step=5,
        key=f"discount_{i}"
    )
    st.session_state.promotions[i]["price_elasticity"] = st.slider(
        f"Price Elasticity (#{i+1})", -3.0, 0.0, promo["price_elasticity"], step=0.1,
        key=f"elasticity_{i}"
    )

# ----------------------------
# Fake baseline revenue (demo)
# ----------------------------
dates = pd.date_range(start=pd.Timestamp.today(), periods=n_days)
baseline_revenue = 1000 + 50*np.sin(np.linspace(0, 3.14*2, n_days))  # base seasonal trend

# Seasonality
if seasonality == "Weekly":
    weekly_effect = np.tile([0.9, 1.0, 1.1, 1.2, 1.1, 0.95, 0.8], n_days // 7 + 1)[:n_days]
    baseline_revenue *= weekly_effect
elif seasonality == "Monthly":
    monthly_effect = 1 + 0.2*np.sin(np.linspace(0, 3.14*2, n_days))
    baseline_revenue *= monthly_effect

# ----------------------------
# Apply promotions
# ----------------------------
simulated_revenue = baseline_revenue.copy()

for promo in st.session_state.promotions:
    promo_multiplier = 1.0
    if promo["promo_type"] == "Flat Discount":
        demand_increase = (promo["discount"] / 100) * abs(promo["price_elasticity"])
        promo_multiplier += demand_increase
        simulated_revenue *= (1 - promo["discount"]/100)  # reduce unit price
    elif promo["promo_type"] == "Bundle Offer":
        promo_multiplier *= 1.2
    elif promo["promo_type"] == "Buy X Get Y":
        promo_multiplier *= 1.15

    simulated_revenue *= promo_multiplier

# External factors
if external_factor == "Holiday/Event":
    simulated_revenue *= 1.3
elif external_factor == "Bad Weather":
    simulated_revenue *= 0.8

# Add randomness
if randomness:
    noise = np.random.normal(1.0, 0.05, n_days)  # 5% noise
    simulated_revenue *= noise

# ----------------------------
# Results DF
# ----------------------------
simulated_df = pd.DataFrame({
    "date": dates,
    "baseline_revenue": baseline_revenue,
    "simulated_revenue": simulated_revenue
})

# ----------------------------
# Plot
# ----------------------------
fig = px.line(simulated_df, x="date", y=["baseline_revenue", "simulated_revenue"],
              labels={"value": "Revenue"},
              title=f"Revenue Simulation ({', '.join(selected_stores)} | {', '.join(selected_products)})")
st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# Summary Metrics
# ----------------------------
baseline_total = simulated_df["baseline_revenue"].sum()
sim_total = simulated_df["simulated_revenue"].sum()

st.metric("Baseline Revenue (Total)", f"{baseline_total:,.0f} GEL")
st.metric("Simulated Revenue (Total)", f"{sim_total:,.0f} GEL", delta=f"{(sim_total-baseline_total)/baseline_total*100:.1f}%")

# ----------------------------
# Download Report
# ----------------------------
csv = simulated_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Simulation Report (CSV)",
    data=csv,
    file_name="simulation_report.csv",
    mime="text/csv",
)

