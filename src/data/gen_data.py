import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

np.random.seed(42)

# ============ REAL JAKARTA LOCATION DATA ============
AIRPORT = (-6.1256, 106.6558)

# Major malls with coordinates
MALLS = [
    ('Grand Indonesia', -6.1944, 106.8220, 'Central'),
    ('Plaza Indonesia', -6.1933, 106.8217, 'Central'),
    ('Pondok Indah Mall', -6.2652, 106.7837, 'South'),
    ('Senayan City', -6.2274, 106.7978, 'South'),
    ('Kota Kasablanka', -6.2237, 106.8438, 'South'),
    ('Gandaria City', -6.2439, 106.7829, 'South'),
    ('Central Park', -6.1775, 106.7910, 'West'),
    ('Kelapa Gading Mall', -6.1587, 106.9085, 'North'),
    ('AEON Mall BSD', -6.3030, 106.6434, 'South'),
    ('Lippo Mall Puri', -6.1870, 106.7381, 'West'),
    ('Mall of Indonesia', -6.1517, 106.8885, 'North'),
    ('Emporium Pluit', -6.1135, 106.7893, 'North'),
    ('Kuningan City', -6.2270, 106.8288, 'Central'),
    ('Cilandak Town Square', -6.2888, 106.7985, 'South'),
    ('Baywalk Pluit', -6.1095, 106.7846, 'North'),
]

# Small mosques (hidden from user but affect prices)
MOSQUES = [
    (-6.2000, 106.8100), (-6.2200, 106.8300), (-6.1800, 106.7900),
    (-6.2400, 106.8500), (-6.1600, 106.8200), (-6.2500, 106.8000),
    (-6.1900, 106.8400), (-6.2100, 106.8100), (-6.2300, 106.8300),
    (-6.1700, 106.8500), (-6.2600, 106.8200), (-6.2000, 106.8600),
    (-6.1400, 106.8700), (-6.2800, 106.8400), (-6.1950, 106.8550),
    (-6.2350, 106.7750), (-6.1550, 106.8350), (-6.2150, 106.7950),
    (-6.1750, 106.8650), (-6.2450, 106.8150), (-6.1850, 106.8050),
    (-6.2050, 106.8450), (-6.2550, 106.7850), (-6.1650, 106.8550),
]

# Regions with real price data and boundaries
REGIONS = {
    'Jakarta Selatan': {
        'base_house': 25_000_000, 'base_apartment': 18_000_000,
        'center': (-6.2600, 106.8000), 'color': '#FF6B6B',
        'areas': ['Kebayoran Baru', 'Cilandak', 'Tebet', 'Pasar Minggu', 'Mampang', 'Setiabudi', 'Pancoran']
    },
    'Jakarta Pusat': {
        'base_house': 30_000_000, 'base_apartment': 22_000_000,
        'center': (-6.1860, 106.8300), 'color': '#4ECDC4',
        'areas': ['Menteng', 'Tanah Abang', 'Gambir', 'Sawah Besar', 'Kemayoran']
    },
    'Jakarta Utara': {
        'base_house': 18_000_000, 'base_apartment': 15_000_000,
        'center': (-6.1200, 106.9000), 'color': '#45B7D1',
        'areas': ['Kelapa Gading', 'Penjaringan', 'Koja', 'Pademangan', 'Tanjung Priok']
    },
    'Jakarta Barat': {
        'base_house': 15_000_000, 'base_apartment': 12_000_000,
        'center': (-6.1700, 106.7700), 'color': '#96CEB4',
        'areas': ['Kebon Jeruk', 'Kembangan', 'Cengkareng', 'Grogol Petamburan']
    },
    'Jakarta Timur': {
        'base_house': 12_000_000, 'base_apartment': 9_000_000,
        'center': (-6.2200, 106.8800), 'color': '#FFEAA7',
        'areas': ['Duren Sawit', 'Cakung', 'Pulo Gadung', 'Jatinegara', 'Kramat Jati']
    }
}

# Housing names
REGAL_PATTERNS = ['Royal', 'Grand', 'Palace', 'Garden', 'Park', 'Hill', 'Villa', 'Residence', 'Mansion', 'Elite', 'Premium', 'Luxury', 'Spring', 'Green', 'Lake', 'View', 'Heights']
INDONESIAN_PATTERNS = ['Griya', 'Puri', 'Pondok', 'Permai', 'Indah', 'Asri', 'Sejahtera', 'Damai', 'Sederhana', 'Sari', 'Mulya', 'Wisma']

# Apartment names
APARTMENT_NAMES = ['The {name} Tower', '{name} Residences', '{name} Apartments', 'The {name} Suites', '{name} City', '{name} Parkview', '{name} Mansion']

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

def generate_name(price_m2, prop_type):
    if prop_type == 'apartment':
        base = np.random.choice(REGAL_PATTERNS[:8])
        return np.random.choice(APARTMENT_NAMES).format(name=base)
    else:
        if price_m2 > 20_000_000:
            base = np.random.choice(REGAL_PATTERNS[:10])
            return f"{base} {np.random.choice(['Residences', 'Villas', 'Estate'])}"
        elif price_m2 > 10_000_000:
            base = np.random.choice(REGAL_PATTERNS[5:] + INDONESIAN_PATTERNS[:5])
            return f"{base} {np.random.choice(['Homes', 'Garden', 'Park'])}"
        else:
            return f"{np.random.choice(INDONESIAN_PATTERNS)} {np.random.choice(['Asri', 'Indah', 'Permai'])}"

# ============ GENERATE DATA ============
data = []
for i in range(3000):  # More data for better analysis
    prop_type = np.random.choice(['house', 'apartment'], p=[0.6, 0.4])
    region = np.random.choice(list(REGIONS.keys()))
    region_info = REGIONS[region]
    area = np.random.choice(region_info['areas'])
    
    if prop_type == 'house':
        land = np.random.choice([60, 72, 90, 100, 120, 150, 200, 250, 300, 400])
        building = land * np.random.uniform(0.4, 0.9)
        floors = max(1, min(4, int(np.random.choice([1, 1, 1, 2, 2, 3]))))
        base_price_m2 = region_info['base_house']
    else:  # apartment
        land = 0
        building = np.random.choice([36, 45, 54, 72, 90, 108, 120])
        floors = 1  # Apartments are single-floor units
        base_price_m2 = region_info['base_apartment']
    
    price_per_m2 = base_price_m2 * np.random.uniform(0.7, 2.5)
    
    # Coordinates
    lat = region_info['center'][0] + np.random.normal(0, 0.025)
    lon = region_info['center'][1] + np.random.normal(0, 0.025)
    prop_coords = (lat, lon)
    
    # Distance calculations
    dist_airport = haversine(prop_coords, AIRPORT)
    
    # Mall distances
    mall_distances = [(m[0], haversine(prop_coords, (m[1], m[2]))) for m in MALLS]
    mall_distances.sort(key=lambda x: x[1])
    dist_nearest_mall = mall_distances[0][1]
    malls_within_2km = sum(1 for m in mall_distances if m[1] < 2)
    malls_within_5km = sum(1 for m in mall_distances if m[1] < 5)
    
    # Hidden mosque effect
    nearby_mosques = sum(1 for m in MOSQUES if haversine(prop_coords, m) < 0.5)
    mosque_discount = 0.96 ** nearby_mosques
    
    # Name effect
    name = generate_name(price_per_m2, prop_type)
    name_premium = 1.18 if any(p in name for p in ['Royal', 'Grand', 'Palace', 'Mansion']) else 1.0
    
    # Mall proximity effect (stronger for apartments near malls)
    if prop_type == 'apartment' and dist_nearest_mall < 1:
        mall_multiplier = 1.25  # Apartments near malls are premium
    elif dist_nearest_mall < 1:
        mall_multiplier = 1.15
    elif dist_nearest_mall < 3:
        mall_multiplier = 1.05
    else:
        mall_multiplier = 0.95
    
    # Airport effect (properties 15-30km from airport are most valuable)
    if 15 <= dist_airport <= 30:
        airport_factor = 1.10
    else:
        airport_factor = 0.95
    
    # Price calculation
    if prop_type == 'house':
        base_price = land * price_per_m2
        construction = building * floors * np.random.uniform(4_000_000, 7_000_000)
    else:
        base_price = building * price_per_m2 * 1.3  # Apartments higher per m²
        construction = 0
    
    market_noise = np.random.normal(1, 0.12)
    final_price = (base_price + construction) * market_noise * name_premium * mall_multiplier * airport_factor * mosque_discount
    
    data.append({
        'id': i,
        'region': region,
        'area': area,
        'property_type': prop_type,
        'name': name,
        'land_m2': land if prop_type == 'house' else 0,
        'building_m2': round(building, 1),
        'floors': floors,
        'bedrooms': max(1, min(8, int(building / 25))),
        'bathrooms': max(1, min(4, int(building / 35))),
        'price_idr': round(final_price, 0),
        'price_million_idr': round(final_price / 1_000_000, 0),
        'price_per_m2': round(price_per_m2, 0),
        'dist_airport_km': round(dist_airport, 2),
        'dist_nearest_mall_km': round(dist_nearest_mall, 2),
        'malls_within_2km': malls_within_2km,
        'malls_within_5km': malls_within_5km,
        'lat': round(lat, 6),
        'lon': round(lon, 6),
    })

df = pd.DataFrame(data)
df.to_csv('data/raw/jakarta_data.csv', index=False)

print(f"✅ Generated {len(df)} listings ({len(df[df['property_type']=='house'])} houses, {len(df[df['property_type']=='apartment'])} apartments)")
print(f"\n📊 Average Prices by Region & Type:")
print(df.groupby(['region', 'property_type'])['price_million_idr'].agg(['mean', 'median']).round(0))
print(f"\n🕌 Mosque effect applied discretely (not shown to users)")