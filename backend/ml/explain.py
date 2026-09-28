def explain(e, scores, anomaly_score, prediction):
    reasons=[]
    checks=[
      (e['requests_per_minute']>100,'High request frequency exceeded the learned normal behavior range.'),
      (e['failed_logins']>10,'Failed login attempts are significantly higher than the normal profile.'),
      (e['unique_ports']>20,'Unusual port activity increased the network risk score.'),
      (e['unique_ips']>15,'The event contacted an unusually broad set of IPs.'),
      (e['cpu_usage']>75 or e['memory_usage']>80,'System resource usage differs significantly from the learned baseline.'),
      (e['unusual_process_activity']>3,'New or unusual process activity contributed to system risk.'),
      (e['api_requests']>150 or e['request_frequency']>30,'Application request frequency is materially above the normal profile.'),
      (e['error_rate']>.15,'Elevated application error rate indicates abnormal request behavior.'),
      (e['unusual_endpoints']>5,'Unusual endpoint activity increased application risk.'),
      (e['authentication_failures']>5,'Repeated authentication failures contributed to application risk.'),
      (e['files_accessed']>30 or e['resources_accessed']>30,'Resource access volume is unusually high.'),
      (e['privilege_changes']>0,'Privilege changes were observed and increased user-behavior risk.'),
      (anomaly_score>.65,'The behavior differs substantially from the learned normal baseline.')]
    for cond,msg in checks:
        if cond and msg not in reasons: reasons.append(msg)
    if not reasons: reasons=['Observed features remain within the learned behavioral baseline.']
    if prediction in ('UNKNOWN_ANOMALY','HIGH-RISK THREAT','CRITICAL THREAT') and len(reasons)<2:
        reasons.append('The combined multi-layer evidence indicates behavior that warrants investigation.')
    return reasons[:5]
