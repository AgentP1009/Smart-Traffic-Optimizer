import pandas as pd
import numpy as np
import sys
import os

# Add project root to Python path
project_root = os.path.join(os.path.dirname(__file__), '../..')
sys.path.insert(0, project_root)

try:
    from shared.config import settings
    print("✅ Successfully imported settings from shared.config")
except ImportError as e:
    print(f"❌ Could not import from shared.config: {e}")
    print("🔄 Using fallback settings...")
    
    # Fallback settings
    class FallbackSettings:
        MODELS_DIR = "training_engine/models"
        TRAINING_DAYS = 30
        TEST_SIZE = 0.2
        RANDOM_STATE = 42
    
    settings = FallbackSettings()

from .data_loader import DataLoader
from .preprocessor import DataPreprocessor
from .model_builder import ModelTrainer
from .evaluator import ModelEvaluator
import joblib
import json
from datetime import datetime

class TrainingPipeline:
    def __init__(self):
        self.settings = settings
        self.data_loader = DataLoader()
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.evaluator = ModelEvaluator()
    
    def run_training(self, days=30):
        """Complete training pipeline"""
        print("🚀 Starting Traffic Model Training Pipeline...")
        
        # 1. Load data
        print("📊 Step 1: Loading training data...")
        df = self.data_loader.load_historical_data(days)
        
        if df.empty:
            print("❌ No data available for training")
            return None
            
        print(f"✅ Loaded {len(df)} records")
        
        # 2. Preprocess data
        print("🔧 Step 2: Preprocessing data...")
        X, y, feature_names = self.preprocessor.prepare_features(df)
        
        # 3. Train model
        print("🤖 Step 3: Training model...")
        model, metrics = self.trainer.train(X, y)
        
        # 4. Evaluate model
        print("📈 Step 4: Evaluating model...")
        evaluation_results = self.evaluator.evaluate(model, X, y, feature_names)
        metrics.update(evaluation_results)
        
        # 5. Save model
        print("💾 Step 5: Saving model...")
        self.save_model(model, feature_names, metrics)
        
        print("🎯 Training completed successfully!")
        return metrics
    
    def save_model(self, model, feature_names, metrics):
        """Save model and metadata"""
        os.makedirs(self.settings.MODELS_DIR, exist_ok=True)
        
        model_path = os.path.join(self.settings.MODELS_DIR, 'traffic_model.pkl')
        metadata_path = os.path.join(self.settings.MODELS_DIR, 'model_metadata.json')
        
        # Save model
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata = {
            'feature_names': feature_names,
            'metrics': metrics,
            'model_type': type(model).__name__,
            'training_date': datetime.now().isoformat(),
            'feature_count': len(feature_names)
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Model saved to: {model_path}")
        print(f"✅ Metadata saved to: {metadata_path}")

def main():
    """Main function to run training"""
    pipeline = TrainingPipeline()
    metrics = pipeline.run_training(days=30)
    
    if metrics:
        print(f"\\n📊 Final Metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value:.4f}")

if __name__ == "__main__":
    main()
