import numpy as np, pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier, IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, f1_score, confusion_matrix

FEATS = [f"lag{i}" for i in range(1, 8)] + ["roll7", "s", "c"]

def mann_kendall(x):
    x = np.asarray(x, float); n = len(x)
    s = sum(np.sign(x[j] - x[i]) for i in range(n - 1) for j in range(i + 1, n))
    z = (s - np.sign(s)) / np.sqrt(n * (n - 1) * (2 * n + 5) / 18)
    slope = np.median([(x[j] - x[i]) / (j - i) for i in range(n - 1) for j in range(i + 1, n)])
    return z, 2 * (1 - norm.cdf(abs(z))), slope

def feats(df):
    d = df[["time", "tmean"]].copy()
    for i in range(1, 8): d[f"lag{i}"] = d.tmean.shift(i)
    d["roll7"] = d.tmean.shift(1).rolling(7).mean()
    doy = d.time.dt.dayofyear
    d["s"], d["c"] = np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)
    d["y"] = d.tmean
    return d.dropna()

def compare(df):
    d = feats(df); cut = int(len(d) * .8); tr, te = d.iloc[:cut], d.iloc[cut:]
    ms = {"Linear Regression": LinearRegression(),
          "Random Forest": RandomForestRegressor(150, n_jobs=-1, random_state=1),
          "Gradient Boosting": GradientBoostingRegressor(random_state=1)}
    preds = {"Persistence (kal = aaj)": te.lag1.values}
    for n, m in ms.items():
        m.fit(tr[FEATS], tr.y); preds[n] = m.predict(te[FEATS])
    met = pd.DataFrame([(n, mean_absolute_error(te.y, p), np.sqrt(mean_squared_error(te.y, p)), r2_score(te.y, p))
                        for n, p in preds.items()], columns=["Model", "MAE", "RMSE", "R2"]).sort_values("RMSE")
    return met, ms, te[["time", "y"]].assign(**preds)

def forecast7(model, df):
    v = list(df.tmean.values[-7:]); t = df.time.iloc[-1]; out = []
    for _ in range(7):
        t = t + pd.Timedelta(days=1); doy = t.dayofyear
        x = [v[-i] for i in range(1, 8)] + [np.mean(v[-7:]), np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)]
        p = float(model.predict(pd.DataFrame([x], columns=FEATS))[0]); v.append(p); out.append((t, p))
    return pd.DataFrame(out, columns=["time", "pred_tmean"])

def rain_clf(df):
    d = df.copy(); d["wet"] = (d.rain >= 1).astype(int)
    for i in (1, 2, 3):
        for c in ("rain", "tmean", "wind"): d[f"{c}{i}"] = d[c].shift(i)
    doy = d.time.dt.dayofyear
    d["s"], d["c"] = np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)
    d = d.dropna(); X = [c for c in d.columns if c[-1] in "123" or c in ("s", "c")]
    cut = int(len(d) * .8); m = RandomForestClassifier(200, class_weight="balanced", n_jobs=-1, random_state=1)
    m.fit(d[X].iloc[:cut], d.wet.iloc[:cut]); p = m.predict(d[X].iloc[cut:]); y = d.wet.iloc[cut:]
    return accuracy_score(y, p), f1_score(y, p), confusion_matrix(y, p), pd.Series(m.feature_importances_, X).sort_values()

def anomalies(df, contamination=0.01):
    d = df.copy(); X = d[["tmax", "tmin", "rain", "wind"]]
    d["anomaly"] = IsolationForest(contamination=contamination, random_state=1).fit_predict(X) == -1
    return d
