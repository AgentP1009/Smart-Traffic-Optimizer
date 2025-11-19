import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the training
try:
    from training_engine.src.train import main
    print("✅ Successfully imported training module")
    main()
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔄 Falling back to standalone training...")
    from training_engine.standalone_train import *
