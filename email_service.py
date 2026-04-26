import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER     = os.getenv("SMTP_USER",     "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_NAME     = os.getenv("FROM_NAME",     "Referral Tracker")
FROM_EMAIL    = os.getenv("FROM_EMAIL",    SMTP_USER)
EMAIL_ENABLED = bool(SMTP_USER and SMTP_PASSWORD)

def _send(to_email, subject, html_body):
    if not EMAIL_ENABLED:
        print(f"\n[EMAIL – nicht gesendet]\n  An: {to_email}\n  Betreff: {subject}\n")
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo(); s.starttls(); s.login(SMTP_USER, SMTP_PASSWORD)
            s.sendmail(FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def _template(title, content):
    return f"""<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8">
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;background:#0a0f1e;margin:0;padding:0;}}
.wrap{{max-width:600px;margin:40px auto;background:#0d1528;border-radius:16px;
       overflow:hidden;border:1px solid #1e3a5f;}}
.head{{background:linear-gradient(135deg,#0a1628,#0d2545);padding:32px 40px;
       border-bottom:1px solid #1e3a5f;}}
.head h1{{margin:0;font-size:20px;font-weight:700;color:#60a5fa;letter-spacing:.5px;}}
.head p{{margin:6px 0 0;color:#475569;font-size:13px;}}
.body{{padding:32px 40px;color:#cbd5e1;line-height:1.7;}}
.card{{background:#0a1628;border:1px solid #1e3a5f;border-radius:10px;
       padding:20px 24px;margin:20px 0;}}
.card p{{margin:5px 0;font-size:14px;}}
.card strong{{color:#93c5fd;}}
.badge{{display:inline-block;padding:5px 14px;border-radius:20px;
        font-size:12px;font-weight:700;background:#1e3a5f;color:#60a5fa;}}
.foot{{background:#080d1a;padding:20px 40px;font-size:12px;
       color:#334155;text-align:center;border-top:1px solid #1e3a5f;}}
</style></head><body>
<div class="wrap">
  <div class="head"><h1>🤝 Referral Tracker</h1><p>{title}</p></div>
  <div class="body">{content}</div>
  <div class="foot">Referral Tracker · Automatische Benachrichtigung</div>
</div></body></html>"""

def notify_receiver_new_referral(referral):
    content = f"""
    <p>Hallo <strong style="color:#93c5fd">{referral['receiver_name']}</strong>,</p>
    <p>du hast eine neue Empfehlung von <strong>{referral['sender_name']}</strong>!</p>
    <div class="card">
      <p><strong>Lead:</strong> {referral['lead_name']}</p>
      {'<p><strong>Unternehmen:</strong> ' + referral['lead_company'] + '</p>' if referral.get('lead_company') else ''}
      {'<p><strong>E-Mail:</strong> ' + referral['lead_email'] + '</p>' if referral.get('lead_email') else ''}
      {'<p><strong>Telefon:</strong> ' + referral['lead_phone'] + '</p>' if referral.get('lead_phone') else ''}
      <p><strong>Empfehlung:</strong> {referral.get('reason','–')}</p>
    </div>
    <span class="badge">Status: Offen</span>"""
    return _send(referral["receiver_email"],
                 f"🎁 Neue Empfehlung von {referral['sender_name']}",
                 _template("Neue Empfehlung eingegangen", content))

def notify_sender_referral_received(referral):
    content = f"""
    <p>Hallo <strong style="color:#93c5fd">{referral['sender_name']}</strong>,</p>
    <p>deine Empfehlung für <strong>{referral['lead_name']}</strong> wurde an
       <strong>{referral['receiver_name']}</strong> weitergeleitet.</p>
    <div class="card">
      <p><strong>Lead:</strong> {referral['lead_name']}</p>
      <p><strong>Empfänger:</strong> {referral['receiver_name']}</p>
      <p><strong>Datum:</strong> {referral['created_at']}</p>
    </div>
    <span class="badge">Status: Offen</span>"""
    return _send(referral["sender_email"], "✅ Empfehlung übermittelt",
                 _template("Empfehlung erfolgreich übermittelt", content))

def notify_sender_lead_contacted(referral):
    content = f"""
    <p>Hallo <strong style="color:#93c5fd">{referral['sender_name']}</strong>,</p>
    <p><strong>{referral['receiver_name']}</strong> hat deinen Lead
       <strong>{referral['lead_name']}</strong> kontaktiert!</p>
    <div class="card">
      <p><strong>Lead:</strong> {referral['lead_name']}</p>
      <p><strong>Kontaktiert am:</strong> {referral.get('contacted_at','–')}</p>
    </div>
    <span class="badge">Status: Kontaktiert</span>"""
    return _send(referral["sender_email"],
                 f"📞 Dein Lead wurde kontaktiert – {referral['lead_name']}",
                 _template("Lead kontaktiert", content))
