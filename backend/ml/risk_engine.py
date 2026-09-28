from backend.config import RISK_THRESHOLDS

def clamp(v): return round(max(0,min(100,float(v))),2)

def layer_scores(e):
    network = clamp(
        0.22*min(e['requests_per_minute']/120*100,100)+0.18*min(e['unique_ports']/25*100,100)+0.16*min(e['unique_ips']/15*100,100)+
        0.14*min(e['connection_count']/40*100,100)+0.12*min(e['packets_sent']/700*100,100)+0.10*min(e['destination_count']/30*100,100)+0.08*min(e['system_connections']/40*100,100)
    )
    user = clamp(0.35*min(e['failed_logins']/20*100,100)+0.15*min(e['login_attempts']/20*100,100)+0.12*min(e['files_accessed']/40*100,100)+0.10*min(e['resources_accessed']/30*100,100)+0.1*e['unusual_login_time']*100+0.08*e['new_device']*100+0.05*e['new_ip']*100+0.05*min(e['privilege_changes']/3*100,100))
    system = clamp(0.25*e['cpu_usage']+0.2*e['memory_usage']+0.15*min(e['new_processes']/12*100,100)+0.12*min(e['file_modifications']/25*100,100)+0.1*min(e['system_connections']/50*100,100)+0.1*min(e['executable_count']/30*100,100)+0.08*min(e['unusual_process_activity']/10*100,100))
    app = clamp(0.25*min(e['api_requests']/250*100,100)+0.2*min(e['request_frequency']/60*100,100)+0.15*min(e['endpoint_count']/50*100,100)+0.15*min(e['error_rate']*200,100)+0.1*min(e['unusual_endpoints']/15*100,100)+0.1*min(e['authentication_failures']/15*100,100)+0.05*min(e['response_size']/15000*100,100))
    return {'network_score':network,'user_score':user,'system_score':system,'application_score':app}

def risk_level(score):
    t=RISK_THRESHOLDS
    if score<=t['LOW_MAX']: return 'LOW'
    if score<=t['MEDIUM_MAX']: return 'MEDIUM'
    if score<=t['HIGH_MAX']: return 'HIGH'
    return 'CRITICAL'

def overall_score(scores, anomaly_score=0, known_probability=0):
    base=scores['network_score']*.30+scores['user_score']*.20+scores['system_score']*.30+scores['application_score']*.20
    return clamp(base*.75 + anomaly_score*100*.15 + known_probability*100*.10)
