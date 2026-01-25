import streamlit as st
import pandas as pd
import math
import random
from datetime import datetime, timedelta
from urllib.parse import quote
import pycountry

# Set page config
st.set_page_config(page_title="Reverse Travel Planner V5", layout="wide")

# Custom CSS for Pro Polish
st.markdown("""
<style>
    .travel-card {
        background-color: #262730;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #444;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .card-header {
        color: #fff;
        font-size: 1.3em;
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
    }
    
    .price-big {
        color: #4CAF50;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin: 15px 0;
    }
    
    .price-small {
        color: #aaa;
        font-size: 0.9em;
        text-align: center;
        margin-bottom: 15px;
    }
    
    .breakdown {
        color: #ccc;
        font-size: 0.85em;
        border-top: 1px solid #444;
        padding-top: 12px;
    }
    
    .booking-button {
        display: inline-block;
        padding: 10px 20px;
        margin: 5px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
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
    # Convert to string and handle NaN
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

def create_country_name_to_iso_map():
    """Create mapping from country name to ISO code using pycountry"""
    name_to_iso = {}
    for country in pycountry.countries:
        name_to_iso[country.name] = country.alpha_2
        # Add common alternative names
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

@st.cache_data
def load_real_data():
    """V5: Load and merge real airport data with cost of living indices"""
    
    try:
        # Step 1: Load Global Airports
        airports_url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
        airports_df = pd.read_csv(airports_url)
        
        # Filter for large and medium airports with valid IATA codes
        airports_df = airports_df[
            (airports_df['type'].isin(['large_airport', 'medium_airport'])) &
            (airports_df['iata_code'].notna())
        ].copy()
        
        # Keep only needed columns
        airports_df = airports_df[['ident', 'name', 'municipality', 'iso_country', 'iata_code']]
        
        # Step 2: Load Cost of Living Index
        col_df = pd.read_csv("Cost_of_Living_Index_by_Country_2024.csv")
        col_df.columns = col_df.columns.str.strip()
        
        # Step 3: Create country name to ISO code mapping
        name_to_iso = create_country_name_to_iso_map()
        
        # Map country names to ISO codes in cost of living data
        col_df['iso_country'] = col_df['Country'].map(name_to_iso)
        
        # Step 4: Merge airports with cost of living data
        merged_df = airports_df.merge(
            col_df[['iso_country', 'Cost of Living Index']],
            on='iso_country',
            how='left'
        )
        
        # Fill missing cost of living indices with global average
        global_avg = col_df['Cost of Living Index'].mean()
        merged_df['Cost of Living Index'].fillna(global_avg, inplace=True)
        
        # Step 5: Calculate costs
        # Daily Cost = CoL Index * 2.5
        merged_df['Est_Daily_Cost'] = merged_df['Cost of Living Index'] * 2.5
        
        # Map ISO country to region for flight costs
        merged_df['Region'] = merged_df['iso_country'].map(ISO_TO_REGION)
        merged_df['Region'].fillna('Other', inplace=True)
        
        # Assign regional flight costs
        merged_df['Avg_Flight_Cost'] = merged_df['Region'].map(REGION_FLIGHT_COSTS)
        merged_df['Avg_Flight_Cost'].fillna(800, inplace=True)  # Default for 'Other'
        
        # Step 6: Final formatting
        # Create Destination as "City, CountryCode"
        merged_df['Destination'] = merged_df['municipality'].fillna('Unknown').astype(str) + ', ' + merged_df['iso_country'].fillna('??').astype(str)
        
        # Ensure Destination is clean string and no NaNs
        merged_df = merged_df.dropna(subset=['Destination'])
        
        # Select and rename final columns
        final_df = merged_df[[
            'Destination', 'Region', 'Avg_Flight_Cost', 'Est_Daily_Cost', 'iata_code'
        ]].rename(columns={'iata_code': 'IATA'})
        
        # Remove duplicates (some cities have multiple airports)
        final_df = final_df.drop_duplicates(subset=['Destination'], keep='first')
        
        return final_df
        
    except Exception as e:
        st.error(f"Error loading real airport data: {e}")
        return pd.DataFrame()

def enrich_data(df):
    """Add mock enrichment data (activities, weather, safety, transport)"""
    def get_activities(name):
        # Convert to string and handle NaN
        name_str = str(name) if pd.notna(name) else "Unknown"
        random.seed(hash(name_str) % 10000)
        k = random.randint(2, 4)
        return random.sample(MOCK_ACTIVITIES_LIST, min(k, len(MOCK_ACTIVITIES_LIST)))

    def get_weather(name):
        # Convert to string and handle NaN
        name_str = str(name) if pd.notna(name) else "Unknown"
        random.seed(hash(name_str + "w") % 10000)
        return random.choice(MOCK_WEATHER)

    def get_safety(name):
        # Convert to string and handle NaN
        name_str = str(name) if pd.notna(name) else "Unknown"
        random.seed(hash(name_str + "s") % 10000)
        return random.randint(1, 5)

    df['Activities'] = df['Destination'].apply(get_activities)
    df['Weather'] = df['Destination'].apply(get_weather)
    df['Safety_Score'] = df['Destination'].apply(get_safety)
    df['Transport_Cost_Daily'] = df['Destination'].apply(calculate_transport_cost)
    
    return df

# Load Real Data
with st.spinner("Loading real airport and cost of living data..."):
    destinations_df = load_real_data()

if destinations_df.empty:
    st.error("Failed to load destination data. Please check your internet connection and local files.")
    st.stop()

# Enrich with mock data
destinations_df = enrich_data(destinations_df)

# Rename for compatibility with existing code
destinations_df.rename(columns={
    'Avg_Flight_Cost': 'Base_Flight_Cost',
    'Est_Daily_Cost': 'Base_Daily_Cost'
}, inplace=True)

# Title
st.title("🌍 Reverse Travel Planner V5")
st.caption("Powered by real global airport data and cost of living indices")

# --- Sidebar Navigation ---

st.sidebar.header("What is your goal?")

mode_options = ["Find Destinations 🌍", "Maximize Days 📅", "Price a Trip 💰"]
selected_mode = st.sidebar.pills("Navigation", mode_options, label_visibility="collapsed")

# Dynamic Explainer
if selected_mode == "Find Destinations 🌍":
    st.sidebar.info("ℹ️ Goal: You have a fixed budget and want to see all the places you can afford.")
elif selected_mode == "Maximize Days 📅":
    st.sidebar.info("ℹ️ Goal: You know where you want to go, and want to see how long you can stay.")
else:
    st.sidebar.info("ℹ️ Goal: You have a dream destination and duration, and want the total price tag.")

# Essential Trip Details
st.sidebar.subheader("Essential Trip Details")

# For V5, we'll use a simplified origin selection (major US airports)
major_us_airports = destinations_df[destinations_df['Destination'].str.contains(', US', na=False)]['Destination'].unique().tolist()
usable_origins = sorted([str(d) for d in major_us_airports if pd.notna(d)])
origin_city = st.sidebar.selectbox("✈️ Origin City", options=usable_origins[:50])  # Limit to 50 for UX

num_travelers = st.sidebar.number_input("👥 Number of Travelers", min_value=1, max_value=10, value=1)

# Dynamic Inputs
target_dest = None
duration = 7
total_budget = 3000.0

if selected_mode == "Find Destinations 🌍":
    total_budget = st.sidebar.number_input("💰 Total Group Budget ($)", min_value=100, value=3000, step=100)
    duration = st.sidebar.slider("📅 Trip Duration (Days)", min_value=3, max_value=30, value=7)
    
    # V4/V5: Real-Time Filters
    st.sidebar.subheader("🔍 Filters")
    selected_regions = st.sidebar.multiselect("🌎 Regions", 
                                               options=sorted(destinations_df['Region'].unique()),
                                               default=[])
    
    selected_weather = st.sidebar.multiselect("🌤️ Weather", 
                                               options=MOCK_WEATHER,
                                               default=[])
    
    selected_activities = st.sidebar.multiselect("🎯 Activities",
                                                  options=MOCK_ACTIVITIES_LIST,
                                                  default=[])
    
    safety_thresh = st.sidebar.slider("🛡️ Min Safety", 1, 5, 1)
    
elif selected_mode == "Maximize Days 📅":
    total_budget = st.sidebar.number_input("💰 Total Group Budget ($)", min_value=100, value=3000, step=100)
    all_dests = sorted([str(d) for d in destinations_df['Destination'].unique() if pd.notna(d)])
    target_dest = st.sidebar.selectbox("🎯 Select Your Destination", options=all_dests)
    selected_regions = []
    selected_weather = []
    selected_activities = []
    safety_thresh = 1

else:  # Price a Trip
    duration = st.sidebar.slider("📅 Trip Duration (Days)", min_value=3, max_value=30, value=7)
    all_dests = sorted(destinations_df['Destination'].unique())
    target_dest = st.sidebar.selectbox("🎯 Select Your Destination", options=all_dests)
    selected_regions = []
    selected_weather = []
    selected_activities = []
    safety_thresh = 1

# Travel Style Expander
with st.sidebar.expander("💸 Customize Spending & Style", expanded=False):
    st.markdown("**✈️ Flight Class**")
    flight_class_name = st.selectbox(
        "Choose your flight class",
        options=list(FLIGHT_CLASS_TIERS.keys()),
        index=1,
        help="This multiplier affects the base flight cost.",
        label_visibility="collapsed"
    )
    flight_mult = FLIGHT_CLASS_TIERS[flight_class_name]
    
    st.markdown("**🏨 Accommodation Level**")
    accom_tier_name = st.selectbox(
        "Choose your accommodation style",
        options=list(ACCOM_TIERS.keys()),
        index=1,
        label_visibility="collapsed"
    )
    accom_mult = ACCOM_TIERS[accom_tier_name]
    
    st.markdown("**🍽️ Food & Activities**")
    act_tier_name = st.selectbox(
        "Choose your food and activity spending",
        options=list(ACTIVITY_TIERS.keys()),
        index=1,
        label_visibility="collapsed"
    )
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
        if remaining_budget <= 0:
            max_days = 0
        else:
            max_days = math.floor(remaining_budget / daily_cost)
            
        metric_display = ("You can stay for", f"{max_days} Days")
        result_df = row.copy()
        result_df['Trip_Cost'] = flight_cost + (daily_cost * max_days)
        result_df['_Calculated_Duration'] = max_days
    else:
        st.error("Destination not found in data.")

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
        st.error("Destination not found in data.")

# Apply filters
if not result_df.empty:
    result_df = result_df[result_df['Safety_Score'] >= safety_thresh]
    
    if selected_regions:
        result_df = result_df[result_df['Region'].isin(selected_regions)]
    
    if selected_weather:
        result_df = result_df[result_df['Weather'].isin(selected_weather)]
    
    if selected_activities:
        def has_activity(activity_list):
            return not set(selected_activities).isdisjoint(activity_list)
        result_df = result_df[result_df['Activities'].apply(has_activity)]

# --- Display Results ---

if selected_mode == "Price a Trip 💰" and metric_display and not result_df.empty:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; 
                border-radius: 15px; 
                text-align: center; 
                margin-bottom: 30px;'>
        <h2 style='color: white; margin: 0; font-size: 1.2em;'>{metric_display[0]}</h2>
        <h1 style='color: white; margin: 10px 0; font-size: 3em;'>{metric_display[1]}</h1>
        <p style='color: rgba(255,255,255,0.8); margin: 0;'>for {duration} days in {target_dest}</p>
    </div>
    """, unsafe_allow_html=True)
elif selected_mode == "Maximize Days 📅" and metric_display and not result_df.empty:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                padding: 30px; 
                border-radius: 15px; 
                text-align: center; 
                margin-bottom: 30px;'>
        <h2 style='color: white; margin: 0; font-size: 1.2em;'>{metric_display[0]}</h2>
        <h1 style='color: white; margin: 10px 0; font-size: 3em;'>{metric_display[1]}</h1>
        <p style='color: rgba(255,255,255,0.8); margin: 0;'>in {target_dest} with ${total_budget:,.0f} budget</p>
    </div>
    """, unsafe_allow_html=True)

if not result_df.empty:
    if selected_mode == "Find Destinations 🌍":
        st.success(f"✅ Found **{len(result_df)}** destinations matching your criteria")
        result_df = result_df.sort_values(by='Trip_Cost')
    
    st.markdown("### Your Destinations" if selected_mode == "Find Destinations 🌍" else "### Trip Breakdown")
    
    # Calculate travel date (2 months from today)
    travel_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
    
    # Create grid of cards
    cols = st.columns(3)
    
    for idx, (index, row) in enumerate(result_df.iterrows()):
        col = cols[idx % 3]
        
        with col:
            activities_html = "".join([
                f"<span class='activity-badge'>{ACTIVITY_EMOJIS.get(act, '🎯')} {act}</span>"
                for act in row['Activities']
            ])
            
            safety_display = "🛡️" * row['Safety_Score']
            
            # V5: Use IATA code for better booking links
            iata_code = row.get('IATA', '')
            dest_encoded = quote(row['Destination'])
            
            flight_url = f"http://googleusercontent.com/google.com/travel/flights?q=Flights+to+{iata_code if iata_code else dest_encoded}+on+{travel_date}"
            hotel_url = f"https://www.booking.com/searchresults.html?ss={dest_encoded}&checkin={travel_date}"
            
            card_html = f"""
            <div class='travel-card'>
                <div class='card-header'>{row['Destination']}</div>
                <div class='card-metadata'>{row['Region']} • {row['Weather']} • {safety_display}</div>
                <div style='margin: 12px 0;'>
                    {activities_html}
                </div>
                <div class='price-big'>${row['Trip_Cost']:,.0f}</div>
                <div class='price-small'>Per person: ${row['Trip_Cost'] / num_travelers:,.0f}</div>
                <div class='breakdown'>
                    <p style='margin: 5px 0;'><strong>✈️ Flight:</strong> ${row['Total_Flight_Group']:,.0f}</p>
                    <p style='margin: 5px 0;'><strong>🏨 Hotel/Day:</strong> ${row['Daily_Hotel_Group']:,.0f}</p>
                    <p style='margin: 5px 0;'><strong>🍽️ Food/Day:</strong> ${row['Daily_Food_Group']:,.0f}</p>
                    <p style='margin: 5px 0;'><strong>🚗 Transport/Day:</strong> ${row['Daily_Transport_Group']:,.0f}</p>
                </div>
                <div style='text-align: center; margin-top: 15px;'>
                    <a href='{flight_url}' target='_blank' class='booking-button'>✈️ Book Flight</a>
                    <a href='{hotel_url}' target='_blank' class='booking-button'>🏨 Book Hotel</a>
                </div>
            </div>
            """
            
            st.markdown(card_html, unsafe_allow_html=True)

else:
    st.warning("😔 No destinations found matching your criteria. Try adjusting your filters or budget!")
