from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
'user_id','timestamp','requests_per_minute','packets_sent','packets_received','bytes_sent','bytes_received','connection_count','connection_duration','unique_ports','unique_ips','protocol','destination_count','login_attempts','failed_logins','session_duration','files_accessed','resources_accessed','unusual_login_time','new_device','new_ip','privilege_changes','process_count','new_processes','cpu_usage','memory_usage','file_modifications','executable_count','system_connections','unusual_process_activity','api_requests','request_frequency','endpoint_count','error_rate','response_size','http_methods','unusual_endpoints','authentication_failures','label','attack_type']

PROFILES = {
    'normal': dict(req=(12,55), ps=(60,240), pr=(70,300), bs=(6000,30000), br=(8000,42000), conn=(3,15), dur=(60,600), ports=(1,8), ips=(1,6), dest=(2,8), log=(1,3), fail=(0,1), sess=(300,2400), files=(1,12), res=(2,15), cpu=(10,55), mem=(25,65), mods=(0,8), exe=(4,16), sysconn=(3,14), api=(8,70), freq=(1,8), endpoints=(2,10), err=(0.0,0.08), resp=(600,6000), unusual=(0,1), authfail=(0,1)),
    'brute_force': dict(req=(25,90), ps=(80,400), pr=(80,350), bs=(8000,45000), br=(9000,50000), conn=(8,30), dur=(30,300), ports=(2,10), ips=(1,5), dest=(2,8), log=(20,80), fail=(12,60), sess=(30,500), files=(1,10), res=(2,12), cpu=(15,65), mem=(30,75), mods=(0,6), exe=(4,18), sysconn=(5,20), api=(15,100), freq=(3,15), endpoints=(2,12), err=(0.08,0.35), resp=(500,5000), unusual=(0,2), authfail=(10,50)),
    'port_scan': dict(req=(30,110), ps=(250,900), pr=(180,700), bs=(15000,90000), br=(12000,70000), conn=(30,120), dur=(2,30), ports=(25,120), ips=(4,25), dest=(20,80), log=(1,5), fail=(0,3), sess=(30,400), files=(0,5), res=(1,8), cpu=(20,70), mem=(25,70), mods=(0,4), exe=(3,15), sysconn=(30,100), api=(20,120), freq=(5,25), endpoints=(10,50), err=(0.03,0.25), resp=(300,3000), unusual=(4,20), authfail=(0,3)),
    'traffic_anomaly': dict(req=(150,500), ps=(1200,6000), pr=(1000,5500), bs=(200000,900000), br=(180000,800000), conn=(80,300), dur=(5,90), ports=(5,25), ips=(10,60), dest=(20,100), log=(2,8), fail=(0,5), sess=(20,300), files=(2,15), res=(3,25), cpu=(55,98), mem=(55,95), mods=(2,20), exe=(5,25), sysconn=(50,220), api=(60,350), freq=(20,90), endpoints=(4,20), err=(0.05,0.3), resp=(1000,10000), unusual=(1,8), authfail=(0,5)),
    'api_anomaly': dict(req=(60,220), ps=(250,1200), pr=(250,1100), bs=(25000,180000), br=(25000,160000), conn=(10,60), dur=(10,180), ports=(2,15), ips=(2,15), dest=(5,30), log=(1,8), fail=(2,20), sess=(20,500), files=(3,25), res=(10,60), cpu=(20,80), mem=(30,80), mods=(0,12), exe=(4,20), sysconn=(8,35), api=(180,800), freq=(30,150), endpoints=(20,100), err=(0.15,0.6), resp=(100,30000), unusual=(5,30), authfail=(2,25)),
    'unknown': dict(req=(75,135), ps=(350,850), pr=(600,1800), bs=(50000,160000), br=(120000,450000), conn=(12,45), dur=(20,420), ports=(8,28), ips=(8,30), dest=(12,45), log=(4,12), fail=(3,12), sess=(80,900), files=(20,80), res=(8,45), cpu=(40,90), mem=(20,92), mods=(10,45), exe=(8,35), sysconn=(10,70), api=(70,260), freq=(12,60), endpoints=(12,55), err=(0.05,0.25), resp=(500,18000), unusual=(2,15), authfail=(1,12)),
}

def _clip_int(rng): return max(0, int(rng))
def _sample(profile, key, size, rng): return np.rint(rng.uniform(*profile[key], size=size)).astype(int)

def make_records(n, profile_name, label, attack_type, seed=42, start=None):
    rng = np.random.default_rng(seed)
    p = PROFILES[profile_name]
    start = start or datetime.utcnow() - timedelta(minutes=n)
    rows=[]
    for i in range(n):
        protocol = rng.choice(['HTTPS','HTTP','SSH','DNS','TCP'], p=[.48,.14,.12,.10,.16])
        method = rng.choice(['GET','POST','PUT','PATCH','DELETE'], p=[.56,.27,.08,.05,.04])
        row = {
            'user_id': f'user-{rng.integers(1,201):03d}', 'timestamp': start + timedelta(minutes=i),
            'requests_per_minute': _clip_int(_sample(p,'req',1,rng)[0]), 'packets_sent': _clip_int(_sample(p,'ps',1,rng)[0]),
            'packets_received': _clip_int(_sample(p,'pr',1,rng)[0]), 'bytes_sent': _clip_int(_sample(p,'bs',1,rng)[0]),
            'bytes_received': _clip_int(_sample(p,'br',1,rng)[0]), 'connection_count': _clip_int(_sample(p,'conn',1,rng)[0]),
            'connection_duration': _clip_int(_sample(p,'dur',1,rng)[0]), 'unique_ports': _clip_int(_sample(p,'ports',1,rng)[0]),
            'unique_ips': _clip_int(_sample(p,'ips',1,rng)[0]), 'protocol': protocol, 'destination_count': _clip_int(_sample(p,'dest',1,rng)[0]),
            'login_attempts': _clip_int(_sample(p,'log',1,rng)[0]), 'failed_logins': _clip_int(_sample(p,'fail',1,rng)[0]),
            'session_duration': _clip_int(_sample(p,'sess',1,rng)[0]), 'files_accessed': _clip_int(_sample(p,'files',1,rng)[0]),
            'resources_accessed': _clip_int(_sample(p,'res',1,rng)[0]), 'unusual_login_time': int(rng.random() < .08 if profile_name=='normal' else rng.random() < .45),
            'new_device': int(rng.random() < .06 if profile_name=='normal' else rng.random() < .3), 'new_ip': int(rng.random() < .08 if profile_name=='normal' else rng.random() < .4),
            'privilege_changes': int(rng.poisson(.1 if profile_name=='normal' else (1.2 if profile_name=='unknown' else .5))),
            'process_count': _clip_int(_sample(p,'exe',1,rng)[0] + rng.integers(20,45)), 'new_processes': int(rng.integers(0,5 if profile_name=='normal' else 15)),
            'cpu_usage': round(float(rng.uniform(*p['cpu'])),2), 'memory_usage': round(float(rng.uniform(*p['mem'])),2),
            'file_modifications': _clip_int(_sample(p,'mods',1,rng)[0]), 'executable_count': _clip_int(_sample(p,'exe',1,rng)[0]),
            'system_connections': _clip_int(_sample(p,'sysconn',1,rng)[0]), 'unusual_process_activity': _clip_int(_sample(p,'unusual',1,rng)[0]),
            'api_requests': _clip_int(_sample(p,'api',1,rng)[0]), 'request_frequency': _clip_int(_sample(p,'freq',1,rng)[0]),
            'endpoint_count': _clip_int(_sample(p,'endpoints',1,rng)[0]), 'error_rate': round(float(rng.uniform(*p['err'])),4),
            'response_size': _clip_int(_sample(p,'resp',1,rng)[0]), 'http_methods': method,
            'unusual_endpoints': _clip_int(_sample(p,'unusual',1,rng)[0]), 'authentication_failures': _clip_int(_sample(p,'authfail',1,rng)[0]),
            'label': label, 'attack_type': attack_type
        }
        rows.append(row)
    return pd.DataFrame(rows, columns=FEATURE_COLUMNS)

def generate_all(data_dir: Path, seed=42):
    data_dir.mkdir(parents=True, exist_ok=True)
    normal = make_records(10000,'normal',0,'NORMAL',seed)
    known_parts=[]
    for idx,(name,count,atype) in enumerate([('brute_force',750,'BRUTE_FORCE'),('port_scan',750,'PORT_SCAN'),('traffic_anomaly',750,'TRAFFIC_ANOMALY'),('api_anomaly',750,'API_ANOMALY')]):
        known_parts.append(make_records(count,name,1,atype,seed+idx+1))
    known = pd.concat(known_parts, ignore_index=True)
    unknown = make_records(1000,'unknown',1,'UNKNOWN_ANOMALY',seed+20)
    normal.to_csv(data_dir/'normal_behavior.csv', index=False)
    known.to_csv(data_dir/'known_attacks.csv', index=False)
    unknown.to_csv(data_dir/'unknown_behavior.csv', index=False)
    train = pd.concat([normal,known], ignore_index=True).sample(frac=1, random_state=seed)
    train.to_csv(data_dir/'training_dataset.csv', index=False)
    return {'normal':len(normal),'known':len(known),'unknown':len(unknown),'training':len(train)}
