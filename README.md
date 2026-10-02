# Aura – Semantic Message Triage System

# Aura - Semantic Message Triage System

![Visitors](https://api.visitorbadge.io/api/visitors?path=siliconsagenerd%2Faura-semantic-triage&countColor=%23263759)
![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![Vue 3](https://img.shields.io/badge/Vue.js-3.x-4FC08D?logo=vuedotjs)

[Deutsch](#deutsch) | [English](#english)

---

## English

### Overview

Aura is an AI-powered message triage system designed for a grief counseling agency. It automatically analyzes incoming social media messages and categorizes them by urgency, sentiment, and emotional intensity using Google's Gemini API. Built with FastAPI (Python), Vue 3, and Docker.

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
- Nginx (SPA server)
- Multi-stage builds
- Health checks & auto-restart

### Installation & Setup

#### Prerequisites
- Docker & Docker Compose
- Google Gemini API key (get one at [ai.google.dev](https://ai.google.dev))

#### Quick Start

1. Clone/download the project
   ```bash
   cd Aura
   ```

2. Set up environment variables
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > backend/.env
   ```

3. Start the stack
   ```bash
   docker compose up --build
   ```

4. Access the app
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`

### Project Structure

```
Aura/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   ├── .env
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf
│   ├── Dockerfile
│   └── serve.json
├── docker-compose.yml
├── .dockerignore
└── README.md
```

### API Endpoints

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
- High: Crisis intervention needed (suicidal ideation, immediate distress)
- Medium: Service inquiry, technical issue, stable but emotional
- Low: General comment, feedback, thanks

**Categories:**
- Grief Support
- Crisis Intervention
- Service Inquiry
- Pricing/Sales
- Technical Support
- Feedback
- General Comment
- Memorial Request

**Sentiment:** Sorrowful, Anxious, Angry, Neutral, Grateful, Confused, Hopeful, Desperate

**Emotion Score:** 0-100 (measures emotional intensity)

### Error Handling

Frontend errors show inline validation messages and toast notifications. Backend returns descriptive HTTP error responses with validation details.

### Configuration

Environment variables in `backend/.env`:
```
GEMINI_API_KEY=sk-xxx...
```

Docker Compose config:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Database: `./aura_messages.db` (SQLite, auto-created)
- Network: `aura-network` (bridge)

### Development

#### Adding a Feature

1. Backend endpoint – Add to `main.py`, use Pydantic for validation
2. Database model – Update `database.py` if new fields needed
3. Frontend component – Update `App.vue`
4. Test via Swagger UI at `/docs`

#### Testing the API

```bash
# Health check
curl http://localhost:8000/api/health

# Analyze message
curl -X POST http://localhost:8000/api/triage \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "text": "Ich bin sehr traurig...", "platform": "Instagram"}'

# Get analytics
curl http://localhost:8000/api/analytics
```

### Performance

- Multi-stage builds reduce image sizes (backend ~200MB, frontend ~50MB)
- SQLite suitable for demo/single-server use. Use PostgreSQL for production.
- Batch triage processes up to 50 messages efficiently
- Emotion score filtering enables high-impact message queries

### Deployment

For development/portfolio:
- Keep as-is (Docker Compose works locally)
- Deploy to Heroku, Railway, or Fly.io for hosting

For production:
- Switch SQLite to PostgreSQL
- Add Redis for caching
- Use Kubernetes for scaling
- Implement CI/CD (GitHub Actions)
- Add authentication & rate limiting

### Known Limitations

- In-memory message cache on frontend
- Batch triage max 50 messages
- Emotion score validation 0-100
- German language focus

---

## Deutsch

### Übersicht

Aura ist ein KI-gestütztes Message-Triage-System für eine Trauer- und Gedenkbegleitung. Es analysiert automatisch eingehende Social-Media-Nachrichten und kategorisiert sie nach Dringlichkeit, Sentiment und emotionaler Intensität mithilfe von Googles Gemini API. Entwickelt mit FastAPI (Python), Vue 3 und Docker.

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
- Nginx (SPA Server)
- Multi-Stage Builds
- Health Checks & Auto-Restart

### Installation & Setup

#### Voraussetzungen
- Docker & Docker Compose
- Google Gemini API-Schlüssel (von [ai.google.dev](https://ai.google.dev))

#### Schnellstart

1. Projekt klonen/herunterladen
   ```bash
   cd Aura
   ```

2. Umgebungsvariablen einrichten
   ```bash
   echo "GEMINI_API_KEY=dein_api_key_hier" > backend/.env
   ```

3. Stack starten
   ```bash
   docker compose up --build
   ```

4. App aufrufen
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API-Dokumentation: `http://localhost:8000/docs`

### Projektstruktur

```
Aura/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   ├── .env
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf
│   ├── Dockerfile
│   └── serve.json
├── docker-compose.yml
├── .dockerignore
└── README.md
```

### API-Endpoints

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
- Hoch: Krisenintervention erforderlich (Suizidgedanken, akute Bedrängnis)
- Mittel: Serviceabfrage, technisches Problem, stabil aber emotional
- Niedrig: Allgemeiner Kommentar, Feedback, Dank

**Kategorien:**
- Trauerbewältigung
- Krisenintervention
- Service-Anfrage
- Preis/Verkauf
- Technischer Support
- Feedback
- Allgemeiner Kommentar
- Gedenkseite-Anfrage

**Sentiment:** Sorrowful (Traurig), Anxious (Angespannt), Angry (Wütend), Neutral, Grateful (Dankbar), Confused (Verwirrt), Hopeful (Hoffnungsvoll), Desperate (Verzweifelt)

**Emotionsintensität:** 0-100

### Fehlerbehandlung

Frontend-Fehler zeigen Inline-Validierungsmeldungen und Toast-Benachrichtigungen. Backend gibt aussagekräftige HTTP-Fehlerresponses mit Validierungsdetails zurück.

### Konfiguration

Umgebungsvariablen in `backend/.env`:
```
GEMINI_API_KEY=sk-xxx...
```

Docker Compose Konfiguration:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Datenbank: `./aura_messages.db` (SQLite, automatisch erstellt)
- Netzwerk: `aura-network` (bridge)

### Entwicklung

#### Neue Funktion hinzufügen

1. Backend-Endpoint – Zu `main.py` hinzufügen, Pydantic für Validierung verwenden
2. Datenbankmodell – `database.py` aktualisieren, falls neue Felder nötig
3. Frontend-Component – `App.vue` aktualisieren
4. Test via Swagger UI unter `/docs`

#### API testen

```bash
# Gesundheitsstatus
curl http://localhost:8000/api/health

# Nachricht analysieren
curl -X POST http://localhost:8000/api/triage \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "text": "Ich bin sehr traurig...", "platform": "Instagram"}'

# Analytics abrufen
curl http://localhost:8000/api/analytics
```

### Leistung

- Multi-Stage Builds reduzieren Bildgröße (Backend ~200MB, Frontend ~50MB)
- SQLite für Demo/Single-Server geeignet. Für Produktion PostgreSQL verwenden.
- Batch-Triage verarbeitet bis zu 50 Nachrichten effizient
- Emotionsintensitäts-Filterung ermöglicht effiziente Abfrage von Hochpriorität-Nachrichten

### Deployment

Für Entwicklung/Portfolio:
- So lassen (Docker Compose funktioniert lokal prima)
- Bereitstellung auf Heroku, Railway oder Fly.io

Für Produktion:
- SQLite zu PostgreSQL wechseln
- Redis für Caching hinzufügen
- Kubernetes für Skalierung verwenden
- CI/CD implementieren (GitHub Actions)
- Authentifizierung & Rate Limiting hinzufügen

### Bekannte Einschränkungen

- In-Memory-Message-Cache im Frontend
- Batch-Triage max 50 Nachrichten
- Emotionsintensitäts-Validierung 0-100
- Deutschsprachiger Fokus
