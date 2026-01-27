import pandas as pd
import numpy as np
import pycountry
import math
import re

# --- Constants & Helpers ---
ISO_TO_REGION = {
    'CH': 'Europe', 'IS': 'Europe', 'NO': 'Europe', 'DK': 'Europe', 'AT': 'Europe',
    'IE': 'Europe', 'FR': 'Europe', 'FI': 'Europe', 'NL': 'Europe', 'LU': 'Europe',
    'DE': 'Europe', 'GB': 'Europe', 'BE': 'Europe', 'SE': 'Europe', 'IT': 'Europe',
    'CY': 'Europe', 'MT': 'Europe', 'GR': 'Europe', 'EE': 'Europe', 'SI': 'Europe',
    'LV': 'Europe', 'ES': 'Europe', 'LT': 'Europe', 'SK': 'Europe', 'CZ': 'Europe',
    'HR': 'Europe', 'PT': 'Europe', 'AL': 'Europe', 'HU': 'Europe', 'PL': 'Europe',
    'ME': 'Europe', 'BG': 'Europe', 'RS': 'Europe', 'RO': 'Europe', 'BA': 'Europe',
    'MK': 'Europe', 'MD': 'Europe', 'RU': 'Europe', 'BY': 'Europe', 'UA': 'Europe',
    'SG': 'Asia', 'HK': 'Asia', 'KR': 'Asia', 'AE': 'Asia', 'BH': 'Asia',
    'QA': 'Asia', 'JP': 'Asia', 'SA': 'Asia', 'TW': 'Asia', 'OM': 'Asia',
    'KW': 'Asia', 'LB': 'Asia', 'PS': 'Asia', 'JO': 'Asia', 'AM': 'Asia',
    'TR': 'Asia', 'KH': 'Asia', 'TH': 'Asia', 'GE': 'Asia', 'KZ': 'Asia',
    'CN': 'Asia', 'AZ': 'Asia', 'PH': 'Asia', 'MY': 'Asia', 'IQ': 'Asia',
    'VN': 'Asia', 'KG': 'Asia', 'ID': 'Asia', 'IR': 'Asia', 'UZ': 'Asia',
    'SY': 'Asia', 'BD': 'Asia', 'IN': 'Asia', 'PK': 'Asia', 'IL': 'Asia',
    'LK': 'Asia', 'NP': 'Asia',
    'UY': 'South America', 'CL': 'South America', 'VE': 'South America',
    'EC': 'South America', 'BR': 'South America', 'PE': 'South America',
    'AR': 'South America', 'CO': 'South America', 'BO': 'South America',
    'PY': 'South America',
    'AU': 'Oceania', 'NZ': 'Oceania', 'FJ': 'Oceania',
    'MU': 'Africa', 'ZA': 'Africa', 'NG': 'Africa', 'GH': 'Africa',
    'KE': 'Africa', 'BW': 'Africa', 'MA': 'Africa', 'UG': 'Africa',
    'DZ': 'Africa', 'TN': 'Africa', 'MG': 'Africa', 'TZ': 'Africa',
    'EG': 'Africa', 'LY': 'Africa', 'CM': 'Africa', 'ZW': 'Africa',
    'BS': 'North America', 'BB': 'North America', 'US': 'North America',
    'CA': 'North America', 'PR': 'North America', 'JM': 'North America',
    'TT': 'North America', 'CR': 'North America', 'CU': 'North America',
    'PA': 'North America', 'SV': 'North America', 'GT': 'North America',
    'DO': 'North America', 'MX': 'North America',
}

REGION_FLIGHT_COSTS = {
    "Europe": 850, "Asia": 1200, "South America": 700,
    "Africa": 1100, "Oceania": 1600, "North America": 400
}

def get_country_name(iso_code):
    try:
        country = pycountry.countries.get(alpha_2=iso_code)
        return country.name if country else iso_code
    except:
        return iso_code

def create_name_to_iso_map():
    mapping = {}
    for country in pycountry.countries:
        mapping[country.name] = country.alpha_2
        if hasattr(country, 'common_name'):
            mapping[country.common_name] = country.alpha_2
    mapping.update({
        'United States': 'US', 'United Kingdom': 'GB', 'South Korea': 'KR',
        'Hong Kong (China)': 'HK', 'Palestine': 'PS', 'Kosovo': 'XK',
        'Bosnia And Herzegovina': 'BA', 'Trinidad And Tobago': 'TT',
        'Vietnam': 'VN', 'Russia': 'RU'
    })
    return mapping

COUNTRY_POPULARITY = {
    'France': 100, 'Spain': 98, 'United States': 95, 'Italy': 92, 'Turkey': 88,
    'Mexico': 85, 'United Kingdom': 82, 'Germany': 80, 'Greece': 78, 'Austria': 75,
    'Japan': 74, 'Thailand': 72, 'United Arab Emirates': 70, 'Saudi Arabia': 68,
    'Netherlands': 65, 'China': 64, 'Poland': 62, 'Croatia': 60, 'Portugal': 58,
    'Canada': 56, 'Singapore': 54, 'Vietnam': 52, 'Indonesia': 50, 'Switzerland': 48,
    'South Korea': 46, 'Egypt': 44, 'India': 42, 'Australia': 40, 'Brazil': 38,
    'Argentina': 36, 'Iceland': 35, 'Ireland': 34, 'New Zealand': 32, 'Norway': 30,
}

def clean_temp(val):
    if pd.isna(val): return np.nan
    try:
        match = re.search(r'([-+]?\d*\.\d+|\d+)', str(val))
        return float(match.group(1)) if match else np.nan
    except:
        return np.nan

# --- V9.0: GLOBAL TRAVEL ANCHORS (Top-Tier Destinations) ---
TIER_1_ANCHORS = {
    'London', 'Paris', 'New York', 'Tokyo', 'Dubai', 'Singapore', 'Amsterdam', 'Madrid', 
    'Rome', 'Bangkok', 'Istanbul', 'Seoul', 'Sydney', 'Barcelona', 'Mexico City', 
    'Hong Kong', 'Las Vegas', 'Orlando', 'Miami', 'Los Angeles', 'Chicago', 'San Francisco', 
    'Venice', 'Florence', 'Lisbon', 'Berlin', 'Zurich', 'Geneva', 'Cancun', 'Bali', 'Phuket'
}

TIER_2_ANCHORS = {
    'Vancouver', 'Toronto', 'Washington', 'Seattle', 'Boston', 'Philadelphia', 'Atlanta', 'Dallas', 
    'Houston', 'Phoenix', 'San Diego', 'Denver', 'Nashville', 'New Orleans', 'Austin', 
    'Montreal', 'Dublin', 'Edinburgh', 'Brussels', 'Frankfurt', 'Munich', 'Milan', 'Nice', 
    'Athens', 'Warsaw', 'Tel Aviv', 'Abu Dhabi', 'Doha', 'Riyadh', 'Beijing', 'Shanghai', 
    'Kyoto', 'Osaka', 'Auckland', 'Melbourne'
}

GLOBAL_GATEWAYS = {'LHR', 'CDG', 'JFK', 'HND', 'DXB', 'SIN', 'HKG', 'IST', 'AMS', 'FRA', 'PEK', 'HND', 'ICN'}

def run_data_prep():
    print("🚀 Starting WanderWise V9.0 Build-Time Data Engine...")
    
    # 1. Load All 4 Raw Inputs
    airports_url = "https://davidmegginson.github.io/ourairports-data/airports.csv"
    df_airports = pd.read_csv(airports_url)
    df_col_country = pd.read_csv("Cost_of_Living_Index_by_Country_2024.csv")
    df_col_country.columns = df_col_country.columns.str.strip()
    df_col_city = pd.read_csv("Cost_of_living_index_by_city.csv")
    df_col_city.columns = df_col_city.columns.str.strip()
    df_weather = pd.read_csv("avg_temp_cities.csv")
    
    # 2. Process Airports (Atomic V5.22 Logic)
    mask = (
        (df_airports['type'] == 'large_airport') | 
        ((df_airports['type'] == 'medium_airport') & df_airports['name'].str.contains('International', na=False))
    ) & (df_airports['scheduled_service'] == 'yes') & (df_airports['iata_code'].notna())
    df_airports = df_airports[mask].copy()
    
    def fix_iata(row):
        iata = str(row['iata_code']).strip().upper()
        city = str(row['municipality']).lower()
        if 'paris' in city and row['iso_country'] == 'FR' and iata == 'LGB': return 'CDG'
        return iata
    df_airports['iata_code'] = df_airports.apply(fix_iata, axis=1)
    df_airports = df_airports[~((df_airports['iata_code'] == 'LGB') & (df_airports['iso_country'] != 'US'))]
    
    df_airports = df_airports.sort_values(by='type', ascending=True)
    df_airports = df_airports.drop_duplicates(subset=['iata_code'], keep='first').reset_index(drop=True)
    df_airports['Clean_City'] = df_airports['municipality'].fillna('Unknown').str.split('(').str[0].str.strip()
    df_airports['Full_Country'] = df_airports['iso_country'].apply(get_country_name)
    
    # --- V9.0: CALCULATE HUB DENSITY (Unique scheduled airports per city) ---
    city_counts = df_airports.groupby(['municipality', 'iso_country']).size().reset_index(name='Airport_Density')
    df_airports = df_airports.merge(city_counts, on=['municipality', 'iso_country'], how='left')

    # 3. Process City COL Metadata for Merge
    def parse_city_col(row):
        parts = [p.strip() for p in row['City'].split(',')]
        return parts[0], parts[-1]
    df_col_city[['Match_City', 'Match_Country']] = df_col_city.apply(
        lambda r: pd.Series(parse_city_col(r)), axis=1
    )
    
    # 4. Process Weather Metadata for Merge
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for m in months:
        df_weather[m] = df_weather[m].apply(clean_temp)
    
    # 5. MERGE PIPELINE
    name_to_iso = create_name_to_iso_map()
    df_col_country['iso_country'] = df_col_country['Country'].map(name_to_iso)
    df_col_country = df_col_country.drop_duplicates(subset=['iso_country'], keep='first')
    
    master = df_airports.merge(
        df_col_country[['iso_country', 'Cost of Living Index', 'Rent Index', 'Restaurant Price Index']],
        on='iso_country', how='left'
    )
    
    city_master = master.merge(
        df_col_city[['Match_City', 'Match_Country', 'Cost of Living Index', 'Rent Index', 'Restaurant Price Index']],
        left_on=['Clean_City', 'Full_Country'], right_on=['Match_City', 'Match_Country'],
        how='left', suffixes=('', '_City')
    )
    
    for col in ['Cost of Living Index', 'Rent Index', 'Restaurant Price Index']:
        city_master[col] = city_master[col + '_City'].fillna(city_master[col])
    
    weather_master = city_master.merge(
        df_weather[['City', 'Country'] + months],
        left_on=['Clean_City', 'Full_Country'], right_on=['City', 'Country'],
        how='left', suffixes=('', '_W')
    )
    
    country_weather_avg = df_weather.groupby('Country')[months].mean().reset_index()
    weather_master = weather_master.merge(
        country_weather_avg, left_on='Full_Country', right_on='Country',
        how='left', suffixes=('', '_C_Avg')
    )
    for m in months:
        weather_master[m] = weather_master[m].fillna(weather_master[m + '_C_Avg'])
    
    # 6. INTELLIGENT POPULARITY ENGINE (V9.0)
    def calculate_popularity(row):
        score = 0
        country_score = COUNTRY_POPULARITY.get(row['Full_Country'], 10)
        score += country_score * 0.3 # Base (Max 30)
        
        city_name = str(row['Clean_City'])
        if city_name in TIER_1_ANCHORS: score += 40
        elif city_name in TIER_2_ANCHORS: score += 20
        
        # Density Bonus: 5 pts per unique scheduled airport (Max 15)
        density = min(row['Airport_Density'], 3)
        score += density * 5
        
        # Global Gateway Bonus
        if str(row['iata_code']) in GLOBAL_GATEWAYS: score += 15
        
        # Hub Score Bonus (Native quality metric)
        def score_hub_lite(r):
            s = 0
            if r['type'] == 'large_airport': s += 5
            if 'International' in str(r['name']): s += 2
            return s
        score += score_hub_lite(row)
        
        return min(max(score, 10), 100) # Norm to 10-100 range

    weather_master['Popularity_Score'] = weather_master.apply(calculate_popularity, axis=1)
    
    # Second Pass: Deduplication
    # Prioritize hub score/type for selection within same city
    def score_hub_legacy(row):
        score = 0
        if row['type'] == 'large_airport': score += 100
        elif row['type'] == 'medium_airport': score += 50
        if 'international' in str(row['name']).lower(): score += 30
        if any(hub in str(row['iata_code']) for hub in ['CDG', 'LHR', 'HND', 'JFK']): score += 500
        return score
    
    weather_master['Legacy_Hub_Score'] = weather_master.apply(score_hub_legacy, axis=1)
    weather_master = weather_master.sort_values(by=['municipality', 'iso_country', 'Legacy_Hub_Score'], ascending=[True, True, False])
    final = weather_master.drop_duplicates(subset=['municipality', 'iso_country'], keep='first').reset_index(drop=True)

    # 7. PRE-CALCULATIONS
    final['Daily_Cost_Budget'] = (final['Cost of Living Index'] * 1.5) + (final['Rent Index'] * 0.5)
    final['Daily_Cost_Luxury'] = (final['Cost of Living Index'] * 3.0) + (final['Rent Index'] * 5.0)
    
    global_avg_col = df_col_country['Cost of Living Index'].mean()
    global_avg_rent = df_col_country['Rent Index'].mean()
    final['Daily_Cost_Budget'] = final['Daily_Cost_Budget'].fillna((global_avg_col * 1.5) + (global_avg_rent * 0.5))
    final['Daily_Cost_Luxury'] = final['Daily_Cost_Luxury'].fillna((global_avg_col * 3.0) + (global_avg_rent * 5.0))
    
    final['Region'] = final['iso_country'].map(ISO_TO_REGION).fillna('Other')
    final['Base_Flight_Cost'] = final['Region'].map(REGION_FLIGHT_COSTS).fillna(800)
    
    def get_seasonality(row):
        region = row['Region']
        if region == 'Europe': return "Summer Peak (Jun-Aug)"
        if region == 'Asia': return "Varies (Nov-Mar ideal)"
        if region == 'Oceania': return "Winter Peak (Dec-Feb)"
        return "Year-round"
    final['Seasonality'] = final.apply(get_seasonality, axis=1)

    # 8. CLEANUP & SAVE
    final['Destination'] = final['Clean_City'] + ", " + final['iso_country']
    final['Search_Term'] = final['Clean_City'] + ", " + final['Full_Country']
    
    cols_to_save = [
        'Destination', 'IATA', 'Search_Term', 'Full_Country', 'iso_country', 'Region', 
        'Base_Flight_Cost', 'Daily_Cost_Budget', 'Daily_Cost_Luxury', 'Seasonality',
        'latitude_deg', 'longitude_deg', 'Popularity_Score'
    ] + months
    
    final = final.rename(columns={'iata_code': 'IATA'})
    
    print(f"✅ Generated {len(final)} unique destinations.")
    final[cols_to_save].to_csv("master_travel_data.csv", index=False)
    print("📁 Master dataset saved to master_travel_data.csv")

if __name__ == "__main__":
    run_data_prep()
