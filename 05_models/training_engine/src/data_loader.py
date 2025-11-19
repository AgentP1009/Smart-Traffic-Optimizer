import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import numpy as np
import os

class DataLoader:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '../../traffic_data.db')
    
    def load_historical_data(self, days=30):
        """Load historical traffic data from SQLite database"""
        try:
            # Use absolute path to database
            db_abs_path = os.path.abspath(self.db_path)
            print(f"🔍 Looking for database at: {db_abs_path}")
            
            if not os.path.exists(db_abs_path):
                print("❌ Database file not found, creating sample data...")
                return self.create_sample_data(days)
            
            conn = sqlite3.connect(db_abs_path)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Try to read data
            query = """
            SELECT * FROM traffic_data 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
            """
            
            df = pd.read_sql_query(query, conn, params=[start_date, end_date])
            conn.close()
            
            if df.empty:
                print("ℹ️ No historical data found, creating sample data...")
                return self.create_sample_data(days)
            
            print(f"✅ Loaded {len(df)} historical records")
            return df
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            print("🔄 Creating sample data for training...")
            return self.create_sample_data(days)
    
    def create_sample_data(self, days=30):
        """Create realistic sample traffic data for training"""
        print("📝 Generating sample traffic data...")
        
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days),
            end=datetime.now(),
            freq='H'  # Hourly data
        )
        
        sample_data = []
        for date in dates:
            for intersection_id in range(1, 4):  # 3 intersections
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
                if day_of_week >= 5:  # Weekend
                    base_count = base_count * 0.6
                
                # Add noise and ensure minimum
                noise = np.random.normal(0, 6)
                vehicle_count = max(5, int(base_count + noise))
                
                # Calculate related metrics
                avg_speed = max(20, 60 - vehicle_count * 0.7 + np.random.normal(0, 4))
                queue_length = max(0, vehicle_count - 18 + np.random.normal(0, 2))
                
                sample_data.append({
                    'intersection_id': f'intersection_{intersection_id}',
                    'vehicle_count': vehicle_count,
                    'timestamp': date,
                    'avg_speed': avg_speed,
                    'queue_length': queue_length,
                    'congestion_level': 'high' if vehicle_count > 35 else 'medium' if vehicle_count > 20 else 'low'
                })
        
        df = pd.DataFrame(sample_data)
        print(f"✅ Created {len(df)} sample records")
        return df
