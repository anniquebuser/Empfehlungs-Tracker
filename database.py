import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "referral_tracker.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # ── USERS ──────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            company     TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── REFERRALS ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id       INTEGER NOT NULL REFERENCES users(id),
            receiver_id     INTEGER NOT NULL REFERENCES users(id),
            -- Lead info
            lead_name       TEXT    NOT NULL,
            lead_email      TEXT,
            lead_phone      TEXT,
            lead_company    TEXT,
            reason          TEXT,
            -- Status workflow: open → contacted → in_progress → closed
            status          TEXT    NOT NULL DEFAULT 'open',
            -- Revenue (only filled when status = closed)
            revenue         REAL,
            -- Timestamps
            created_at      TEXT    DEFAULT (datetime('now')),
            contacted_at    TEXT,
            in_progress_at  TEXT,
            closed_at       TEXT,
            -- Notification flags
            notified_receiver   INTEGER DEFAULT 0,
            notified_sender_contacted INTEGER DEFAULT 0
        )
    """)

    # ── DEMO DATA ──────────────────────────────────────────────────────────────
    # Insert demo users if table is empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        demo_users = [
            ("Anna Müller",  "anna@demo.com",  hash_password("demo123"), "Müller Consulting"),
            ("Ben Schneider","ben@demo.com",   hash_password("demo123"), "Schneider GmbH"),
            ("Clara Becker", "clara@demo.com", hash_password("demo123"), "Becker & Partner"),
            ("David Lehmann","david@demo.com", hash_password("demo123"), "Lehmann Tech"),
        ]
        c.executemany(
            "INSERT INTO users (name, email, password, company) VALUES (?,?,?,?)",
            demo_users
        )

        # Insert demo referrals
        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        demo_referrals = [
            (1, 2, "Thomas Huber",   "t.huber@example.com",   "+41 79 111 22 33",
             "Huber AG",   "Kennt sich super im Bereich ERP aus, sucht Beratung.",
             "closed",   12500.0, now, now, now, now),
            (2, 1, "Sandra Vogel",   "s.vogel@example.com",   "+41 78 222 33 44",
             "Vogel GmbH", "Hat mir erzählt, dass sie eine neue Website braucht.",
             "in_progress", None, now, now, now, None),
            (3, 1, "Marc Zimmermann","m.zimm@example.com",    "+41 76 333 44 55",
             "Zimm Bau",   "Interessiert an digitaler Transformation.",
             "contacted",   None, now, now, None, None),
            (1, 3, "Eva Keller",     "e.keller@example.com",  "+41 77 444 55 66",
             "Keller Shop","Sucht jemanden für Social-Media-Strategie.",
             "open",        None, now, None, None, None),
            (4, 2, "Peter Lenz",     "p.lenz@example.com",    "+41 79 555 66 77",
             "Lenz IT",    "Benötigt Cloud-Migration-Projekt.",
             "closed",   8750.0,  now, now, now, now),
        ]
        c.executemany("""
            INSERT INTO referrals
              (sender_id, receiver_id, lead_name, lead_email, lead_phone, lead_company,
               reason, status, revenue, created_at, contacted_at, in_progress_at, closed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, demo_referrals)

    conn.commit()
    conn.close()


# ── AUTH ───────────────────────────────────────────────────────────────────────

def login_user(email: str, password: str):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def register_user(name, email, password, company=""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password, company) VALUES (?,?,?,?)",
            (name, email, hash_password(password), company)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_users():
    conn = get_connection()
    users = conn.execute("SELECT id, name, email, company FROM users").fetchall()
    conn.close()
    return [dict(u) for u in users]


# ── REFERRALS ──────────────────────────────────────────────────────────────────

def create_referral(sender_id, receiver_id, lead_name, lead_email,
                    lead_phone, lead_company, reason):
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO referrals
          (sender_id, receiver_id, lead_name, lead_email, lead_phone, lead_company, reason)
        VALUES (?,?,?,?,?,?,?)
    """, (sender_id, receiver_id, lead_name, lead_email, lead_phone, lead_company, reason))
    referral_id = cur.lastrowid
    conn.commit()
    conn.close()
    return referral_id

def get_referrals_for_user(user_id):
    """Returns all referrals sent OR received by user_id, with sender/receiver names."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.*,
               s.name  AS sender_name,  s.email  AS sender_email,
               rc.name AS receiver_name, rc.email AS receiver_email
        FROM   referrals r
        JOIN   users s  ON s.id  = r.sender_id
        JOIN   users rc ON rc.id = r.receiver_id
        WHERE  r.sender_id = ? OR r.receiver_id = ?
        ORDER  BY r.created_at DESC
    """, (user_id, user_id)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_referral_by_id(referral_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT r.*,
               s.name  AS sender_name,  s.email  AS sender_email,
               rc.name AS receiver_name, rc.email AS receiver_email
        FROM   referrals r
        JOIN   users s  ON s.id  = r.sender_id
        JOIN   users rc ON rc.id = r.receiver_id
        WHERE  r.id = ?
    """, (referral_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

STATUS_TIMESTAMPS = {
    "contacted":    "contacted_at",
    "in_progress":  "in_progress_at",
    "closed":       "closed_at",
}

def update_referral_status(referral_id, new_status, revenue=None):
    conn = get_connection()
    ts_col = STATUS_TIMESTAMPS.get(new_status)
    now    = datetime.now().isoformat(sep=" ", timespec="seconds")

    if ts_col:
        conn.execute(
            f"UPDATE referrals SET status=?, {ts_col}=? WHERE id=?",
            (new_status, now, referral_id)
        )
    else:
        conn.execute("UPDATE referrals SET status=? WHERE id=?", (new_status, referral_id))

    if new_status == "closed" and revenue is not None:
        conn.execute("UPDATE referrals SET revenue=? WHERE id=?", (revenue, referral_id))

    conn.commit()
    conn.close()

def mark_notified_receiver(referral_id):
    conn = get_connection()
    conn.execute("UPDATE referrals SET notified_receiver=1 WHERE id=?", (referral_id,))
    conn.commit()
    conn.close()

def mark_notified_sender_contacted(referral_id):
    conn = get_connection()
    conn.execute("UPDATE referrals SET notified_sender_contacted=1 WHERE id=?", (referral_id,))
    conn.commit()
    conn.close()


# ── DASHBOARD STATS ────────────────────────────────────────────────────────────

def get_dashboard_stats(user_id):
    conn = get_connection()

    # Referrals received
    rec = conn.execute("""
        SELECT
            COUNT(*)                                    AS total_received,
            SUM(status='closed')                        AS closed_received,
            COALESCE(SUM(CASE WHEN status='closed' THEN revenue ELSE 0 END), 0) AS total_revenue
        FROM referrals WHERE receiver_id=?
    """, (user_id,)).fetchone()

    # Referrals sent
    sent = conn.execute("""
        SELECT COUNT(*) AS total_sent
        FROM referrals WHERE sender_id=?
    """, (user_id,)).fetchone()

    # Network-wide total (visible to all)
    net = conn.execute("""
        SELECT COALESCE(SUM(CASE WHEN status='closed' THEN revenue ELSE 0 END),0) AS network_revenue
        FROM referrals
    """).fetchone()

    conn.close()
    return {
        "total_received":  rec["total_received"],
        "closed_received": rec["closed_received"],
        "total_revenue":   rec["total_revenue"],
        "total_sent":      sent["total_sent"],
        "network_revenue": net["network_revenue"],
    }
