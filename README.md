# AI-Driven Multi-Layer Cybersecurity System Using Machine Learning and Synthetic Behavioral Data for Zero-Day Threat Detection

A complete defensive cybersecurity demonstration platform for final-year BE Computer Science / AI-ML projects. It combines synthetic behavioral data, supervised classification, unsupervised anomaly detection, multi-layer risk scoring, explainable analysis, safe attack simulation, persistence, and a React SOC dashboard.

> **Important terminology:** this project uses “zero-day-style detection” to mean detection of previously unseen or anomalous behavioral patterns. It is **not** a guarantee of detecting all real-world zero-day attacks.

## What is implemented

- React + Vite + Tailwind CSS frontend
- FastAPI + Uvicorn backend
- MongoDB integration with automatic local JSON fallback
- Synthetic generator: 10,000 normal + 3,000 known attack + 1,000 unknown anomaly records
- Random Forest known-attack classifier
- Isolation Forest normal-behavior anomaly detector
- Shared preprocessing pipeline with missing-value handling, categorical encoding and scaling
- Four layer scores: Network 30%, User 20%, System 30%, Application 20%
- Configurable risk thresholds
- Explainable feature-based reasons
- Safe synthetic simulations for normal, brute force, port scan, traffic anomaly, API anomaly and unknown anomaly scenarios
- Backend-driven dashboard statistics and event stream
- Threat history and detailed investigation pages
- Model metrics and real retraining endpoint
- Synthetic dataset generation and sample display
- Responsive cybersecurity/SOC visual design

## Project structure

```text
cybersecurity-project/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── mongodb.py
│   ├── data/
│   │   ├── normal_behavior.csv
│   │   ├── known_attacks.csv
│   │   ├── unknown_behavior.csv
│   │   ├── training_dataset.csv
│   │   └── runtime/              # local JSON fallback storage
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── preprocessing.py
│   │   ├── train_classifier.py
│   │   ├── train_anomaly_detector.py
│   │   ├── predict.py
│   │   ├── risk_engine.py
│   │   ├── explain.py
│   │   └── models/
│   ├── models/
│   │   └── schemas.py
│   ├── simulation/
│   │   ├── generator.py
│   │   └── scenarios.py
│   ├── utils/
│   ├── config.py
│   ├── generate_data.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── services/api.js
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10+
- Node.js 18+
- npm
- MongoDB is optional because the backend automatically falls back to local JSON storage.

## 1. Backend setup

Open a terminal in the project root:

```bash
cd backend
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`.

Windows:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

## 2. Generate synthetic data

From the project root:

```bash
python -m backend.generate_data
```

This creates:

- `backend/data/normal_behavior.csv` — 10,000 records
- `backend/data/known_attacks.csv` — 3,000 records
- `backend/data/unknown_behavior.csv` — 1,000 records
- `backend/data/training_dataset.csv` — normal + known attack training corpus

No real malware, payloads, external scanning, credentials, or live attacks are generated.

## 3. Train the ML models

```bash
python -m backend.ml.train_classifier
python -m backend.ml.train_anomaly_detector
```

The Random Forest prints:

- Accuracy
- Precision
- Recall
- F1 score
- Classification report

The trained artifacts are saved under `backend/ml/models/`.

## 4. Start the backend

From the **project root** with the virtual environment active:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

Health check:

- `http://localhost:8000/api/health`

## 5. Frontend setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

Optional frontend environment file:

```text
VITE_API_URL=http://localhost:8000
```

## 6. MongoDB

MongoDB is optional.

If you have MongoDB, set:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=cybersecurity_ai
```

Collections used:

- `security_events`
- `threats`
- `alerts`
- `simulation_results`
- `model_metrics`

If MongoDB is unavailable or `MONGODB_URI` is empty, the same operations use JSON files under `backend/data/runtime/` so the demonstration still works.

## 7. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Service information |
| GET | `/api/health` | Health/database/model status |
| POST | `/api/analyze` | Analyze one security event |
| POST | `/api/simulate` | Run safe synthetic scenario |
| GET | `/api/dashboard` | Dashboard aggregates |
| GET | `/api/threats` | Threat history |
| GET | `/api/threats/{id}` | Detailed event |
| GET | `/api/events` | Security event stream |
| GET | `/api/statistics` | Statistics and distributions |
| GET | `/api/model-info` | Model metrics/status |
| POST | `/api/generate-data` | Regenerate datasets |
| POST | `/api/retrain` | Retrain both models |
| POST | `/api/reset` | Reset stored event/threat/alert history |
| GET | `/api/alerts` | Alert history |
| GET | `/api/data/sample` | Sample generated records |

## 8. Risk scoring

The risk engine computes each layer from the event's actual behavioral features:

```text
Network       30%
User          20%
System        30%
Application   20%
```

The layer scores are then combined with anomaly and known-threat evidence. Risk thresholds are configurable through environment variables:

```env
RISK_LOW_MAX=30
RISK_MEDIUM_MAX=60
RISK_HIGH_MAX=80
```

Levels:

- 0–30: LOW
- 31–60: MEDIUM
- 61–80: HIGH
- 81–100: CRITICAL

## 9. How unknown-anomaly detection works

1. An incoming event is validated by Pydantic.
2. The same reusable preprocessing logic used during training prepares the features.
3. Random Forest produces a known-class prediction and class probabilities.
4. Isolation Forest compares the behavior with the learned normal baseline.
5. The risk engine combines Network/User/System/Application evidence.
6. If Isolation Forest flags strong abnormality while Random Forest sees the event as `NORMAL`, the final classification can become `UNKNOWN_ANOMALY`.
7. Human-readable explanations are generated from the actual feature values.
8. The result is stored as an event, and high-risk results also create threat/alert records.

This is the project's zero-day-style demonstration: the system is detecting behavior outside the known classification space rather than claiming knowledge of every future attack.

## 10. Safe attack simulation

From the dashboard's **Attack Simulator**, use:

- Simulate Normal
- Simulate Brute Force
- Simulate Port Scan
- Simulate Traffic Anomaly
- Simulate API Anomaly
- Simulate Unknown Behavior

Each action follows:

```text
React button
→ POST /api/simulate
→ synthetic event generator
→ Random Forest + Isolation Forest
→ risk engine
→ persistence
→ dashboard result
```

No real network activity is performed.

## 11. Demonstration flow

1. Open the landing page.
2. Enter the Security Dashboard.
3. Open Attack Simulator.
4. Run **Brute Force** and inspect the known-threat result.
5. Run **Unknown Behavior** and inspect whether the model produces an anomalous/unknown classification.
6. Open Threat History.
7. Open the event's Threat Detail page.
8. Inspect layer scores and explanations.
9. Open ML Models to show training metrics.
10. Open Synthetic Data to show the generated corpus.

## Limitations

- Synthetic data is not a substitute for production telemetry.
- Isolation Forest is an unsupervised anomaly detector, not a semantic zero-day oracle.
- Thresholds and synthetic profiles are designed for a project demonstration.
- Real SOC deployments require stronger identity, asset, time-series, streaming, model-governance, access-control and adversarial-validation mechanisms.

## Ethical considerations

This is a defensive cybersecurity project. It intentionally avoids:

- attacking real websites
- scanning external IP addresses
- exploiting vulnerabilities
- generating malware
- stealing credentials
- real brute-force attacks
- real port scans

All security incidents are simulated inside generated behavioral data.

## Final statement

> This project demonstrates detection of previously unseen behavioral anomalies and should not be interpreted as a guarantee of detecting all real-world zero-day attacks.
