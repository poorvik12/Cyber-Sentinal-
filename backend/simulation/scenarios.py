from simulation.generator import make_records
def scenario_event(name):
    mapping={
      'normal':('normal','NORMAL'), 'brute_force':('brute_force','BRUTE_FORCE'), 'port_scan':('port_scan','PORT_SCAN'),
      'traffic_anomaly':('traffic_anomaly','TRAFFIC_ANOMALY'), 'api_anomaly':('api_anomaly','API_ANOMALY'), 'unknown':('unknown','UNKNOWN_ANOMALY')}
    key,atype=mapping.get(name, mapping['normal'])
    seeds={'normal':101,'brute_force':202,'port_scan':303,'traffic_anomaly':404,'api_anomaly':505,'unknown':606}
    row=make_records(1,key,0 if key=='normal' else 1,atype,seed=seeds.get(name,101)).iloc[0].to_dict()
    row.pop('label',None); row.pop('attack_type',None)
    return row
