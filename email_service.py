"""
E-Mail-Benachrichtigungen via SMTP.
Konfiguration über Umgebungsvariablen oder .env-Datei.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Config (Umgebungsvariablen oder Fallback) ──────────────────────────────────
SMTP_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER",     "")        # deine@gmail.com
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")        # App-Passwort
FROM_NAME     = os.getenv("FROM_NAME",     "Business Referral Tracker")
FROM_EMAIL    = os.getenv("FROM_EMAIL",    SMTP_USER)
EMAIL_ENABLED = bool(SMTP_USER and SMTP_PASSWORD)


def _send(to_email: str, subject: str, html_body: str) -> bool:
    """Sendet eine HTML-E-Mail. Gibt True bei Erfolg zurück."""
    if not EMAIL_ENABLED:
        # Entwicklungs-Fallback: nur in der Konsole ausgeben
        print(f"\n[EMAIL – nicht gesendet, da SMTP nicht konfiguriert]\n"
              f"  An:      {to_email}\n"
              f"  Betreff: {subject}\n")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


# ── Templates ─────────────────────────────────────────────────────────────────

def _base_template(title: str, content: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="de">
    <head><meta charset="UTF-8">
    <style>
      body   {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f4f6f9; margin:0; padding:0; }}
      .wrap  {{ max-width:600px; margin:40px auto; background:#fff;
                border-radius:12px; overflow:hidden;
                box-shadow:0 4px 20px rgba(0,0,0,.08); }}
      .head  {{ background: linear-gradient(135deg,#1a1a2e,#16213e);
                color:#fff; padding:32px 40px; }}
      .head h1 {{ margin:0; font-size:22px; font-weight:600; letter-spacing:.5px; }}
      .head p  {{ margin:6px 0 0; color:#94a3b8; font-size:13px; }}
      .body  {{ padding:32px 40px; color:#334155; line-height:1.7; }}
      .card  {{ background:#f8fafc; border:1px solid #e2e8f0;
                border-radius:8px; padding:20px 24px; margin:20px 0; }}
      .card p {{ margin:5px 0; font-size:14px; }}
      .card strong {{ color:#1e293b; }}
      .badge {{ display:inline-block; padding:4px 12px; border-radius:20px;
                font-size:12px; font-weight:600; letter-spacing:.5px;
                background:#dbeafe; color:#1d4ed8; }}
      .btn   {{ display:inline-block; margin-top:20px; padding:12px 28px;
                background:#1a1a2e; color:#fff; border-radius:8px;
                text-decoration:none; font-weight:600; font-size:14px; }}
      .foot  {{ background:#f8fafc; padding:20px 40px;
                font-size:12px; color:#94a3b8; text-align:center;
                border-top:1px solid #e2e8f0; }}
    </style>
    </head>
    <body>
      <div class="wrap">
        <div class="head">
          <h1>🤝 Business Referral Tracker</h1>
          <p>{title}</p>
        </div>
        <div class="body">{content}</div>
        <div class="foot">Business Referral Tracker · Automatische Benachrichtigung</div>
      </div>
    </body>
    </html>
    """


def notify_receiver_new_referral(referral: dict) -> bool:
    """E-Mail an Empfänger: neue Empfehlung eingegangen."""
    subject = f"🎁 Neue Empfehlung von {referral['sender_name']}"
    content = f"""
    <p>Hallo <strong>{referral['receiver_name']}</strong>,</p>
    <p>du hast eine neue Empfehlung von <strong>{referral['sender_name']}</strong> erhalten!</p>

    <div class="card">
      <p><strong>Lead:</strong> {referral['lead_name']}</p>
      {'<p><strong>Unternehmen:</strong> ' + referral['lead_company'] + '</p>' if referral.get('lead_company') else ''}
      {'<p><strong>E-Mail:</strong> ' + referral['lead_email'] + '</p>' if referral.get('lead_email') else ''}
      {'<p><strong>Telefon:</strong> ' + referral['lead_phone'] + '</p>' if referral.get('lead_phone') else ''}
      <p><strong>Empfehlung:</strong> {referral.get('reason', '–')}</p>
    </div>

    <p>Bitte melde dich so bald wie möglich bei dem Lead und aktualisiere den Status im Tracker.</p>
    <span class="badge">Status: Offen</span>
    """
    return _send(referral["receiver_email"], subject, _base_template("Neue Empfehlung eingegangen", content))


def notify_sender_referral_received(referral: dict) -> bool:
    """Bestätigung an Absender: Empfehlung wurde übermittelt."""
    subject = f"✅ Deine Empfehlung wurde übermittelt"
    content = f"""
    <p>Hallo <strong>{referral['sender_name']}</strong>,</p>
    <p>deine Empfehlung für <strong>{referral['lead_name']}</strong> wurde erfolgreich
       an <strong>{referral['receiver_name']}</strong> weitergeleitet.</p>

    <div class="card">
      <p><strong>Lead:</strong> {referral['lead_name']}</p>
      <p><strong>Empfänger:</strong> {referral['receiver_name']}</p>
      <p><strong>Erstellt am:</strong> {referral['created_at']}</p>
    </div>

    <p>Du wirst benachrichtigt, sobald {referral['receiver_name']} den Lead kontaktiert hat.</p>
    <span class="badge">Status: Offen</span>
    """
    return _send(referral["sender_email"], subject, _base_template("Empfehlung übermittelt", content))


def notify_sender_lead_contacted(referral: dict) -> bool:
    """E-Mail an Absender: Lead wurde kontaktiert."""
    subject = f"📞 Dein Lead wurde kontaktiert – {referral['lead_name']}"
    content = f"""
    <p>Hallo <strong>{referral['sender_name']}</strong>,</p>
    <p>gute Neuigkeiten! <strong>{referral['receiver_name']}</strong> hat deinen empfohlenen
       Lead <strong>{referral['lead_name']}</strong> kontaktiert.</p>

    <div class="card">
      <p><strong>Lead:</strong> {referral['lead_name']}</p>
      <p><strong>Kontaktiert am:</strong> {referral.get('contacted_at', '–')}</p>
      <p><strong>Empfänger:</strong> {referral['receiver_name']}</p>
    </div>

    <p>Wir halten dich über weitere Statusänderungen auf dem Laufenden.</p>
    <span class="badge">Status: Kontaktiert</span>
    """
    return _send(referral["sender_email"], subject, _base_template("Lead kontaktiert", content))
