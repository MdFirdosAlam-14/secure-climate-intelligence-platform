import requests, pandas as pd, streamlit as st
G = "https://geocoding-api.open-meteo.com/v1/search"
A = "https://archive-api.open-meteo.com/v1/archive"
F = "https://api.open-meteo.com/v1/forecast"
Q = "https://air-quality-api.open-meteo.com/v1/air-quality"

def _json(url, params, timeout=30):
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise ValueError(payload.get("reason", "Weather service returned an error"))
    return payload

@st.cache_data(ttl=3600)
def coords(city):
    results = _json(G, {"name": city, "count": 1}).get("results") or []
    if not results:
        raise ValueError(f"No matching city found for '{city}'")
    r = results[0]
    return r["latitude"], r["longitude"], r["name"]

@st.cache_data(ttl=3600)
def history(lat, lon, start, end):
    p = {"latitude": lat, "longitude": lon, "start_date": start, "end_date": end, "timezone": "auto",
         "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_max"}
    daily = _json(A, p, timeout=90).get("daily")
    if not daily or not daily.get("time"):
        raise ValueError("No historical weather data returned for this location/date range")
    df = pd.DataFrame(daily)
    df.columns = ["time", "tmax", "tmin", "tmean", "rain", "wind"]
    df["time"] = pd.to_datetime(df["time"])
    return df.dropna().reset_index(drop=True)

@st.cache_data(ttl=600)
def live(lat, lon):
    p = {"latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 7,
         "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,surface_pressure,precipitation",
         "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum"}
    j = _json(F, p)
    if "current" not in j or "daily" not in j:
        raise ValueError("Live weather service did not return current and daily data")
    d = pd.DataFrame(j["daily"]); d.columns = ["time", "tmax", "tmin", "rain"]
    d["time"] = pd.to_datetime(d["time"])
    return j["current"], d

@st.cache_data(ttl=600)
def aqi(lat, lon):
    j = _json(Q, {"latitude": lat, "longitude": lon, "current": "us_aqi,pm2_5,pm10"})
    return j.get("current", {})
