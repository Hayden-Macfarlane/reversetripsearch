import streamlit as st
import pandas as pd
import math
import random
from datetime import datetime, timedelta
from urllib.parse import quote
import pycountry

# Set page config
st.set_page_config(page_title="WanderWise", layout="wide")

# Custom CSS for WanderWise (V5.4)
st.markdown("""
<style>
    /* Gradient Header Text */
    h1 {
        background: linear-gradient(to right, #00D4BD, #2E86DE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* NUCLEAR CONTRAST FIXES - MAXIMUM READABILITY */
    
    /* 1. Dropdown Popover Redesign: Midnight with White Text */
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #1E212B !important; /* Midnight background match */
        border: 2px solid #00D4BD !important; /* Teal border */
    }
    
    /* Dropdown Option Text - Force White */
    div[data-baseweb="popover"] li, 
    div[data-baseweb="popover"] div,
    li[role="option"] {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }

    /* Highlighted / Selected Option - Teal Background with BLACK Text */
    li[aria-selected="true"], 
    li:hover,
    [data-baseweb="menu"] div:hover {
        background-color: #00D4BD !important;
        color: #000000 !important;
    }

    /* 2. Input Boxes: Force Selected Text to be White */
    div[data-baseweb="select"] div[class*="content"],
    input {
        color: #FFFFFF !important;
    }

    /* 3. Hero Metrics & Banners: Forced High-Contrast White */
    /* Target h1 and h2 inside the custom hero results div strictly */
    .hero-banner h1, .hero-banner h2, .hero-banner p {
        color: #FFFFFF !important;
        background: none !important;
        -webkit-text-fill-color: #FFFFFF !important;
        text-shadow: 0px 2px 10px rgba(0,0,0,0.5) !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.8);
    }
    
    [data-testid="stMetricValue"] > div {
        color: #FFFFFF !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #00D4BD !important; /* Brand Teal for the Label */
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricLabel"] > div {
        color: #00D4BD !important;
    }

    /* 4. Cleanup UI Cruft */
    .st-emotion-cache-1plkea0 a, .st-emotion-cache-10trblm a {
        display: none !important;
    }
    
    [data-testid="stHeaderAction"],
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0) !important;
    }
    
    [data-testid="stHeader"]::after {
        display: none !important;
    }

    /* Modern Travel Cards with Depth */
    .travel-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border: 1px solid #333;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .travel-card:hover {
        transform: translateY(-5px);
        border-color: #00D4BD;
    }
    
    .card-header {
        color: #fff;
        font-size: 1.4em;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .card-metadata {
        color: #aaa;
        font-size: 0.85em;
        margin-bottom: 12px;
    }
    
    .activity-badge {
        background-color: #444;
        color: #fff;
        padding: 5px 10px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-right: 5px;
        margin-bottom: 5px;
        display: inline-block;
        border: 1px solid #555;
    }
    
    .price-container {
        text-align: center;
        margin: 20px 0;
        padding: 10px;
        background: rgba(0, 212, 189, 0.1);
        border-radius: 10px;
    }

    .price-big {
        color: #00D4BD; /* Brand Teal */
        font-size: 2.8em;
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
    
    .price-small {
        color: #aaa;
        font-size: 0.9em;
        margin-top: 5px;
    }
    
    /* V5.14: Premium Clickable Card Buttons */
    div.stButton > button {
        height: 160px !important;
        width: 100% !important;
        background-color: #262730 !important;
        border: 1px solid #444 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
        white-space: pre-wrap !important; /* Forces newlines to work */
        font-size: 22px !important;
        color: #FFFFFF !important;
        transition: all 0.2s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 20px !important;
        line-height: 1.4 !important;
    }
    
    div.stButton > button:hover {
        transform: scale(1.02) !important;
        border-color: #00D4BD !important;
        box-shadow: 0 8px 12px rgba(0,212,189,0.15) !important;
        background-color: #2d2f3a !important;
    }

    div.stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* V5.17: Premium Back Button (Teal Theme) */
    /* Target the specific container for the back button */
    .back-btn-wrapper div.stButton > button {
        background-color: transparent !important;
        border: 2px solid #00D4BD !important;
        color: #00D4BD !important;
        border-radius: 8px !important;
        width: auto !important;
        padding: 4px 12px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        height: 36px !important; /* V6.1: Explicit compact height */
        line-height: 1 !important; /* V6.1: Tighten text alignment */
        min-height: 0 !important;
        box-shadow: none !important;
        margin-bottom: 20px !important;
    }
    
    .back-btn-wrapper div.stButton > button:hover {
        background-color: #00D4BD !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
    }

    
    .breakdown {
        color: #ccc;
        font-size: 0.85em;
        border-top: 1px solid #444;
        padding-top: 12px;
        margin-top: 10px;
    }
    
    .booking-button {
        display: inline-block;
        width: 100%;
        padding: 12px;
        margin-top: 10px;
        background: linear-gradient(135deg, #00D4BD 0%, #2E86DE 100%);
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        transition: opacity 0.2s;
    }
    .booking-button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Constants
ISO_TO_REGION = {
    # Europe
    'CH': 'Europe', 'IS': 'Europe', 'NO': 'Europe', 'DK': 'Europe', 'AT': 'Europe',
    'IE': 'Europe', 'FR': 'Europe', 'FI': 'Europe', 'NL': 'Europe', 'LU': 'Europe',
    'DE': 'Europe', 'GB': 'Europe', 'BE': 'Europe', 'SE': 'Europe', 'IT': 'Europe',
    'CY': 'Europe', 'MT': 'Europe', 'GR': 'Europe', 'EE': 'Europe', 'SI': 'Europe',
    'LV': 'Europe', 'ES': 'Europe', 'LT': 'Europe', 'SK': 'Europe', 'CZ': 'Europe',
    'HR': 'Europe', 'PT': 'Europe', 'AL': 'Europe', 'HU': 'Europe', 'PL': 'Europe',
    'ME': 'Europe', 'BG': 'Europe', 'RS': 'Europe', 'RO': 'Europe', 'BA': 'Europe',
    'MK': 'Europe', 'MD': 'Europe', 'RU': 'Europe', 'BY': 'Europe', 'UA': 'Europe',
    
    # Asia
    'SG': 'Asia', 'HK': 'Asia', 'KR': 'Asia', 'AE': 'Asia', 'BH': 'Asia',
    'QA': 'Asia', 'JP': 'Asia', 'SA': 'Asia', 'TW': 'Asia', 'OM': 'Asia',
    'KW': 'Asia', 'LB': 'Asia', 'PS': 'Asia', 'JO': 'Asia', 'AM': 'Asia',
    'TR': 'Asia', 'KH': 'Asia', 'TH': 'Asia', 'GE': 'Asia', 'KZ': 'Asia',
    'CN': 'Asia', 'AZ': 'Asia', 'PH': 'Asia', 'MY': 'Asia', 'IQ': 'Asia',
    'VN': 'Asia', 'KG': 'Asia', 'ID': 'Asia', 'IR': 'Asia', 'UZ': 'Asia',
    'SY': 'Asia', 'BD': 'Asia', 'IN': 'Asia', 'PK': 'Asia', 'IL': 'Asia',
    'LK': 'Asia', 'NP': 'Asia',
    
    # South America
    'UY': 'South America', 'CL': 'South America', 'VE': 'South America',
    'EC': 'South America', 'BR': 'South America', 'PE': 'South America',
    'AR': 'South America', 'CO': 'South America', 'BO': 'South America',
    'PY': 'South America',
    
    # Oceania
    'AU': 'Oceania', 'NZ': 'Oceania', 'FJ': 'Oceania',
    
    # Africa
    'MU': 'Africa', 'ZA': 'Africa', 'NG': 'Africa', 'GH': 'Africa',
    'KE': 'Africa', 'BW': 'Africa', 'MA': 'Africa', 'UG': 'Africa',
    'DZ': 'Africa', 'TN': 'Africa', 'MG': 'Africa', 'TZ': 'Africa',
    'EG': 'Africa', 'LY': 'Africa', 'CM': 'Africa', 'ZW': 'Africa',
    
    # North America
    'BS': 'North America', 'BB': 'North America', 'US': 'North America',
    'CA': 'North America', 'PR': 'North America', 'JM': 'North America',
    'TT': 'North America', 'CR': 'North America', 'CU': 'North America',
    'PA': 'North America', 'SV': 'North America', 'GT': 'North America',
    'DO': 'North America', 'MX': 'North America',
}

# V5.9: Global Tourist Popularity Score (1-100) - DEPRECATED in V8.0 (Build-time shift)
# Use 'Popularity_Score' column from master_travel_data.csv instead.

REGION_FLIGHT_COSTS = {
    "Europe": 850,
    "Asia": 1200,
    "South America": 700,
    "Africa": 1100,
    "Oceania": 1600,
    "North America": 400
}

ACCOM_TIERS = {
    "Bare Essential (1 Star/Camping)": 0.5,
    "Economy (2-4 Star Hotel)": 1.0,
    "Luxury (5 Star Only)": 4.0
}

ACTIVITY_TIERS = {
    "Budget (Street Food / Free Activities)": 0.5,
    "Standard (Restaurants / Museums)": 1.0,
    "Extra Spend (Fine Dining / Guided Tours)": 2.0
}

FLIGHT_CLASS_TIERS = {
    "Bare Essential (Spirit/Ryanair / Basic Economy)": 1.0,
    "Standard (Main Cabin / Checked Bag)": 1.5,
    "Luxury (First Class / Business)": 3.5
}

MOCK_ACTIVITIES_LIST = ['Beach', 'Hiking', 'Caves', 'Skiing', 'History', 'Nightlife', 'Foodie', 'Nature', 'Adventure']
MOCK_WEATHER = ["☀️ Sunny", "❄️ Snowy", "🌧️ Rainy", "🌤️ Temperate"]

ACTIVITY_EMOJIS = {
    'Beach': '🏖️',
    'Hiking': '🥾',
    'Caves': '🕳️',
    'Skiing': '⛷️',
    'History': '🏛️',
    'Nightlife': '🌃',
    'Foodie': '🍽️',
    'Nature': '🌲',
    'Adventure': '🏔️'
}

def calculate_transport_cost(destination_name):
    """Calculate daily transportation cost based on destination type"""
    dest_str = str(destination_name) if pd.notna(destination_name) else "Unknown"
    dest_lower = dest_str.lower()
    
    mega_cities = ['london', 'tokyo', 'new york', 'paris', 'berlin', 'singapore', 
                   'hong kong', 'barcelona', 'amsterdam', 'seoul', 'taipei', 'chicago',
                   'boston', 'washington', 'san francisco', 'toronto', 'montreal']
    
    sprawl_cities = ['los angeles', 'houston', 'miami', 'dubai', 'atlanta',
                     'dallas', 'phoenix', 'san diego', 'las vegas', 'orlando']
    
    nature_rural = ['reykjavik', 'iceland', 'yellowstone', 'banff', 'queenstown',
                    'patagonia', 'safari', 'fjord', 'highlands', 'anchorage']
    
    for city in mega_cities:
        if city in dest_lower:
            return 10.0
    
    for city in sprawl_cities:
        if city in dest_lower:
            return 50.0
    
    for location in nature_rural:
        if location in dest_lower:
            return 80.0
    
    return 30.0

def get_country_name(iso_code):
    """Helper to get full country name from ISO code for search routing"""
    try:
        country = pycountry.countries.get(alpha_2=iso_code)
        return country.name if country else iso_code
    except Exception:
        return iso_code

def create_country_name_to_iso_map():
    """Create mapping from country name to ISO code using pycountry"""
    name_to_iso = {}
    for country in pycountry.countries:
        name_to_iso[country.name] = country.alpha_2
        if hasattr(country, 'common_name'):
            name_to_iso[country.common_name] = country.alpha_2
    
    # Manual additions for special cases
    name_to_iso['United States'] = 'US'
    name_to_iso['United Kingdom'] = 'GB'
    name_to_iso['South Korea'] = 'KR'
    name_to_iso['Hong Kong (China)'] = 'HK'
    name_to_iso['Palestine'] = 'PS'
    name_to_iso['Kosovo (Disputed Territory)'] = 'XK'
    name_to_iso['Bosnia And Herzegovina'] = 'BA'
    name_to_iso['Trinidad And Tobago'] = 'TT'
    return name_to_iso

def make_bold(text):
    """V5.14: Convert standard text to mathematical bold unicode equivalents for button labels"""
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789$"
    bold = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗💲"
    trans = str.maketrans(normal, bold)
    return str(text).translate(trans)

def get_flag_emoji(country_code):
    """V5.14: Helper to convert ISO country code to Emoji flag"""
    if not country_code or len(country_code) != 2:
        return "🌐"
    return "".join(chr(127397 + ord(c)) for c in country_code.upper())

def calculate_haversine(lat1, lon1, lat2, lon2):
    """V7.1: Great-circle distance between two points in km"""
    if any(pd.isna([lat1, lon1, lat2, lon2])): return 0
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2)**2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def get_booking_url(search_term, level, checkin_date):
    """V10.0: Precision Hotel Routing using Booking.com filters (nflt)"""
    base_url = f"https://www.booking.com/searchresults.html?ss={quote(search_term)}&checkin={checkin_date}"
    
    if "Luxury" in level:
        # V10.2: 5-star only
        return f"{base_url}&nflt=class%3D5"
    elif "Economy" in level:
        # V10.2: 4-star, 3-star, 2-star
        return f"{base_url}&nflt=class%3D4%3Bclass%3D3%3Bclass%3D2"
    else:
        # V10.0: Bare Essentials: 2-star, 1-star
        return f"{base_url}&nflt=class%3D2%3Bclass%3D1"

@st.cache_data
def load_real_data(v="V9.0"):
    """Load pre-processed master travel dataset (V6.0 Build-Time Shift)"""
    try:
        df = pd.read_csv("master_travel_data.csv")
        return df
    except Exception as e:
        st.error(f"Error loading master dataset: {e}")
        return pd.DataFrame()

def enrich_data(df):
    """Add lightweight mock enrichment (activities, transport)"""
    def get_activities(name):
        name_str = str(name) if pd.notna(name) else "Unknown"
        random.seed(hash(name_str) % 10000)
        k = random.randint(2, 4)
        return random.sample(MOCK_ACTIVITIES_LIST, min(k, len(MOCK_ACTIVITIES_LIST)))

    df['Activities'] = df['Destination'].apply(get_activities)
    df['Transport_Cost_Daily'] = df['Destination'].apply(calculate_transport_cost)
    return df

# Load Real Data
with st.spinner("🚀 Booting WanderWise Data Engine..."):
    destinations_df = load_real_data()

if destinations_df.empty:
    st.error("Failed to load WanderWise data. Did you run data_prep.py?")
    st.stop()

destinations_df = enrich_data(destinations_df)

# Title Redesign
st.markdown("""
    <div style='text-align: center; padding-bottom: 20px;'>
        <h1 style='font-size: 80px; margin-bottom: 0; background: linear-gradient(to right, #00D4BD, #2E86DE); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block;'>
            WanderWise
        </h1>
        <h3 style='font-size: 24px; color: #E0E0E0; font-weight: 300; margin-top: -10px;'>
            Intelligent Travel Computation
        </h3>
    </div>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.header("What is your goal?")
mode_options = ["Find Destinations 🌍", "Maximize Days 📅", "Price a Trip 💰"]
selected_mode = st.sidebar.pills("Navigation", mode_options, label_visibility="collapsed", default=mode_options[0])

# Initialize drill-down and sorting state
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

if 'sort_selection' not in st.session_state:
    st.session_state.sort_selection = "Popularity (High to Low)"

if 'last_mode' not in st.session_state:
    st.session_state.last_mode = selected_mode
if st.session_state.last_mode != selected_mode:
    st.session_state.selected_country = None
    st.session_state.last_mode = selected_mode

all_usable_airports = sorted([str(d) for d in destinations_df['Destination'].unique() if pd.notna(d)])

try:
    default_origin_idx = next(i for i, x in enumerate(all_usable_airports) if "New York" in x)
except StopIteration:
    default_origin_idx = 0

try:
    default_dest_idx = next((i for i, x in enumerate(all_usable_airports) if x.startswith("London, GB") or x == "London, United Kingdom"), 0)
except StopIteration:
    default_dest_idx = 0

if selected_mode == "Find Destinations 🌍":
    st.sidebar.info("ℹ️ Goal: You have a fixed budget and want to see all the places you can afford.")
elif selected_mode == "Maximize Days 📅":
    st.sidebar.info("ℹ️ Goal: You know where you want to go, and want to see how long you can stay.")
else:
    st.sidebar.info("ℹ️ Goal: You have a dream destination and duration, and want the total price tag.")

st.sidebar.subheader("Essential Trip Details")
origin_city = st.sidebar.selectbox("✈️ Origin City", options=all_usable_airports, index=default_origin_idx)
num_travelers = st.sidebar.number_input("👥 Number of Travelers", min_value=1, max_value=10, value=1)

# Dynamic Inputs
target_dest = None
duration = 7
total_budget = 3000.0

if selected_mode == "Find Destinations 🌍":
    total_budget = st.sidebar.number_input("💰 Total Group Budget ($)", min_value=100, value=3000, step=100)
    duration = st.sidebar.slider("📅 Trip Duration (Days)", min_value=3, max_value=30, value=7)
    
    st.sidebar.subheader("🔍 Filters")
    selected_regions = st.sidebar.multiselect("🌎 Regions", options=sorted(destinations_df['Region'].unique()), default=[])
    selected_activities = st.sidebar.multiselect("🎯 Activities", options=MOCK_ACTIVITIES_LIST, default=[])
    
elif selected_mode == "Maximize Days 📅":
    total_budget = st.sidebar.number_input("💰 Total Group Budget ($)", min_value=100, value=3000, step=100)
    target_dest = st.sidebar.selectbox("🎯 Select Your Destination", options=all_usable_airports, index=default_dest_idx)
    selected_regions, selected_activities = [], []

else:  # Price a Trip 💰
    duration = st.sidebar.slider("📅 Trip Duration (Days)", min_value=3, max_value=30, value=7)
    target_dest = st.sidebar.selectbox("🎯 Select Your Destination", options=all_usable_airports, index=default_dest_idx)
    selected_regions, selected_activities = [], []

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Travel Style Expander
with st.sidebar.expander("💸 Customize Spending & Style", expanded=False):
    st.markdown("**✈️ Flight Class**")
    flight_class_name = st.selectbox("Choose flight class", options=list(FLIGHT_CLASS_TIERS.keys()), index=1, label_visibility="collapsed")
    flight_mult = FLIGHT_CLASS_TIERS[flight_class_name]
    
    st.markdown("**🏨 Accommodation Level**")
    accom_tier_name = st.selectbox("Choose accommodation style", options=list(ACCOM_TIERS.keys()), index=1, label_visibility="collapsed")
    accom_mult = ACCOM_TIERS[accom_tier_name]
    
    st.markdown("**🍽️ Food & Activities**")
    act_tier_name = st.selectbox("Choose spending style", options=list(ACTIVITY_TIERS.keys()), index=1, label_visibility="collapsed")
    act_mult = ACTIVITY_TIERS[act_tier_name]

# --- Cost Logic (V7.1 Distance-Aware) ---
origin_row = destinations_df[destinations_df['Destination'] == origin_city]
if not origin_row.empty:
    o_lat = origin_row['latitude_deg'].values[0]
    o_lon = origin_row['longitude_deg'].values[0]
    origin_iata = origin_row['IATA'].values[0]
else:
    o_lat, o_lon, origin_iata = 0, 0, "AUS" # Default AUS if lookup fails

# Map selected tier to pre-calculated Base Daily Cost
if "Luxury" in accom_tier_name:
    daily_base = destinations_df['Daily_Cost_Luxury']
else:
    daily_base = destinations_df['Daily_Cost_Budget']

# Haversine Distance & Variable Flight Pricing
destinations_df['Distance_KM'] = destinations_df.apply(
    lambda r: calculate_haversine(o_lat, o_lon, r['latitude_deg'], r['longitude_deg']), axis=1
)

# Variable flight cost: $150 base + $0.08 per km
# Ensures longer flights are more expensive while keeping local flights cheap
destinations_df['Calculated_Flight_Base'] = 150 + (destinations_df['Distance_KM'] * 0.08)

# Apply multipliers
destinations_df['Daily_Hotel_Group'] = (daily_base * 0.4) * accom_mult * math.ceil(num_travelers / 2)
destinations_df['Daily_Food_Group'] = (daily_base * 0.4) * num_travelers * act_mult
destinations_df['Daily_Transport_Group'] = destinations_df['Transport_Cost_Daily'] * num_travelers

destinations_df['Total_Daily_Group'] = destinations_df['Daily_Food_Group'] + destinations_df['Daily_Hotel_Group'] + destinations_df['Daily_Transport_Group']
destinations_df['Total_Flight_Group'] = destinations_df['Calculated_Flight_Base'] * flight_mult * num_travelers

st.markdown("---")

# --- Logic Engine ---
result_df = pd.DataFrame()
metric_display = None

if selected_mode == "Find Destinations 🌍":
    destinations_df['Trip_Cost'] = destinations_df['Total_Flight_Group'] + (destinations_df['Total_Daily_Group'] * duration)
    result_df = destinations_df[destinations_df['Trip_Cost'] <= total_budget].copy()
    
elif selected_mode == "Maximize Days 📅":
    row = destinations_df[destinations_df['Destination'] == target_dest]
    if not row.empty:
        flight_cost = row['Total_Flight_Group'].values[0]
        daily_cost = row['Total_Daily_Group'].values[0]
        remaining_budget = total_budget - flight_cost
        max_days = math.floor(remaining_budget / daily_cost) if remaining_budget > 0 else 0
        metric_display = ("You can stay for", f"{max_days} Days")
        result_df = row.copy()
        result_df['Trip_Cost'] = flight_cost + (daily_cost * max_days)
    else:
        st.error("Destination not found.")

else:  # Price a Trip
    row = destinations_df[destinations_df['Destination'] == target_dest]
    if not row.empty:
        flight_cost = row['Total_Flight_Group'].values[0]
        daily_cost = row['Total_Daily_Group'].values[0]
        trip_cost = flight_cost + (daily_cost * duration)
        metric_display = ("Total Cost for Your Dream Trip", f"${trip_cost:,.0f}")
        result_df = row.copy()
        result_df['Trip_Cost'] = trip_cost
    else:
        st.error("Destination not found.")

if not result_df.empty:
    if selected_regions: result_df = result_df[result_df['Region'].isin(selected_regions)]
    if selected_activities:
        def has_activity(activity_list): return not set(selected_activities).isdisjoint(activity_list)
        result_df = result_df[result_df['Activities'].apply(has_activity)]

# --- Display Results ---
if metric_display and not result_df.empty:
    st.markdown(f"""
    <div class='hero-banner' style='background: linear-gradient(135deg, #00D4BD 0%, #2E86DE 100%); 
                padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
        <h2 style='margin: 0; font-size: 1.2em;'>{metric_display[0]}</h2>
        <h1 style='margin: 10px 0; font-size: 3.5em; font-weight: 800;'>{metric_display[1]}</h1>
        <p style='margin: 0;'>{f"for {duration} days" if selected_mode == "Price a Trip 💰" else f"with ${total_budget:,.0f} budget"} in {target_dest}</p>
    </div>
    """, unsafe_allow_html=True)

if not result_df.empty:
    # Get current Month for weather lookup
    travel_dt = datetime.now() + timedelta(days=60)
    month_col = travel_dt.strftime("%b") # e.g., "Mar"

    if selected_mode == "Find Destinations 🌍":
        if st.session_state.selected_country is None:
            st.success(f"✅ Found **{len(result_df)}** destinations across **{result_df['Full_Country'].nunique()}** countries")
            
            col_header, col_sort = st.columns([2, 1])
            with col_header:
                st.markdown("### Select a Country to Explore")
            with col_sort:
                sort_option = st.selectbox(
                    "Sort By",
                    options=["Popularity (High to Low)", "Popularity (Low to High)", "Price (Low to High)", "Price (High to Low)", "Name (A-Z)"],
                    key="sort_selection", label_visibility="collapsed"
                )
            
            country_groups = result_df.groupby('Full_Country').agg({
                'Trip_Cost': 'min',
                'Destination': 'count',
                'iso_country': 'first',
                'Popularity_Score': 'max' # Inherit the strongest city score for the country level breakdown
            }).reset_index().rename(columns={'Trip_Cost': 'Min_Price', 'Destination': 'City_Count'})
            
            if sort_option == "Popularity (High to Low)":
                country_groups = country_groups.sort_values(by=['Popularity_Score', 'Min_Price'], ascending=[False, True])
            elif sort_option == "Popularity (Low to High)":
                country_groups = country_groups.sort_values(by=['Popularity_Score', 'Min_Price'], ascending=[True, True])
            elif sort_option == "Price (Low to High)":
                country_groups = country_groups.sort_values(by='Min_Price', ascending=True)
            elif sort_option == "Price (High to Low)":
                country_groups = country_groups.sort_values(by='Min_Price', ascending=False)
            elif sort_option == "Name (A-Z)":
                country_groups = country_groups.sort_values(by='Full_Country', ascending=True)
            
            cols = st.columns(3)
            for idx, (index, c_row) in enumerate(country_groups.iterrows()):
                with cols[idx % 3]:
                    country_name = c_row['Full_Country']
                    iso_code = c_row['iso_country']
                    flag = get_flag_emoji(iso_code)
                    bold_country = make_bold(country_name)
                    formatted_price = f"${c_row['Min_Price']:,.0f}"
                    bold_price = make_bold(formatted_price)
                    btn_label = f"{flag} {bold_country}\n\n{int(c_row['City_Count'])} Cities  |  From {bold_price}"
                    if st.button(btn_label, key=f"nav_{country_name}", use_container_width=True):
                        st.session_state.selected_country = country_name
                        # V7.2.2: Ensure the city view inherits the country view sort immediately
                        st.session_state.sort_selection_city = st.session_state.sort_selection
                        st.rerun()

        else:
            # Child View (City Level)
            st.markdown("<div class='back-btn-wrapper'>", unsafe_allow_html=True)
            if st.button("⬅️ Back to All Countries", key="back_btn"):
                st.session_state.selected_country = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
                
            col_city_header, col_city_sort = st.columns([2, 1])
            with col_city_header:
                st.markdown(f"### Exploring {st.session_state.selected_country}")
            with col_city_sort:
                sort_option = st.selectbox(
                    "Sort By",
                    options=["Popularity (High to Low)", "Popularity (Low to High)", "Price (Low to High)", "Price (High to Low)", "Name (A-Z)"],
                    key="sort_selection_city", label_visibility="collapsed"
                )
                # Sync city sort back to master state if it changes
                if st.session_state.sort_selection_city != st.session_state.sort_selection:
                    st.session_state.sort_selection = st.session_state.sort_selection_city
                    st.rerun()
            
            # Apply Hierarchical Sorting
            result_df = result_df[result_df['Full_Country'] == st.session_state.selected_country].copy()
            
            # Key V7.2.2 Fix: Use the city-specific key for the actual sorting logic here
            city_sort = st.session_state.sort_selection_city
            if city_sort == "Popularity (High to Low)":
                result_df = result_df.sort_values(by=['Popularity_Score', 'Trip_Cost'], ascending=[False, True])
            elif city_sort == "Popularity (Low to High)":
                result_df = result_df.sort_values(by=['Popularity_Score', 'Trip_Cost'], ascending=[True, True])
            elif city_sort == "Price (Low to High)":
                result_df = result_df.sort_values(by='Trip_Cost', ascending=True)
            elif city_sort == "Price (High to Low)":
                result_df = result_df.sort_values(by='Trip_Cost', ascending=False)
            elif city_sort == "Name (A-Z)":
                result_df = result_df.sort_values(by='Destination', ascending=True)
            
            travel_date = travel_dt.strftime("%Y-%m-%d")
            cols = st.columns(3)
            
            for idx, (index, row) in enumerate(result_df.iterrows()):
                with cols[idx % 3]:
                    activities_html = "".join([f"<span class='activity-badge'>{ACTIVITY_EMOJIS.get(act, '🎯')} {act}</span>" for act in row['Activities']])
                    iata_code = row['IATA']
                    search_query = quote(row['Search_Term'])
                    
                    flight_suffix = "+Business+Class" if "Luxury" in flight_class_name else ""
                    flight_url = f"https://www.google.com/travel/flights?q=Flights+from+{origin_iata}+to+{iata_code}+on+{travel_date}{flight_suffix}"
                    hotel_url = get_booking_url(row['Search_Term'], accom_tier_name, travel_date)
                    
                    # Weather V6.2: Dual C/F Metric
                    temp_c = row[month_col]
                    if pd.notna(temp_c):
                        temp_f = (temp_c * 9/5) + 32
                        weather_label = f"{temp_c:.1f}°C ({temp_f:.0f}°F)"
                    else:
                        weather_label = "Season-dependent"
                    
                    st.markdown(f"""
                    <div class='travel-card'>
                        <div class='card-header'>{row['Destination']}</div>
                        <div class='card-metadata'>{row['Region']} • {weather_label}</div>
                        <div style='margin: 12px 0;'>{activities_html}</div>
                        <div class='price-container'>
                            <div class='price-big'>${row['Trip_Cost']:,.0f}</div>
                            <div class='price-small'>Approx. ${row['Trip_Cost'] / num_travelers:,.0f} per person</div>
                        </div>
                        <div class='breakdown'>
                            <p style='margin: 5px 0;'><strong>✈️ Flight:</strong> ${row['Total_Flight_Group']:,.0f}</p>
                            <p style='margin: 5px 0;'><strong>🏨 Hotel:</strong> ${row['Daily_Hotel_Group']:,.0f}/day</p>
                            <p style='margin: 5px 0;'><strong>🍽️ Daily spend:</strong> ${row['Daily_Food_Group'] + row['Daily_Transport_Group']:,.0f}</p>
                        </div>
                        <a href='{flight_url}' target='_blank' class='booking-button'>✈️ Book Flight</a>
                        <a href='{hotel_url}' target='_blank' class='booking-button'>🏨 Book Hotel</a>
                    </div>
                    """, unsafe_allow_html=True)

    else:
        # Price a Trip or Maximize Days
        st.markdown("### Trip Breakdown")
        travel_date = travel_dt.strftime("%Y-%m-%d")
        cols = st.columns(3)
        
        for idx, (index, row) in enumerate(result_df.iterrows()):
            with cols[idx % 3]:
                activities_html = "".join([f"<span class='activity-badge'>{ACTIVITY_EMOJIS.get(act, '🎯')} {act}</span>" for act in row['Activities']])
                iata_code = row['IATA']
                search_query = quote(row['Search_Term'])
                
                flight_suffix = "+Business+Class" if "Luxury" in flight_class_name else ""
                flight_url = f"https://www.google.com/travel/flights?q=Flights+from+{origin_iata}+to+{iata_code}+on+{travel_date}{flight_suffix}"
                hotel_url = get_booking_url(row['Search_Term'], accom_tier_name, travel_date)
                
                # Weather V6.2: Dual C/F Metric
                temp_c = row[month_col]
                if pd.notna(temp_c):
                    temp_f = (temp_c * 9/5) + 32
                    weather_label = f"{temp_c:.1f}°C ({temp_f:.0f}°F)"
                else:
                    weather_label = "Season-dependent"
                
                st.markdown(f"""
                <div class='travel-card'>
                    <div class='card-header'>{row['Destination']}</div>
                    <div class='card-metadata'>{row['Region']} • {weather_label}</div>
                    <div style='margin: 12px 0;'>{activities_html}</div>
                    <div class='price-container'>
                        <div class='price-big'>${row['Trip_Cost']:,.0f}</div>
                        <div class='price-small'>Approx. ${row['Trip_Cost'] / num_travelers:,.0f} per person</div>
                    </div>
                    <div class='breakdown'>
                        <p style='margin: 5px 0;'><strong>✈️ Flight:</strong> ${row['Total_Flight_Group']:,.0f}</p>
                        <p style='margin: 5px 0;'><strong>🏨 Hotel:</strong> ${row['Daily_Hotel_Group']:,.0f}/day</p>
                        <p style='margin: 5px 0;'><strong>🍽️ Daily spend:</strong> ${row['Daily_Food_Group'] + row['Daily_Transport_Group']:,.0f}</p>
                    </div>
                    <a href='{flight_url}' target='_blank' class='booking-button'>✈️ Book Flight</a>
                    <a href='{hotel_url}' target='_blank' class='booking-button'>🏨 Book Hotel</a>
                </div>
                """, unsafe_allow_html=True)
else:
    st.warning("😔 No destinations found matching your criteria.")

# --- SEO & About Section ---
st.divider()  # Adds a visual line separator

with st.expander("ℹ️ About WanderWise & How it Works", expanded=True):
    st.markdown("""
    ### **The Intelligent Reverse Trip Planner**
    
    **WanderWise** is a **reverse flight search engine** designed for budget travelers who want to maximize their experiences. Instead of asking *"Where do you want to go?"*, we ask *"What is your budget?"* and show you every possibility.
    
    #### **How We Find Cheap Vacation Destinations**
    Our algorithm combines real-time data to find the best value trips:
    * **Flight Costs:** We estimate average round-trip airfare from your origin city.
    * **Cost of Living:** We use global economic indexes to calculate daily expenses (food, hotel, transport) for each country.
    * **Your Budget:** We do the math to see exactly how many days you can afford to stay in 200+ countries.
    ßß
    #### **Why Use a Reverse Flight Search?**
    * **Find Hidden Gems:** Discover affordable countries like **Vietnam**, **Portugal**, or **Colombia** that fit your budget perfectly.
    * **Maximize Your Trip:** See exactly how many days your money will last in different parts of the world.
    * **Budget Travel Planning:** Compare expensive destinations vs. affordable alternatives side-by-side.
    
    *Built with ❤️ for travelers who want to see the world without breaking the bank.*
    """)