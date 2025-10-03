import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import google.generativeai as genai
import os  # used for fetching the API key
from dotenv import load_dotenv


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
# Load transactions and metrics
# ----------------------------
df = pd.read_sql("""
    SELECT t.date, t.total_price, t.location, t.weather, t.promotion_applied,
           p.product_name, s.store_name
    FROM transactions t
    JOIN products p ON t.product_name = p.product_name
    JOIN stores s ON t.location = s.store_name;
""", engine)

df['date'] = pd.to_datetime(df['date'])

# Sidebar filters
st.title("Filters")
stores = ["All"] + sorted(df["store_name"].unique())
products = ["All"] + sorted(df["product_name"].unique())

selected_store = st.selectbox("Select Store", stores)
selected_product = st.selectbox("Select Product", products)
date_range = st.date_input("Select Date Range", [df["date"].min(), df["date"].max()])

# Apply filters
filtered_df = df.copy()
if selected_store != "All":
    filtered_df = filtered_df[filtered_df["store_name"] == selected_store]
if selected_product != "All":
    filtered_df = filtered_df[filtered_df["product_name"] == selected_product]

filtered_df = filtered_df[
    (filtered_df["date"] >= pd.to_datetime(date_range[0])) &
    (filtered_df["date"] <= pd.to_datetime(date_range[1]))
    ]

# ----------------------------
# Summarize metrics
# ----------------------------
st.title("🤖 AI Recommendations Dashboard")

if filtered_df.empty:
    st.warning("No data for selected filters.")
    st.stop()

summary_text = f"""
Company Situation Summary:

- Selected Store: {selected_store}
- Selected Product: {selected_product}
- Date Range: {date_range[0]} to {date_range[1]}
- Total Revenue: {filtered_df['total_price'].sum():,.0f} GEL
- Average Daily Revenue: {filtered_df.groupby('date')['total_price'].sum().mean():,.0f} GEL
- Promotions Applied: {filtered_df['promotion_applied'].unique().tolist()}
- Weather Factors: {filtered_df['weather'].unique().tolist()}
- Number of Transactions: {len(filtered_df)}
"""

st.subheader("📋 Situation Summary")
st.text(summary_text)

# ----------------------------
# LLM Recommendation
# ----------------------------
st.subheader("💡 AI Recommendations")

# Configure the Gemini API key
# It's recommended to set this as a Streamlit secret
# like st.secrets["GEMINI_API_KEY"]
# or as an environment variable
genai.configure(api_key=GEMINI_API_KEY)

if st.button("Generate Recommendations"):
    with st.spinner("Generating suggestions..."):
        prompt = f"""
You are a retail strategy assistant. Based on the company situation below, suggest actionable recommendations for:
- Promotions / discounts
- Product focus
- Store strategy
- Revenue improvement

Company situation:
{summary_text}

Give 5 concise, numbered recommendations.
"""
        try:
            # Select the Gemini model
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Generate content from the model
            response = model.generate_content(prompt)

            # Display the generated text
            st.write(response.text)

        except Exception as e:
            st.error(f"Error generating recommendations: {e}")