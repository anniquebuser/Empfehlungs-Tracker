"""
Business Referral Tracker – Streamlit App
Run: streamlit run app.py
"""
import streamlit as st
from database import (
    init_db, login_user, register_user, get_all_users,
    create_referral, get_referrals_for_user, get_referral_by_id,
    update_referral_status, get_dashboard_stats,
    mark_notified_receiver, mark_notified_sender_contacted,
)
from email_service import (
    notify_receiver_new_referral,
    notify_sender_referral_received,
    notify_sender_lead_contacted,
)

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Business Referral Tracker",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── INIT DB ────────────────────────────────────────────────────────────────────
init_db()

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Main background */
.stApp { background: #0f0f1a; color: #e2e8f0; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #13131f 0%, #1a1a2e 100%);
    border-right: 1px solid #2d2d4e;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Cards */
.ref-card {
    background: linear-gradient(135deg, #1e1e35 0%, #1a1a2e 100%);
    border: 1px solid #2d2d4e;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: border-color .2s;
}
.ref-card:hover { border-color: #4f46e5; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1e1e35, #1a1a2e);
    border: 1px solid #2d2d4e;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #818cf8; }
.metric-label { font-size: .85rem; color: #64748b; margin-top: 4px; }

/* Status badges */
.badge-open        { background:#1e3a2f; color:#4ade80; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }
.badge-contacted   { background:#1e2e4a; color:#60a5fa; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }
.badge-in_progress { background:#2d1e4a; color:#c084fc; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }
.badge-closed      { background:#2d1e1e; color:#f87171; border-radius:20px; padding:3px 12px; font-size:12px; font-weight:600; }

/* Section headers */
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #818cf8;
    border-bottom: 1px solid #2d2d4e;
    padding-bottom: 8px;
    margin-bottom: 20px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    transform: translateY(-1px);
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: #1e1e35 !important;
    border: 1px solid #2d2d4e !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

/* Alert box */
.info-box {
    background: #1e2e4a;
    border-left: 4px solid #4f46e5;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 16px;
    font-size: 13px;
    color: #93c5fd;
}
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE INIT ─────────────────────────────────────────────────────────
for key, val in [("user", None), ("page", "dashboard")]:
    if key not in st.session_state:
        st.session_state[key] = val


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH SCREENS
# ══════════════════════════════════════════════════════════════════════════════

def show_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; margin-bottom:32px;'>
            <div style='font-size:3rem;'>🤝</div>
            <h1 style='color:#818cf8; margin:8px 0 4px; font-size:1.8rem;'>
                Business Referral Tracker
            </h1>
            <p style='color:#64748b; font-size:.9rem;'>
                Empfehlungen verfolgen · Netzwerk stärken · Umsatz messen
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔐 Anmelden", "📝 Registrieren"])

        with tab_login:
            email    = st.text_input("E-Mail",    key="login_email")
            password = st.text_input("Passwort",  type="password", key="login_pw")
            if st.button("Anmelden", use_container_width=True, key="btn_login"):
                user = login_user(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("E-Mail oder Passwort falsch.")
            st.markdown("""
            <div class='info-box'>
                🧪 <strong>Demo-Zugänge:</strong><br>
                anna@demo.com · ben@demo.com · clara@demo.com · david@demo.com<br>
                Passwort: <code>demo123</code>
            </div>
            """, unsafe_allow_html=True)

        with tab_register:
            r_name    = st.text_input("Name",        key="reg_name")
            r_email   = st.text_input("E-Mail",      key="reg_email")
            r_company = st.text_input("Unternehmen", key="reg_company")
            r_pw      = st.text_input("Passwort",    type="password", key="reg_pw")
            r_pw2     = st.text_input("Passwort bestätigen", type="password", key="reg_pw2")
            if st.button("Registrieren", use_container_width=True, key="btn_register"):
                if not (r_name and r_email and r_pw):
                    st.error("Name, E-Mail und Passwort sind Pflichtfelder.")
                elif r_pw != r_pw2:
                    st.error("Passwörter stimmen nicht überein.")
                elif register_user(r_name, r_email, r_pw, r_company):
                    st.success("Konto erstellt! Jetzt anmelden.")
                else:
                    st.error("E-Mail bereits registriert.")


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def show_sidebar():
    user = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:16px 0 24px;'>
            <div style='font-size:2rem; text-align:center;'>🤝</div>
            <div style='text-align:center; margin-top:8px;'>
                <div style='font-weight:700; font-size:1rem; color:#818cf8;'>
                    {user['name']}
                </div>
                <div style='font-size:.8rem; color:#64748b; margin-top:2px;'>
                    {user.get('company', '')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pages = {
            "dashboard":   ("📊", "Dashboard"),
            "referrals":   ("📋", "Empfehlungen"),
            "new":         ("➕", "Neue Empfehlung"),
            "network":     ("👥", "Netzwerk"),
        }
        for key, (icon, label) in pages.items():
            active = "background:#2d2d4e; border-radius:8px;" if st.session_state.page == key else ""
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        if st.button("🚪  Abmelden", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER
# ══════════════════════════════════════════════════════════════════════════════

STATUS_LABELS = {
    "open":        ("Offen",        "badge-open"),
    "contacted":   ("Kontaktiert",  "badge-contacted"),
    "in_progress": ("In Bearbeitung","badge-in_progress"),
    "closed":      ("Abgeschlossen","badge-closed"),
}
STATUS_FLOW = ["open", "contacted", "in_progress", "closed"]
STATUS_DE   = {
    "open":        "Offen",
    "contacted":   "Kontaktiert",
    "in_progress": "In Bearbeitung",
    "closed":      "Abgeschlossen",
}

def badge(status):
    label, cls = STATUS_LABELS.get(status, (status, "badge-open"))
    return f"<span class='{cls}'>{label}</span>"


# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════

def page_dashboard():
    user  = st.session_state.user
    stats = get_dashboard_stats(user["id"])

    st.markdown("<div class='section-title'>📊 Dashboard</div>", unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, stats["total_sent"],      "Empfehlungen gesendet",      "📤"),
        (c2, stats["total_received"],  "Empfehlungen erhalten",      "📥"),
        (c3, stats["closed_received"], "Abgeschlossen",              "✅"),
        (c4, f"CHF {stats['total_revenue']:,.0f}", "Eigener Umsatz", "💰"),
        (c5, f"CHF {stats['network_revenue']:,.0f}", "Netzwerk-Umsatz", "🌐"),
    ]
    for col, val, label, icon in kpis:
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:1.6rem;'>{icon}</div>
                <div class='metric-value'>{val}</div>
                <div class='metric-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent referrals ──────────────────────────────────────────────────────
    col_r, col_s = st.columns(2)

    referrals = get_referrals_for_user(user["id"])
    received  = [r for r in referrals if r["receiver_id"] == user["id"]]
    sent      = [r for r in referrals if r["sender_id"]   == user["id"]]

    with col_r:
        st.markdown("#### 📥 Zuletzt erhalten")
        if not received:
            st.info("Noch keine Empfehlungen erhalten.")
        for r in received[:5]:
            st.markdown(f"""
            <div class='ref-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <strong style='color:#e2e8f0;'>{r['lead_name']}</strong>
                    {badge(r['status'])}
                </div>
                <div style='font-size:.8rem; color:#64748b; margin-top:6px;'>
                    Von {r['sender_name']} · {r['created_at'][:10]}
                </div>
                {'<div style="font-size:.85rem; color:#94a3b8; margin-top:4px;">' + r['reason'][:80] + ('…' if len(r.get('reason',''))>80 else '') + '</div>' if r.get('reason') else ''}
            </div>
            """, unsafe_allow_html=True)

    with col_s:
        st.markdown("#### 📤 Zuletzt gesendet")
        if not sent:
            st.info("Noch keine Empfehlungen gesendet.")
        for r in sent[:5]:
            st.markdown(f"""
            <div class='ref-card'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <strong style='color:#e2e8f0;'>{r['lead_name']}</strong>
                    {badge(r['status'])}
                </div>
                <div style='font-size:.8rem; color:#64748b; margin-top:6px;'>
                    An {r['receiver_name']} · {r['created_at'][:10]}
                </div>
                {'<div style="font-size:.85rem; color:#94a3b8; margin-top:4px;">💰 CHF ' + f"{r['revenue']:,.0f}" + '</div>' if r.get('revenue') else ''}
            </div>
            """, unsafe_allow_html=True)


def page_referrals():
    user      = st.session_state.user
    referrals = get_referrals_for_user(user["id"])

    st.markdown("<div class='section-title'>📋 Alle Empfehlungen</div>", unsafe_allow_html=True)

    # ── Filter row ────────────────────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([1, 1, 2])
    with fc1:
        direction = st.selectbox("Richtung", ["Alle", "Erhalten", "Gesendet"])
    with fc2:
        status_filter = st.selectbox("Status", ["Alle"] + list(STATUS_DE.values()))
    with fc3:
        search = st.text_input("🔍 Suche (Lead / Unternehmen)")

    # Apply filters
    filtered = referrals
    if direction == "Erhalten":
        filtered = [r for r in filtered if r["receiver_id"] == user["id"]]
    elif direction == "Gesendet":
        filtered = [r for r in filtered if r["sender_id"] == user["id"]]
    if status_filter != "Alle":
        rev_map = {v: k for k, v in STATUS_DE.items()}
        filtered = [r for r in filtered if r["status"] == rev_map.get(status_filter, "")]
    if search:
        s = search.lower()
        filtered = [r for r in filtered
                    if s in r["lead_name"].lower()
                    or s in (r.get("lead_company") or "").lower()]

    st.markdown(f"<p style='color:#64748b; font-size:.85rem;'>{len(filtered)} Einträge</p>",
                unsafe_allow_html=True)

    if not filtered:
        st.info("Keine Empfehlungen gefunden.")
        return

    for r in filtered:
        is_receiver = r["receiver_id"] == user["id"]
        direction_label = "📥 Von " + r["sender_name"] if is_receiver else "📤 An " + r["receiver_name"]

        with st.expander(
            f"{r['lead_name']}  ·  {r.get('lead_company', '')}  ·  {STATUS_LABELS[r['status']][0]}"
        ):
            d1, d2 = st.columns([2, 1])
            with d1:
                st.markdown(f"""
                <div class='ref-card' style='margin:0;'>
                    <p><strong>Lead:</strong> {r['lead_name']}</p>
                    {'<p><strong>Unternehmen:</strong> ' + r["lead_company"] + '</p>' if r.get("lead_company") else ''}
                    {'<p><strong>E-Mail:</strong> ' + r["lead_email"] + '</p>' if r.get("lead_email") else ''}
                    {'<p><strong>Telefon:</strong> ' + r["lead_phone"] + '</p>' if r.get("lead_phone") else ''}
                    {'<p><strong>Empfehlung:</strong> ' + r["reason"] + '</p>' if r.get("reason") else ''}
                    <p style='margin-top:12px; color:#64748b; font-size:.8rem;'>
                        {direction_label} · {r['created_at'][:10]}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            with d2:
                st.markdown(f"**Status:** {badge(r['status'])}", unsafe_allow_html=True)

                # Timeline
                timeline = []
                if r.get("created_at"):    timeline.append(("📝 Erstellt",       r["created_at"][:16]))
                if r.get("contacted_at"):  timeline.append(("📞 Kontaktiert",     r["contacted_at"][:16]))
                if r.get("in_progress_at"):timeline.append(("⚙️ In Bearbeitung",  r["in_progress_at"][:16]))
                if r.get("closed_at"):     timeline.append(("✅ Abgeschlossen",   r["closed_at"][:16]))
                if r.get("revenue"):       timeline.append(("💰 Umsatz", f"CHF {r['revenue']:,.0f}"))

                for icon_label, ts in timeline:
                    st.markdown(
                        f"<div style='font-size:.8rem; color:#64748b; margin-top:4px;'>"
                        f"{icon_label}: <span style='color:#94a3b8;'>{ts}</span></div>",
                        unsafe_allow_html=True
                    )

                # Status change (only receiver)
                if is_receiver and r["status"] != "closed":
                    current_idx = STATUS_FLOW.index(r["status"])
                    next_status = STATUS_FLOW[current_idx + 1]

                    st.markdown("<br>", unsafe_allow_html=True)
                    revenue_input = None
                    if next_status == "closed":
                        revenue_input = st.number_input(
                            "Auftragssumme (CHF)",
                            min_value=0.0, step=100.0,
                            key=f"rev_{r['id']}"
                        )

                    if st.button(
                        f"➡️ Auf '{STATUS_DE[next_status]}' setzen",
                        key=f"status_{r['id']}"
                    ):
                        update_referral_status(r["id"], next_status, revenue_input)

                        # Notify sender when lead is contacted
                        if next_status == "contacted" and not r.get("notified_sender_contacted"):
                            full = get_referral_by_id(r["id"])
                            notify_sender_lead_contacted(full)
                            mark_notified_sender_contacted(r["id"])

                        st.success(f"Status auf '{STATUS_DE[next_status]}' aktualisiert!")
                        st.rerun()


def page_new_referral():
    user  = st.session_state.user
    users = [u for u in get_all_users() if u["id"] != user["id"]]

    st.markdown("<div class='section-title'>➕ Neue Empfehlung abgeben</div>",
                unsafe_allow_html=True)

    if not users:
        st.warning("Noch keine anderen Mitglieder im Netzwerk.")
        return

    with st.form("new_referral_form"):
        st.markdown("#### 👤 Lead-Informationen")
        c1, c2 = st.columns(2)
        with c1:
            lead_name    = st.text_input("Name des Leads *")
            lead_email   = st.text_input("E-Mail des Leads")
        with c2:
            lead_company = st.text_input("Unternehmen des Leads")
            lead_phone   = st.text_input("Telefon des Leads")

        st.markdown("#### 📋 Empfehlung")
        reason = st.text_area("Warum empfehle ich? *", height=120,
                              placeholder="Z.B. Thomas sucht eine neue ERP-Lösung und hat mich auf deine Expertise angesprochen…")

        st.markdown("#### 📬 Empfänger")
        receiver_options = {f"{u['name']} ({u.get('company','')})": u["id"] for u in users}
        receiver_label   = st.selectbox("Wer soll die Empfehlung erhalten? *",
                                        list(receiver_options.keys()))

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Empfehlung abgeben", use_container_width=True)

        if submitted:
            if not lead_name or not reason:
                st.error("Bitte fülle alle Pflichtfelder (*) aus.")
            else:
                receiver_id = receiver_options[receiver_label]
                ref_id = create_referral(
                    sender_id=user["id"],
                    receiver_id=receiver_id,
                    lead_name=lead_name,
                    lead_email=lead_email,
                    lead_phone=lead_phone,
                    lead_company=lead_company,
                    reason=reason,
                )
                full = get_referral_by_id(ref_id)
                # Send emails
                notify_receiver_new_referral(full)
                mark_notified_receiver(ref_id)
                notify_sender_referral_received(full)

                st.success(f"✅ Empfehlung für **{lead_name}** wurde erfolgreich abgegeben!")
                st.balloons()


def page_network():
    st.markdown("<div class='section-title'>👥 Netzwerk</div>", unsafe_allow_html=True)
    users = get_all_users()

    st.markdown(f"**{len(users)} Mitglieder** in deinem Netzwerk")
    st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, u in enumerate(users):
        stats = get_dashboard_stats(u["id"])
        with cols[i % 3]:
            me = u["id"] == st.session_state.user["id"]
            border = "border-color:#818cf8;" if me else ""
            st.markdown(f"""
            <div class='ref-card' style='{border}'>
                <div style='font-size:2rem; text-align:center;'>👤</div>
                <div style='text-align:center; margin-top:8px;'>
                    <strong style='color:#e2e8f0;'>{u['name']}</strong>
                    {'<span style="font-size:.75rem; color:#818cf8; margin-left:6px;">(Du)</span>' if me else ''}
                    <div style='font-size:.8rem; color:#64748b; margin-top:2px;'>
                        {u.get('company', '–')}
                    </div>
                </div>
                <div style='display:flex; justify-content:space-around; margin-top:16px;'>
                    <div style='text-align:center;'>
                        <div style='font-weight:700; color:#818cf8;'>{stats['total_sent']}</div>
                        <div style='font-size:.75rem; color:#64748b;'>Gesendet</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-weight:700; color:#818cf8;'>{stats['total_received']}</div>
                        <div style='font-size:.75rem; color:#64748b;'>Erhalten</div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-weight:700; color:#4ade80;'>
                            CHF {stats['total_revenue']:,.0f}
                        </div>
                        <div style='font-size:.75rem; color:#64748b;'>Umsatz</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    if not st.session_state.user:
        show_login()
    else:
        show_sidebar()
        page = st.session_state.page
        if page == "dashboard":
            page_dashboard()
        elif page == "referrals":
            page_referrals()
        elif page == "new":
            page_new_referral()
        elif page == "network":
            page_network()

if __name__ == "__main__":
    main()
