import pandas as pd
import numpy as np
import json
import joblib
import os
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

print("="*60)
print("🏠 JAKARTA HOUSING PRICE PREDICTION MODEL")
print("="*60)

# Load data
df = pd.read_csv("data/raw/jakarta_data.csv")
print(f"\n📊 Loaded {len(df)} listings")

# Encode categorical
le_region = LabelEncoder()
le_name = LabelEncoder()
df['region_e'] = le_region.fit_transform(df['region'])
df['name_e'] = le_name.fit_transform(df['housing_name'])
df['name_type_e'] = (df['name_type'] == 'REGAL').astype(int)

# Features
feats = [
    'land_m2', 'building_m2', 'floors', 'bedrooms', 'bathrooms',
    'dist_airport_km', 'dist_mall_km', 'nearby_mosques',
    'region_e', 'name_type_e'
]

X = df[feats].copy()
y = df['price_million_idr']

# Scale
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled = pd.DataFrame(X_scaled, columns=feats)

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

print(f"\n🔧 Training on {len(X_train)} samples, Testing on {len(X_test)} samples")
print(f"\n📈 Target Variable Stats:")
print(f"  Median: Rp {y.median():,.0f}M")
print(f"  Range: Rp {y.min():,.0f}M - Rp {y.max():,.0f}M")

# Models
models = {
    'Linear Regression': LinearRegression(),
    'Ridge (L2)': Ridge(alpha=1.0),
    'Lasso (L1)': Lasso(alpha=0.1),
    'KNN (k=5)': KNeighborsRegressor(n_neighbors=5, weights='distance'),
    'KNN (k=10)': KNeighborsRegressor(n_neighbors=10, weights='distance'),
    'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=200, max_depth=5, random_state=42),
    'XGBoost': XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
}

# Train & evaluate
print(f"\n{'='*60}")
print("🤖 MODEL TRAINING & EVALUATION")
print(f"{'='*60}")

results = {}
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
    
    results[name] = {
        'rmse': float(rmse),
        'r2': float(r2),
        'mae': float(mae),
        'mape': float(mape),
        'cv_r2_mean': float(cv_scores.mean()),
        'cv_r2_std': float(cv_scores.std())
    }
    
    print(f"\n{name}:")
    print(f"  📊 RMSE: Rp {rmse:,.0f}M")
    print(f"  📊 R²: {r2:.3f} ({r2*100:.1f}% variance explained)")
    print(f"  📊 MAE: Rp {mae:,.0f}M")
    print(f"  📊 MAPE: {mape:.1f}%")
    print(f"  📊 CV R²: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")

# Best model
best = max(results, key=lambda x: results[x]['r2'])
print(f"\n{'='*60}")
print(f"🏆 BEST MODEL: {best}")
print(f"   R²: {results[best]['r2']:.3f} | RMSE: Rp {results[best]['rmse']:,.0f}M")
print(f"{'='*60}")

# Feature importance for tree models
if best in ['Random Forest', 'Gradient Boosting', 'XGBoost']:
    if hasattr(models[best], 'feature_importances_'):
        importance = pd.DataFrame({
            'feature': feats,
            'importance': models[best].feature_importances_
        }).sort_values('importance', ascending=False)
        print(f"\n📊 Feature Importance ({best}):")
        for _, row in importance.iterrows():
            print(f"  {row['feature']}: {row['importance']:.3f}")

# Save
os.makedirs('models', exist_ok=True)
joblib.dump(models[best], 'models/best_model.joblib')
joblib.dump(scaler, 'models/scaler.joblib')
json.dump(results, open('models/results.json', 'w'), indent=2)

# Save feature names
with open('models/features.json', 'w') as f:
    json.dump({'features': feats, 'regions': list(le_region.classes_)}, f)

print(f"\n✅ Models saved to /models/")