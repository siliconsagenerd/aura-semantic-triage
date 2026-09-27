# Aura – Semantic Message Triage System

[Deutsch](#deutsch) | [English](#english)

---

## English

### Overview

**Aura** is an AI-powered message triage system designed for a grief counseling agency. It automatically analyzes incoming social media messages and categorizes them by urgency, sentiment, and emotional intensity using Google's Gemini API. Built with FastAPI (Python), Vue 3, and Docker.

**Key Features:**
- 🤖 AI-powered message analysis using Gemini 1.5 Flash
- 📊 Real-time analytics dashboard (urgency, category, platform breakdown)
- 🚨 Automatic crisis detection with high-priority alerts
- 💾 SQLite database persistence with full message history
- 🎨 Modern Vue 3 UI with multi-tab interface
- 🐳 Full Docker/Docker Compose setup
- ✅ Input validation (frontend + backend)
- 📱 Responsive design
- ⚡ Intelligent fallback when API is unavailable

### Tech Stack

**Backend:**
- FastAPI (Python 3.10)
- SQLAlchemy ORM + SQLite
- Google Generative AI (Gemini 1.5 Flash)
- Pydantic validation

**Frontend:**
- Vue 3 (Composition API)
- Tailwind CSS + Vite
- Heroicons
- Responsive grid layout

**Infrastructure:**
- Docker & Docker Compose
- Nginx (frontend SPA server)
- Multi-stage builds
- Health checks & auto-restart

### Installation & Setup

#### Prerequisites
- Docker & Docker Compose
- Google Gemini API key (get one at [ai.google.dev](https://ai.google.dev))

#### Quick Start

1. **Clone/download the project**
   ```bash
   cd Aura
   ```

2. **Set up environment variables**
   ```bash
   # Create backend/.env
   echo "GEMINI_API_KEY=your_api_key_here" > backend/.env
   ```

3. **Start the stack**
   ```bash
   docker compose up --build
   ```

4. **Access the app**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`

### Project Structure

```
Aura/
├── backend/
│   ├── main.py                 # FastAPI app with 10 endpoints
│   ├── database.py             # SQLAlchemy models & DB config
│   ├── requirements.txt         # Python dependencies
│   ├── .env                     # Environment variables (API key)
│   ├── Dockerfile              # Multi-stage Python build
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── App.vue             # Main Vue component (4 tabs)
│   │   ├── main.js             # Vue entry point
│   │   └── style.css           # Global styles
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf              # SPA routing config
│   ├── Dockerfile              # Multi-stage Node build
│   └── serve.json              # Serve configuration
├── docker-compose.yml          # Orchestration
├── .dockerignore
└── README.md
```

### API Endpoints

All endpoints require valid input validation. Errors return descriptive messages.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check + DB status |
| POST | `/api/triage` | Analyze single message |
| POST | `/api/triage/batch` | Analyze 1-50 messages |
| GET | `/api/history` | Message history (filterable) |
| GET | `/api/analytics` | Dashboard analytics |
| GET | `/api/messages/high-priority` | High urgency messages |
| GET | `/api/messages/by-emotion` | Filter by emotion score |
| POST | `/api/feedback` | Record response feedback |
| POST | `/api/clear-history` | Clear all messages |
| GET | `/` | API documentation |

### Message Categorization

**Urgency Levels:**
- **High** – Crisis intervention needed (suicidal ideation, immediate distress)
- **Medium** – Service inquiry, technical issue, stable but emotional
- **Low** – General comment, feedback, thanks

**Categories:**
- Grief Support
- Crisis Intervention
- Service Inquiry
- Pricing/Sales
- Technical Support
- Feedback
- General Comment
- Memorial Request

**Sentiment:**
Sorrowful, Anxious, Angry, Neutral, Grateful, Confused, Hopeful, Desperate

**Emotion Score:** 0-100 (measures emotional intensity)

### Key Features Explained

#### 1. AI-Powered Triage
Messages are sent to Google Gemini 1.5 Flash for intelligent categorization. Responses are context-aware in German.

#### 2. Intelligent Fallback
If the Gemini API is unavailable, the system uses keyword-based fallback logic to still categorize messages. No downtime!

#### 3. Input Validation
- **Frontend:** Real-time validation with error messages
- **Backend:** Pydantic models enforce strict typing
- Min/max character limits, platform whitelist, emotion score bounds

#### 4. Database Persistence
All messages, analyses, and feedback are stored in SQLite. Full audit trail with timestamps.

#### 5. Toast Notifications
Success/error feedback appears as non-intrusive toasts (bottom-right).

#### 6. Loading States
UI shows processing status during API calls. Buttons disable during analysis to prevent double-clicks.

### UI Tabs

1. **Inbox** – Incoming messages with platform filter, refresh button, manual message input
2. **Results** – Processed messages with AI analysis, suggested replies, clear history
3. **Analytics** – KPIs (total, high-priority, avg emotion), breakdowns by urgency/category/platform
4. **Critical** – High-priority alerts for crisis detection

### Error Handling

**Frontend Errors:**
- Invalid input (character limits, empty messages) → inline error message
- API connection failure → toast notification + console log
- HTTP errors → descriptive message from backend

**Backend Errors:**
- Validation errors (422) → Pydantic validation details
- Missing API key (500) → Clear message to reconfigure
- Database errors → Logged + returned to frontend

### Configuration

#### Environment Variables
```bash
# backend/.env
GEMINI_API_KEY=sk-xxx...
```

#### Docker Compose
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Database: ./aura_messages.db (SQLite, auto-created)
- Network: aura-network (bridge)

### Development

#### Adding a New Feature

1. **Backend endpoint** – Add to `main.py`, use Pydantic for validation
2. **Database model** – Update `database.py` if new fields needed
3. **Frontend component** – Update `App.vue`, add toast notifications
4. **Test** – Use Swagger UI at `/docs` or test manually in UI

#### Testing the API
```bash
# Get health status
curl http://localhost:8000/api/health

# Triage a single message
curl -X POST http://localhost:8000/api/triage \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "text": "Ich bin sehr traurig...",
    "platform": "Instagram"
  }'

# Get analytics
curl http://localhost:8000/api/analytics
```

### Performance Considerations

- **Multi-stage builds** reduce image size (backend ~200MB, frontend ~50MB)
- **SQLite** is suitable for demo/single-server use. For production, use PostgreSQL.
- **Batch triage** processes up to 50 messages efficiently
- **Caching** on frontend keeps state in memory (no Redux/Pinia needed for this scope)
- **Emotion score filtering** allows efficient querying of high-impact messages

### Deployment Recommendations

For a **part-time student project** showcasing skills:
- ✅ Keep as-is (Docker Compose works great locally)
- Deploy to Heroku, Railway, or Fly.io for easy hosting

For **production:**
- Switch SQLite → PostgreSQL
- Add Redis for caching
- Use Kubernetes for scaling
- Add CI/CD pipeline (GitHub Actions)
- Implement authentication
- Add rate limiting

### Known Limitations

- In-memory message cache on frontend (no persisted UI state)
- Batch triage has 50-message limit
- Emotion score threshold validation (0-100)
- German language focus (prompts in German)

### License

Built as a portfolio project for a job application. Use freely for educational purposes.

---

## Deutsch

### Übersicht

**Aura** ist ein KI-gestütztes Message-Triage-System, das für eine Trauer- und Gedenkbegleitung entwickelt wurde. Es analysiert automatisch eingehende Social-Media-Nachrichten und kategorisiert sie nach Dringlichkeit, Sentiment und emotionaler Intensität mithilfe von Googles Gemini API. Entwickelt mit FastAPI (Python), Vue 3 und Docker.

**Hauptmerkmale:**
- 🤖 KI-gestützte Nachrichtenanalyse mit Gemini 1.5 Flash
- 📊 Echtzeit-Analytics-Dashboard (Dringlichkeit, Kategorie, Plattformen)
- 🚨 Automatische Krisenerkennung mit Hochpriorität-Warnungen
- 💾 SQLite-Datenbankpersistierung mit vollständiger Nachrichtenhistorie
- 🎨 Modernes Vue 3 UI mit Multi-Tab-Interface
- 🐳 Vollständiges Docker/Docker Compose Setup
- ✅ Input-Validierung (Frontend + Backend)
- 📱 Responsive Design
- ⚡ Intelligentes Fallback bei API-Ausfall

### Tech-Stack

**Backend:**
- FastAPI (Python 3.10)
- SQLAlchemy ORM + SQLite
- Google Generative AI (Gemini 1.5 Flash)
- Pydantic Validierung

**Frontend:**
- Vue 3 (Composition API)
- Tailwind CSS + Vite
- Heroicons
- Responsive Grid Layout

**Infrastruktur:**
- Docker & Docker Compose
- Nginx (Frontend SPA Server)
- Multi-Stage Builds
- Health Checks & Auto-Restart

### Installation & Setup

#### Voraussetzungen
- Docker & Docker Compose
- Google Gemini API-Schlüssel (von [ai.google.dev](https://ai.google.dev))

#### Schnellstart

1. **Projekt klonen/herunterladen**
   ```bash
   cd Aura
   ```

2. **Umgebungsvariablen einrichten**
   ```bash
   # Erstelle backend/.env
   echo "GEMINI_API_KEY=dein_api_key_hier" > backend/.env
   ```

3. **Stack starten**
   ```bash
   docker compose up --build
   ```

4. **App aufrufen**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API-Dokumentation: `http://localhost:8000/docs`

### Projektstruktur

```
Aura/
├── backend/
│   ├── main.py                 # FastAPI-App mit 10 Endpoints
│   ├── database.py             # SQLAlchemy-Modelle & DB-Config
│   ├── requirements.txt         # Python-Abhängigkeiten
│   ├── .env                     # Umgebungsvariablen (API-Schlüssel)
│   ├── Dockerfile              # Multi-Stage Python Build
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── App.vue             # Haupt-Vue-Component (4 Tabs)
│   │   ├── main.js             # Vue Entry Point
│   │   └── style.css           # Globale Styles
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf              # SPA-Routing-Config
│   ├── Dockerfile              # Multi-Stage Node Build
│   └── serve.json              # Serve-Konfiguration
├── docker-compose.yml          # Orchestrierung
├── .dockerignore
└── README.md
```

### API-Endpoints

Alle Endpoints erfordern valide Input-Validierung. Fehler geben aussagekräftige Meldungen zurück.

| Methode | Endpoint | Beschreibung |
|---------|----------|-------------|
| GET | `/api/health` | Gesundheitsstatus + DB-Status |
| POST | `/api/triage` | Einzelne Nachricht analysieren |
| POST | `/api/triage/batch` | 1-50 Nachrichten analysieren |
| GET | `/api/history` | Nachrichtenhistorie (filterbar) |
| GET | `/api/analytics` | Dashboard-Analytics |
| GET | `/api/messages/high-priority` | Hochpriorität-Nachrichten |
| GET | `/api/messages/by-emotion` | Nach Emotionsintensität filtern |
| POST | `/api/feedback` | Feedback zur Antwort erfassen |
| POST | `/api/clear-history` | Alle Nachrichten löschen |
| GET | `/` | API-Dokumentation |

### Nachricht-Kategorisierung

**Dringlichkeitsstufen:**
- **Hoch** – Krisenintervention erforderlich (Suizidgedanken, akute Bedrängnis)
- **Mittel** – Serviceabfrage, technisches Problem, stabil aber emotional
- **Niedrig** – Allgemeiner Kommentar, Feedback, Dank

**Kategorien:**
- Trauerbewältigung
- Krisenintervention
- Service-Anfrage
- Preis/Verkauf
- Technischer Support
- Feedback
- Allgemeiner Kommentar
- Gedenkseite-Anfrage

**Sentiment:**
Sorrowful (Traurig), Anxious (Angespannt), Angry (Wütend), Neutral, Grateful (Dankbar), Confused (Verwirrt), Hopeful (Hoffnungsvoll), Desperate (Verzweifelt)

**Emotionsintensität:** 0-100 (Maßstab für emotionale Belastung)

### Erklärung der Hauptmerkmale

#### 1. KI-gestützte Triage
Nachrichten werden an Google Gemini 1.5 Flash zur intelligenten Kategorisierung gesendet. Antworten sind kontextbewusst und auf Deutsch.

#### 2. Intelligentes Fallback
Wenn die Gemini API nicht verfügbar ist, nutzt das System schlüsselwortbasierte Fallback-Logik. Keine Ausfallzeiten!

#### 3. Input-Validierung
- **Frontend:** Echtzeit-Validierung mit Fehlermeldungen
- **Backend:** Pydantic-Modelle erzwingen strenge Typisierung
- Min/Max-Zeichenlimits, Plattform-Whitelist, Emotionsintensitäts-Grenzen

#### 4. Datenbankpersistierung
Alle Nachrichten, Analysen und Feedback werden in SQLite gespeichert. Vollständiges Audit-Trail mit Zeitstempeln.

#### 5. Toast-Benachrichtigungen
Erfolgs-/Fehlerfeedback erscheint als unauffällige Toasts (unten rechts).

#### 6. Lade-Zustände
Die UI zeigt Verarbeitungsstatus während API-Aufrufen. Buttons sind während der Analyse deaktiviert, um Doppelklicks zu verhindern.

### UI-Tabs

1. **Posteingang** – Eingehende Nachrichten mit Plattform-Filter, Aktualisierungs-Button, manuelle Nachrichteneingabe
2. **Ergebnisse** – Verarbeitete Nachrichten mit KI-Analyse, vorgeschlagene Antworten, Historie löschen
3. **Analytik** – KPIs (Gesamt, Hochpriorität, durchschn. Emotion), Aufschlüsseling nach Dringlichkeit/Kategorie/Plattform
4. **Kritisch** – Hochpriorität-Warnungen zur Krisenerkennung

### Fehlerbehandlung

**Frontend-Fehler:**
- Ungültige Eingabe (Zeichenlimits, leere Nachrichten) → Inline-Fehlermeldung
- API-Verbindungsfehler → Toast-Benachrichtigung + Console-Log
- HTTP-Fehler → Aussagekräftige Meldung vom Backend

**Backend-Fehler:**
- Validierungsfehler (422) → Pydantic-Validierungsdetails
- Fehlender API-Schlüssel (500) → Klare Meldung zur Neukonfigurierung
- Datenbankfehler → Protokolliert + zurück zum Frontend

### Konfiguration

#### Umgebungsvariablen
```bash
# backend/.env
GEMINI_API_KEY=sk-xxx...
```

#### Docker Compose
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Datenbank: ./aura_messages.db (SQLite, automatisch erstellt)
- Netzwerk: aura-network (bridge)

### Entwicklung

#### Neue Funktion hinzufügen

1. **Backend-Endpoint** – Zu `main.py` hinzufügen, Pydantic für Validierung verwenden
2. **Datenbankmodell** – `database.py` aktualisieren, falls neue Felder nötig
3. **Frontend-Component** – `App.vue` aktualisieren, Toast-Benachrichtigungen hinzufügen
4. **Test** – Swagger UI unter `/docs` verwenden oder manuell im UI testen

#### API testen
```bash
# Gesundheitsstatus prüfen
curl http://localhost:8000/api/health

# Einzelne Nachricht analysieren
curl -X POST http://localhost:8000/api/triage \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "text": "Ich bin sehr traurig...",
    "platform": "Instagram"
  }'

# Analytics abrufen
curl http://localhost:8000/api/analytics
```

### Leistungsüberlegungen

- **Multi-Stage Builds** reduzieren Bildgröße (Backend ~200MB, Frontend ~50MB)
- **SQLite** ist für Demo/Single-Server geeignet. Für Produktion PostgreSQL verwenden.
- **Batch-Triage** verarbeitet bis zu 50 Nachrichten effizient
- **Caching** im Frontend speichert Zustand im Speicher (kein Redux/Pinia für diesen Umfang nötig)
- **Emotionsintensitäts-Filterung** ermöglicht effiziente Abfrage von Hochpriorität-Nachrichten

### Deployment-Empfehlungen

Für ein **Teilzeit-Studentenprojekt** zur Fähigkeitendemonstration:
- ✅ So lassen (Docker Compose funktioniert lokal prima)
- Bereitstellung auf Heroku, Railway oder Fly.io für einfaches Hosting

Für **Produktion:**
- SQLite → PostgreSQL wechseln
- Redis für Caching hinzufügen
- Kubernetes für Skalierung verwenden
- CI/CD-Pipeline hinzufügen (GitHub Actions)
- Authentifizierung implementieren
- Rate Limiting hinzufügen

### Bekannte Einschränkungen

- In-Memory-Message-Cache im Frontend (kein persistierter UI-Zustand)
- Batch-Triage hat 50-Nachricht-Limit
- Emotionsintensitäts-Schwellenwert-Validierung (0-100)
- Deutschsprachiger Fokus (Prompts auf Deutsch)

### Lizenz

Erstellt als Portfolio-Projekt für eine Bewerbung. Frei für Bildungszwecke nutzbar.

