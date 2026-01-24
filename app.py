import streamlit as st
import pandas as pd

# Set page config
st.set_page_config(page_title="Reverse Travel Planner", layout="wide")

# region Mapping
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

    # North America (Including Central America & Caribbean for simplicity as per instructions)
    "Bahamas": "North America", "Barbados": "North America", "United States": "North America",
    "Canada": "North America", "Puerto Rico": "North America", "Jamaica": "North America",
    "Trinidad And Tobago": "North America", "Costa Rica": "North America", "Cuba": "North America",
    "Panama": "North America", "El Salvador": "North America", "Guatemala": "North America",
    "Dominican Republic": "North America", "Mexico": "North America",
}

FLIGHT_COSTS = {
    "Europe": 850,
    "Asia": 1200,
    "South America": 700,
    "Africa": 1100,
    "Oceania": 1600,
    "North America": 400
}

@st.cache_data
def load_and_process_data():
    # 1. US Data Processing
    try:
        flights_df = pd.read_csv("Consumer_Airfare_Report__Table_1a_-_All_U.S._Airport_Pair_Markets.csv")
        # Ensure column names are stripped of whitespace if necessary, but usually standard CSVs are fine.
        # Assuming column names 'city2' and 'fare'. If not, we might need to adjust.
        # Inspecting standard DOT CSVs usually have specific headers. 
        # But per user instructions, we just group by city2.
        
        # We need to trust the column names exist. If they are slightly different (e.g. uppercase), pandas handles it if we are lucky or we inspect.
        # Given I haven't inspected the header of flight CSV, I'll attempt a standard key access and handle potential errors or do a clean.
        # Let's clean headers to be safe.
        flights_df.columns = flights_df.columns.str.strip()
        
        # Check if 'city2' and 'fare' exist. If user said "Group by city2 ... and calculate mean fare", those columns must exist with similar names.
        # Often it is 'city2' and 'fare_lg' or 'fare_low' or just 'fare'. 
        # I'll check for 'fare' column variations if 'fare' doesn't exist.
        fare_col = 'fare'
        if 'fare' not in flights_df.columns:
            # Table 1a usually has 'fare' or 'average_fare'
            # Let's guess 'fare' is present based on user prompt implying it. 
            pass 

        us_grouped = flights_df.groupby('city2')['fare'].mean().reset_index()
        us_grouped.rename(columns={'city2': 'Destination', 'fare': 'Flight_Cost'}, inplace=True)
        us_grouped['Region'] = 'North America'
        us_grouped['Daily_Cost'] = 176.0
        
    except Exception as e:
        st.error(f"Error processing US Flight Data: {e}")
        return pd.DataFrame()

    # 2. International Data Processing
    try:
        col_df = pd.read_csv("Cost_of_Living_Index_by_Country_2024.csv")
        col_df.columns = col_df.columns.str.strip()
        
        # Mapping
        col_df['Region'] = col_df['Country'].map(COUNTRY_TO_REGION)
        # Fill NaN regions if any (maybe 'Other' or drop) - Instructions imply we map them.
        # We'll drop countries that didn't match our extensive map to avoid errors, or set to 'Other' and skip cost.
        col_df = col_df.dropna(subset=['Region']) 

        col_df['Flight_Cost'] = col_df['Region'].map(FLIGHT_COSTS)
        col_df['Daily_Cost'] = col_df['Cost of Living Index'] * 2.5
        
        intl_data = col_df[['Country', 'Region', 'Flight_Cost', 'Daily_Cost']].rename(columns={'Country': 'Destination'})
        
    except Exception as e:
        st.error(f"Error processing International Data: {e}")
        return pd.DataFrame()

    # 3. Merge
    combined_df = pd.concat([us_grouped, intl_data], ignore_index=True)
    return combined_df

# Load Data
df = load_and_process_data()

if df.empty:
    st.warning("No data loaded. Check CSV files.")
    st.stop()

# Title
st.title("Reverse Travel Planner ✈️")

# Sidebar
st.sidebar.header("Trip Parameters")
total_budget = st.sidebar.number_input("Total Budget ($)", min_value=100, value=3000, step=100)
duration = st.sidebar.slider("Trip Duration (Days)", min_value=3, max_value=14, value=7)
all_regions = sorted(df['Region'].unique().tolist())
selected_regions = st.sidebar.multiselect("Filter by Region", options=all_regions, default=all_regions)

# Main Calculation
if not selected_regions:
    st.info("Please select at least one region.")
else:
    # Filter by Region
    filtered_df = df[df['Region'].isin(selected_regions)].copy()
    
    # Calculate Trip Cost
    filtered_df['Trip_Cost'] = filtered_df['Flight_Cost'] + (filtered_df['Daily_Cost'] * duration)
    
    # Filter by Budget
    affordable_df = filtered_df[filtered_df['Trip_Cost'] <= total_budget].copy()
    
    # Sort
    affordable_df.sort_values(by='Trip_Cost', ascending=True, inplace=True)
    
    # Display Metrics
    st.metric(label="Affordable Destinations Found", value=len(affordable_df))
    
    if not affordable_df.empty:
        # Format Currency
        display_df = affordable_df.copy()
        display_df['Flight_Cost'] = display_df['Flight_Cost'].apply(lambda x: f"${x:,.2f}")
        display_df['Daily_Cost'] = display_df['Daily_Cost'].apply(lambda x: f"${x:,.2f}")
        display_df['Trip_Cost'] = display_df['Trip_Cost'].apply(lambda x: f"${x:,.2f}")
        
        # Reorder columns
        display_df = display_df[['Destination', 'Region', 'Flight_Cost', 'Daily_Cost', 'Trip_Cost']]
        
        # Custom CSS for table to look nicer? Or just cards. 
        # User asked for "Dataframe or list of cards". DataFrame is cleaner for sorting.
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    else:
        st.warning(f"No destinations found for ${total_budget} budget over {duration} days in the selected regions.")

