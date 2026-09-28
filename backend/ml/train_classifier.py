from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import train_test_split
from backend.config import DATA_DIR, MODEL_DIR
from backend.ml.preprocessing import FEATURES, build_preprocessor, fit_and_save_preprocessor

METRICS_PATH = MODEL_DIR / 'classifier_metrics.json'

def train():
    path = DATA_DIR/'training_dataset.csv'
    if not path.exists():
        from backend.simulation.generator import generate_all
        generate_all(DATA_DIR)
    df = pd.read_csv(path)
    X=df[FEATURES]; y=df['attack_type']
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    pre=build_preprocessor(); Xtr_t=pre.fit_transform(Xtr); Xte_t=pre.transform(Xte)
    model=RandomForestClassifier(n_estimators=220,max_depth=18,min_samples_leaf=2,class_weight='balanced',random_state=42,n_jobs=-1)
    model.fit(Xtr_t,ytr); pred=model.predict(Xte_t)
    metrics={
        'model':'Random Forest','training_samples':int(len(Xtr)),'test_samples':int(len(Xte)),'features':FEATURES,
        'accuracy':round(float(accuracy_score(yte,pred)),4),'precision':round(float(precision_score(yte,pred,average='weighted',zero_division=0)),4),
        'recall':round(float(recall_score(yte,pred,average='weighted',zero_division=0)),4),'f1':round(float(f1_score(yte,pred,average='weighted',zero_division=0)),4),
        'classes':list(model.classes_)
    }
    joblib.dump({'model':model,'preprocessor':pre},MODEL_DIR/'random_forest.pkl')
    (METRICS_PATH).write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps(metrics,indent=2)); print(classification_report(yte,pred,zero_division=0))
    return metrics
if __name__=='__main__': train()
