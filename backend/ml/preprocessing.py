from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from config import MODEL_DIR
CATEGORICAL = ['protocol', 'http_methods']
TARGETS = ['label', 'attack_type']
NUMERICAL = [
    'requests_per_minute','packets_sent','packets_received','bytes_sent','bytes_received','connection_count',
    'connection_duration','unique_ports','unique_ips','destination_count','login_attempts','failed_logins',
    'session_duration','files_accessed','resources_accessed','unusual_login_time','new_device','new_ip',
    'privilege_changes','process_count','new_processes','cpu_usage','memory_usage','file_modifications',
    'executable_count','system_connections','unusual_process_activity','api_requests','request_frequency',
    'endpoint_count','error_rate','response_size','unusual_endpoints','authentication_failures'
]
FEATURES = NUMERICAL + CATEGORICAL

def build_preprocessor():
    numeric = Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])
    categorical = Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))])
    return ColumnTransformer([('num', numeric, NUMERICAL), ('cat', categorical, CATEGORICAL)], remainder='drop')

def fit_and_save_preprocessor(df: pd.DataFrame):
    p = build_preprocessor()
    p.fit(df[FEATURES])
    joblib.dump(p, MODEL_DIR / 'preprocessor.pkl')
    return p

def load_preprocessor():
    path = MODEL_DIR / 'preprocessor.pkl'
    if not path.exists():
        raise FileNotFoundError('Preprocessor is not trained. Run train_classifier.py first.')
    return joblib.load(path)
