
import re
import datetime as dt

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import data
import ml
import chain
import security
import agent


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Climate Intelligence Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# 2. PREMIUM DARK THEME
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: #080f1b;
    color: #e5edf7;
}

[data-testid="stHeader"] {
    background: rgba(8,15,27,0.9);
}

[data-testid="stSidebar"] {
    background: #101b2b;
    border-right: 1px solid #24364d;
}

.block-container {
    max-width: 1550px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(120deg,#132d49,#16445a,#172b46);
    border: 1px solid #315574;
    padding: 27px;
    border-radius: 18px;
    margin-bottom: 22px;
}

.hero h1 {
    color: #f0f7ff;
    font-size: 2.1rem;
    margin: 0;
}

.hero p {
    color: #a9c4dc;
    margin-top: 8px;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg,#14263c,#192f49);
    border: 1px solid #2a4562;
    padding: 18px;
    border-radius: 14px;
}

[data-testid="stMetricLabel"] {
    color: #a9bfd4;
}

[data-testid="stMetricValue"] {
    color: #f0f7ff;
}

div[data-testid="stTabs"] button {
    font-weight: 600;
    color: #b9cce0;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #60c7ff;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

.stButton > button {
    border-radius: 9px;
    font-weight: 600;
}

.section-title {
    color: #70caff;
    font-weight: 700;
    font-size: 1.15rem;
}

.footer {
    text-align: center;
    color: #8297ad;
    padding: 25px;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. INITIALIZE SECURITY
# --------------------------------------------------

security.init()

if "user" not in st.session_state:
    st.session_state.user = None


# --------------------------------------------------
# 4. LOGIN PAGE
# --------------------------------------------------

if not st.session_state.user:

    st.markdown("""
    <div class="hero">
        <h1>🌍 Climate Intelligence Platform</h1>
        <p>AI-assisted climate monitoring · Machine Learning ·
        Blockchain verification · Cybersecurity</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1, 1.2])

    with left:

        st.subheader("🔐 Secure Authentication")

        username = st.text_input("Username", key="login_user")

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        c1, c2 = st.columns(2)

        if c1.button("Login", use_container_width=True,
                      type="primary"):

            ok, result = security.login(username, password)

            if ok:
                st.session_state.user = (username, result)
                st.rerun()
            else:
                st.error(result)

        if c2.button("Register", use_container_width=True):

            ok, result = security.register(username, password)

            if ok:
                st.success(result)
            else:
                st.error(result)

        st.caption(
            "Demo account: admin / Admin@123. "
            "Change the demo password before deployment."
        )

    with right:

        st.markdown("### Welcome to Climate Intelligence")

        st.info(
            "Monitor real-time weather, analyse historical climate "
            "patterns, evaluate machine learning predictions and "
            "verify climate data integrity."
        )

        st.markdown("""
        **Platform capabilities**

        - 🌦️ Live Weather Intelligence
        - 🤖 Climate Sentinel
        - 📊 Machine Learning Forecasting
        - 🔍 Anomaly Detection
        - ⛓️ Blockchain Verification
        - 🛡️ Security Monitoring
        """)

    st.stop()


# --------------------------------------------------
# 5. USER SESSION
# --------------------------------------------------

user, role = st.session_state.user


# --------------------------------------------------
# 6. SIDEBAR
# --------------------------------------------------

st.sidebar.markdown("# 🌍 Climate AI")

st.sidebar.caption("SECURE CLIMATE INTELLIGENCE")

st.sidebar.divider()

st.sidebar.write(f"👤 **{user}**")
st.sidebar.caption(f"Role: {role}")

if st.sidebar.button("Logout", use_container_width=True):

    security.log(user, "logout")
    st.session_state.user = None
    st.rerun()

st.sidebar.divider()

st.sidebar.markdown("### 📍 Location Settings")

city = st.sidebar.text_input(
    "Search city",
    value="Dhanbad"
)

years = st.sidebar.slider(
    "Historical data period",
    min_value=5,
    max_value=30,
    value=20
)

if not re.fullmatch(r"[A-Za-z .\-]{2,40}", city):
    st.error("Please enter a valid city name.")
    st.stop()


# --------------------------------------------------
# 7. WEATHER DATA
# --------------------------------------------------

end = dt.date.today() - dt.timedelta(days=7)
start = dt.date(end.year - years, 1, 1)

with st.spinner("Loading climate intelligence..."):

    try:

        lat, lon, name = data.coords(city)

        df = data.history(
            lat, lon, str(start), str(end)
        )

        current, forecast = data.live(lat, lon)

    except Exception as error:

        st.error(f"Weather data unavailable: {error}")
        st.stop()

security.log(user, f"view {name}")

try:
    air = data.aqi(lat, lon)
except Exception:
    air = None


# --------------------------------------------------
# 8. MAIN DASHBOARD HEADER
# --------------------------------------------------

st.markdown(f"""
<div class="hero">
    <h1>🌦️ {name} Climate Overview</h1>
    <p>Real-time weather · Climate analytics · AI risk assessment
    · Secure data monitoring</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 9. WEATHER METRICS
# --------------------------------------------------

st.markdown("### 📊 Live Weather Intelligence")

m = st.columns(5)

m[0].metric(
    "Temperature",
    f"{current.get('temperature_2m', '—')} °C"
)

m[1].metric(
    "Humidity",
    f"{current.get('relative_humidity_2m', '—')} %"
)

m[2].metric(
    "Wind Speed",
    f"{current.get('wind_speed_10m', '—')} km/h"
)

m[3].metric(
    "Pressure",
    f"{current.get('surface_pressure', '—')} hPa"
)

m[4].metric(
    "US AQI",
    str(air.get("us_aqi", "—")) if air else "Unavailable"
)


# --------------------------------------------------
# 10. CLIMATE SENTINEL
# --------------------------------------------------

st.markdown("---")
st.markdown("### 🤖 Climate Sentinel AI")

report = agent.assess(current, forecast, air)

with st.container(border=True):

    st.write(f"**Assessment:** {report['summary']}")

    st.caption(f"Last scan: {report['generated_at']}")

    for level, message in report["alerts"]:

        if level == "HIGH":
            st.error("🔴 HIGH RISK · " + message)

        elif level == "MEDIUM":
            st.warning("🟠 MEDIUM RISK · " + message)

        else:
            st.success("🟢 LOW RISK · " + message)

    st.markdown("**Recommended Actions**")

    for action in report["actions"]:
        st.write("• " + action)

    st.caption(
        "Rule-based screening only. Not an official emergency "
        "warning service."
    )


# --------------------------------------------------
# 11. NAVIGATION
# --------------------------------------------------

tabs = st.tabs([
    "🌦️ Overview",
    "📚 History",
    "📈 Climate Trends",
    "🤖 ML Forecast",
    "🔍 Anomalies",
    "⛓️ Blockchain",
    "🛡️ Security"
])


# --------------------------------------------------
# 12. OVERVIEW
# --------------------------------------------------

with tabs[0]:

    st.subheader("7-Day Weather Outlook")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.line(
            forecast,
            x="time",
            y=["tmax", "tmin"],
            markers=True,
            title="Temperature Forecast"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        fig = px.bar(
            forecast,
            x="time",
            y="rain",
            title="Expected Rainfall (mm)"
        )

        st.plotly_chart(fig, use_container_width=True)

    if air:

        st.subheader("Air Quality Information")

        st.json({
            "US AQI": air.get("us_aqi"),
            "PM2.5": air.get("pm2_5"),
            "PM10": air.get("pm10")
        })


# --------------------------------------------------
# 13. HISTORICAL DATA
# --------------------------------------------------

with tabs[1]:

    st.subheader("Historical Climate Analysis")

    st.plotly_chart(
        px.line(
            df,
            x="time",
            y=["tmax", "tmin"],
            title="Historical Temperature"
        ),
        use_container_width=True
    )

    monthly = (
        df.set_index("time")
        .rain.resample("MS")
        .sum()
        .reset_index()
    )

    st.plotly_chart(
        px.bar(
            monthly,
            x="time",
            y="rain",
            title="Monthly Rainfall"
        ),
        use_container_width=True
    )

    pivot = df.assign(
        Year=df.time.dt.year,
        Month=df.time.dt.month
    ).pivot_table(
        index="Year",
        columns="Month",
        values="tmean"
    )

    st.plotly_chart(
        px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="RdYlBu_r",
            title="Temperature Heatmap"
        ),
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download Historical CSV",
        df.to_csv(index=False),
        file_name=f"{name}_climate.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# 14. CLIMATE TRENDS
# --------------------------------------------------

with tabs[2]:

    st.subheader("Long-Term Climate Trends")

    yr = df.groupby(
        df.time.dt.year
    ).agg(
        tmean=("tmean", "mean"),
        heat=("tmax", lambda x: (x >= 40).sum()),
        rain=("rain", "sum")
    )

    if len(yr) > 3:
        yr = yr.iloc[:-1]

    if len(yr) >= 3:

        z, pv, slope = ml.mann_kendall(yr.tmean)

        fig = px.line(
            yr,
            y="tmean",
            title="Annual Mean Temperature"
        )

        fig.add_scatter(
            x=yr.index,
            y=np.polyval(
                np.polyfit(yr.index, yr.tmean, 1),
                yr.index
            ),
            name="Linear Trend"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.info(
            f"Mann-Kendall Z: {z:.2f} | "
            f"P-value: {pv:.4f} | "
            f"Sen's slope: {slope * 10:+.2f} °C/decade"
        )

    else:
        st.warning("Insufficient yearly data for trend analysis.")

    st.plotly_chart(
        px.bar(
            yr,
            y="heat",
            title="Annual Extreme Heat Days"
        ),
        use_container_width=True
    )

    cities = st.multiselect(
        "Compare Cities",
        ["Dhanbad", "Asansol", "Kolkata", "Ranchi", "Delhi", "Mumbai"],
        ["Dhanbad", "Kolkata"]
    )

    rows = []

    for selected_city in cities:

        try:

            la, lo, nm = data.coords(selected_city)

            historical = data.history(
                la, lo, str(start), str(end)
            )

            annual = historical.groupby(
                historical.time.dt.year
            ).tmean.mean().iloc[:-1]

            rows.extend(
                [(nm, year, value) for year, value in annual.items()]
            )

        except Exception as error:
            st.warning(f"{selected_city}: {error}")

    if rows:

        comparison = pd.DataFrame(
            rows,
            columns=["City", "Year", "Mean Temperature"]
        )

        st.plotly_chart(
            px.line(
                comparison,
                x="Year",
                y="Mean Temperature",
                color="City",
                title="City Climate Comparison"
            ),
            use_container_width=True
        )


# --------------------------------------------------
# 15. MACHINE LEARNING
# --------------------------------------------------

with tabs[3]:

    st.subheader("Machine Learning Forecasting")

    try:

        metrics, models, test = ml.compare(df)

        st.markdown("**Model Performance Comparison**")

        st.dataframe(
            metrics.round(3),
            use_container_width=True
        )

        eligible = metrics[
            metrics.Model.isin(models)
        ]

        if not eligible.empty:

            best = eligible.iloc[0].Model

            st.success(f"Best trained model: {best}")

            st.plotly_chart(
                px.line(
                    test.tail(120),
                    x="time",
                    y=["y", best],
                    title="Actual vs Predicted Temperature"
                ),
                use_container_width=True
            )

            st.plotly_chart(
                px.line(
                    ml.forecast7(models[best], df),
                    x="time",
                    y="pred_tmean",
                    markers=True,
                    title="Experimental 7-Day ML Forecast"
                ),
                use_container_width=True
            )

            if hasattr(models[best], "feature_importances_"):

                st.plotly_chart(
                    px.bar(
                        x=models[best].feature_importances_,
                        y=ml.FEATS,
                        orientation="h",
                        title="Feature Importance"
                    ),
                    use_container_width=True
                )

        accuracy, f1, cm, _ = ml.rain_clf(df)

        st.markdown("**Rainfall Classification**")

        c1, c2 = st.columns(2)

        c1.metric("Accuracy", f"{accuracy:.2%}")
        c2.metric("F1 Score", f"{f1:.3f}")

        st.plotly_chart(
            px.imshow(
                cm,
                text_auto=True,
                x=["Dry", "Wet"],
                y=["Dry", "Wet"],
                labels={"x": "Predicted", "y": "Actual"},
                title="Confusion Matrix"
            ),
            use_container_width=True
        )

    except Exception as error:

        st.error(f"ML analysis could not complete: {error}")

    st.caption(
        "Historical holdout metrics are experimental and do not "
        "guarantee future prediction accuracy."
    )


# --------------------------------------------------
# 16. ANOMALY DETECTION
# --------------------------------------------------

with tabs[4]:

    st.subheader("Weather Anomaly Detection")

    contamination = st.slider(
        "Expected anomaly fraction (%)",
        0.5,
        5.0,
        1.0
    ) / 100

    try:

        anomalies = ml.anomalies(df, contamination)

        st.plotly_chart(
            px.scatter(
                anomalies,
                x="time",
                y="tmax",
                color="anomaly",
                color_discrete_map={
                    True: "#fb7185",
                    False: "#94a3b8"
                },
                title="Isolation Forest Anomaly Screening"
            ),
            use_container_width=True
        )

        st.dataframe(
            anomalies[
                anomalies.anomaly
            ].drop(columns="anomaly").tail(30),
            use_container_width=True
        )

    except Exception as error:
        st.error(f"Anomaly detection error: {error}")


# --------------------------------------------------
# 17. BLOCKCHAIN
# --------------------------------------------------

with tabs[5]:

    st.subheader("Blockchain Data Verification")

    st.info(
        "Climate snapshots are linked using SHA-256 hashes "
        "and a proof-of-work demonstration."
    )

    if st.button("⛏️ Mine New Block", type="primary"):

        block = chain.add(
            name, lat, lon,
            str(start), str(end), df
        )

        security.log(
            user,
            f"mined block {block['index']}"
        )

        st.success(
            f"Block {block['index']} created: "
            f"{block['hash'][:24]}..."
        )

    blocks = chain.load()

    if blocks:

        st.dataframe(
            pd.DataFrame(blocks)[
                [
                    "index", "city", "start", "end",
                    "rows", "mean_temp", "nonce",
                    "hash", "prev"
                ]
            ],
            use_container_width=True
        )

        valid, index, message = chain.verify(blocks)

        if valid:
            st.success(message)
        else:
            st.error(message)

        st.subheader("Tamper Detection Test")

        idx = st.number_input(
            "Select Block Index",
            min_value=0,
            max_value=len(blocks) - 1,
            value=0
        )

        if st.button("Test Tamper Detection"):

            altered = [dict(b) for b in blocks]

            altered[idx]["mean_temp"] += 5

            ok, bad, message = chain.verify(altered)

            st.error(
                f"Tampering detected at block {bad}: {message}"
            )

        if st.button("Verify Against Source Data"):

            block = blocks[idx]

            fresh = data.history(
                block["lat"],
                block["lon"],
                block["start"],
                block["end"]
            )

            match = (
                chain.data_hash(fresh) ==
                block["data_hash"]
            )

            if match:
                st.success("Source data hash matches.")
            else:
                st.warning(
                    "Source data hash differs. "
                    "The source may have changed."
                )

    else:
        st.info("No blockchain records available yet.")


# --------------------------------------------------
# 18. SECURITY CENTER
# --------------------------------------------------

with tabs[6]:

    st.subheader("🛡️ Security Monitoring Center")

    st.markdown("**Input Validation Test**")

    if st.button("Run Security Validation Demo"):

        fake = df.copy()

        fake.loc[
            len(fake) // 2,
            ["tmax", "tmean", "rain"]
        ] = [80, 70, 900]

        invalid = fake[
            ~fake.apply(security.plausible, axis=1)
        ]

        st.error(
            f"{len(invalid)} invalid weather record(s) detected."
        )

        st.dataframe(
            invalid,
            use_container_width=True
        )

    if role == "admin":

        st.divider()

        st.markdown("**Authentication Audit Logs**")

        logs = security.audit_log()

        st.dataframe(
            pd.DataFrame(
                logs,
                columns=["Time", "User", "Action"]
            ),
            use_container_width=True
        )

    else:

        st.info(
            "Authentication audit logs are available to administrators only."
        )


# --------------------------------------------------
# 19. FOOTER
# --------------------------------------------------

st.markdown("""
<div class="footer">
    Secure Climate Intelligence Platform · Version 2.0
    <br>
    AI-assisted analysis · Machine Learning · Data Integrity · Cybersecurity
</div>
""", unsafe_allow_html=True)
