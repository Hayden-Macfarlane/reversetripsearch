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
        padding: 5px 15px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        height: auto !important;
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

# V5.9: Global Tourist Popularity Score (1-100)
# Based on UN Tourism / World Bank data for 2023/2024
COUNTRY_POPULARITY = {
    'France': 100, 'Spain': 98, 'United States': 95, 'Italy': 92, 'Turkey': 88,
    'Mexico': 85, 'United Kingdom': 82, 'Germany': 80, 'Greece': 78, 'Austria': 75,
    'Japan': 74, 'Thailand': 72, 'United Arab Emirates': 70, 'Saudi Arabia': 68,
    'Netherlands': 65, 'China': 64, 'Poland': 62, 'Croatia': 60, 'Portugal': 58,
    'Canada': 56, 'Singapore': 54, 'Vietnam': 52, 'Indonesia': 50, 'Switzerland': 48,
    'South Korea': 46, 'Egypt': 44, 'India': 42, 'Australia': 40, 'Brazil': 38,
    'Argentina': 36, 'Iceland': 35, 'Ireland': 34, 'New Zealand': 32, 'Norway': 30,
}

REGION_FLIGHT_COSTS = {
    "Europe": 850,
    "Asia": 1200,
    "South America": 700,
    "Africa": 1100,
    "Oceania": 1600,
    "North America": 400
}

ACCOM_TIERS = {
    "Bare Essential (Hostel/Camping)": 0.5,
    "Economy (2-3 Star Hotel / Basic Airbnb)": 1.0,
    "Luxury (4-5 Star / Resort)": 4.0
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

@st.cache_data
def load_real_data():
    """Load and merge real airport data with cost of living indices"""
    try:
        airports_url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
        airports_df = pd.read_csv(airports_url)
        
        # V5.7: Manually blacklist cities with no real commercial service
        blacklist_iata = ['BRX']
        airports_df = airports_df[~airports_df['iata_code'].isin(blacklist_iata)]
        
        # V5.2: Strict filtering for major hubs
        mask = (
            (airports_df['type'] == 'large_airport') | 
            ((airports_df['type'] == 'medium_airport') & airports_df['name'].str.contains('International', na=False))
        ) & (airports_df['scheduled_service'] == 'yes') & (airports_df['iata_code'].notna())
        
        airports_df = airports_df[mask].copy()
        
        # 1. V5.22: Atomic IATA Uniqueness & Safeguards
        # Fix known data anomalies immediately
        def fix_iata(row):
            iata = str(row['iata_code']).strip().upper()
            city = str(row['municipality']).lower()
            # Absolute Paris Safeguard
            if 'paris' in city and row['iso_country'] == 'FR' and iata == 'LGB':
                return 'CDG' # Correct a known anomaly if found
            return iata

        airports_df['iata_code'] = airports_df.apply(fix_iata, axis=1)
        
        # Ensure LGB is strictly US
        mask_lgb = (airports_df['iata_code'] == 'LGB') & (airports_df['iso_country'] != 'US')
        airports_df = airports_df[~mask_lgb].copy()

        # Deduplicate IATA early - Large hubs first
        airports_df = airports_df.sort_values(by='type', ascending=True)
        airports_df = airports_df.drop_duplicates(subset=['iata_code'], keep='first').reset_index(drop=True)
        
        # 2. Metadata Extraction
        airports_df['Clean_City'] = airports_df['municipality'].fillna('Unknown').str.split('(').str[0].str.strip()
        
        # 3. COL Merge (By Country)
        col_df = pd.read_csv("Cost_of_Living_Index_by_Country_2024.csv")
        col_df.columns = col_df.columns.str.strip()
        name_to_iso = create_country_name_to_iso_map()
        col_df['iso_country'] = col_df['Country'].map(name_to_iso)
        col_df = col_df.drop_duplicates(subset=['iso_country'], keep='first')
        
        merged_df = airports_df.merge(col_df[['iso_country', 'Cost of Living Index']], on='iso_country', how='left')
        
        # 4. Hub Significance Score (V5.20/V5.22)
        def score_hub(row):
            score = 0
            if row['type'] == 'large_airport': score += 100
            elif row['type'] == 'medium_airport': score += 50
            name_str = str(row['name']).lower()
            if 'international' in name_str: score += 30
            if 'global' in name_str: score += 20
            # Metropolitan matching
            city_match = str(row['Clean_City']).lower()
            if city_match in name_str: score += 40
            # Special Global Tier Hubs (CDG, LHR, HND, JFK)
            if any(hub in str(row['iata_code']) for hub in ['CDG', 'LHR', 'HND', 'JFK']): score += 500
            return score

        merged_df['Hub_Score'] = merged_df.apply(score_hub, axis=1)
        
        # 5. Final Deduplication (One primary hub per metropolis per nation)
        merged_df = merged_df.sort_values(by=['Clean_City', 'iso_country', 'Hub_Score'], ascending=[True, True, False])
        merged_df = merged_df.drop_duplicates(subset=['Clean_City', 'iso_country'], keep='first').reset_index(drop=True)

        # 6. ATOMIC TAGGING (Do all metadata in one step for absolute alignment)
        def generate_metadata(row):
            country = get_country_name(row['iso_country'])
            dest = f"{row['Clean_City']}, {row['iso_country']}"
            search = f"{row['Clean_City']}, {country}"
            return pd.Series([country, dest, search])

        merged_df[['Full_Country', 'Destination', 'Search_Term']] = merged_df.apply(generate_metadata, axis=1)
        
        # Costs
        global_avg = col_df['Cost of Living Index'].mean()
        merged_df['Cost of Living Index'].fillna(global_avg, inplace=True)
        merged_df['Est_Daily_Cost'] = merged_df['Cost of Living Index'] * 2.5
        merged_df['Region'] = merged_df['iso_country'].map(ISO_TO_REGION).fillna('Other')
        merged_df['Avg_Flight_Cost'] = merged_df['Region'].map(REGION_FLIGHT_COSTS).fillna(800)
        
        merged_df = merged_df.dropna(subset=['Destination'])
        
        return merged_df[[
            'Destination', 'Region', 'Avg_Flight_Cost', 'Est_Daily_Cost', 'iata_code', 'Search_Term', 'Full_Country', 'iso_country'
        ]].rename(columns={'iata_code': 'IATA'})
    except Exception as e:
        st.error(f"Error loading real airport data: {e}")
        return pd.DataFrame()

def enrich_data(df):
    """Add mock enrichment data (activities, weather, safety, transport)"""
    def get_activities(name):
        name_str = str(name) if pd.notna(name) else "Unknown"
        random.seed(hash(name_str) % 10000)
        k = random.randint(2, 4)
        return random.sample(MOCK_ACTIVITIES_LIST, min(k, len(MOCK_ACTIVITIES_LIST)))

    def get_weather(name):
        name_str = str(name) if pd.notna(name) else "Unknown"
        random.seed(hash(name_str + "w") % 10000)
        return random.choice(MOCK_WEATHER)

    def get_safety(name):
        name_str = str(name) if pd.notna(name) else "Unknown"
        random.seed(hash(name_str + "s") % 10000)
        return random.randint(1, 5)

    df['Activities'] = df['Destination'].apply(get_activities)
    df['Weather'] = df['Destination'].apply(get_weather)
    df['Safety_Score'] = df['Destination'].apply(get_safety)
    df['Transport_Cost_Daily'] = df['Destination'].apply(calculate_transport_cost)
    return df

# Load Real Data
with st.spinner("🚀 Booting WanderWise Data Engine..."):
    destinations_df = load_real_data()

if destinations_df.empty:
    st.error("Failed to load WanderWise data.")
    st.stop()

destinations_df = enrich_data(destinations_df)
destinations_df.rename(columns={'Avg_Flight_Cost': 'Base_Flight_Cost', 'Est_Daily_Cost': 'Base_Daily_Cost'}, inplace=True)

# Title
# Title Redesign (Centered & Massive Hero)
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

# Initialize drill-down state (V5.8)
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# Reset country selection if mode changes
if 'last_mode' not in st.session_state:
    st.session_state.last_mode = selected_mode
if st.session_state.last_mode != selected_mode:
    st.session_state.selected_country = None
    st.session_state.last_mode = selected_mode

# Shared airport list for both Origin and Destination (Synchronized)
all_usable_airports = sorted([str(d) for d in destinations_df['Destination'].unique() if pd.notna(d)])

# Smart Defaults (New York for origin, London for destination)
try:
    default_origin_idx = next(i for i, x in enumerate(all_usable_airports) if "New York" in x)
except StopIteration:
    default_origin_idx = 0

# Fix Default Logic (London, GB) - Priority fix for V5.4
try:
    default_dest_idx = next((i for i, x in enumerate(all_usable_airports) if x.startswith("London, GB") or x == "London, United Kingdom"), 0)
except StopIteration:
    default_dest_idx = 0

# Dynamic Explainer
if selected_mode == "Find Destinations 🌍":
    st.sidebar.info("ℹ️ Goal: You have a fixed budget and want to see all the places you can afford.")
elif selected_mode == "Maximize Days 📅":
    st.sidebar.info("ℹ️ Goal: You know where you want to go, and want to see how long you can stay.")
else:
    st.sidebar.info("ℹ️ Goal: You have a dream destination and duration, and want the total price tag.")

# Essential Trip Details
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
    selected_weather = st.sidebar.multiselect("🌤️ Weather", options=MOCK_WEATHER, default=[])
    selected_activities = st.sidebar.multiselect("🎯 Activities", options=MOCK_ACTIVITIES_LIST, default=[])
    safety_thresh = st.sidebar.slider("🛡️ Min Safety", 1, 5, 1)
    
elif selected_mode == "Maximize Days 📅":
    total_budget = st.sidebar.number_input("💰 Total Group Budget ($)", min_value=100, value=3000, step=100)
    target_dest = st.sidebar.selectbox("🎯 Select Your Destination", options=all_usable_airports, index=default_dest_idx)
    selected_regions, selected_weather, selected_activities, safety_thresh = [], [], [], 1

else:  # Price a Trip 💰
    duration = st.sidebar.slider("📅 Trip Duration (Days)", min_value=3, max_value=30, value=7)
    target_dest = st.sidebar.selectbox("🎯 Select Your Destination", options=all_usable_airports, index=default_dest_idx)
    selected_regions, selected_weather, selected_activities, safety_thresh = [], [], [], 1

# Sidebar Spacing
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

# --- Cost Calculations ---
destinations_df['Daily_Food_Group'] = (destinations_df['Base_Daily_Cost'] * 0.5) * num_travelers * act_mult
destinations_df['Daily_Hotel_Group'] = (destinations_df['Base_Daily_Cost'] * 0.5) * accom_mult * math.ceil(num_travelers / 2)
destinations_df['Daily_Transport_Group'] = destinations_df['Transport_Cost_Daily'] * num_travelers
destinations_df['Total_Daily_Group'] = destinations_df['Daily_Food_Group'] + destinations_df['Daily_Hotel_Group'] + destinations_df['Daily_Transport_Group']
destinations_df['Total_Flight_Group'] = destinations_df['Base_Flight_Cost'] * flight_mult * num_travelers

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

# Apply filters
if not result_df.empty:
    result_df = result_df[result_df['Safety_Score'] >= safety_thresh]
    if selected_regions: result_df = result_df[result_df['Region'].isin(selected_regions)]
    if selected_weather: result_df = result_df[result_df['Weather'].isin(selected_weather)]
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
    if selected_mode == "Find Destinations 🌍":
        # Hierarchical Navigation Logic (V5.8)
        if st.session_state.selected_country is None:
            # Transition Logic
            st.success(f"✅ Found **{len(result_df)}** destinations across **{result_df['Full_Country'].nunique()}** countries")
            
            # V5.16: Sort Controls
            col_header, col_sort = st.columns([2, 1])
            with col_header:
                st.markdown("### Select a Country to Explore")
            with col_sort:
                sort_option = st.selectbox(
                    "Sort By",
                    options=["Popularity (High to Low)", "Popularity (Low to High)", "Price (Low to High)", "Price (High to Low)", "Name (A-Z)"],
                    index=0,
                    label_visibility="collapsed"
                )
            
            # Group by Country for Parent View
            country_groups = result_df.groupby('Full_Country').agg({
                'Trip_Cost': 'min',
                'Destination': 'count',
                'iso_country': 'first'
            }).reset_index().rename(columns={'Trip_Cost': 'Min_Price', 'Destination': 'City_Count'})
            
            # V5.9 / V5.16: Sorting Logic
            country_groups['Popularity'] = country_groups['Full_Country'].map(COUNTRY_POPULARITY).fillna(10)
            
            if sort_option == "Popularity (High to Low)":
                country_groups = country_groups.sort_values(by=['Popularity', 'Min_Price'], ascending=[False, True])
            elif sort_option == "Popularity (Low to High)":
                country_groups = country_groups.sort_values(by=['Popularity', 'Min_Price'], ascending=[True, True])
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
                    
                    # V5.14: Unicode-Bold Card Label Construction
                    bold_country = make_bold(country_name)
                    formatted_price = f"${c_row['Min_Price']:,.0f}"
                    bold_price = make_bold(formatted_price)
                    
                    # Construction: Flag + Bold Name \n\n {cities} Cities | From {bold_price}
                    btn_label = f"{flag} {bold_country}\n\n{int(c_row['City_Count'])} Cities  |  From {bold_price}"
                    
                    if st.button(btn_label, key=f"nav_{country_name}"):
                        st.session_state.selected_country = country_name
                        st.rerun()
                    


        else:
            # Child View (City Level)
            st.markdown("<div class='back-btn-wrapper'>", unsafe_allow_html=True)
            if st.button("⬅️ Back to All Countries", key="back_btn"):
                st.session_state.selected_country = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
                
            st.markdown(f"### Exploring {st.session_state.selected_country}")
            result_df = result_df[result_df['Full_Country'] == st.session_state.selected_country].sort_values(by='Trip_Cost')
            
            travel_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
            cols = st.columns(3)
            
            for idx, (index, row) in enumerate(result_df.iterrows()):
                with cols[idx % 3]:
                    activities_html = "".join([f"<span class='activity-badge'>{ACTIVITY_EMOJIS.get(act, '🎯')} {act}</span>" for act in row['Activities']])
                    iata_code = row['IATA']
                    search_query = quote(row['Search_Term'])
                    
                    # V5.23: Luxury-to-Business Flight Alignment
                    flight_suffix = "+Business+Class" if "Luxury" in flight_class_name else ""
                    hotel_suffix = "+5+star+hotel" if "Luxury" in accom_tier_name else ""
                    
                    flight_url = f"https://www.google.com/travel/flights?q=Flights+to+{iata_code}+on+{travel_date}{flight_suffix}"
                    hotel_url = f"https://www.booking.com/searchresults.html?ss={search_query}+{hotel_suffix}&checkin={travel_date}"
                    
                    st.markdown(f"""
                    <div class='travel-card'>
                        <div class='card-header'>{row['Destination']}</div>
                        <div class='card-metadata'>{row['Region']} • {row['Weather']} • {"🛡️" * row['Safety_Score']}</div>
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
        # Price a Trip or Maximize Days (Existing Logic)
        st.markdown("### Trip Breakdown")
        travel_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        cols = st.columns(3)
        
        for idx, (index, row) in enumerate(result_df.iterrows()):
            with cols[idx % 3]:
                activities_html = "".join([f"<span class='activity-badge'>{ACTIVITY_EMOJIS.get(act, '🎯')} {act}</span>" for act in row['Activities']])
                iata_code = row['IATA']
                search_query = quote(row['Search_Term'])
                
                # V5.23: Luxury-to-Business Flight Alignment
                flight_suffix = "+Business+Class" if "Luxury" in flight_class_name else ""
                hotel_suffix = "+5+star+hotel" if "Luxury" in accom_tier_name else ""
                
                flight_url = f"https://www.google.com/travel/flights?q=Flights+to+{iata_code}+on+{travel_date}{flight_suffix}"
                hotel_url = f"https://www.booking.com/searchresults.html?ss={search_query}+{hotel_suffix}&checkin={travel_date}"
                
                st.markdown(f"""
                <div class='travel-card'>
                    <div class='card-header'>{row['Destination']}</div>
                    <div class='card-metadata'>{row['Region']} • {row['Weather']} • {"🛡️" * row['Safety_Score']}</div>
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
