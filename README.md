# Secure Climate Intelligence Platform

A free, portfolio-oriented Streamlit application combining Open-Meteo weather data, historical climate analytics, scikit-learn models, a hash-linked integrity demo, SQLite authentication and an explainable rule-based Climate Sentinel.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

First-run demo login: `admin` / `Admin@123`. Change the demo password and configure proper secrets before any shared deployment.

## Current modules
- `app.py`: dark Streamlit UI and analytics tabs
- `data.py`: Open-Meteo geocoding, archive, forecast and air-quality APIs
- `ml.py`: time-ordered evaluation, temperature models, rain classifier, anomaly detection and Mann–Kendall trend
- `agent.py`: explainable threshold-based climate monitoring and recommendations (not an LLM and not an official warning service)
- `chain.py`: SHA-256 hash-linked proof-of-work integrity demonstration
- `security.py`: PBKDF2 password hashing, lockout and audit logging

## Important limitations
- Forecast model is an educational baseline trained on historical data; validate against a proper rolling-origin backtest before operational use.
- Climate Sentinel uses transparent rules; it does not independently execute external actions.
- Hash-linked local JSON storage demonstrates integrity concepts; it is not a distributed blockchain network.
- Weather data depends on Open-Meteo service availability and coverage.
