import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os

class ModelEvaluator:
    def __init__(self):
        self.plots_dir = "training_engine/models/plots"
        os.makedirs(self.plots_dir, exist_ok=True)
    
    def evaluate(self, model, X, y, feature_names):
        """Comprehensive model evaluation"""
        print("📈 Evaluating model performance...")
        
        # Make predictions
        y_pred = model.predict(X)
        
        # Calculate metrics
        metrics = {
            'mse': mean_squared_error(y, y_pred),
            'mae': mean_absolute_error(y, y_pred),
            'r2': r2_score(y, y_pred)
        }
        metrics['rmse'] = np.sqrt(metrics['mse'])
        
        # Create plots
        self.plot_predictions(y, y_pred)
        
        # Feature importance if available
        if hasattr(model, 'feature_importances_'):
            self.plot_feature_importance(model, feature_names)
        
        print(f"✅ Evaluation completed:")
        print(f"   RMSE: {metrics['rmse']:.2f}")
        print(f"   MAE: {metrics['mae']:.2f}")
        print(f"   R²: {metrics['r2']:.4f}")
        
        return metrics
    
    def plot_predictions(self, y_true, y_pred):
        """Plot actual vs predicted values"""
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.scatter(y_true, y_pred, alpha=0.6)
        plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        plt.xlabel('Actual Vehicle Count')
        plt.ylabel('Predicted Vehicle Count')
        plt.title('Actual vs Predicted')
        
        plt.subplot(1, 2, 2)
        residuals = y_true - y_pred
        plt.scatter(y_pred, residuals, alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Predicted')
        plt.ylabel('Residuals')
        plt.title('Residual Plot')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.plots_dir, 'predictions_analysis.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_feature_importance(self, model, feature_names):
        """Plot feature importance"""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_imp = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            plt.figure(figsize=(10, 6))
            sns.barplot(data=feature_imp.head(15), x='importance', y='feature')
            plt.title('Top 15 Feature Importances')
            plt.tight_layout()
            plt.savefig(os.path.join(self.plots_dir, 'feature_importance.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            print("📊 Feature importance plot saved")
