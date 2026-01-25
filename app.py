import streamlit as st
import pandas as pd
import math

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

TIER_MULTIPLIERS = {
    "Bare Essential": {"flight": 1.0, "daily": 0.5},
    "Economy": {"flight": 1.0, "daily": 1.0},
    "Mid Tier": {"flight": 1.5, "daily": 2.0},
    "Luxury": {"flight": 3.5, "daily": 4.0},
}

@st.cache_data
def load_data():
    try:
        flights_df = pd.read_csv("Consumer_Airfare_Report__Table_1a_-_All_U.S._Airport_Pair_Markets.csv")
        # Clean column names
        flights_df.columns = flights_df.columns.str.strip()
        
        col_df = pd.read_csv("Cost_of_Living_Index_by_Country_2024.csv")
        col_df.columns = col_df.columns.str.strip()
        
        return flights_df, col_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Load Data
flights_raw, col_raw = load_data()

if flights_raw.empty or col_raw.empty:
    st.warning("Data not loaded. Please ensure CSV files are present.")
    st.stop()

# Title
st.title("Reverse Travel Planner ✈️")

# --- Sidebar Inputs ---
st.sidebar.header("Trip Parameters")

# Origin City
all_origins = sorted(flights_raw['city1'].unique().tolist())
# Default to NYC if available
default_origin_index = 0
if "New York City, NY (Metropolitan Area)" in all_origins:
    default_origin_index = all_origins.index("New York City, NY (Metropolitan Area)")
origin_city = st.sidebar.selectbox("Origin City", options=all_origins, index=default_origin_index)

# Travelers
num_travelers = st.sidebar.number_input("Number of Travelers", min_value=1, max_value=10, value=1)

# Travel Style
travel_style = st.sidebar.selectbox("Travel Style", options=list(TIER_MULTIPLIERS.keys()), index=1)
tier_mults = TIER_MULTIPLIERS[travel_style]

# Budget & Duration
total_budget = st.sidebar.number_input("Total Group Budget ($)", min_value=100, value=3000, step=100)
duration = st.sidebar.slider("Trip Duration (Days)", min_value=3, max_value=14, value=7)


# --- Data Processing ---

# 1. Process US Data (Filtering by Origin)
# Filter for flights FROM the selected origin
us_filtered = flights_raw[flights_raw['city1'] == origin_city].copy()

# Group by city2 (Destination) and take mean fare
# Note: 'fare' is the column name based on previous inspection
if 'fare' in us_filtered.columns:
    us_data = us_filtered.groupby('city2')['fare'].mean().reset_index()
    us_data.rename(columns={'city2': 'Destination', 'fare': 'Base_Flight_Cost'}, inplace=True)
    us_data['Region'] = 'North America'
    us_data['Base_Daily_Cost'] = 176.0 # Static US daily cost
else:
    st.error("Column 'fare' not found in flights CSV.")
    us_data = pd.DataFrame()

# 2. Process International Data
intl_data = col_raw.copy()
intl_data['Region'] = intl_data['Country'].map(COUNTRY_TO_REGION)
intl_data = intl_data.dropna(subset=['Region']) # Drop unmapped

# Set Base Flight Cost from static map
intl_data['Base_Flight_Cost'] = intl_data['Region'].map(FLIGHT_COSTS_INTL)
# Set Base Daily Cost from Index
intl_data['Base_Daily_Cost'] = intl_data['Cost of Living Index'] * 2.5
intl_data = intl_data[['Country', 'Region', 'Base_Flight_Cost', 'Base_Daily_Cost']].rename(columns={'Country': 'Destination'})

# 3. Merge
if not us_data.empty:
    combined_df = pd.concat([us_data, intl_data], ignore_index=True)
else:
    combined_df = intl_data

# --- Math & Logic ---

# Apply Multipliers and Calculating Totals
# Total Flight Cost = Base Flight * Flight Multiplier * Num Travelers
combined_df['Total_Flight_Cost'] = combined_df['Base_Flight_Cost'] * tier_mults['flight'] * num_travelers

# Daily Components
# Food/Activity = (Base Daily * 0.5) * Num Travelers * Daily Multiplier
# Hotel = (Base Daily * 0.5) * Daily Multiplier * ceil(Num Travelers / 2)
daily_food_cost_group = (combined_df['Base_Daily_Cost'] * 0.5) * num_travelers * tier_mults['daily']
daily_hotel_cost_group = (combined_df['Base_Daily_Cost'] * 0.5) * tier_mults['daily'] * math.ceil(num_travelers / 2)

combined_df['Total_Daily_Cost'] = daily_food_cost_group + daily_hotel_cost_group

# Total Trip Cost
combined_df['Trip_Cost'] = combined_df['Total_Flight_Cost'] + (combined_df['Total_Daily_Cost'] * duration)

# Calculate Per Person Cost for Display
combined_df['Per_Person_Cost'] = combined_df['Trip_Cost'] / num_travelers

# Filtering
affordable_df = combined_df[combined_df['Trip_Cost'] <= total_budget].copy()
affordable_df.sort_values(by='Trip_Cost', ascending=True, inplace=True)

# --- Display ---

st.divider()

if not affordable_df.empty:
    st.success(f"Found {len(affordable_df)} destinations you can afford with a budget of ${total_budget:,}.")
    
    # Grid Layout
    # Iterate through rows and create columns
    # We'll use st.columns(3) in a loop
    
    cols = st.columns(3)
    
    for index, row in affordable_df.iterrows():
        # Cycle through columns 0, 1, 2
        col = cols[index % 3]
        
        with col:
            # Card Container
            with st.container(border=True):
                st.subheader(f"{row['Destination']}")
                st.caption(f"{row['Region']}")
                
                # Big Bold Total Cost
                st.markdown(f"<h3 style='text-align: center; color: #4CAF50;'>${row['Trip_Cost']:,.0f}</h3>", unsafe_allow_html=True)
                
                # Per Person (Small)
                st.markdown(f"<p style='text-align: center; font-size: 0.9em; color: gray;'>Per Person: ${row['Per_Person_Cost']:,.0f}</p>", unsafe_allow_html=True)
                
                st.divider()
                
                # Breakdown
                # "Flight: $X | Hotel/Day: $Y"
                # Using Total Flight Cost and Total Daily Cost
                flight_disp = f"${row['Total_Flight_Cost']:,.0f}"
                # For "Hotel/Day", looking at user prompt: "Breakdown: 'Flight: $X | Hotel/Day: $Y'"
                # The prompt explicitly asked for "Hotel/Day". 
                # Calculating separate Hotel Daily just for display? The user logic had 'Hotel Portion'.
                # Let's calculate that specific Hotel Portion Daily total again for display.
                # Hotel Daily Total = (Base * 0.5) * DailyMult * ceil(Travelers/2)
                # Basically it is `daily_hotel_cost_group` for this row.
                # Since we did vectorized calc above, we need to re-derive or store it. 
                # Let's just use Total Daily Cost which captures everything (Hotel + Food).
                # But to follow specific instruction "Hotel/Day", I'll isolate it.
                
                hotel_daily_val = (row['Base_Daily_Cost'] * 0.5) * tier_mults['daily'] * math.ceil(num_travelers / 2)
                
                st.markdown(f"**Flight:** {flight_disp}")
                st.markdown(f"**Hotel/Day:** ${hotel_daily_val:,.0f}")
                # Optional: Show Total Daily including food
                st.caption(f"(Total Daily: ${row['Total_Daily_Cost']:,.0f})")

else:
    st.error(f"No destinations found for ${total_budget:,} from {origin_city}.")
    st.info("Try increasing your budget, changing your travel style, or picking a different origin.")
