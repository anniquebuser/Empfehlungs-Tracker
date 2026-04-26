import sqlite3
import hashlib
from datetime import datetime

DB_PATH = "referral_tracker.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # ── NETWORKS ───────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS networks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            description TEXT,
            invite_code TEXT    NOT NULL UNIQUE,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── USERS ──────────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            company     TEXT,
            network_id  INTEGER REFERENCES networks(id),
            is_admin    INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── REFERRALS ──────────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id       INTEGER NOT NULL REFERENCES users(id),
            receiver_id     INTEGER NOT NULL REFERENCES users(id),
            network_id      INTEGER NOT NULL REFERENCES networks(id),
            lead_name       TEXT    NOT NULL,
            lead_email      TEXT,
            lead_phone      TEXT,
            lead_company    TEXT,
            reason          TEXT,
            status          TEXT    NOT NULL DEFAULT 'open',
            revenue         REAL,
            created_at      TEXT    DEFAULT (datetime('now')),
            updated_at      TEXT    DEFAULT (datetime('now')),
            contacted_at    TEXT,
            in_progress_at  TEXT,
            closed_at       TEXT,
            notified_receiver           INTEGER DEFAULT 0,
            notified_sender_contacted   INTEGER DEFAULT 0
        )
    """)

    # ── DEMO DATA ──────────────────────────────────────────────────────────────
    c.execute("SELECT COUNT(*) FROM networks")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO networks (name, description, invite_code)
            VALUES ('Demo Netzwerk', 'Das offizielle Demo-Netzwerk', 'DEMO2024')
        """)
        network_id = c.lastrowid

        demo_users = [
            ("Anna Müller",   "anna@demo.com",  hash_password("demo123"), "Müller Consulting", network_id, 1),
            ("Ben Schneider", "ben@demo.com",   hash_password("demo123"), "Schneider GmbH",    network_id, 0),
            ("Clara Becker",  "clara@demo.com", hash_password("demo123"), "Becker & Partner",  network_id, 0),
            ("David Lehmann", "david@demo.com", hash_password("demo123"), "Lehmann Tech",      network_id, 0),
        ]
        c.executemany(
            "INSERT INTO users (name, email, password, company, network_id, is_admin) VALUES (?,?,?,?,?,?)",
            demo_users
        )

        now = datetime.now().isoformat(sep=" ", timespec="seconds")
        demo_referrals = [
            (1, 2, network_id, "Thomas Huber",    "t.huber@example.com",  "+41 79 111 22 33", "Huber AG",
             "Kennt sich super im Bereich ERP aus.", "closed",      12500.0, now, now, now, now),
            (2, 1, network_id, "Sandra Vogel",    "s.vogel@example.com",  "+41 78 222 33 44", "Vogel GmbH",
             "Braucht eine neue Website.", "in_progress", None,    now, now, now, None),
            (3, 1, network_id, "Marc Zimmermann", "m.zimm@example.com",   "+41 76 333 44 55", "Zimm Bau",
             "Interessiert an digitaler Transformation.", "contacted",   None,    now, now, None, None),
            (1, 3, network_id, "Eva Keller",      "e.keller@example.com", "+41 77 444 55 66", "Keller Shop",
             "Sucht jemanden für Social-Media.", "open",        None,    now, None, None, None),
            (4, 2, network_id, "Peter Lenz",      "p.lenz@example.com",   "+41 79 555 66 77", "Lenz IT",
             "Benötigt Cloud-Migration.", "closed",      8750.0,  now, now, now, now),
        ]
        c.executemany("""
            INSERT INTO referrals
              (sender_id, receiver_id, network_id, lead_name, lead_email, lead_phone,
               lead_company, reason, status, revenue, created_at, contacted_at, in_progress_at, closed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, demo_referrals)

    conn.commit()
    conn.close()


# ── AUTH ───────────────────────────────────────────────────────────────────────

def login_user(email, password):
    conn = get_connection()
    user = conn.execute(
        "SELECT u.*, n.name as network_name, n.invite_code FROM users u "
        "LEFT JOIN networks n ON n.id = u.network_id "
        "WHERE u.email=? AND u.password=?",
        (email, hash_password(password))
    ).fetchone()
    conn.close()
    return dict(user) if user else None

def register_user(name, email, password, company, invite_code):
    conn = get_connection()
    try:
        network = conn.execute(
            "SELECT * FROM networks WHERE invite_code=?", (invite_code,)
        ).fetchone()
        if not network:
            return False, "Ungültiger Einladungscode."
        conn.execute(
            "INSERT INTO users (name, email, password, company, network_id) VALUES (?,?,?,?,?)",
            (name, email, hash_password(password), company, network["id"])
        )
        conn.commit()
        return True, "Erfolgreich registriert!"
    except sqlite3.IntegrityError:
        return False, "E-Mail bereits registriert."
    finally:
        conn.close()

def delete_account(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM referrals WHERE sender_id=? OR receiver_id=?", (user_id, user_id))
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def get_all_users(network_id):
    conn = get_connection()
    users = conn.execute(
        "SELECT id, name, email, company, is_admin FROM users WHERE network_id=?",
        (network_id,)
    ).fetchall()
    conn.close()
    return [dict(u) for u in users]

def create_network(name, description, invite_code, admin_name, admin_email, admin_password, admin_company):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO networks (name, description, invite_code) VALUES (?,?,?)",
            (name, description, invite_code)
        )
        network_id = c.lastrowid
        c.execute(
            "INSERT INTO users (name, email, password, company, network_id, is_admin) VALUES (?,?,?,?,?,1)",
            (admin_name, admin_email, hash_password(admin_password), admin_company, network_id)
        )
        conn.commit()
        return True, "Netzwerk erstellt!"
    except sqlite3.IntegrityError as e:
        return False, f"Name oder Einladungscode bereits vergeben."
    finally:
        conn.close()


# ── REFERRALS ──────────────────────────────────────────────────────────────────

def create_referral(sender_id, receiver_id, network_id, lead_name,
                    lead_email, lead_phone, lead_company, reason):
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO referrals
          (sender_id, receiver_id, network_id, lead_name, lead_email, lead_phone, lead_company, reason)
        VALUES (?,?,?,?,?,?,?,?)
    """, (sender_id, receiver_id, network_id, lead_name, lead_email, lead_phone, lead_company, reason))
    ref_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ref_id

def get_referrals_for_user(user_id, network_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT r.*,
               s.name  AS sender_name,  s.email AS sender_email,
               rc.name AS receiver_name, rc.email AS receiver_email
        FROM   referrals r
        JOIN   users s  ON s.id = r.sender_id
        JOIN   users rc ON rc.id = r.receiver_id
        WHERE  (r.sender_id=? OR r.receiver_id=?) AND r.network_id=?
        ORDER  BY r.created_at DESC
    """, (user_id, user_id, network_id)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_referral_by_id(referral_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT r.*,
               s.name AS sender_name, s.email AS sender_email,
               rc.name AS receiver_name, rc.email AS receiver_email
        FROM referrals r
        JOIN users s  ON s.id = r.sender_id
        JOIN users rc ON rc.id = r.receiver_id
        WHERE r.id=?
    """, (referral_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_referral(referral_id, lead_name, lead_email, lead_phone, lead_company, reason):
    conn = get_connection()
    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    conn.execute("""
        UPDATE referrals SET
            lead_name=?, lead_email=?, lead_phone=?, lead_company=?, reason=?, updated_at=?
        WHERE id=?
    """, (lead_name, lead_email, lead_phone, lead_company, reason, now, referral_id))
    conn.commit()
    conn.close()

def delete_referral(referral_id):
    conn = get_connection()
    conn.execute("DELETE FROM referrals WHERE id=?", (referral_id,))
    conn.commit()
    conn.close()

STATUS_TIMESTAMPS = {
    "contacted":   "contacted_at",
    "in_progress": "in_progress_at",
    "closed":      "closed_at",
}
STATUS_FLOW = ["open", "contacted", "in_progress", "closed"]

def update_referral_status(referral_id, new_status, revenue=None):
    conn = get_connection()
    now    = datetime.now().isoformat(sep=" ", timespec="seconds")
    ts_col = STATUS_TIMESTAMPS.get(new_status)
    if ts_col:
        conn.execute(f"UPDATE referrals SET status=?, {ts_col}=?, updated_at=? WHERE id=?",
                     (new_status, now, now, referral_id))
    else:
        conn.execute("UPDATE referrals SET status=?, updated_at=? WHERE id=?",
                     (new_status, now, referral_id))
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

def get_dashboard_stats(user_id, network_id):
    conn = get_connection()
    rec = conn.execute("""
        SELECT COUNT(*) AS total_received,
               SUM(status='closed') AS closed_received,
               COALESCE(SUM(CASE WHEN status='closed' THEN revenue ELSE 0 END),0) AS total_revenue
        FROM referrals WHERE receiver_id=? AND network_id=?
    """, (user_id, network_id)).fetchone()
    sent = conn.execute(
        "SELECT COUNT(*) AS total_sent FROM referrals WHERE sender_id=? AND network_id=?",
        (user_id, network_id)
    ).fetchone()
    net = conn.execute(
        "SELECT COALESCE(SUM(CASE WHEN status='closed' THEN revenue ELSE 0 END),0) AS network_revenue "
        "FROM referrals WHERE network_id=?",
        (network_id,)
    ).fetchone()
    conn.close()
    return {
        "total_received":  rec["total_received"],
        "closed_received": rec["closed_received"] or 0,
        "total_revenue":   rec["total_revenue"],
        "total_sent":      sent["total_sent"],
        "network_revenue": net["network_revenue"],
    }
