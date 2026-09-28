from datetime import datetime, timezone
import json
from pathlib import Path
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from config import DATA_DIR, MODEL_DIR, SIMULATION_MODE
from database.mongodb import db
from models.schemas import SecurityEvent, SimulationRequest
from ml.predict import detector
from simulation.scenarios import scenario_event
from simulation.generator import generate_all
router=APIRouter()

def _event_result(event_dict, result, simulation=None):
    event_id=f"EVT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[-10:]}"
    now=datetime.now(timezone.utc)
    doc={**event_dict,'event_id':event_id,'timestamp':now.isoformat(),'prediction':result['prediction'],'risk_score':result['risk_score'],'risk_level':result['risk_level'],
         'network_score':result['scores']['network_score'],'user_score':result['scores']['user_score'],'system_score':result['scores']['system_score'],'application_score':result['scores']['application_score'],
         'anomaly_score':result['anomaly_score'],'confidence':result['confidence'],'is_anomaly':result['is_anomaly'],'rf_prediction':result['rf_prediction'],'rf_probabilities':result['rf_probabilities'],'explanation':result['explanation']}
    db.insert('security_events',doc)
    if result['prediction']!='NORMAL' or result['risk_level'] in ('HIGH','CRITICAL'):
        threat={k:doc[k] for k in ['event_id','timestamp','prediction','risk_score','risk_level','network_score','user_score','system_score','application_score','anomaly_score','confidence','explanation','rf_prediction']}
        db.insert('threats',threat)
    if result['risk_level'] in ('MEDIUM','HIGH','CRITICAL'):
        alert={'alert_id':f"ALT-{event_id[4:]}",'event_id':event_id,'timestamp':now.isoformat(),'risk_score':result['risk_score'],'risk_level':result['risk_level'],'threat_type':result['prediction'],'message':result['explanation'][0],'status':'OPEN' if result['risk_level'] in ('HIGH','CRITICAL') else 'WARNING'}
        db.insert('alerts',alert)
    if simulation:
        db.insert('simulation_results',{'simulation_id':f"SIM-{event_id[4:]}",'event_id':event_id,'scenario':simulation,'timestamp':now.isoformat(),'result':result})
    return event_id,now,doc

@router.get('/')
def root(): return {'name':'AI-Driven Multi-Layer Cybersecurity System','status':'running','mode':'defensive synthetic simulation'}

@router.get('/api/health')
def health(): return {'status':'ok','database':db.status(),'simulation_mode':SIMULATION_MODE,'models_ready':bool(detector.rf and detector.iso)}

@router.post('/api/analyze')
def analyze(event: SecurityEvent):
    payload=event.model_dump(); payload.pop('timestamp',None); payload.pop('label',None); payload.pop('attack_type',None)
    result=detector.analyze(payload); event_id,now,doc=_event_result(payload,result)
    return {'event_id':event_id,'timestamp':now,'prediction':result['prediction'],'risk_score':result['risk_score'],'risk_level':result['risk_level'],**result['scores'],'anomaly_score':result['anomaly_score'],'confidence':result['confidence'],'is_anomaly':result['is_anomaly'],'explanation':result['explanation'],'rf_probabilities':result['rf_probabilities'],'event':doc}

@router.post('/api/simulate')
def simulate(req: SimulationRequest):
    if not SIMULATION_MODE: raise HTTPException(403,'Simulation mode is disabled.')
    allowed={'normal','brute_force','port_scan','traffic_anomaly','api_anomaly','unknown'}
    if req.scenario not in allowed: raise HTTPException(400,f'Unsupported scenario. Use: {sorted(allowed)}')
    payload=scenario_event(req.scenario); result=detector.analyze(payload); event_id,now,doc=_event_result(payload,result,req.scenario)
    return {'scenario':req.scenario,'event_id':event_id,'timestamp':now,'prediction':result['prediction'],'risk_score':result['risk_score'],'risk_level':result['risk_level'],**result['scores'],'anomaly_score':result['anomaly_score'],'confidence':result['confidence'],'is_anomaly':result['is_anomaly'],'explanation':result['explanation'],'rf_probabilities':result['rf_probabilities'],'event':doc}

@router.get('/api/events')
def events(limit:int=Query(100,ge=1,le=500)): return db.find('security_events',limit=limit)

@router.get('/api/threats')
def threats(limit:int=Query(200,ge=1,le=500), risk_level:str|None=None, threat_type:str|None=None):
    docs=db.find('threats',limit=limit)
    if risk_level: docs=[d for d in docs if d.get('risk_level')==risk_level]
    if threat_type: docs=[d for d in docs if d.get('prediction')==threat_type]
    return docs

@router.get('/api/threats/{id}')
def threat(id:str):
    d=db.get('security_events','event_id',id)
    if not d: raise HTTPException(404,'Threat/event not found')
    return d

@router.get('/api/statistics')
def statistics():
    events=db.find('security_events',limit=5000)
    total=len(events); threats=sum(1 for e in events if e.get('prediction')!='NORMAL'); critical=sum(1 for e in events if e.get('risk_level')=='CRITICAL'); unknown=sum(1 for e in events if e.get('prediction')=='UNKNOWN_ANOMALY')
    avg=round(sum(float(e.get('risk_score',0)) for e in events)/total,2) if total else 0
    layers={k:round(sum(float(e.get(k,0)) for e in events)/total,2) if total else 0 for k in ['network_score','user_score','system_score','application_score']}
    distribution={}
    for e in events: distribution[e.get('prediction','NORMAL')]=distribution.get(e.get('prediction','NORMAL'),0)+1
    timeline=[]
    for e in events[:50]: timeline.append({'timestamp':e.get('timestamp'),'risk_score':e.get('risk_score',0),'prediction':e.get('prediction')})
    return {'total_events':total,'threats_detected':threats,'critical_threats':critical,'unknown_anomalies':unknown,'system_risk_score':avg,'layer_risk':layers,'threat_distribution':distribution,'timeline':list(reversed(timeline))}

@router.get('/api/dashboard')
def dashboard(): return statistics()

@router.get('/api/model-info')
def model_info():
    def load(name):
        p=MODEL_DIR/name
        return json.loads(p.read_text()) if p.exists() else None
    return {'random_forest':load('classifier_metrics.json'),'isolation_forest':load('anomaly_metrics.json'),'trained':bool(detector.rf and detector.iso)}

@router.post('/api/generate-data')
def generate_data():
    stats=generate_all(DATA_DIR,seed=42)
    return {'message':'Synthetic datasets regenerated','stats':stats,'files':[p.name for p in DATA_DIR.glob('*.csv')]}

@router.post('/api/retrain')
def retrain():
    from ml.train_classifier import train as train_classifier
    from ml.train_anomaly_detector import train as train_anomaly
    c=train_classifier(); a=train_anomaly(); detector.reload(); db.insert('model_metrics',{'timestamp':datetime.now(timezone.utc).isoformat(),'classifier':c,'anomaly':a})
    return {'message':'Models retrained successfully','random_forest':c,'isolation_forest':a}

@router.post('/api/reset')
def reset():
    db.clear(); return {'message':'Security event, threat, alert and simulation history reset.'}

@router.get('/api/alerts')
def alerts(limit:int=Query(100,ge=1,le=500)): return db.find('alerts',limit=limit)

@router.get('/api/data/download/{filename}')
def download_data(filename: str):
    allowed={'normal_behavior.csv','known_attacks.csv','unknown_behavior.csv','training_dataset.csv'}
    if filename not in allowed: raise HTTPException(400,'Unsupported dataset file.')
    p=DATA_DIR/filename
    if not p.exists(): raise HTTPException(404,'Dataset has not been generated yet.')
    return FileResponse(p, media_type='text/csv', filename=filename)

@router.get('/api/data/sample')
def data_sample(limit:int=20):
    files=['normal_behavior.csv','known_attacks.csv','unknown_behavior.csv']
    out={}
    for f in files:
        p=DATA_DIR/f
        if p.exists(): out[f]=pd.read_csv(p).head(limit).fillna('').to_dict(orient='records')
    return out
