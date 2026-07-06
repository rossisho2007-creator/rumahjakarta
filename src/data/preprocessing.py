import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

class HousingDataProcessor:
    def __init__(self, data_path='data/raw/'):
        self.data_path = data_path
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def load_data(self, filename='synthetic_jakarta_housing.csv'):
        df = pd.read_csv(f'{self.data_path}{filename}')
        print(f"Loaded {len(df)} listings")
        return df
    
    def clean_data(self, df):
        df = df[df['land_m2'] <= 1000].copy()
        q1 = df['price_million_idr'].quantile(0.01)
        q99 = df['price_million_idr'].quantile(0.99)
        df = df[(df['price_million_idr'] >= q1) & 
                (df['price_million_idr'] <= q99)]
        df['log_price'] = np.log1p(df['price_million_idr'])
        df.fillna(df.median(numeric_only=True), inplace=True)
        print(f"After cleaning: {len(df)} listings")
        return df
    
    def engineer_features(self, df):
        df['building_ratio'] = df['building_m2'] / df['land_m2']
        df['price_per_m2'] = df['price_million_idr'] / df['land_m2']
        df['room_density'] = df['bedrooms'] / df['building_m2'] * 100
        
        df['mrt_proximity'] = pd.cut(df['distance_to_mrt_km'], 
                                       bins=[0, 1, 3, 5, 10, 100],
                                       labels=['Very Close', 'Close', 'Medium', 'Far', 'Very Far'])
        df['flood_category'] = pd.cut(df['flood_risk'],
                                       bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                                       labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])
        
        categorical_cols = ['area', 'mrt_proximity', 'flood_category']
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        return df
    
    def prepare_modeling_data(self, df):
        feature_cols = [
            'land_m2', 'building_m2', 'bedrooms', 'bathrooms',
            'distance_to_mrt_km', 'flood_risk', 'building_ratio',
            'room_density', 'area_encoded', 'mrt_proximity_encoded',
            'flood_category_encoded'
        ]
        
        X = df[feature_cols].copy()
        y = df['price_million_idr'].copy()
        
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        return X_train, X_test, y_train, y_test
    
    def save_processed_data(self, df, X_train, X_test, y_train, y_test):
        df.to_csv('data/processed/processed_housing.csv', index=False)
        for name, data in [('X_train', X_train), ('X_test', X_test),
                           ('y_train', y_train), ('y_test', y_test)]:
            data.to_csv(f'data/processed/{name}.csv', index=False)
        print("All processed data saved to data/processed/")

if __name__ == "__main__":
    processor = HousingDataProcessor()
    df = processor.load_data()
    df = processor.clean_data(df)
    df = processor.engineer_features(df)
    X_train, X_test, y_train, y_test = processor.prepare_modeling_data(df)
    processor.save_processed_data(df, X_train, X_test, y_train, y_test)
