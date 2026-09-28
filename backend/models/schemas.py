from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class SecurityEvent(BaseModel):
    model_config = ConfigDict(extra='allow')
    user_id: str = 'demo-user'
    timestamp: Optional[datetime] = None
    requests_per_minute: float = Field(30, ge=0)
    packets_sent: float = Field(120, ge=0)
    packets_received: float = Field(150, ge=0)
    bytes_sent: float = Field(12000, ge=0)
    bytes_received: float = Field(18000, ge=0)
    connection_count: float = Field(8, ge=0)
    connection_duration: float = Field(180, ge=0)
    unique_ports: float = Field(4, ge=0)
    unique_ips: float = Field(3, ge=0)
    protocol: str = 'HTTPS'
    destination_count: float = Field(4, ge=0)
    login_attempts: float = Field(2, ge=0)
    failed_logins: float = Field(0, ge=0)
    session_duration: float = Field(900, ge=0)
    files_accessed: float = Field(5, ge=0)
    resources_accessed: float = Field(6, ge=0)
    unusual_login_time: int = Field(0, ge=0, le=1)
    new_device: int = Field(0, ge=0, le=1)
    new_ip: int = Field(0, ge=0, le=1)
    privilege_changes: float = Field(0, ge=0)
    process_count: float = Field(45, ge=0)
    new_processes: float = Field(2, ge=0)
    cpu_usage: float = Field(25, ge=0, le=100)
    memory_usage: float = Field(45, ge=0, le=100)
    file_modifications: float = Field(4, ge=0)
    executable_count: float = Field(10, ge=0)
    system_connections: float = Field(8, ge=0)
    unusual_process_activity: float = Field(0, ge=0)
    api_requests: float = Field(30, ge=0)
    request_frequency: float = Field(3, ge=0)
    endpoint_count: float = Field(4, ge=0)
    error_rate: float = Field(0.02, ge=0, le=1)
    response_size: float = Field(2400, ge=0)
    http_methods: str = 'GET'
    unusual_endpoints: float = Field(0, ge=0)
    authentication_failures: float = Field(0, ge=0)
    label: Optional[str] = None
    attack_type: Optional[str] = None

class AnalyzeResponse(BaseModel):
    event_id: str
    timestamp: datetime
    prediction: str
    risk_score: float
    risk_level: str
    network_score: float
    user_score: float
    system_score: float
    application_score: float
    anomaly_score: float
    confidence: float
    is_anomaly: bool
    explanation: List[str]
    rf_probabilities: Dict[str, float]
    event: Dict[str, Any]

class SimulationRequest(BaseModel):
    scenario: str

class RiskThresholds(BaseModel):
    low_max: int = Field(30, ge=1, le=99)
    medium_max: int = Field(60, ge=2, le=99)
    high_max: int = Field(80, ge=3, le=100)
