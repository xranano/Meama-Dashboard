# Meama Analytics & AI Dashboard

A comprehensive retail analytics and AI dashboard built with **Streamlit** to monitor sales, footfall, inventory, promotions, and staffing. The dashboard provides actionable insights for retail strategy, simulations of revenue under promotions, ARIMA-based forecasts, and AI-generated recommendations.

## Features

- **KPIs & Visualizations**
  - Total sales, units sold, visitors, conversion rate
  - Interactive charts for revenue, sales by product, revenue vs footfall, and footfall analytics

- **Revenue Simulation**
  - Model revenue impact of promotions, discounts, seasonality, and external factors
  - Customize simulations for selected stores, products, and time horizons
  - Download simulation reports as CSV

- **Forecasting**
  - ARIMA-based revenue predictions
  - Daily revenue aggregation and forecasts for selected stores/products
  - Option to download forecasted data

- **AI Recommendations**
  - Generates actionable recommendations for promotions, product focus, and store strategies
  - Uses Google Gemini API for natural language suggestions

- **Data Integration**
  - Connects to PostgreSQL database with transactions, products, stores, footfall, inventory, and staffing data
  - Uses SQLAlchemy for efficient data loading

## Technologies

- Python
- Streamlit
- PostgreSQL
- SQLAlchemy
- Plotly
- Pandas, NumPy
- ARIMA (statsmodels)
- Google Gemini API (LLM for AI recommendations)

## Installation

1. Clone the repository

2. Install dependencies:
pip install -r requirements.txt


3. Set up database connection in the code:
- DB_USER = "your_user"
- DB_PASS = "your_password"
- DB_HOST = "localhost"
- DB_NAME = "Meama"


5. (Optional) Set Google Gemini API key as environment variable:
export GEMINI_API_KEY="your_api_key"


## Usage
Run the Streamlit app:
streamlit run meama_dashboard.py

Use the sidebar filters to select stores, products, and date ranges
Explore interactive KPIs, visualizations, and forecast tabs
Simulate revenue under promotions and external factors
Generate AI-driven recommendations
