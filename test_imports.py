print("Testing imports...")

try:
    import pandas as pd
    print("✅ pandas imported successfully")
except ImportError as e:
    print(f"❌ pandas import failed: {e}")

try:
    import numpy as np
    print("✅ numpy imported successfully")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")

try:
    from sklearn.ensemble import RandomForestRegressor
    print("✅ scikit-learn imported successfully")
except ImportError as e:
    print(f"❌ scikit-learn import failed: {e}")

try:
    import xgboost as xgb
    print("✅ xgboost imported successfully")
except ImportError as e:
    print(f"❌ xgboost import failed: {e}")

print("\\nImport test completed.")
