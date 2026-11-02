import hashlib, json, os, time
FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chain.json")
def _h(o): return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()
def load():
    if not os.path.exists(FILE): return []
    with open(FILE, encoding="utf-8") as f: return json.load(f)
def data_hash(df): return hashlib.sha256(df.to_csv(index=False).encode()).hexdigest()
def block_hash(b): return _h({k: v for k, v in b.items() if k != "hash"})

def add(city, lat, lon, start, end, df, difficulty=3):
    c = load()
    b = {"index": len(c), "time": time.time(), "city": city, "lat": lat, "lon": lon, "start": start, "end": end,
         "rows": len(df), "mean_temp": round(float(df.tmean.mean()), 3), "data_hash": data_hash(df),
         "prev": c[-1]["hash"] if c else "0" * 64, "nonce": 0}
    while not block_hash(b).startswith("0" * difficulty): b["nonce"] += 1   # proof of work
    b["hash"] = block_hash(b); c.append(b)
    tmp = FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(c, f, indent=1)
    os.replace(tmp, FILE)
    return b

def verify(c):
    for i, b in enumerate(c):
        if block_hash(b) != b["hash"]: return False, i, "Block ka data badla gaya (hash mismatch)"
        if i and b["prev"] != c[i - 1]["hash"]: return False, i, "Chain link toota (prev hash mismatch)"
    return True, None, "Poori chain valid hai"
