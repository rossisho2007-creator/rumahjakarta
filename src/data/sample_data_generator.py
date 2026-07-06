import pandas as pd
import numpy as np

def generate_jakarta_samples(n_samples=1000):
    """Generate realistic Jakarta housing data"""
    np.random.seed(42)
    
    areas = {
        'Jakarta Selatan': {'base_price': 25000, 'premium': 1.5},
        'Jakarta Pusat': {'base_price': 28000, 'premium': 1.8},
        'Jakarta Barat': {'base_price': 15000, 'premium': 1.2},
        'Jakarta Timur': {'base_price': 12000, 'premium': 1.0},
        'Jakarta Utara': {'base_price': 18000, 'premium': 1.3},
    }
    
    data = []
    for _ in range(n_samples):
        area = np.random.choice(list(areas.keys()))
        area_info = areas[area]
        
        land = np.random.lognormal(mean=4.5, sigma=0.8)
        building = land * np.random.uniform(0.4, 0.9)
        bedrooms = max(1, int(np.random.normal(3, 1)))
        
        price_per_meter = area_info['base_price'] * area_info['premium']
        base_price = land * price_per_meter
        noise = np.random.normal(0, 0.2)
        price = base_price * (1 + noise)
        
        data.append({
            'area': area,
            'land_m2': round(land, 1),
            'building_m2': round(building, 1),
            'bedrooms': bedrooms,
            'bathrooms': max(1, bedrooms - 1),
            'price_million_idr': round(price, 0),
            'distance_to_mrt_km': round(np.random.exponential(3), 2),
            'flood_risk': np.random.beta(1, 3),
        })
    
    df = pd.DataFrame(data)
    df.to_csv('data/raw/synthetic_jakarta_housing.csv', index=False)
    print(f"Generated {len(df)} synthetic listings")
    return df

if __name__ == "__main__":
    generate_jakarta_samples()
