
from datetime import datetime
import math


def safe_number(value):
    """Convert weather values safely into numbers."""
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def assess(current, forecast, air=None):
    """
    Free, explainable rule-based Climate Sentinel.
    No API key or paid AI service required.
    """

    alerts = []
    actions = []

    temp = safe_number(current.get("temperature_2m"))
    humidity = safe_number(current.get("relative_humidity_2m"))
    wind = safe_number(current.get("wind_speed_10m"))

    # Current temperature assessment
    if temp is not None:
        if temp >= 40:
            alerts.append(("HIGH", f"Extreme heat detected: {temp}°C"))
            actions.append("Avoid prolonged outdoor activity and stay hydrated.")
        elif temp >= 35:
            alerts.append(("MEDIUM", f"High temperature: {temp}°C"))
            actions.append("Limit outdoor activity during peak afternoon heat.")

    # Humidity assessment
    if humidity is not None and humidity >= 85:
        alerts.append(("MEDIUM", f"Very high humidity: {humidity}%"))
        actions.append("Maintain ventilation and monitor heat discomfort.")

    # Wind assessment
    if wind is not None:
        if wind >= 60:
            alerts.append(("HIGH", f"Strong wind conditions: {wind} km/h"))
            actions.append("Secure loose outdoor objects and monitor local advisories.")
        elif wind >= 40:
            alerts.append(("MEDIUM", f"Elevated wind speed: {wind} km/h"))
            actions.append("Use caution around trees and temporary structures.")

    # Forecast assessment
    if forecast is not None and not forecast.empty:
        if "rain" in forecast.columns:
            rainfall = forecast["rain"].apply(safe_number).dropna()

            if not rainfall.empty:
                max_rain = float(rainfall.max())

                if max_rain >= 100:
                    alerts.append(("HIGH", f"Heavy rainfall forecast: {max_rain} mm/day"))
                    actions.append("Monitor local flood advisories and avoid waterlogged routes.")
                elif max_rain >= 50:
                    alerts.append(("MEDIUM", f"Heavy rain possibility: {max_rain} mm/day"))
                    actions.append("Carry rain protection and check local weather updates.")

        if "tmax" in forecast.columns:
            temperatures = forecast["tmax"].apply(safe_number).dropna()

            if not temperatures.empty and temperatures.max() >= 40:
                alerts.append(("HIGH", "Extreme heat appears in the upcoming forecast."))
                actions.append("Plan outdoor activities around cooler hours.")

    # Air quality assessment
    if air:
        aqi = safe_number(air.get("us_aqi"))
        pm25 = safe_number(air.get("pm2_5"))

        if aqi is not None:
            if aqi > 150:
                alerts.append(("HIGH", f"Unhealthy air quality: US AQI {aqi}"))
                actions.append("Reduce outdoor exertion and check official air quality guidance.")
            elif aqi > 100:
                alerts.append(("MEDIUM", f"Elevated air pollution: US AQI {aqi}"))
                actions.append("Sensitive individuals should consider limiting outdoor exertion.")

        if pm25 is not None and pm25 > 35:
            alerts.append(("MEDIUM", f"Elevated PM2.5 concentration: {pm25}"))

    # Default status
    if not alerts:
        alerts.append(("LOW", "No significant weather risk detected by current screening rules."))
        actions.append("Continue monitoring live weather and forecast conditions.")

    # Remove duplicate recommendations
    actions = list(dict.fromkeys(actions))

    high_count = sum(1 for level, _ in alerts if level == "HIGH")
    medium_count = sum(1 for level, _ in alerts if level == "MEDIUM")

    if high_count:
        summary = f"{high_count} high-risk and {medium_count} medium-risk condition(s) detected."
    elif medium_count:
        summary = f"{medium_count} medium-risk condition(s) detected."
    else:
        summary = "Weather conditions currently appear relatively stable."

    return {
        "summary": summary,
        "generated_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        "alerts": alerts,
        "actions": actions
    }
