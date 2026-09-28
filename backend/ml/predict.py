from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from config import MODEL_DIR
from ml.preprocessing import FEATURES
from ml.risk_engine import layer_scores, overall_score, risk_level
from ml.explain import explain

class Detector:
    def __init__(self):
        self.rf=None; self.iso=None; self.reload()
    def reload(self):
        rf=MODEL_DIR/'random_forest.pkl'; iso=MODEL_DIR/'isolation_forest.pkl'
        if rf.exists(): self.rf=joblib.load(rf)
        if iso.exists(): self.iso=joblib.load(iso)
    def ensure(self):
        if not self.rf or not self.iso:
            from ml.train_classifier import train as train_classifier
            from ml.train_anomaly_detector import train as train_anomaly
            train_classifier(); train_anomaly(); self.reload()
    def analyze(self,event):
        self.ensure()
        df=pd.DataFrame([event])[FEATURES]
        Xt=self.rf['preprocessor'].transform(df)
        probs=self.rf['model'].predict_proba(Xt)[0]
        classes=self.rf['model'].classes_
        idx=int(np.argmax(probs)); pred=str(classes[idx]); confidence=float(probs[idx])
        # IsolationForest decision_function: larger is more normal. Convert to bounded anomaly intensity.
        Xi=self.iso['preprocessor'].transform(df)
        decision=float(self.iso['model'].decision_function(Xi)[0])
        anomaly_score=float(np.clip(.5 - decision,0,1))
        flag=bool(self.iso['model'].predict(Xi)[0] == -1)
        scores=layer_scores(event)
        known_threat_prob=float(max(probs[1:]) if len(probs)>1 else 0)
        risk=overall_score(scores, anomaly_score, known_threat_prob)
        # Unknown behavior is emphasized when anomaly is high while RF sees NORMAL.
        if flag and anomaly_score>=.52 and (pred=='NORMAL' or confidence < 0.80): final='UNKNOWN_ANOMALY'
        elif pred=='NORMAL' and not flag and anomaly_score<.52: final='NORMAL'
        elif risk>=82: final='CRITICAL THREAT'
        elif risk>=61 and pred!='NORMAL': final='HIGH-RISK THREAT'
        elif pred!='NORMAL': final='KNOWN THREAT'
        elif anomaly_score>=.45: final='SUSPICIOUS'
        else: final='NORMAL'
        probs_dict={str(c):round(float(p),4) for c,p in zip(classes,probs)}
        return {'prediction':final,'rf_prediction':pred,'confidence':round(confidence,4),'rf_probabilities':probs_dict,'anomaly_score':round(anomaly_score,4),'is_anomaly':flag,'risk_score':risk,'risk_level':risk_level(risk),'scores':scores,'explanation':explain(event,scores,anomaly_score,final)}

detector=Detector()
