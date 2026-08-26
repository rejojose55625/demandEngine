
import pandas as pd
import numpy as np
from datetime import datetime
import os
import csv
from config import *
np.random.seed(42)

# -----------------------------------------------
# CONFIG
# -----------------------------------------------
today = datetime.today()
start_year = today.year - 10
start_date = f"{start_year}-01-01"
end_date = today.strftime("%Y-%m-%d")
dates = pd.date_range(start=start_date, end=end_date, freq='D')

output_dir = "data/generated"
os.makedirs(output_dir, exist_ok=True)

# -----------------------------------------------
# MASTER DATA
# -----------------------------------------------

regions_df = pd.DataFrame({
    "region_id": range(1, len(REGIONS)+1),
    "region": REGIONS
})
regions_df.to_csv(f"{output_dir}/regions.csv", index=False)

# -----------------------------------------------
# HOLIDAYS BY STATE
# -----------------------------------------------


# -----------------------------------------------
# H. FESTIVAL INTENSITY SCORE
# Maps holiday name → intensity score (1–10)
# Better for ML than a binary is_holiday flag
# -----------------------------------------------

def get_holiday_boost(date, region, category):
    holidays = STATE_HOLIDAYS.get(region, [])
    max_boost = 1.0
    for h in holidays:
        month, day, name = h
        if date.month == month:
            if day == 0 or date.day == day:
                boost_map = HOLIDAY_BOOSTS.get(name, {})
                boost = boost_map.get(category, 1.0)
                max_boost = max(max_boost, boost)
    return max_boost

def get_festival_intensity(date, region):
    """Return the highest festival intensity score for a given date/region."""
    holidays = STATE_HOLIDAYS.get(region, [])
    max_intensity = 0
    for h in holidays:
        month, day, name = h
        if date.month == month and (day == 0 or date.day == day):
            intensity = FESTIVAL_INTENSITY_MAP.get(name, 0)
            max_intensity = max(max_intensity, intensity)
    return max_intensity

# -----------------------------------------------
# STORE NAMES
# -----------------------------------------------

def assign_store_names(city, num_stores):
    templates = STORE_NAME_TEMPLATES.get(city, [f"{city} Store {i+1}" for i in range(10)])
    shuffled = templates.copy()
    np.random.shuffle(shuffled)
    names = []
    for i in range(num_stores):
        if i < len(shuffled):
            names.append(shuffled[i])
        else:
            names.append(f"{city} Outlet {i+1}")
    return names

# -----------------------------------------------
# CITIES
# -----------------------------------------------

cities = []
city_id = 1
for region, city_dict in CITIES_RAW.items():
    for city, attrs in city_dict.items():
        cities.append({
            "city_id": city_id,
            "city": city,
            "region": region,
            "population_density": attrs["population_density"],
            "gdp_per_capita": attrs["gdp_per_capita"],
            "mall_count": attrs["mall_count"],
            "is_metro": int(attrs["metro"])
        })
        city_id += 1

cities_df = pd.DataFrame(cities)
cities_df.to_csv(f"{output_dir}/cities.csv", index=False)

# -----------------------------------------------
# STORES
# -----------------------------------------------

# F. Customer Segmentation — store area type
# Assigned once per store (static characteristic)
area_types = ["residential", "commercial", "student", "office", "mixed"]

stores = []
store_id = 1

for _, city_row in cities_df.iterrows():
    city = city_row["city"]
    num_stores = np.random.randint(2, 5)
    store_names = assign_store_names(city, num_stores)

    for i, store_name in enumerate(store_names):
        mall_prob = min(0.8, city_row["mall_count"] / 40)
        in_mall = int(np.random.rand() < mall_prob)

        if in_mall:
            store_size_sqft = np.random.randint(3000, 10000)
        else:
            store_size_sqft = np.random.randint(500, 4000)

        local_competitor_count = int(num_stores - 1 + np.random.randint(0, 5))

        foot_traffic_base = (city_row["population_density"] / 20000) * 40
        mall_bonus = 30 if in_mall else 0
        metro_bonus = 15 if city_row["is_metro"] else 0
        foot_traffic_index = min(100, int(foot_traffic_base + mall_bonus + metro_bonus + np.random.randint(-5, 10)))

        parking = int(np.random.rand() < (0.8 if not in_mall else 0.95))
        store_age_years = np.random.randint(1, 15)
        online_pickup = int(np.random.rand() < 0.5)

        # F. Customer segmentation flags
        area_type = np.random.choice(area_types, p=[0.3, 0.25, 0.15, 0.2, 0.1])
        premium_store_flag = int(
            city_row["gdp_per_capita"] > 180000 and store_size_sqft > 4000
        )
        student_area_flag = int(area_type == "student")
        office_area_flag  = int(area_type == "office")

        # Avg basket size proxy (INR): influenced by area type, metro, premium
        avg_basket_size = int(
            np.random.randint(500, 2000)
            * (1.4 if premium_store_flag else 1.0)
            * (1.2 if city_row["is_metro"] else 0.9)
            * (0.8 if student_area_flag else 1.0)
        )

        # E. Supplier lead time — varies by city type
        # Metro cities get faster replenishment
        if city_row["is_metro"]:
            supplier_lead_time_days = np.random.randint(1, 5)
        else:
            supplier_lead_time_days = np.random.randint(3, 10)

        # Reorder point: days of safety stock (function of lead time)
        reorder_point = supplier_lead_time_days * np.random.randint(5, 15)

        stores.append({
            "store_id":               store_id,
            "store":                  store_name,
            "city":                   city,
            "region":                 city_row["region"],
            "in_mall":                in_mall,
            "store_size_sqft":        store_size_sqft,
            "local_competitor_count": local_competitor_count,
            "foot_traffic_index":     foot_traffic_index,
            "parking_available":      parking,
            "store_age_years":        store_age_years,
            "online_pickup_point":    online_pickup,
            # F. Customer segmentation
            "area_type":              area_type,
            "premium_store_flag":     premium_store_flag,
            "student_area_flag":      student_area_flag,
            "office_area_flag":       office_area_flag,
            "avg_basket_size":        avg_basket_size,
            # E. Replenishment
            "supplier_lead_time_days": supplier_lead_time_days,
            "reorder_point":           reorder_point,
        })
        store_id += 1

stores_df = pd.DataFrame(stores)
stores_df.to_csv(f"{output_dir}/stores.csv", index=False)

print(f"✅ Stores created: {len(stores_df)}")

# -----------------------------------------------
# PRODUCTS
# -----------------------------------------------

products = []
product_id = 1
for cat, brand_list in BRANDS.items():
    for brand in brand_list:
        for i in range(3):
            products.append([
                product_id,
                f"{brand} {cat} {i+1}",
                brand,
                cat
            ])
            product_id += 1

products_df = pd.DataFrame(products, columns=["product_id", "product", "brand", "category"])
products_df.to_csv(f"{output_dir}/products.csv", index=False)

# -----------------------------------------------
# PRODUCT AVAILABILITY
# -----------------------------------------------
availability = []
for _, prod in products_df.iterrows():
    for region in REGIONS:
        if np.random.rand() < 0.8:
            availability.append([prod.product_id, region])

availability_df = pd.DataFrame(availability, columns=["product_id", "region"])
availability_df.to_csv(f"{output_dir}/availability.csv", index=False)

# -----------------------------------------------
# C. WEATHER CONFIG
# City → seasonal weather profiles
# (mean_temp_C, rainfall_mm_per_day, humidity_pct) by month bucket
# Buckets: [Jan-Feb, Mar-May, Jun-Sep(monsoon), Oct-Dec]
# -----------------------------------------------

def get_month_bucket(month):
    if month in [1, 2]:       return 1   # Winter / dry
    elif month in [3, 4, 5]:  return 2   # Summer
    elif month in [6, 7, 8, 9]: return 3 # Monsoon
    else:                       return 4  # Post-monsoon / festive

weather_conditions = ["Sunny", "Cloudy", "Rainy", "Stormy", "Foggy"]

def get_weather(city, date):
    """Simulate weather for a city on a given date."""
    bucket = get_month_bucket(date.month)
    profile = CITY_WEATHER_PROFILES.get(city, CITY_WEATHER_PROFILES["Bangalore"])
    temp_mean, temp_std, rain_mean, rain_std, hum_mean = profile[bucket]

    temperature   = round(np.random.normal(temp_mean, temp_std), 1)
    rainfall_mm   = max(0, round(np.random.normal(rain_mean, rain_std), 1))
    humidity_pct  = min(100, max(20, int(np.random.normal(hum_mean, 8))))

    if rainfall_mm > 20:
        condition = "Stormy"
    elif rainfall_mm > 5:
        condition = "Rainy"
    elif humidity_pct > 80:
        condition = "Cloudy"
    elif temperature < 15:
        condition = "Foggy"
    else:
        condition = "Sunny"

    return temperature, rainfall_mm, humidity_pct, condition

# Weather demand modifiers per category
def weather_demand_modifier(category, rainfall_mm, temperature, condition):
    """
    Returns a multiplier on base demand based on weather.
    - Heavy rain reduces footfall (lower demand for Electronics, Clothing)
    - Extreme heat reduces Clothing sales, boosts cold Grocery items
    - Kerala monsoon hugely affects Grocery
    """
    mod = 1.0
    if category == "Electronics":
        if rainfall_mm > 20: mod *= 0.7     # people stay home
        elif rainfall_mm > 5: mod *= 0.85
        if condition == "Stormy": mod *= 0.75
    elif category == "Clothing":
        if rainfall_mm > 10: mod *= 0.80    # wet weather → people don't shop
        if temperature > 38: mod *= 0.85    # extreme heat
        if temperature < 15: mod *= 1.15    # cold → buy warm clothes
    elif category == "Grocery":
        if rainfall_mm > 20: mod *= 1.20    # stock up during heavy rain
        elif rainfall_mm > 5: mod *= 1.10
        if condition == "Stormy": mod *= 1.25  # panic buying
    return round(mod, 4)

# -----------------------------------------------
# B. PROMOTION CAMPAIGNS
# Generate a random set of promotions per store × category over the date range
# -----------------------------------------------
promo_types = ["None", "Discount_Sale", "BOGO", "Clearance", "Launch_Offer", "Loyalty_Points"]

# Pre-generate promo calendar: (store_id, category) → list of (start_date, end_date, promo_type, spend)
# ~15% of store-category combinations run a promo at any time
promo_calendar = {}   # key: (store_id, category), value: list of [start, end, type, spend]

all_store_ids = stores_df["store_id"].tolist()
for sid in all_store_ids:
    for cat in CATEGORIES:
        promos = []
        # Generate 3–8 random promotions spread across the 10-year window
        n_promos = np.random.randint(3, 9)
        for _ in range(n_promos):
            # Random start date within range
            offset_days   = np.random.randint(0, len(dates) - 30)
            duration_days = np.random.randint(3, 21)
            ptype         = np.random.choice(promo_types[1:])  # exclude "None"
            spend         = np.random.randint(5000, 100000)     # INR marketing spend
            start = dates[offset_days]
            end   = dates[min(offset_days + duration_days, len(dates) - 1)]
            promos.append((start, end, ptype, spend))
        promo_calendar[(sid, cat)] = promos

def get_promo_info(store_id, category, date):
    """Returns (is_promo_campaign, promo_type, marketing_spend) for a given date."""
    promos = promo_calendar.get((store_id, category), [])
    for start, end, ptype, spend in promos:
        if start <= date <= end:
            return 1, ptype, spend
    return 0, "None", 0


# G. Competitor price index — store-level, category-level, varies slightly over time
# Simulated as a static store×category index with minor random walk over time
# We'll compute a per-row value using a simple formula
# Range: 0.80 (competitors are much cheaper) → 1.20 (you are much cheaper)
# Centred at 1.0 (price parity)
competitor_base_index = {}
for sid in all_store_ids:
    for cat in CATEGORIES:
        competitor_base_index[(sid, cat)] = round(np.random.uniform(0.85, 1.15), 4)

def get_competitor_price_index(store_id, category, date):
    """Simulate slow drift in competitive pricing over time."""
    base = competitor_base_index[(store_id, category)]
    drift = np.random.normal(0, 0.01)   # small daily noise
    return round(np.clip(base + drift, 0.75, 1.25), 4)

# -----------------------------------------------
# D. SALARY / PAYDAY LOGIC
# -----------------------------------------------
def get_salary_flags(date):
    """
    Returns (is_month_start, is_month_end, salary_week_flag).
    Salary typically credited on 1st or 7th of month in India.
    Buying peaks in the first 2 weeks post-salary.
    """
    is_month_start = int(date.day <= 7)
    is_month_end   = int(date.day >= 25)
    # Salary week: days 1–10 (post-credit spending surge)
    salary_week_flag = int(1 <= date.day <= 10)
    return is_month_start, is_month_end, salary_week_flag

salary_boost_by_category = {
    "Electronics": 1.20,   # big-ticket, bought after salary
    "Clothing":    1.15,
    "Grocery":     1.05,   # grocery is more uniform
}

# -----------------------------------------------
# SALES DATA GENERATION
# -----------------------------------------------
sales_columns = [
    # ---- ORIGINAL COLUMNS (unchanged) ----
    "date", "region", "city", "store", "store_id",
    "product", "brand", "category",
    "price", "discount", "final_price",
    "inventory", "demand", "sales_qty", "sales",
    # Store-level features
    "in_mall", "store_size_sqft", "local_competitor_count",
    "foot_traffic_index", "parking_available", "store_age_years", "online_pickup_point",
    # City-level features
    "population_density", "gdp_per_capita", "mall_count", "is_metro",
    # Date features
    "is_weekend", "is_holiday", "holiday_name",
    # Boost factors
    "year_factor", "weekend_boost", "festival_boost", "holiday_boost",

    # ---- A. STOCKOUT FLAGS ----
    "stockout_flag",        # 1 if demand > inventory (lost sales event)
    "lost_sales",           # units of unmet demand

    # ---- B. PROMOTION ----
    "is_promo_campaign",    # 1 if an active promotion is running
    "promo_type",           # type: Discount_Sale, BOGO, Clearance, etc.
    "marketing_spend",      # INR spend on this promotion

    # ---- C. WEATHER ----
    "temperature",          # degrees Celsius
    "rainfall_mm",          # mm of rain that day
    "humidity_pct",         # % relative humidity
    "weather_condition",    # Sunny / Rainy / Stormy / Cloudy / Foggy
    "weather_demand_mod",   # demand multiplier from weather (transparency)

    # ---- D. SALARY / PAYDAY ----
    "is_month_start",       # 1 if day 1–7 (salary credited zone)
    "is_month_end",         # 1 if day 25+ (cash-tight zone)
    "salary_week_flag",     # 1 if day 1–10 (post-salary spending surge)

    # ---- E. REPLENISHMENT ----
    "supplier_lead_time_days",  # days to restock from supplier
    "reorder_point",            # units threshold to trigger reorder

    # ---- F. CUSTOMER SEGMENTATION ----
    "area_type",            # residential / commercial / student / office / mixed
    "premium_store_flag",   # 1 = premium catchment area
    "student_area_flag",    # 1 = near colleges / universities
    "office_area_flag",     # 1 = corporate / office district
    "avg_basket_size",      # INR — proxy for customer spending power

    # ---- G. COMPETITOR PRICE INDEX ----
    "competitor_price_index",  # >1 = you're cheaper; <1 = competitors are cheaper

    # ---- H. FESTIVAL INTENSITY SCORE ----
    "festival_intensity_score",  # 0 (no festival) → 10 (Diwali)
]

sales_filepath = f"{output_dir}/sales_data.csv"

city_region_map = cities_df.set_index("city")["region"].to_dict()
city_attrs = cities_df.set_index("city").to_dict("index")

# Build a store lookup dict for fast access
store_lookup = stores_df.set_index("store_id").to_dict("index")

# Write header
with open(sales_filepath, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(sales_columns)

print("⏳ Generating sales data (this may take a few minutes)...")

with open(sales_filepath, "a", newline="") as f:
    writer = csv.writer(f)

    for date in dates:
        year_factor   = 1 + (date.year - start_year) * 0.08
        weekend_boost = 1.2 if date.weekday() >= 5 else 1.0
        is_weekend    = int(date.weekday() >= 5)

        festival_boost = 1.0
        festival_name  = ""
        if date.month in [10, 11]:
            festival_boost = 1.5
            festival_name  = "Diwali_Season"
        elif date.month == 8:
            festival_boost = 1.3
            festival_name  = "Onam_Season"
        elif date.month == 3:
            festival_boost = 1.15
            festival_name  = "Holi_Season"

        # D. Salary flags — same for all stores on a given date
        is_month_start, is_month_end, salary_week_flag = get_salary_flags(date)

        for _, store_row in stores_df.iterrows():
            city   = store_row["city"]
            region = store_row["region"]
            sid    = store_row["store_id"]

            available_products = availability_df[
                availability_df.region == region
            ].product_id.values

            c_attrs = city_attrs[city]

            # C. Weather — computed once per city per date
            temperature, rainfall_mm, humidity_pct, weather_condition = get_weather(city, date)

            for product_id in available_products:
                prod     = products_df[products_df.product_id == product_id].iloc[0]
                category = prod["category"]

                # ---- Holiday ----
                h_boost    = get_holiday_boost(date, region, category)
                is_holiday = int(h_boost > 1.0)
                h_name     = ""
                for h in STATE_HOLIDAYS.get(region, []):
                    m, d, name = h
                    if date.month == m and (d == 0 or date.day == d):
                        h_name = name
                        break

                # H. Festival intensity score
                fest_intensity = get_festival_intensity(date, region)

                # ---- Price ----
                base_price = {
                    "Electronics": np.random.randint(20000, 60000),
                    "Clothing":    np.random.randint(1000, 5000),
                    "Grocery":     np.random.randint(50, 500)
                }[category]

                discount    = np.random.choice([0, 5, 10, 15, 20], p=[0.4, 0.2, 0.2, 0.1, 0.1])
                final_price = base_price * (1 - discount / 100)

                # ---- B. Promotion ----
                is_promo, promo_type, marketing_spend = get_promo_info(sid, category, date)
                promo_boost = PROMO_BOOST_MAP.get(promo_type, 1.0)

                # ---- G. Competitor price index ----
                comp_price_idx = get_competitor_price_index(sid, category, date)
                # Higher index (you're cheaper) → slightly more demand
                comp_price_demand_mod = 0.85 + comp_price_idx * 0.15  # range ~0.97–1.03

                # ---- C. Weather demand modifier ----
                w_mod = weather_demand_modifier(category, rainfall_mm, temperature, weather_condition)

                # ---- D. Salary demand modifier ----
                salary_mod = salary_boost_by_category[category] if salary_week_flag else 1.0

                # ---- Demand ----
                base_demand = {
                    "Electronics": np.random.randint(5, 20),
                    "Clothing":    np.random.randint(10, 40),
                    "Grocery":     np.random.randint(30, 100)
                }[category]

                pop_factor     = 0.7 + (c_attrs["population_density"] / 20000) * 0.6
                mall_factor    = 1.2 if store_row["in_mall"] else 1.0
                traffic_factor = 0.8 + (store_row["foot_traffic_index"] / 100) * 0.5
                comp_factor    = max(0.6, 1 - store_row["local_competitor_count"] * 0.03)
                parking_boost  = 1.1 if (category == "Electronics" and store_row["parking_available"]) else 1.0

                demand = int(
                    base_demand
                    * year_factor
                    * weekend_boost
                    * festival_boost
                    * h_boost
                    * pop_factor
                    * mall_factor
                    * traffic_factor
                    * comp_factor
                    * parking_boost
                    * promo_boost           # B.
                    * w_mod                 # C.
                    * salary_mod            # D.
                    * comp_price_demand_mod # G.
                    * np.random.uniform(0.8, 1.2)
                )

                inventory = int(demand * np.random.uniform(0.8, 1.5))
                sales_qty = min(demand, inventory)
                sales     = sales_qty * final_price

                # A. Stockout
                stockout_flag = int(demand > inventory)
                lost_sales    = max(0, demand - inventory)

                writer.writerow([
                    # ---- ORIGINAL ----
                    date.strftime("%Y-%m-%d"),
                    region,
                    city,
                    store_row["store"],
                    sid,
                    prod["product"],
                    prod["brand"],
                    category,
                    base_price,
                    discount,
                    round(final_price, 2),
                    inventory,
                    demand,
                    sales_qty,
                    round(sales, 2),
                    store_row["in_mall"],
                    store_row["store_size_sqft"],
                    store_row["local_competitor_count"],
                    store_row["foot_traffic_index"],
                    store_row["parking_available"],
                    store_row["store_age_years"],
                    store_row["online_pickup_point"],
                    c_attrs["population_density"],
                    c_attrs["gdp_per_capita"],
                    c_attrs["mall_count"],
                    c_attrs["is_metro"],
                    is_weekend,
                    is_holiday,
                    h_name,
                    round(year_factor, 4),
                    round(weekend_boost, 4),
                    round(festival_boost, 4),
                    round(h_boost, 4),
                    # ---- A. STOCKOUT ----
                    stockout_flag,
                    lost_sales,
                    # ---- B. PROMOTION ----
                    is_promo,
                    promo_type,
                    marketing_spend,
                    # ---- C. WEATHER ----
                    temperature,
                    rainfall_mm,
                    humidity_pct,
                    weather_condition,
                    w_mod,
                    # ---- D. SALARY ----
                    is_month_start,
                    is_month_end,
                    salary_week_flag,
                    # ---- E. REPLENISHMENT ----
                    store_row["supplier_lead_time_days"],
                    store_row["reorder_point"],
                    # ---- F. CUSTOMER SEGMENTATION ----
                    store_row["area_type"],
                    store_row["premium_store_flag"],
                    store_row["student_area_flag"],
                    store_row["office_area_flag"],
                    store_row["avg_basket_size"],
                    # ---- G. COMPETITOR PRICE INDEX ----
                    comp_price_idx,
                    # ---- H. FESTIVAL INTENSITY SCORE ----
                    fest_intensity,
                ])

print(f"✅ Data generation complete. Files saved in: {output_dir}/")
print(f"   → sales_data.csv  (columns: {len(sales_columns)})")
print(f"   → stores.csv      ({len(stores_df)} stores)")
print(f"   → cities.csv      ({len(cities_df)} cities)")
print(f"   → products.csv")
print(f"   → regions.csv")
print(f"   → availability.csv")
print()
print("New columns added:")
print("  A. stockout_flag, lost_sales")
print("  B. is_promo_campaign, promo_type, marketing_spend")
print("  C. temperature, rainfall_mm, humidity_pct, weather_condition, weather_demand_mod")
print("  D. is_month_start, is_month_end, salary_week_flag")
print("  E. supplier_lead_time_days, reorder_point  (in stores.csv)")
print("  F. area_type, premium_store_flag, student_area_flag, office_area_flag, avg_basket_size  (in stores.csv)")
print("  G. competitor_price_index")
print("  H. festival_intensity_score")
