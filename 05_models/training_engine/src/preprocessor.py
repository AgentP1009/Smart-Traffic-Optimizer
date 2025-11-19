import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
    
    def create_features(self, df):
        """Create time-based and traffic features"""
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(['intersection_id', 'timestamp'])
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['month'] = df['timestamp'].dt.month
        df['is_rush_hour'] = ((df['hour'] >= 7) & (df['hour'] <= 9)) | ((df['hour'] >= 16) & (df['hour'] <= 18))
        
        # Cyclical features for time
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Encode intersection_id
        if 'intersection_id' in df.columns:
            self.label_encoders['intersection_id'] = LabelEncoder()
            df['intersection_id_encoded'] = self.label_encoders['intersection_id'].fit_transform(df['intersection_id'])
        
        # Traffic intensity (normalize vehicle count)
        if 'vehicle_count' in df.columns:
            max_count = df['vehicle_count'].max()
            if max_count > 0:
                df['traffic_intensity'] = df['vehicle_count'] / max_count
        
        # Lag features (previous time periods)
        for lag in [1, 2, 3, 24]:  # 1,2,3 hours ago, 24 hours ago (same time yesterday)
            lag_col = f'vehicle_count_lag_{lag}'
            df[lag_col] = df.groupby('intersection_id')['vehicle_count'].shift(lag)
        
        # Rolling statistics
        if 'vehicle_count' in df.columns:
            df['vehicle_count_rolling_3'] = df.groupby('intersection_id')['vehicle_count'].rolling(3, min_periods=1).mean().reset_index(0, drop=True)
            df['vehicle_count_rolling_6'] = df.groupby('intersection_id')['vehicle_count'].rolling(6, min_periods=1).mean().reset_index(0, drop=True)
        
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        # Fill missing numerical values with median
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def prepare_features(self, df, target_column='vehicle_count'):
        """Main preprocessing pipeline"""
        print("🔧 Preprocessing data...")
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Create features
        df = self.create_features(df)
        
        # Define feature columns
        self.feature_columns = [
            'hour', 'day_of_week', 'is_weekend', 'month', 'is_rush_hour',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'intersection_id_encoded', 'traffic_intensity'
        ]
        
        # Add lag and rolling features if they exist
        lag_rolling_features = [col for col in df.columns if 'lag_' in col or 'rolling_' in col]
        self.feature_columns.extend(lag_rolling_features)
        
        # Only use columns that exist in dataframe
        self.feature_columns = [col for col in self.feature_columns if col in df.columns]
        
        print(f"📋 Using {len(self.feature_columns)} features")
        
        # Remove rows with NaN values in features or target
        df_clean = df.dropna(subset=self.feature_columns + [target_column])
        
        X = df_clean[self.feature_columns]
        y = df_clean[target_column]
        
        print(f"✅ Final dataset: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y, self.feature_columns
