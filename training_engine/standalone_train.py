import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import json

print("🚀 Starting Standalone Training Pipeline...")

# Configuration
MODELS_DIR = "training_engine/models"
os.makedirs(MODELS_DIR, exist_ok=True)

# Step 1: Load or create data
print("📊 Step 1: Loading data...")
db_path = "traffic_data.db"

def load_or_create_data():
    try:
        if not os.path.exists(db_path):
            print("🔄 Creating sample data...")
            return create_sample_data()
        
        conn = sqlite3.connect(db_path)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        query = "SELECT * FROM traffic_data WHERE timestamp >= ? AND timestamp <= ?"
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        if df.empty:
            return create_sample_data()
        
        print(f"✅ Loaded {len(df)} records from database")
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create realistic sample traffic data"""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='H'
    )
    
    sample_data = []
    for date in dates:
        for intersection_id in range(1, 4):
            hour = date.hour
            day_of_week = date.weekday()
            
            # Realistic traffic patterns
            if 7 <= hour <= 9:  # Morning rush
                base_count = 40 + 15 * np.sin(2 * np.pi * (hour - 7) / 3)
            elif 16 <= hour <= 18:  # Evening rush
                base_count = 45 + 12 * np.sin(2 * np.pi * (hour - 16) / 3)
            else:  # Off-peak
                base_count = 20 + 8 * np.sin(2 * np.pi * hour / 24)
            
            # Weekend effect
            if day_of_week >= 5:
                base_count = base_count * 0.6
            
            noise = np.random.normal(0, 6)
            vehicle_count = max(5, int(base_count + noise))
            
            sample_data.append({
                'intersection_id': f'intersection_{intersection_id}',
                'vehicle_count': vehicle_count,
                'timestamp': date,
                'avg_speed': max(20, 60 - vehicle_count * 0.7 + np.random.normal(0, 4)),
                'queue_length': max(0, vehicle_count - 18 + np.random.normal(0, 2)),
                'congestion_level': 'high' if vehicle_count > 35 else 'medium' if vehicle_count > 20 else 'low'
            })
    
    df = pd.DataFrame(sample_data)
    print(f"✅ Created {len(df)} sample records")
    return df

# Load data
df = load_or_create_data()

# Step 2: Preprocess data
print("🔧 Step 2: Preprocessing data...")

# Fix timestamp parsing - use format='mixed' to handle different formats
df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
df['is_rush_hour'] = ((df['hour'] >= 7) & (df['hour'] <= 9)) | ((df['hour'] >= 16) & (df['hour'] <= 18))

# Cyclical features
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

# Encode intersection_id
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
df['intersection_id_encoded'] = le.fit_transform(df['intersection_id'])

# Select features and target
feature_columns = ['hour', 'day_of_week', 'is_weekend', 'is_rush_hour', 'hour_sin', 'hour_cos', 'intersection_id_encoded']
X = df[feature_columns]
y = df['vehicle_count']

print(f"📋 Using {len(feature_columns)} features: {feature_columns}")
print(f"📊 Dataset shape: {X.shape}")

# Step 3: Train model
print("🤖 Step 3: Training model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Step 4: Evaluate
print("📈 Step 4: Evaluating model...")
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"✅ Model Performance:")
print(f"   RMSE: {rmse:.2f}")
print(f"   R²: {r2:.4f}")

# Step 5: Save model
print("💾 Step 5: Saving model...")
model_path = os.path.join(MODELS_DIR, 'traffic_model.pkl')
metadata_path = os.path.join(MODELS_DIR, 'model_metadata.json')

joblib.dump(model, model_path)

metadata = {
    'feature_names': feature_columns,
    'metrics': {'rmse': rmse, 'r2': r2, 'mse': mse},
    'model_type': 'RandomForestRegressor',
    'training_date': datetime.now().isoformat(),
    'feature_count': len(feature_columns)
}

with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Model saved to: {model_path}")
print(f"✅ Metadata saved to: {metadata_path}")
print("🎯 Training completed successfully!")
