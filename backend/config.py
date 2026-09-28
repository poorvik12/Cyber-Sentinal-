import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

MONGODB_URI = os.getenv('MONGODB_URI', '')
MONGODB_DB = os.getenv('MONGODB_DB', 'cybersecurity_ai')
FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', 'http://localhost:5173')
DATA_DIR = BASE_DIR / 'data'
MODEL_DIR = BASE_DIR / 'ml' / 'models'
FALLBACK_DIR = BASE_DIR / 'data' / 'runtime'
FALLBACK_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

RISK_THRESHOLDS = {
    'LOW_MAX': int(os.getenv('RISK_LOW_MAX', '30')),
    'MEDIUM_MAX': int(os.getenv('RISK_MEDIUM_MAX', '60')),
    'HIGH_MAX': int(os.getenv('RISK_HIGH_MAX', '80')),
}
POLLING_INTERVAL = int(os.getenv('POLLING_INTERVAL', '5000'))
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'
