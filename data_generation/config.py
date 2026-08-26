REGIONS = ["Maharashtra", "Kerala", "Karnataka", "Tamil Nadu", "Delhi", "Gujarat"]

STATE_HOLIDAYS = {
    "Maharashtra": [
        (1, 26, "Republic Day"), (4, 14, "Ambedkar Jayanti"),
        (5, 1, "Maharashtra Day"), (8, 15, "Independence Day"),
        (10, 2, "Gandhi Jayanti"), (11, 0, "Diwali"),
        (12, 25, "Christmas")
    ],
    "Kerala": [
        (1, 26, "Republic Day"), (8, 0, "Onam"),
        (8, 15, "Independence Day"), (9, 0, "Onam"),
        (10, 2, "Gandhi Jayanti"), (12, 25, "Christmas"),
        (11, 1, "Kerala Piravi")
    ],
    "Karnataka": [
        (1, 26, "Republic Day"), (8, 15, "Independence Day"),
        (10, 2, "Gandhi Jayanti"), (11, 1, "Kannada Rajyotsava"),
        (11, 0, "Diwali"), (10, 0, "Dasara")
    ],
    "Tamil Nadu": [
        (1, 14, "Pongal"), (1, 15, "Pongal Day2"), (1, 26, "Republic Day"),
        (4, 14, "Tamil New Year"), (8, 15, "Independence Day"),
        (10, 2, "Gandhi Jayanti"), (12, 25, "Christmas")
    ],
    "Delhi": [
        (1, 26, "Republic Day"), (8, 15, "Independence Day"),
        (10, 2, "Gandhi Jayanti"), (11, 0, "Diwali"),
        (10, 0, "Navratri"), (12, 25, "Christmas"),
        (3, 0, "Holi")
    ],
    "Gujarat": [
        (1, 26, "Republic Day"), (8, 15, "Independence Day"),
        (10, 2, "Gandhi Jayanti"), (11, 0, "Diwali"),
        (10, 0, "Navratri"),
        (1, 14, "Uttarayan"), (5, 1, "Gujarat Day")
    ],
}

HOLIDAY_BOOSTS = {
    "Diwali":             {"Electronics": 2.0, "Clothing": 1.8, "Grocery": 1.5},
    "Onam":               {"Electronics": 1.5, "Clothing": 1.6, "Grocery": 1.8},
    "Dasara":             {"Electronics": 1.4, "Clothing": 1.5, "Grocery": 1.3},
    "Navratri":           {"Electronics": 1.2, "Clothing": 1.7, "Grocery": 1.4},
    "Pongal":             {"Electronics": 1.3, "Clothing": 1.4, "Grocery": 1.6},
    "Pongal Day2":        {"Electronics": 1.2, "Clothing": 1.3, "Grocery": 1.5},
    "Tamil New Year":     {"Electronics": 1.3, "Clothing": 1.5, "Grocery": 1.4},
    "Uttarayan":          {"Electronics": 1.1, "Clothing": 1.3, "Grocery": 1.4},
    "Holi":               {"Electronics": 1.2, "Clothing": 1.5, "Grocery": 1.3},
    "Christmas":          {"Electronics": 1.6, "Clothing": 1.5, "Grocery": 1.3},
    "Republic Day":       {"Electronics": 1.1, "Clothing": 1.2, "Grocery": 1.1},
    "Independence Day":   {"Electronics": 1.1, "Clothing": 1.2, "Grocery": 1.1},
    "Gandhi Jayanti":     {"Electronics": 1.0, "Clothing": 1.0, "Grocery": 1.0},
    "Maharashtra Day":    {"Electronics": 1.1, "Clothing": 1.2, "Grocery": 1.1},
    "Kerala Piravi":      {"Electronics": 1.1, "Clothing": 1.2, "Grocery": 1.1},
    "Kannada Rajyotsava": {"Electronics": 1.1, "Clothing": 1.3, "Grocery": 1.1},
    "Gujarat Day":        {"Electronics": 1.1, "Clothing": 1.2, "Grocery": 1.1},
    "Karnataka Piravi":   {"Electronics": 1.1, "Clothing": 1.2, "Grocery": 1.1},
    "Ambedkar Jayanti":   {"Electronics": 1.0, "Clothing": 1.1, "Grocery": 1.0},
}

FESTIVAL_INTENSITY_MAP = {
    "Diwali":             10,
    "Onam":               8,
    "Navratri":           7,
    "Dasara":             7,
    "Pongal":             7,
    "Holi":               6,
    "Tamil New Year":     6,
    "Christmas":          6,
    "Pongal Day2":        5,
    "Uttarayan":          5,
    "Independence Day":   4,
    "Republic Day":       3,
    "Maharashtra Day":    3,
    "Kerala Piravi":      3,
    "Kannada Rajyotsava": 3,
    "Gujarat Day":        3,
    "Karnataka Piravi":   3,
    "Gandhi Jayanti":     2,
    "Ambedkar Jayanti":   2,
}

STORE_NAME_TEMPLATES = {
    "Mumbai":      ["Andheri Mart", "Bandra Hub", "Dadar Central", "Kurla Square", "Borivali Plaza"],
    "Pune":        ["Shivaji Nagar Store", "Kothrud Market", "Hinjewadi Outlet", "Wakad Bazaar"],
    "Nagpur":      ["Sitabuldi Center", "Dharampeth Market", "Wardha Road Store"],
    "Kochi":       ["MG Road Kochi", "Edapally Junction", "Aluva Outlet", "Fort Kochi Store"],
    "Trivandrum":  ["Palayam Market", "Kowdiar Store", "Pattom Outlet"],
    "Bangalore":   ["Koramangala Hub", "Indiranagar Mart", "Whitefield Store", "HSR Layout"],
    "Mysore":      ["Chamundi Mart", "Devaraja Market", "Gokulam Store"],
    "Chennai":     ["Anna Nagar Mall", "T Nagar Market", "Adyar Store", "Velachery Hub"],
    "Coimbatore":  ["RS Puram Store", "Gandhipuram Market", "Peelamedu Outlet"],
    "New Delhi":   ["Connaught Place", "Lajpat Nagar Hub", "Karol Bagh Mart", "Saket Store", "Rajouri Store"],
    "Ahmedabad":   ["CG Road Store", "Satellite Mart", "Navrangpura Hub", "Maninagar Outlet"],
    "Surat":       ["Adajan Market", "Ring Road Store", "Varachha Hub"],
}

CITIES_RAW = {
    "Maharashtra": {
        "Mumbai":   {"population_density": 20000, "gdp_per_capita": 210000, "mall_count": 24, "metro": True},
        "Pune":     {"population_density": 8000,  "gdp_per_capita": 180000, "mall_count": 14, "metro": True},
        "Nagpur":   {"population_density": 4000,  "gdp_per_capita": 120000, "mall_count": 6,  "metro": False},
    },
    "Kerala": {
        "Kochi":       {"population_density": 5800, "gdp_per_capita": 160000, "mall_count": 9, "metro": True},
        "Trivandrum":  {"population_density": 4800, "gdp_per_capita": 150000, "mall_count": 7, "metro": False},
    },
    "Karnataka": {
        "Bangalore":  {"population_density": 11000, "gdp_per_capita": 250000, "mall_count": 28, "metro": True},
        "Mysore":     {"population_density": 3500,  "gdp_per_capita": 110000, "mall_count": 5,  "metro": False},
    },
    "Tamil Nadu": {
        "Chennai":     {"population_density": 14000, "gdp_per_capita": 200000, "mall_count": 20, "metro": True},
        "Coimbatore":  {"population_density": 5500,  "gdp_per_capita": 140000, "mall_count": 8,  "metro": False},
    },
    "Delhi": {
        "New Delhi":  {"population_density": 11000, "gdp_per_capita": 350000, "mall_count": 35, "metro": True},
    },
    "Gujarat": {
        "Ahmedabad":  {"population_density": 9000, "gdp_per_capita": 190000, "mall_count": 16, "metro": True},
        "Surat":      {"population_density": 7500, "gdp_per_capita": 170000, "mall_count": 10, "metro": True},
    },
}

CATEGORIES = ["Electronics", "Clothing", "Grocery"]
BRANDS = {
    "Electronics": ["Samsung", "Sony", "LG"],
    "Clothing":    ["Nike", "Adidas", "Puma"],
    "Grocery":     ["Amul", "Nestle", "Tata"]
}

CITY_WEATHER_PROFILES = {
    # city: {month_bucket: (temp_mean, temp_std, rain_mean, rain_std, humidity_mean)}
    "Mumbai":      {1: (27,2,0,0,65),  2: (33,3,0,1,60),  3: (29,3,15,10,80), 4: (28,2,5,5,72)},
    "Pune":        {1: (26,3,0,0,55),  2: (35,4,0,1,45),  3: (28,4,8,8,70),  4: (26,3,3,4,60)},
    "Nagpur":      {1: (25,4,0,0,55),  2: (40,4,0,1,40),  3: (31,4,10,8,65), 4: (27,4,2,3,55)},
    "Kochi":       {1: (30,2,5,5,78),  2: (33,2,5,5,72),  3: (28,2,30,15,90),4: (29,2,20,10,85)},
    "Trivandrum":  {1: (30,2,5,5,76),  2: (33,2,5,5,70),  3: (27,2,25,12,88),4: (29,2,15,8,82)},
    "Bangalore":   {1: (24,3,0,0,55),  2: (32,4,3,3,50),  3: (25,3,12,8,70), 4: (24,3,5,5,62)},
    "Mysore":      {1: (24,3,0,0,52),  2: (33,4,2,3,48),  3: (25,3,10,8,68), 4: (24,3,5,5,60)},
    "Chennai":     {1: (28,2,2,2,72),  2: (36,3,1,2,65),  3: (30,3,5,5,78),  4: (27,2,20,12,82)},
    "Coimbatore":  {1: (26,3,1,2,62),  2: (34,4,1,2,55),  3: (27,3,8,7,72),  4: (25,3,8,8,68)},
    "New Delhi":   {1: (16,5,1,1,70),  2: (38,5,0,1,40),  3: (32,4,10,8,65), 4: (22,5,2,3,55)},
    "Ahmedabad":   {1: (22,4,0,0,55),  2: (40,4,0,1,38),  3: (31,4,12,8,65), 4: (26,4,1,2,52)},
    "Surat":       {1: (25,3,0,0,60),  2: (37,4,0,1,48),  3: (30,3,18,10,78),4: (27,3,5,5,65)},
}

# Promo demand boost per type
PROMO_BOOST_MAP = {
    "None":           1.0,
    "Discount_Sale":  1.35,
    "BOGO":           1.50,
    "Clearance":      1.20,
    "Launch_Offer":   1.40,
    "Loyalty_Points": 1.25,
}

