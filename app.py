import streamlit as st
import pandas as pd
import math
import random

# Set page config
st.set_page_config(page_title="Reverse Travel Planner", layout="wide")

# Constants
COUNTRY_TO_REGION = {
    # Europe
    "Switzerland": "Europe", "Iceland": "Europe", "Norway": "Europe", "Denmark": "Europe",
    "Austria": "Europe", "Ireland": "Europe", "France": "Europe", "Finland": "Europe",
    "Netherlands": "Europe", "Luxembourg": "Europe", "Germany": "Europe", "United Kingdom": "Europe",
    "Belgium": "Europe", "Sweden": "Europe", "Italy": "Europe", "Cyprus": "Europe",
    "Malta": "Europe", "Greece": "Europe", "Estonia": "Europe", "Slovenia": "Europe",
    "Latvia": "Europe", "Spain": "Europe", "Lithuania": "Europe", "Slovakia": "Europe",
    "Czech Republic": "Europe", "Croatia": "Europe", "Portugal": "Europe", "Albania": "Europe",
    "Hungary": "Europe", "Poland": "Europe", "Montenegro": "Europe", "Bulgaria": "Europe",
    "Serbia": "Europe", "Romania": "Europe", "Bosnia And Herzegovina": "Europe",
    "North Macedonia": "Europe", "Moldova": "Europe", "Russia": "Europe", "Belarus": "Europe",
    "Ukraine": "Europe", "Kosovo (Disputed Territory)": "Europe",
    
    # Asia (including Middle East)
    "Singapore": "Asia", "Hong Kong (China)": "Asia", "South Korea": "Asia",
    "United Arab Emirates": "Asia", "Bahrain": "Asia", "Qatar": "Asia", "Japan": "Asia",
    "Saudi Arabia": "Asia", "Taiwan": "Asia", "Oman": "Asia", "Kuwait": "Asia",
    "Lebanon": "Asia", "Palestine": "Asia", "Jordan": "Asia", "Armenia": "Asia",
    "Turkey": "Asia", "Cambodia": "Asia", "Thailand": "Asia", "Georgia": "Asia",
    "Kazakhstan": "Asia", "China": "Asia", "Azerbaijan": "Asia", "Philippines": "Asia",
    "Malaysia": "Asia", "Iraq": "Asia", "Vietnam": "Asia", "Kyrgyzstan": "Asia",
    "Indonesia": "Asia", "Iran": "Asia", "Uzbekistan": "Asia", "Syria": "Asia",
    "Bangladesh": "Asia", "India": "Asia", "Pakistan": "Asia", "Israel": "Asia",
    "Sri Lanka": "Asia", "Nepal": "Asia",

    # South America
    "Uruguay": "South America", "Chile": "South America", "Venezuela": "South America",
    "Ecuador": "South America", "Brazil": "South America", "Peru": "South America",
    "Argentina": "South America", "Colombia": "South America", "Bolivia": "South America",
    "Paraguay": "South America",
    
    # Oceania
    "Australia": "Oceania", "New Zealand": "Oceania", "Fiji": "Oceania",

    # Africa
    "Mauritius": "Africa", "South Africa": "Africa", "Nigeria": "Africa", "Ghana": "Africa",
    "Kenya": "Africa", "Botswana": "Africa", "Morocco": "Africa", "Uganda": "Africa",
    "Algeria": "Africa", "Tunisia": "Africa", "Madagascar": "Africa", "Tanzania": "Africa",
    "Egypt": "Africa", "Libya": "Africa", "Cameroon": "Africa", "Zimbabwe": "Africa",

    # North America
    "Bahamas": "North America", "Barbados": "North America", "United States": "North America",
    "Canada": "North America", "Puerto Rico": "North America", "Jamaica": "North America",
    "Trinidad And Tobago": "North America", "Costa Rica": "North America", "Cuba": "North America",
    "Panama": "North America", "El Salvador": "North America", "Guatemala": "North America",
    "Dominican Republic": "North America", "Mexico": "North America",
}

FLIGHT_COSTS_INTL = {
    "Europe": 850,
    "Asia": 1200,
    "South America": 700,
    "Africa": 1100,
    "Oceania": 1600,
    "North America": 400
}

# Granular Budget Multipliers V3
ACCOM_TIERS = {
    "Bare Essential (Hostel/1*)": 0.5,
    "Economy (2-3*)": 1.0,
    "Luxury (4-5*)": 4.0
}

ACTIVITY_TIERS = {
    "Bare Essential (Free/Cheap)": 0.5,
    "Standard": 1.0,
    "Extra Spend (Tours/Fine Dining)": 2.0
}

MOCK_ACTIVITIES_LIST = ['Beach', 'Hiking', 'Caves', 'Skiing', 'History', 'Nightlife', 'Foodie']
MOCK_WEATHER = ["Tropical", "Arid", "Temperate", "Snowy"]

@st.cache_data
def load_data():
    try:
        flights_df = pd.read_csv("Consumer_Airfare_Report__Table_1a_-_All_U.S._Airport_Pair_Markets.csv")
        flights_df.columns = flights_df.columns.str.strip()
        
        col_df = pd.read_csv("Cost_of_Living_Index_by_Country_2024.csv")
        col_df.columns = col_df.columns.str.strip()
        
        return flights_df, col_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

def enrich_data(df):
    # Mock Data Enrichment
    # We use hashing of destination name to make "random" data consistent across reloads
    
    def get_activities(name):
        random.seed(name) 
        # Pick 1-3 random activities
        k = random.randint(1, 3)
        return random.sample(MOCK_ACTIVITIES_LIST, k)

    def get_weather(name):
        random.seed(name + "w")
        return random.choice(MOCK_WEATHER)

    def get_safety(name):
        random.seed(name + "s")
        return random.randint(1, 5)

    df['Activities'] = df['Destination'].apply(get_activities)
    df['Weather'] = df['Destination'].apply(get_weather)
    df['Safety_Score'] = df['Destination'].apply(get_safety)
    return df

# Load Data
flights_raw, col_raw = load_data()

if flights_raw.empty or col_raw.empty:
    st.warning("Data not loaded. Please ensure CSV files are present.")
    st.stop()

# Title
st.title("Reverse Travel Planner V3 🌍")

# --- Sidebar Inputs ---

st.sidebar.header("1. Who is traveling?")
# Origin City
all_origins = sorted(flights_raw['city1'].unique().tolist())
default_origin_index = 0
if "New York City, NY (Metropolitan Area)" in all_origins:
    default_origin_index = all_origins.index("New York City, NY (Metropolitan Area)")
origin_city = st.sidebar.selectbox("Origin City", options=all_origins, index=default_origin_index)

# Travelers
num_travelers = st.sidebar.number_input("Number of Travelers", min_value=1, max_value=10, value=1)


st.sidebar.header("2. What is your flexible factor?")
flex_factor = st.sidebar.radio("Pick 2 of 3 Constraint", ["Destination", "Duration", "Budget"])

# Dynamic Inputs based on Flex Factor
target_dest = None
duration = 7 # default
total_budget = 3000.0 # default

if flex_factor == "Destination":
    # Logic A: Classic
    total_budget = st.sidebar.number_input("Total Group Budget ($)", min_value=100, value=3000, step=100)
    duration = st.sidebar.slider("Trip Duration (Days)", min_value=3, max_value=30, value=7)
    
elif flex_factor == "Duration":
    # Logic B: Time is flexible
    total_budget = st.sidebar.number_input("Total Group Budget ($)", min_value=100, value=3000, step=100)
    # We need a list of ALL possible destinations to pick one
    # Note: We haven't built the master destination list yet. We'll do a quick pass logic later or just let them pick from a pre-calculated list.
    # Ideally, we merge first then filter. But Sidebar renders first.
    # Let's placeholder this and populate it after logic or verify if we can do it smart.
    # We will compute the master list below and use a placeholder or session state if needed.
    # For MVP, let's just use the International Countries + US Cities list from raw data.
    us_dests = flights_raw['city2'].unique().tolist()
    intl_dests = col_raw['Country'].unique().tolist()
    all_dests = sorted(list(set(us_dests + intl_dests)))
    target_dest = st.sidebar.selectbox("Specific Destination", options=all_dests)

elif flex_factor == "Budget":
    # Logic C: Money is flexible
    duration = st.sidebar.slider("Trip Duration (Days)", min_value=3, max_value=30, value=7)
    us_dests = flights_raw['city2'].unique().tolist()
    intl_dests = col_raw['Country'].unique().tolist()
    all_dests = sorted(list(set(us_dests + intl_dests)))
    target_dest = st.sidebar.selectbox("Specific Destination", options=all_dests)


st.sidebar.header("3. Granular Budgeting")
accom_tier_name = st.sidebar.selectbox("Accommodation Style", options=list(ACCOM_TIERS.keys()), index=1)
accom_mult = ACCOM_TIERS[accom_tier_name]

act_tier_name = st.sidebar.selectbox("Activity/Food Style", options=list(ACTIVITY_TIERS.keys()), index=1)
act_mult = ACTIVITY_TIERS[act_tier_name]


st.sidebar.header("4. Filters (Opt)")
selected_activities = st.sidebar.multiselect("Must-have Activities", options=MOCK_ACTIVITIES_LIST)
safety_thresh = st.sidebar.slider("Minimum Safety Score", 1, 5, 1)


# --- Data Processing ---

# 1. Process US Data (Filtering by Origin)
us_filtered = flights_raw[flights_raw['city1'] == origin_city].copy()
if 'fare' in us_filtered.columns:
    us_data = us_filtered.groupby('city2')['fare'].mean().reset_index()
    us_data.rename(columns={'city2': 'Destination', 'fare': 'Base_Flight_Cost'}, inplace=True)
    us_data['Region'] = 'North America'
    us_data['Base_Daily_Cost'] = 176.0 
else:
    us_data = pd.DataFrame()

# 2. Process International Data
intl_data = col_raw.copy()
intl_data['Region'] = intl_data['Country'].map(COUNTRY_TO_REGION)
intl_data = intl_data.dropna(subset=['Region'])
intl_data['Base_Flight_Cost'] = intl_data['Region'].map(FLIGHT_COSTS_INTL)
intl_data['Base_Daily_Cost'] = intl_data['Cost of Living Index'] * 2.5
intl_data = intl_data[['Country', 'Region', 'Base_Flight_Cost', 'Base_Daily_Cost']].rename(columns={'Country': 'Destination'})

# 3. Merge & Enrich
if not us_data.empty:
    combined_df = pd.concat([us_data, intl_data], ignore_index=True)
else:
    combined_df = intl_data

combined_df = enrich_data(combined_df)

# --- Logic Engine (Pick 2 of 3) ---

# Apply Budget Logic to get daily costs
# Daily Food Cost = (Base Daily * 0.5) * Num Travelers * Food Multiplier
# Daily Hotel Cost = (Base Daily * 0.5) * Accom Multiplier * ceil(Num Travelers / 2)
combined_df['Daily_Food_Group'] = (combined_df['Base_Daily_Cost'] * 0.5) * num_travelers * act_mult
combined_df['Daily_Hotel_Group'] = (combined_df['Base_Daily_Cost'] * 0.5) * accom_mult * math.ceil(num_travelers / 2)
combined_df['Total_Daily_Group'] = combined_df['Daily_Food_Group'] + combined_df['Daily_Hotel_Group']
combined_df['Total_Flight_Group'] = combined_df['Base_Flight_Cost'] * 1.0 * num_travelers # Flight mult is 1.0 base, logic says simple multipliers for now

result_df = pd.DataFrame()
metric_display = None # (Label, Value)

if flex_factor == "Destination":
    # Logic A
    # Calculate Trip Cost for ALL destinations
    combined_df['Trip_Cost'] = combined_df['Total_Flight_Group'] + (combined_df['Total_Daily_Group'] * duration)
    
    # Filter by Budget
    result_df = combined_df[combined_df['Trip_Cost'] <= total_budget].copy()
    
    # Filter by Specific filters (Safety, Activity) logic below applying to all modes
    
elif flex_factor == "Duration":
    # Logic B
    # Find specific destination row
    row = combined_df[combined_df['Destination'] == target_dest]
    if not row.empty:
        # Calc Max Days = (Budget - Flight) / Daily_Group
        # If Budget < Flight, 0 days
        flight_cost = row['Total_Flight_Group'].values[0]
        daily_cost = row['Total_Daily_Group'].values[0]
        
        remaining_budget = total_budget - flight_cost
        if remaining_budget <= 0:
            max_days = 0
        else:
            max_days = math.floor(remaining_budget / daily_cost)
            
        metric_display = ("Days Possible", f"{max_days} Days")
        result_df = row.copy()
        result_df['Trip_Cost'] = flight_cost + (daily_cost * max_days)
        result_df['_Calculated_Duration'] = max_days
    else:
        st.error("Destination not found in data.")

elif flex_factor == "Budget":
    # Logic C
    row = combined_df[combined_df['Destination'] == target_dest]
    if not row.empty:
        # Calc Req Budget
        flight_cost = row['Total_Flight_Group'].values[0]
        daily_cost = row['Total_Daily_Group'].values[0]
        trip_cost = flight_cost + (daily_cost * duration)
        
        metric_display = ("Required Budget", f"${trip_cost:,.0f}")
        result_df = row.copy()
        result_df['Trip_Cost'] = trip_cost
    else:
        st.error("Destination not found in data.")

# --- Common Filtering (Activities & Safety) ---
if not result_df.empty:
    # Safety Filter
    result_df = result_df[result_df['Safety_Score'] >= safety_thresh]
    
    # Activity Filter
    if selected_activities:
        # Check if row['Activities'] (list) has intersection with selected_activities
        # We can use apply
        def has_activity(activity_list):
            return not set(selected_activities).isdisjoint(activity_list)
        
        result_df = result_df[result_df['Activities'].apply(has_activity)]

# --- Display ---

st.divider()

# Show Metric for Logic B/C
if metric_display and not result_df.empty:
    st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>{metric_display[0]}: {metric_display[1]}</h1>", unsafe_allow_html=True)
    if flex_factor == "Duration":
        st.caption(f"Based on ${total_budget:,} budget for {target_dest}")
    elif flex_factor == "Budget":
        st.caption(f"For {duration} days in {target_dest}")
    st.divider()


if not result_df.empty:
    if flex_factor == "Destination":
        st.success(f"Found {len(result_df)} destinations matching your criteria.")
        result_df = result_df.sort_values(by='Trip_Cost')

    cols = st.columns(3)
    
    for index, row in result_df.iterrows():
        col = cols[index % 3]
        
        with col:
            with st.container(border=True):
                st.subheader(f"{row['Destination']}")
                st.caption(f"{row['Region']} | {row['Weather']} | Safety: {row['Safety_Score']}/5")
                
                # Activity Tags
                tags_html = "".join([f"<span style='background-color: #eee; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-right: 4px;'>{act}</span>" for act in row['Activities']])
                st.markdown(tags_html, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Big Bold Cost
                cost_val = row['Trip_Cost']
                st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>${cost_val:,.0f}</h3>", unsafe_allow_html=True)
                
                # Breakdown
                flight_grp = row['Total_Flight_Group']
                daily_grp = row['Total_Daily_Group']
                
                st.markdown(f"**Flight Total:** ${flight_grp:,.0f}")
                st.markdown(f"**Daily Total:** ${daily_grp:,.0f}")
                
                # Per Person
                pp_cost = cost_val / num_travelers
                st.caption(f"Approx ${pp_cost:,.0f} per person")

else:
    st.warning("No destinations found matching all logic and filters.")
