import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import joblib

class ModelTrainer:
    def __init__(self, test_size=0.2, random_state=42):
        self.test_size = test_size
        self.random_state = random_state
        self.models = {}
        self.best_model = None
        self.best_score = float('inf')
    
    def train(self, X, y):
        """Train multiple models and select the best one"""
        print("🤖 Training models...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state, shuffle=False
        )
        
        print(f"📊 Training set: {X_train.shape}, Test set: {X_test.shape}")
        
        # Define models to try
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=self.random_state, n_jobs=-1),
            'xgboost': xgb.XGBRegressor(n_estimators=100, random_state=self.random_state, n_jobs=-1),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=self.random_state),
            'linear_regression': LinearRegression()
        }
        
        metrics = {}
        
        # Train and evaluate each model
        for name, model in self.models.items():
            print(f"\\n📈 Training {name}...")
            model.fit(X_train, y_train)
            
            # Predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            metrics[name] = {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
            
            print(f"  {name} Performance:")
            print(f"    MSE: {mse:.2f}")
            print(f"    RMSE: {rmse:.2f}")
            print(f"    MAE: {mae:.2f}")
            print(f"    R²: {r2:.4f}")
            
            # Update best model
            if mse < self.best_score:
                self.best_score = mse
                self.best_model = model
                self.best_model_name = name
        
        print(f"\\n🎯 Best model: {self.best_model_name} with RMSE: {np.sqrt(self.best_score):.2f}")
        
        # Return best model and metrics
        best_metrics = metrics[self.best_model_name]
        best_metrics['best_model'] = self.best_model_name
        
        return self.best_model, best_metrics
