import os
from dotenv import load_dotenv
load_dotenv()

# PostgreSQL Configuration with encoded password
POSTGRES_SERVER = os.getenv('POSTGRES_SERVER', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'traffic_optimizer')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '%40%23%24Py1009')  # URL encoded

DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}'

# For hybrid_database_final compatibility
SQLITE_PATH = 'traffic_data.db'

# For app.py compatibility
db_config = {
    'url': DATABASE_URL,
    'SQLITE_PATH': SQLITE_PATH  # Add this line
}

ml_config = {
    'model_path': '../training_engine/models/traffic_model.pkl'
}
