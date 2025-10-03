import pandas as pd
import random
from datetime import datetime, timedelta

# ---------------------------
# CONFIG
# ---------------------------
locations = [
    "Meama Space • Tbilisi Mall", "Meama Space • City Mall", "Meama Space • East Point",
    "Meama Collect • Gori", "Meama Collect • Beliashvili", "Meama Collect • Abashidze",
    "Meama Collect • Rustavi", "Meama Collect • Sheni Saxli Jiqia", "Meama Collect • Paliashvili Street",
    "Meama Collect • Abashidze Street", "Meama Collect • Kartozia Street", "Meama Collect • Bukia Garden",
    "Meama Collect • Batumi", "Meama Collect • Digomi", "Meama Collect • Lisi",
    "Meama Collect • Turtle Lake", "Meama Collect • Dedaena"
]

products = [
    "versatile", "multicapsule", "espresso machine", "cappuccino", "Hazelnut", "Brazil", "Caramel",
    "Hazelnut Chocolate", "Guatemala 07", "vanilla", "Ethiopia", "Macapuno Coconut",
    "Mountain Raspberry", "El Salvador 04", "Decaf", "Bulldog", "Colombia 03"
]

# Generate date range from 2023-01-01 to today
start_date = datetime(2023, 1, 1)
end_date = datetime.today()
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# ---------------------------
# FOOTFALL DATA
# ---------------------------
footfall_data = []
for date in date_range:
    for loc in locations:
        footfall_data.append({
            "date": date.date(),
            "location": loc,
            "customer_count": random.randint(50, 500)
        })

df_footfall = pd.DataFrame(footfall_data)
df_footfall.to_csv("footfall.csv", index=False)
print("Footfall data generated:", len(df_footfall), "rows")

# ---------------------------
# WEATHER DATA
# ---------------------------
weather_data = []
for date in date_range:
    for loc in locations:
        weather_data.append({
            "date": date.date(),
            "location": loc,
            "temperature": round(random.uniform(-5, 35), 1),  # Celsius
            "precipitation": round(random.uniform(0, 20), 1), # mm
            "holiday": random.choice([True, False])
        })

df_weather = pd.DataFrame(weather_data)
df_weather.to_csv("weather.csv", index=False)
print("Weather data generated:", len(df_weather), "rows")

# ---------------------------
# INVENTORY DATA
# ---------------------------
inventory_data = []
for date in date_range:
    for loc in locations:
        for prod in products:
            inventory_data.append({
                "date": date.date(),
                "location": loc,
                "product_name": prod,
                "stock_level": random.randint(20, 200)
            })

df_inventory = pd.DataFrame(inventory_data)
df_inventory.to_csv("inventory.csv", index=False)
print("Inventory data generated:", len(df_inventory), "rows")

# ---------------------------
# STAFFING DATA
# ---------------------------
shifts = ["Morning", "Afternoon", "Evening"]
staffing_data = []
for date in date_range:
    for loc in locations:
        for shift in shifts:
            staffing_data.append({
                "date": date.date(),
                "location": loc,
                "shift": shift,
                "staff_count": random.randint(2, 10)
            })

df_staffing = pd.DataFrame(staffing_data)
df_staffing.to_csv("staffing.csv", index=False)
print("Staffing data generated:", len(df_staffing), "rows")
