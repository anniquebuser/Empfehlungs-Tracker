# Business Referral Tracker

## 🚀 Schnellstart

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. (Optional) E-Mail konfigurieren – .env.example → .env kopieren
cp .env.example .env
# .env editieren und SMTP-Zugangsdaten eintragen

# 3. App starten
streamlit run app.py
```

App öffnet sich unter **http://localhost:8501**

---

## 🔑 Demo-Zugänge

| Name           | E-Mail             | Passwort  |
|----------------|--------------------|-----------|
| Anna Müller    | anna@demo.com      | demo123   |
| Ben Schneider  | ben@demo.com       | demo123   |
| Clara Becker   | clara@demo.com     | demo123   |
| David Lehmann  | david@demo.com     | demo123   |

---

## 📁 Dateistruktur

```
referral_tracker/
├── app.py            ← Streamlit Haupt-App
├── database.py       ← SQLite Datenmodell & Datenbankfunktionen
├── email_service.py  ← E-Mail-Benachrichtigungen via SMTP
├── requirements.txt
├── .env.example      ← E-Mail-Konfiguration (Vorlage)
└── README.md
```

---

## 🗄️ Datenmodell

### Tabelle `users`
| Spalte      | Typ     | Beschreibung                  |
|-------------|---------|-------------------------------|
| id          | INTEGER | Primärschlüssel               |
| name        | TEXT    | Vollständiger Name            |
| email       | TEXT    | Eindeutige E-Mail (Login)     |
| password    | TEXT    | SHA-256 gehashtes Passwort    |
| company     | TEXT    | Unternehmen                   |
| created_at  | TEXT    | Erstellungsdatum              |

### Tabelle `referrals`
| Spalte                      | Typ     | Beschreibung                        |
|-----------------------------|---------|-------------------------------------|
| id                          | INTEGER | Primärschlüssel                     |
| sender_id                   | INTEGER | FK → users (wer empfiehlt)          |
| receiver_id                 | INTEGER | FK → users (wer erhält die Empfehlung)|
| lead_name                   | TEXT    | Name des potenziellen Kunden        |
| lead_email                  | TEXT    | Kontakt-E-Mail des Leads            |
| lead_phone                  | TEXT    | Telefon des Leads                   |
| lead_company                | TEXT    | Unternehmen des Leads               |
| reason                      | TEXT    | Begründung / Empfehlungstext        |
| status                      | TEXT    | open / contacted / in_progress / closed |
| revenue                     | REAL    | Auftragssumme (bei Abschluss)       |
| created_at                  | TEXT    | Erstellt am                         |
| contacted_at                | TEXT    | Timestamp Statuswechsel → contacted |
| in_progress_at              | TEXT    | Timestamp Statuswechsel → in_progress|
| closed_at                   | TEXT    | Timestamp Statuswechsel → closed    |
| notified_receiver           | INTEGER | E-Mail an Empfänger gesendet?       |
| notified_sender_contacted   | INTEGER | E-Mail an Absender (kontaktiert)?   |

---

## 📧 E-Mail einrichten (Gmail)

1. Gmail-Konto → Einstellungen → 2-Faktor-Auth aktivieren
2. App-Passwort generieren unter: myaccount.google.com/apppasswords
3. `.env` ausfüllen:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=deine@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_NAME=Business Referral Tracker
FROM_EMAIL=deine@gmail.com
```

---

## 🔄 Status-Workflow

```
Offen → Kontaktiert → In Bearbeitung → Abgeschlossen
         ↑
         E-Mail an Absender wird ausgelöst
```

---

## 🔮 Nächste Schritte (optional)

- [ ] Supabase statt SQLite für Multi-User-Cloud-Betrieb
- [ ] Push-Benachrichtigungen (Streamlit Community Cloud)
- [ ] Export als Excel/CSV
- [ ] Mobile PWA via Streamlit share
