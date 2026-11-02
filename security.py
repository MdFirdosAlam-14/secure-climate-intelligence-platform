import sqlite3
import hashlib
import os
import re
import time
import hmac
from contextlib import contextmanager

# Keep app.db beside this file, regardless of the terminal's working directory.
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")


@contextmanager
def _c():
    """Open a SQLite connection and always commit/rollback and close it."""
    conn = sqlite3.connect(DB, timeout=15)
    conn.execute("PRAGMA busy_timeout = 15000")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _hash(p, s):
    return hashlib.pbkdf2_hmac("sha256", p.encode(), s, 200_000)


def init():
    with _c() as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS users("
            "u TEXT PRIMARY KEY, salt BLOB, h BLOB, role TEXT)"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS audit("
            "t TEXT, u TEXT, a TEXT)"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS fails("
            "u TEXT PRIMARY KEY, n INT, t REAL)"
        )
        user_exists = c.execute(
            "SELECT 1 FROM users LIMIT 1"
        ).fetchone()

    # Create the demo admin only if the users table is empty.
    if not user_exists:
        register("admin", "Admin@123", "admin")


def log(u, a):
    with _c() as c:
        c.execute(
            "INSERT INTO audit VALUES(?,?,?)",
            (time.strftime("%Y-%m-%d %H:%M:%S"), u, a)
        )


def register(u, p, role="user"):
    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", u or ""):
        return False, "Username 3-20 chars (letters/digits/_)"

    if len(p or "") < 8:
        return False, "Password kam se kam 8 chars ka ho"

    salt = os.urandom(16)
    try:
        with _c() as c:
            c.execute(
                "INSERT INTO users VALUES(?,?,?,?)",
                (u, salt, _hash(p, salt), role)
            )
    except sqlite3.IntegrityError:
        return False, "Username already exists"

    log(u, "register")
    return True, "Registered. Ab login karo."


def login(u, p):
    # Finish the fails/users transaction before writing to the audit table.
    with _c() as c:
        failure = c.execute(
            "SELECT n,t FROM fails WHERE u=?", (u,)
        ).fetchone()

        if failure and failure[0] >= 5 and time.time() - failure[1] < 300:
            return False, "5 galat attempts: 5 min ke liye lock"

        user = c.execute(
            "SELECT salt,h,role FROM users WHERE u=?", (u,)
        ).fetchone()

        if user and hmac.compare_digest(_hash(p, user[0]), user[1]):
            c.execute("DELETE FROM fails WHERE u=?", (u,))
            result = (True, user[2])
            action = "login ok"
        else:
            now = time.time()
            c.execute(
                "INSERT INTO fails VALUES(?,1,?) "
                "ON CONFLICT(u) DO UPDATE SET n=n+1, t=?",
                (u, now, now)
            )
            result = (False, "Galat username/password")
            action = "login FAILED"

    # This write happens only after the previous connection has closed.
    log(u or "?", action)
    return result


def audit_log():
    with _c() as c:
        return c.execute(
            "SELECT * FROM audit ORDER BY t DESC LIMIT 200"
        ).fetchall()


def plausible(r):
    return (
        -60 <= r.tmin <= r.tmax <= 56
        and 0 <= r.rain <= 1000
        and 0 <= r.wind <= 250
    )
