"""
Business Referral Tracker V2
Run: streamlit run app.py
"""
import streamlit as st
from database import (
    init_db, login_user, register_user, delete_account,
    get_all_users, create_network,
    create_referral, get_referrals_for_user, get_referral_by_id,
    update_referral, delete_referral,
    update_referral_status, get_dashboard_stats,
    mark_notified_receiver, mark_notified_sender_contacted,
    STATUS_FLOW,
)
from email_service import (
    notify_receiver_new_referral,
    notify_sender_referral_received,
    notify_sender_lead_contacted,
)

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Referral Tracker",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --navy:      #050d1f;
    --navy2:     #081428;
    --navy3:     #0d1f3c;
    --blue-dark: #0f2d54;
    --blue-mid:  #1a4a80;
    --blue:      #2563eb;
    --blue-light:#3b82f6;
    --blue-bright:#60a5fa;
    --sky:       #93c5fd;
    --white:     #f0f6ff;
    --muted:     #4a6080;
    --text:      #c8d8f0;
    --border:    #1a3a60;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--navy) !important;
    color: var(--text) !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--navy2) 0%, var(--navy3) 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: var(--text) !important;
    text-align: left !important;
    font-size: .9rem !important;
    padding: 10px 16px !important;
    border-radius: 10px !important;
    transition: all .2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--blue-dark) !important;
    border-color: var(--blue-mid) !important;
    color: var(--sky) !important;
    transform: none !important;
}

/* ── MAIN BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, var(--blue), var(--blue-light)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 10px 24px !important;
    transition: all .2s !important;
    letter-spacing: .3px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, var(--blue-light), var(--sky)) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(37,99,235,.4) !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: var(--navy3) !important;
    border: 1px solid var(--border) !important;
    color: var(--white) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--blue-light) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,.15) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--navy2) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--blue-dark) !important;
    color: var(--sky) !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: var(--navy3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}
.streamlit-expanderContent {
    background: var(--navy2) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
}

/* ── CARDS ── */
.kpi-card {
    background: linear-gradient(135deg, var(--navy3), var(--navy2));
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    transition: border-color .2s, transform .2s;
}
.kpi-card:hover { border-color: var(--blue-mid); transform: translateY(-2px); }
.kpi-icon  { font-size: 1.6rem; margin-bottom: 8px; }
.kpi-value { font-size: 1.8rem; font-weight: 700; color: var(--blue-bright);
             font-family: 'Space Grotesk', sans-serif; }
.kpi-label { font-size: .8rem; color: var(--muted); margin-top: 4px; letter-spacing: .5px; text-transform: uppercase; }

.ref-card {
    background: linear-gradient(135deg, var(--navy3), var(--navy2));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 10px;
    transition: border-color .2s;
}
.ref-card:hover { border-color: var(--blue-mid); }
.ref-card .lead-name { font-weight: 600; color: var(--white); font-size: 1rem; }
.ref-card .meta { font-size: .8rem; color: var(--muted); margin-top: 4px; }
.ref-card .reason { font-size: .85rem; color: var(--text); margin-top: 8px; line-height: 1.5; }

/* STATUS BADGES */
.badge { display:inline-flex; align-items:center; gap:5px;
         padding:4px 14px; border-radius:20px; font-size:.75rem;
         font-weight:700; letter-spacing:.5px; text-transform:uppercase; }
.badge-open        { background:#0a2010; color:#4ade80; border:1px solid #166534; }
.badge-contacted   { background:#0a1628; color:#60a5fa; border:1px solid #1e40af; }
.badge-in_progress { background:#1a0a2e; color:#a78bfa; border:1px solid #5b21b6; }
.badge-closed      { background:#1a0a0a; color:#f87171; border:1px solid #991b1b; }

/* PAGE TITLE */
.page-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--white);
    margin-bottom: 4px;
}
.page-sub {
    font-size: .85rem;
    color: var(--muted);
    margin-bottom: 28px;
}

/* DIVIDER */
.divider { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

/* ALERT BOXES */
.info-box {
    background: var(--navy3);
    border-left: 3px solid var(--blue-light);
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    font-size: .85rem;
    color: var(--sky);
    margin-bottom: 16px;
}
.success-box {
    background: #0a2010;
    border-left: 3px solid #4ade80;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    font-size: .85rem;
    color: #4ade80;
    margin-bottom: 16px;
}

/* LOGIN PAGE */
.login-wrap {
    max-width: 440px;
    margin: 0 auto;
    padding-top: 40px;
}
.login-logo {
    text-align: center;
    margin-bottom: 32px;
}
.login-logo .icon { font-size: 3rem; }
.login-logo h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--white);
    margin: 10px 0 4px;
}
.login-logo p { font-size: .9rem; color: var(--muted); }

/* NETWORK MEMBER CARD */
.member-card {
    background: var(--navy3);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    transition: border-color .2s;
}
.member-card:hover { border-color: var(--blue-mid); }
.member-avatar {
    width: 52px; height: 52px;
    background: linear-gradient(135deg, var(--blue), var(--blue-light));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; font-weight: 700; color: white;
    margin: 0 auto 12px;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for k, v in [("user", None), ("page", "dashboard"), ("edit_ref", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ───────────────────────────────────────────────────────────────────
STATUS_DE = {
    "open":        ("Offen",          "🟢", "badge-open"),
    "contacted":   ("Kontaktiert",    "🔵", "badge-contacted"),
    "in_progress": ("In Bearbeitung", "🟣", "badge-in_progress"),
    "closed":      ("Abgeschlossen",  "🔴", "badge-closed"),
}
STATUS_NEXT_LABEL = {
    "open":        "Auf Kontaktiert setzen",
    "contacted":   "Auf In Bearbeitung setzen",
    "in_progress": "Auf Abgeschlossen setzen",
}

def badge(status):
    label, dot, cls = STATUS_DE.get(status, (status, "•", "badge-open"))
    return f"<span class='badge {cls}'>{dot} {label}</span>"


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════
def show_auth():
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='login-logo'>
        <div class='icon'>🤝</div>
        <h1>Referral Tracker</h1>
        <p>Empfehlungen verfolgen · Netzwerk stärken</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔐 Anmelden", "📝 Registrieren", "🌐 Netzwerk erstellen"])

    with tab1:
        email = st.text_input("E-Mail", key="li_email")
        pw    = st.text_input("Passwort", type="password", key="li_pw")
        if st.button("Anmelden", use_container_width=True, key="btn_li"):
            user = login_user(email, pw)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("E-Mail oder Passwort falsch.")
        st.markdown("""
        <div class='info-box'>
            🧪 <strong>Demo:</strong> anna@demo.com / demo123
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        r_name    = st.text_input("Name *",           key="r_name")
        r_email   = st.text_input("E-Mail *",         key="r_email")
        r_company = st.text_input("Unternehmen",      key="r_company")
        r_code    = st.text_input("Einladungscode *", key="r_code",
                                  placeholder="Vom Netzwerk-Admin erhalten")
        r_pw      = st.text_input("Passwort *",       type="password", key="r_pw")
        r_pw2     = st.text_input("Passwort bestätigen *", type="password", key="r_pw2")
        if st.button("Registrieren", use_container_width=True, key="btn_reg"):
            if not all([r_name, r_email, r_code, r_pw]):
                st.error("Bitte alle Pflichtfelder ausfüllen.")
            elif r_pw != r_pw2:
                st.error("Passwörter stimmen nicht überein.")
            else:
                ok, msg = register_user(r_name, r_email, r_pw, r_company, r_code)
                if ok:
                    st.success(msg + " Bitte anmelden.")
                else:
                    st.error(msg)

    with tab3:
        st.markdown("<div class='info-box'>Erstelle ein neues Netzwerk und werde Admin.</div>",
                    unsafe_allow_html=True)
        n_name    = st.text_input("Netzwerk-Name *",      key="n_name")
        n_desc    = st.text_input("Beschreibung",         key="n_desc")
        n_code    = st.text_input("Einladungscode *",     key="n_code",
                                  placeholder="z.B. MEINTEAM2024")
        st.markdown("**Dein Admin-Konto**")
        a_name    = st.text_input("Dein Name *",          key="a_name")
        a_email   = st.text_input("Deine E-Mail *",       key="a_email")
        a_company = st.text_input("Dein Unternehmen",     key="a_company")
        a_pw      = st.text_input("Passwort *",           type="password", key="a_pw")
        if st.button("Netzwerk erstellen", use_container_width=True, key="btn_net"):
            if not all([n_name, n_code, a_name, a_email, a_pw]):
                st.error("Bitte alle Pflichtfelder ausfüllen.")
            else:
                ok, msg = create_network(n_name, n_desc, n_code, a_name, a_email, a_pw, a_company)
                if ok:
                    st.success(f"Netzwerk '{n_name}' erstellt! Einladungscode: **{n_code}**")
                else:
                    st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def show_sidebar():
    u = st.session_state.user
    with st.sidebar:
        initials = "".join(p[0].upper() for p in u["name"].split()[:2])
        st.markdown(f"""
        <div style="padding:20px 16px 24px; text-align:center;">
            <div style="width:56px;height:56px;background:linear-gradient(135deg,#2563eb,#60a5fa);
                        border-radius:50%;display:flex;align-items:center;justify-content:center;
                        font-size:1.3rem;font-weight:700;color:white;margin:0 auto 12px;">
                {initials}
            </div>
            <div style="font-weight:600;color:#f0f6ff;font-size:.95rem;">{u['name']}</div>
            <div style="font-size:.78rem;color:#4a6080;margin-top:2px;">{u.get('company','')}</div>
            <div style="font-size:.72rem;color:#1a4a80;margin-top:6px;
                        background:#0d1f3c;border-radius:20px;padding:3px 10px;
                        display:inline-block;">
                🌐 {u.get('network_name','–')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        nav = [
            ("dashboard", "📊", "Dashboard"),
            ("referrals", "📋", "Empfehlungen"),
            ("new",       "➕", "Neue Empfehlung"),
            ("network",   "👥", "Netzwerk"),
            ("settings",  "⚙️", "Einstellungen"),
        ]
        for key, icon, label in nav:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.session_state.edit_ref = None
                st.rerun()

        st.markdown("<hr style='border-color:#1a3a60;margin:12px 0;'>", unsafe_allow_html=True)
        if st.button("🚪  Abmelden", use_container_width=True, key="logout"):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    u     = st.session_state.user
    stats = get_dashboard_stats(u["id"], u["network_id"])

    st.markdown("<div class='page-title'>📊 Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-sub'>Willkommen zurück, {u['name'].split()[0]}!</div>",
                unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, "📤", stats["total_sent"],      "Gesendet"),
        (c2, "📥", stats["total_received"],  "Erhalten"),
        (c3, "✅", stats["closed_received"], "Abgeschlossen"),
        (c4, "💰", f"CHF {stats['total_revenue']:,.0f}", "Eigener Umsatz"),
        (c5, "🌐", f"CHF {stats['network_revenue']:,.0f}", "Netzwerk-Umsatz"),
    ]
    for col, icon, val, label in kpis:
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-icon'>{icon}</div>
                <div class='kpi-value'>{val}</div>
                <div class='kpi-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    refs = get_referrals_for_user(u["id"], u["network_id"])
    received = [r for r in refs if r["receiver_id"] == u["id"]]
    sent     = [r for r in refs if r["sender_id"]   == u["id"]]

    col_r, col_s = st.columns(2)
    with col_r:
        st.markdown("#### 📥 Zuletzt erhalten")
        if not received:
            st.markdown("<div class='info-box'>Noch keine Empfehlungen erhalten.</div>",
                        unsafe_allow_html=True)
        for r in received[:4]:
            st.markdown(f"""
            <div class='ref-card'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                    <div class='lead-name'>{r['lead_name']}</div>
                    {badge(r['status'])}
                </div>
                {'<div style="font-size:.8rem;color:#4a6080;margin-top:2px;">' + r['lead_company'] + '</div>' if r.get('lead_company') else ''}
                <div class='meta'>Von {r['sender_name']} · {r['created_at'][:10]}</div>
                {'<div class="reason">' + r["reason"][:90] + ('…' if len(r.get("reason",""))>90 else "") + '</div>' if r.get('reason') else ''}
            </div>
            """, unsafe_allow_html=True)

    with col_s:
        st.markdown("#### 📤 Zuletzt gesendet")
        if not sent:
            st.markdown("<div class='info-box'>Noch keine Empfehlungen gesendet.</div>",
                        unsafe_allow_html=True)
        for r in sent[:4]:
            st.markdown(f"""
            <div class='ref-card'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                    <div class='lead-name'>{r['lead_name']}</div>
                    {badge(r['status'])}
                </div>
                {'<div style="font-size:.8rem;color:#4a6080;margin-top:2px;">' + r['lead_company'] + '</div>' if r.get('lead_company') else ''}
                <div class='meta'>An {r['receiver_name']} · {r['created_at'][:10]}</div>
                {'<div style="font-size:.85rem;color:#4ade80;margin-top:6px;font-weight:600;">💰 CHF ' + f"{r['revenue']:,.0f}" + '</div>' if r.get('revenue') else ''}
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  REFERRALS LIST
# ══════════════════════════════════════════════════════════════════════════════
def page_referrals():
    u    = st.session_state.user
    refs = get_referrals_for_user(u["id"], u["network_id"])

    # ── EDIT MODE ─────────────────────────────────────────────────────────────
    if st.session_state.edit_ref:
        r = get_referral_by_id(st.session_state.edit_ref)
        st.markdown("<div class='page-title'>✏️ Empfehlung bearbeiten</div>",
                    unsafe_allow_html=True)
        with st.form("edit_form"):
            c1, c2 = st.columns(2)
            with c1:
                ln = st.text_input("Lead Name *",    value=r["lead_name"])
                le = st.text_input("Lead E-Mail",    value=r.get("lead_email",""))
            with c2:
                lc = st.text_input("Unternehmen",    value=r.get("lead_company",""))
                lp = st.text_input("Telefon",        value=r.get("lead_phone",""))
            rs = st.text_area("Empfehlung", value=r.get("reason",""), height=120)
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Speichern", use_container_width=True):
                    if not ln:
                        st.error("Name ist Pflichtfeld.")
                    else:
                        update_referral(r["id"], ln, le, lp, lc, rs)
                        st.session_state.edit_ref = None
                        st.success("Gespeichert!")
                        st.rerun()
            with col_cancel:
                if st.form_submit_button("Abbrechen", use_container_width=True):
                    st.session_state.edit_ref = None
                    st.rerun()
        return

    # ── LIST ──────────────────────────────────────────────────────────────────
    st.markdown("<div class='page-title'>📋 Empfehlungen</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Alle deine gesendeten und erhaltenen Empfehlungen</div>",
                unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([1, 1, 2])
    with fc1:
        direction = st.selectbox("Richtung", ["Alle", "Erhalten", "Gesendet"])
    with fc2:
        st_map = {"Alle":"Alle","Offen":"open","Kontaktiert":"contacted",
                  "In Bearbeitung":"in_progress","Abgeschlossen":"closed"}
        sf = st.selectbox("Status", list(st_map.keys()))
    with fc3:
        search = st.text_input("🔍 Suche")

    filtered = refs
    if direction == "Erhalten":
        filtered = [r for r in filtered if r["receiver_id"] == u["id"]]
    elif direction == "Gesendet":
        filtered = [r for r in filtered if r["sender_id"] == u["id"]]
    if sf != "Alle":
        filtered = [r for r in filtered if r["status"] == st_map[sf]]
    if search:
        s = search.lower()
        filtered = [r for r in filtered
                    if s in r["lead_name"].lower()
                    or s in (r.get("lead_company") or "").lower()]

    st.markdown(f"<p style='color:var(--muted);font-size:.8rem;'>{len(filtered)} Einträge</p>",
                unsafe_allow_html=True)

    if not filtered:
        st.markdown("<div class='info-box'>Keine Empfehlungen gefunden.</div>",
                    unsafe_allow_html=True)
        return

    for r in filtered:
        is_receiver = r["receiver_id"] == u["id"]
        is_sender   = r["sender_id"]   == u["id"]
        label, _, cls = STATUS_DE.get(r["status"], (r["status"],"",""))

        with st.expander(f"{'📥' if is_receiver else '📤'}  {r['lead_name']}  ·  {r.get('lead_company','')}"):
            d1, d2 = st.columns([2, 1])

            with d1:
                st.markdown(f"""
                <div class='ref-card' style='margin:0;'>
                    <div class='lead-name'>{r['lead_name']}</div>
                    {'<div style="color:var(--muted);font-size:.85rem;">' + r["lead_company"] + '</div>' if r.get("lead_company") else ''}
                    <hr class='divider'>
                    {'<p style="font-size:.85rem;">📧 ' + r["lead_email"] + '</p>' if r.get("lead_email") else ''}
                    {'<p style="font-size:.85rem;">📞 ' + r["lead_phone"] + '</p>' if r.get("lead_phone") else ''}
                    {'<p style="font-size:.85rem;margin-top:8px;color:var(--text);">' + r["reason"] + '</p>' if r.get("reason") else ''}
                    <div style="margin-top:12px;font-size:.78rem;color:var(--muted);">
                        {'📥 Von ' + r["sender_name"] if is_receiver else '📤 An ' + r["receiver_name"]}
                        · Erstellt: {r['created_at'][:10]}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Edit / Delete buttons (only sender can edit/delete)
                if is_sender:
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        if st.button("✏️ Bearbeiten", key=f"edit_{r['id']}",
                                     use_container_width=True):
                            st.session_state.edit_ref = r["id"]
                            st.session_state.page = "referrals"
                            st.rerun()
                    with bc2:
                        if st.button("🗑️ Löschen", key=f"del_{r['id']}",
                                     use_container_width=True):
                            delete_referral(r["id"])
                            st.success("Empfehlung gelöscht.")
                            st.rerun()

            with d2:
                st.markdown(f"**Status:** {badge(r['status'])}", unsafe_allow_html=True)

                # Timeline
                tl = []
                if r.get("created_at"):     tl.append(("📝", "Erstellt",        r["created_at"][:16]))
                if r.get("contacted_at"):   tl.append(("📞", "Kontaktiert",     r["contacted_at"][:16]))
                if r.get("in_progress_at"): tl.append(("⚙️", "In Bearbeitung",  r["in_progress_at"][:16]))
                if r.get("closed_at"):      tl.append(("✅", "Abgeschlossen",   r["closed_at"][:16]))
                if r.get("revenue"):        tl.append(("💰", "Umsatz",          f"CHF {r['revenue']:,.0f}"))
                for icon, lbl, ts in tl:
                    st.markdown(
                        f"<div style='font-size:.78rem;color:var(--muted);margin-top:6px;'>"
                        f"{icon} {lbl}: <span style='color:var(--sky);'>{ts}</span></div>",
                        unsafe_allow_html=True
                    )

                # Status advance (receiver only)
                if is_receiver and r["status"] != "closed":
                    idx         = STATUS_FLOW.index(r["status"])
                    next_status = STATUS_FLOW[idx + 1]
                    st.markdown("<br>", unsafe_allow_html=True)
                    revenue_input = None
                    if next_status == "closed":
                        revenue_input = st.number_input(
                            "Auftragssumme (CHF)", min_value=0.0, step=100.0,
                            key=f"rev_{r['id']}"
                        )
                    next_label = STATUS_NEXT_LABEL.get(r["status"], "Weiter")
                    if st.button(f"➡️ {next_label}", key=f"st_{r['id']}",
                                 use_container_width=True):
                        update_referral_status(r["id"], next_status, revenue_input)
                        if next_status == "contacted" and not r.get("notified_sender_contacted"):
                            full = get_referral_by_id(r["id"])
                            notify_sender_lead_contacted(full)
                            mark_notified_sender_contacted(r["id"])
                        st.success(f"Status aktualisiert!")
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  NEW REFERRAL
# ══════════════════════════════════════════════════════════════════════════════
def page_new():
    u     = st.session_state.user
    users = [x for x in get_all_users(u["network_id"]) if x["id"] != u["id"]]

    st.markdown("<div class='page-title'>➕ Neue Empfehlung</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Empfehle einen Lead an ein Netzwerk-Mitglied</div>",
                unsafe_allow_html=True)

    if not users:
        st.markdown("<div class='info-box'>Noch keine anderen Mitglieder im Netzwerk.</div>",
                    unsafe_allow_html=True)
        return

    with st.form("new_ref_form"):
        st.markdown("#### 👤 Lead-Informationen")
        c1, c2 = st.columns(2)
        with c1:
            ln = st.text_input("Name *")
            le = st.text_input("E-Mail")
        with c2:
            lc = st.text_input("Unternehmen")
            lp = st.text_input("Telefon")

        st.markdown("#### 💬 Empfehlung")
        reason = st.text_area("Warum empfehle ich? *", height=110,
                              placeholder="z.B. Thomas sucht eine neue ERP-Lösung…")

        st.markdown("#### 📬 Empfänger")
        opts = {f"{x['name']} – {x.get('company','')}": x["id"] for x in users}
        sel  = st.selectbox("Wer erhält die Empfehlung? *", list(opts.keys()))

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Empfehlung abgeben", use_container_width=True)
        if submitted:
            if not ln or not reason:
                st.error("Pflichtfelder ausfüllen.")
            else:
                rid  = create_referral(u["id"], opts[sel], u["network_id"],
                                       ln, le, lp, lc, reason)
                full = get_referral_by_id(rid)
                notify_receiver_new_referral(full)
                mark_notified_receiver(rid)
                notify_sender_referral_received(full)
                st.success(f"✅ Empfehlung für **{ln}** erfolgreich abgegeben!")
                st.balloons()


# ══════════════════════════════════════════════════════════════════════════════
#  NETWORK
# ══════════════════════════════════════════════════════════════════════════════
def page_network():
    u     = st.session_state.user
    users = get_all_users(u["network_id"])

    st.markdown("<div class='page-title'>👥 Netzwerk</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-sub'>{u.get('network_name','–')} · {len(users)} Mitglieder</div>",
                unsafe_allow_html=True)

    cols = st.columns(3)
    for i, m in enumerate(users):
        stats    = get_dashboard_stats(m["id"], u["network_id"])
        initials = "".join(p[0].upper() for p in m["name"].split()[:2])
        is_me    = m["id"] == u["id"]
        with cols[i % 3]:
            st.markdown(f"""
            <div class='member-card' style='{"border-color:#2563eb;" if is_me else ""}'>
                <div class='member-avatar'>{initials}</div>
                <div style='font-weight:600;color:#f0f6ff;'>{m['name']}
                    {'<span style="font-size:.7rem;color:#60a5fa;"> (Du)</span>' if is_me else ''}
                    {'<span style="font-size:.7rem;color:#f59e0b;"> ★</span>' if m.get('is_admin') else ''}
                </div>
                <div style='font-size:.8rem;color:#4a6080;margin-top:2px;'>{m.get('company','–')}</div>
                <div style='display:flex;justify-content:space-around;margin-top:16px;'>
                    <div style='text-align:center;'>
                        <div style='font-weight:700;color:#60a5fa;font-size:1.1rem;'>{stats['total_sent']}</div>
                        <div style='font-size:.72rem;color:#4a6080;'>Gesendet</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-weight:700;color:#60a5fa;font-size:1.1rem;'>{stats['total_received']}</div>
                        <div style='font-size:.72rem;color:#4a6080;'>Erhalten</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-weight:700;color:#4ade80;font-size:1.1rem;'>
                            CHF {stats['total_revenue']:,.0f}
                        </div>
                        <div style='font-size:.72rem;color:#4a6080;'>Umsatz</div>
                    </div>
                </div>
            </div>
            <br>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
def page_settings():
    u = st.session_state.user
    st.markdown("<div class='page-title'>⚙️ Einstellungen</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-sub'>Konto- und Netzwerk-Einstellungen</div>",
                unsafe_allow_html=True)

    st.markdown("#### 👤 Mein Konto")
    st.markdown(f"""
    <div class='ref-card'>
        <p><strong style='color:#93c5fd;'>Name:</strong> {u['name']}</p>
        <p><strong style='color:#93c5fd;'>E-Mail:</strong> {u['email']}</p>
        <p><strong style='color:#93c5fd;'>Unternehmen:</strong> {u.get('company','–')}</p>
        <p><strong style='color:#93c5fd;'>Netzwerk:</strong> {u.get('network_name','–')}</p>
        {'<p><strong style="color:#f59e0b;">★ Admin</strong></p>' if u.get('is_admin') else ''}
    </div>
    """, unsafe_allow_html=True)

    if u.get("is_admin"):
        st.markdown("#### 🌐 Netzwerk-Einladungscode")
        st.markdown(f"""
        <div class='info-box'>
            Teile diesen Code mit neuen Mitgliedern:<br>
            <strong style='font-size:1.2rem;letter-spacing:2px;'>{u.get('invite_code','–')}</strong>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🗑️ Konto löschen")
    st.markdown("""
    <div class='info-box' style='border-color:#ef4444;color:#fca5a5;'>
        ⚠️ Diese Aktion kann nicht rückgängig gemacht werden.
        Alle deine Empfehlungen werden ebenfalls gelöscht.
    </div>
    """, unsafe_allow_html=True)

    confirm = st.text_input("Tippe DELETE zum Bestätigen", key="del_confirm")
    if st.button("🗑️ Konto endgültig löschen", key="btn_delete"):
        if confirm == "DELETE":
            delete_account(u["id"])
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.success("Konto gelöscht.")
            st.rerun()
        else:
            st.error("Bitte 'DELETE' eintippen zur Bestätigung.")


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.user:
        show_auth()
    else:
        show_sidebar()
        p = st.session_state.page
        if p == "dashboard":  page_dashboard()
        elif p == "referrals": page_referrals()
        elif p == "new":       page_new()
        elif p == "network":   page_network()
        elif p == "settings":  page_settings()

if __name__ == "__main__":
    main()
