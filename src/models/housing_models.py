import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import json
import os

class HousingPriceModels:
    def __init__(self):
        self.models = {}
        self.results = {}
        self.best_model = None
        
    def load_data(self):
        X_train = pd.read_csv('data/processed/X_train.csv')
        X_test = pd.read_csv('data/processed/X_test.csv')
        y_train = pd.read_csv('data/processed/y_train.csv').squeeze()
        y_test = pd.read_csv('data/processed/y_test.csv').squeeze()
        return X_train, X_test, y_train, y_test
    
    def initialize_models(self):
        self.models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.1),
            'KNN (k=5)': KNeighborsRegressor(n_neighbors=5, weights='distance'),
            'KNN (k=10)': KNeighborsRegressor(n_neighbors=10, weights='distance'),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        }
    
    def train_evaluate_all(self, X_train, X_test, y_train, y_test):
        for name, model in self.models.items():
            print(f"\n{'='*50}")
            print(f"Training {name}...")
            
            model.fit(X_train, y_train)
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            
            results = {
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_r2': r2_score(y_train, y_pred_train),
                'test_r2': r2_score(y_test, y_pred_test),
                'train_mae': mean_absolute_error(y_train, y_pred_train),
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'test_mape': np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
            }
            
            self.results[name] = results
            print(f"Test RMSE: Rp {results['test_rmse']:,.0f}M")
            print(f"Test R2: {results['test_r2']:.3f}")
            print(f"Test MAPE: {results['test_mape']:.1f}%")
        
        best_model_name = min(self.results, key=lambda x: self.results[x]['test_rmse'])
        self.best_model = self.models[best_model_name]
        print(f"\n🏆 Best Model: {best_model_name}")
        return self.results
    
    def save_results(self):
        os.makedirs('models', exist_ok=True)
        
        results_json = {}
        for name, metrics in self.results.items():
            results_json[name] = {
                k: float(v) if isinstance(v, (np.floating, np.integer)) else v
                for k, v in metrics.items()
            }
        
        with open('models/results.json', 'w') as f:
            json.dump(results_json, f, indent=2)
        
        joblib.dump(self.best_model, 'models/best_model.joblib')
        print("\n✅ Results and best model saved to /models/")

if __name__ == "__main__":
    pipeline = HousingPriceModels()
    X_train, X_test, y_train, y_test = pipeline.load_data()
    pipeline.initialize_models()
    pipeline.train_evaluate_all(X_train, X_test, y_train, y_test)
    pipeline.save_results()
