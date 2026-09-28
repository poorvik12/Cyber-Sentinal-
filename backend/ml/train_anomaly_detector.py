import json
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from backend.config import DATA_DIR, MODEL_DIR
from backend.ml.preprocessing import FEATURES, build_preprocessor

def train():
    path=DATA_DIR/'normal_behavior.csv'
    if not path.exists():
        from backend.simulation.generator import generate_all; generate_all(DATA_DIR)
    df=pd.read_csv(path)
    pre=build_preprocessor(); Xt=pre.fit_transform(df[FEATURES])
    model=IsolationForest(n_estimators=220, contamination=.035, random_state=42, n_jobs=-1)
    model.fit(Xt)
    joblib.dump({'model':model,'preprocessor':pre},MODEL_DIR/'isolation_forest.pkl')
    metrics={'model':'Isolation Forest','training_samples':len(df),'features':FEATURES,'contamination':.035,'method':'Unsupervised anomaly detection on normal behavior baseline'}
    (MODEL_DIR/'anomaly_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps(metrics,indent=2)); return metrics
if __name__=='__main__': train()
