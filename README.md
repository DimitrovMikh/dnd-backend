# 🐉 D&D Campaign Manager API

Eine asynchrone, modulare REST-API für Dungeons & Dragons Kampagnen. Das Backend ermöglicht die Verwaltung von Charakteren, Inventar-Items und Zaubersprüchen inklusive relationaler Verknüpfungen (1:N und N:M) sowie ein vollumfänglich gehärtetes **Authentifizierungs-, Autorisierungs- und Rollensystem (Argon2id, Dual-Token JWT mit HttpOnly Cookies, CORS & OWASP Hardening, Rate Limiting & RBAC)**.

---

## 🛠️ Tech Stack & Werkzeuge

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
* **Containerisierung & Orchestrierung:** [Docker](https://www.docker.com/) & Docker Compose (Multi-Stage Build, Non-Root System User)
* **Reverse Proxy & TLS:** [Caddy](https://caddyserver.com/) (Automatisches TLS/SSL via Let's Encrypt & Reverse Proxying)
* **Hosting & Cloud:** Contabo Linux VPS (UFW Firewall, Key-only SSH Hardening, Non-Root Deployment User)
* **CI/CD & Registry:** [GitHub Actions](https://github.com/features/actions) & GitHub Container Registry (`ghcr.io`)
* **ORM & Validierung:** [SQLModel](https://sqlmodel.tiangolo.com/) (Kombination aus SQLAlchemy 2.0 & Pydantic)
* **Asynchrone Datenbank:** [PostgreSQL 16](https://www.postgresql.org/) via `asyncpg` & `AsyncSession` (SQLite via `aiosqlite` als Fallback / für Tests)
* **Sicherheit & Auth:** [PyJWT](https://pyjwt.readthedocs.io/) (Dual-Token: Access & Refresh JWTs) & [pwdlib](https://pwdlib.readthedocs.io/) mit `argon2-cffi` (Argon2id Password Hashing)
* **Rate Limiting & Security:** [slowapi](https://github.com/laurents/slowapi) (Brute-Force Protection) & Custom OWASP Security Headers Middleware
* **Konfiguration:** [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) (Fail-Fast `.env` Validierung)
* **Datenbank-Migrationen:** [Alembic](https://alembic.sqlalchemy.org/)
* **Automated Testing:** `pytest`, `pytest-asyncio` & `httpx`
* **ASGI Server:** Uvicorn

---

## 🚀 Key Features & Highlights

* **Containerisierung & Produktionstauglichkeit (Docker & PostgreSQL):**
  * **Multi-Stage Build:** Schlankes, zweistufiges `Dockerfile` trennt Build-Abhängigkeiten vom finalen Runtime-Image.
  * **OWASP Container Hardening:** Ausführung im Container unter einem dedizierten Nicht-Root-System-User (`appuser`).
  * **Docker Compose Orchestrierung:** Integrierter Stack aus FastAPI und PostgreSQL 16 inklusive automatischer Healthchecks (`pg_isready`) und benannter Volumes für Datenpersistenz.
* **Gehärtete Authentifizierung (Argon2id & Dual-Tokens):**
  * **Passworthashing:** Sicheres Argon2id Hashing via modernem `pwdlib`-Framework (OWASP-Standard).
  * **Passwort-Komplexität:** Pydantic Field-Validator erzwingt Mindestlänge (9 Zeichen), Groß-/Kleinbuchstaben, Zahlen und Sonderzeichen.
  * **Access Token:** Kurzlebiges JWT (15 Minuten Gültigkeit) für API-Zugriffe im `Authorization: Bearer`-Header.
  * **Refresh Token:** Langlebiges JWT (7 Tage Gültigkeit), geschützt in einem **`HttpOnly` Cookie** (`SameSite=lax`) gegen XSS-Angriffe.
* **Automatisierte CI/CD Pipeline:** GitHub Actions baut bei jedem Push auf `main` das Docker-Image, lädt es in die GitHub Container Registry (`ghcr.io`) und führt einen automatisierten SSH-Rollout auf den VPS durch.
* **Brute-Force Protection & Rate Limiting:** IP-basierte Begrenzung sensitiver Endpunkte (`/auth/login` auf 5 Requests/Minute) via `slowapi`.
* **OWASP Security Headers & CORS Hardening:** Granulare CORS-Policies sowie automatische Injektion von Sicherheits-Headern (`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`).
* **Role-Based Access Control (RBAC):** Granulare Rechtevergabe über die `RoleChecker`-Dependency für geschützte Aktionen (`DUNGEON_MASTER` / `ADMIN`).
* **Clean Architecture & Service Layer:** Strikte Entkopplung von Datenbank-Tabellen (`app/db/models/`), API-DTOs (`app/schemas/`) und der Business-Logik (`app/services/`).
* **Echtzeit-Healthcheck:** Dedicated `/health`-Endpoint führt eine Live-Verbindungsprüfung (`SELECT 1`) gegen die Datenbank durch.
* **Automatisierte Test-Suite:** 100 % grün durchlaufende Integrationstests mit `pytest-asyncio` über eine In-Memory Test-Datenbank.

---

## 📁 Projektstruktur

```text
DND-BACKEND/
├── .github/                        # 🤖 GitHub Actions Automation
│   └── workflows/
│       ├── cd.yml                  # 🚀 CD Pipeline (GHCR Build/Push & SSH VPS Deployment)
│       └── ci.yml                  # 🧪 CI Pipeline (Ruff, Mypy, Pytest)
├── docker-compose.yml              # 🐳 Docker Compose für lokale Entwicklung (build: ./backend)
├── docker-compose.prod.yml         # 🚀 Docker Compose für Produktion auf dem VPS (image: ghcr.io)
├── .vscode/                        # VS Code Projekt-Konfiguration
│   └── settings.json
├── backend/                        # 🐍 FASTAPI BACKEND SERVICE
│   ├── .dockerignore               # Ausschlussregeln für Docker Build-Kontext
│   ├── Dockerfile                  # Multi-Stage Build & Non-Root User Hardening
│   ├── alembic/                    # Alembic Migrations-Ordner
│   │   ├── versions/               # Versionierte Migrations-Skripte
│   │   ├── env.py                  # Async Migrations-Konfiguration & Model-Importe
│   │   └── script.py.mako          # Jinja-Template für neue Migrationen
│   ├── app/                        # Hauptanwendung
│   │   ├── api/                    # FastAPI Router (Endpoints)
│   │   │   └── v1/                 # Versionierte API v1
│   │   │       ├── auth.py         # Auth-Router (/register, /login, /refresh, /me)
│   │   │       ├── characters.py   # Router für Charaktere
│   │   │       ├── health.py       # Healthcheck-Router (/health)
│   │   │       ├── items.py        # Router für Inventar-Gegenstände
│   │   │       └── spells.py       # Router für Zaubersprüche
│   │   ├── core/                   # Anwendungsweite Kern-Komponenten
│   │   │   ├── config.py           # Pydantic Settings & Env-Validierung
│   │   │   ├── exceptions.py       # Custom Domain Exceptions (DNDGameException)
│   │   │   ├── limiter.py          # Central Rate Limiter Instance (slowapi)
│   │   │   ├── middleware.py       # OWASP Security Headers Middleware
│   │   │   └── security.py         # Argon2 Hashing, Dual-JWT & Auth-Dependencies
│   │   ├── db/                     # Datenbank-Schicht
│   │   │   └── models/             # Rein isolierte SQLModel DB-Tabellen
│   │   │       ├── character.py    # Character-Tabelle
│   │   │       ├── item.py         # Item-Tabelle & Enums
│   │   │       ├── spell.py        # Spell-Tabelle & Link-Tabelle
│   │   │       └── user.py         # User-Tabelle
│   │   ├── schemas/                # Pydantic DTOs & API Request/Response Schemata
│   │   │   ├── character.py    
│   │   │   ├── item.py         
│   │   │   ├── spell.py        
│   │   │   └── user.py         
│   │   ├── services/               # Isolated Business Logic Layer
│   │   │   ├── auth_service.py     # Auth- & Registrierungs-Logik
│   │   │   ├── character_service.py# Charakter-CRUD & Lern-Logik
│   │   │   ├── item_service.py     # Item-Verwaltung
│   │   │   └── spell_service.py    # Spell-Verwaltung & D&D-Regelprüfungen
│   │   ├── database.py             # Async Engine & Session Dependency Injector
│   │   └── main.py                 # App-Einstiegspunkt, Middleware & Global Exception Handler
│   ├── tests/                      # Automatisierte Integrationstests
│   │   ├── conftest.py             # Pytest Fixtures (In-Memory DB & Async Client)
│   │   ├── test_auth.py            # Tests für Argon2, Dual-Tokens & Auth-Routen
│   │   ├── test_characters.py      # Tests für Charakter-Endpunkte & Regelvalidierungen
│   │   ├── test_rbac.py            # Tests für Rollenrechte (Player vs. DM)
│   │   └── test_security.py        # Tests für OWASP-Header, Rate Limiting & Healthcheck
│   ├── .env.example                # Muster-Datei für Umgebungsvariablen
│   ├── alembic.ini                 # Hauptkonfiguration für DB-Migrationen
│   └── requirements.txt            # Abgleich aller Python-Pakete (incl. asyncpg)
│
├── .gitignore                      # Ausschluss lokaler Laufzeit-Dateien & DBs
└── README.md                       # Dokumentation
```

---

## ⚡ Quickstart / Lokale Installation

### Option A: Mit Docker & PostgreSQL (Empfohlen)

#### 1. Repository klonen & Umgebungsvariablen anlegen
```bash
git clone [https://github.com/DimitrovMikh/dnd-backend.git](https://github.com/DimitrovMikh/dnd-backend.git)
cd dnd-backend

# Umgebungsvariablen aus Vorlage kopieren
cp backend/.env.example .env
```

#### 2. Stack mit Docker Compose bauen & starten
```bash
docker compose up --build -d
```

#### 3. Datenbank-Migrationen ausführen
```bash
docker compose exec backend alembic upgrade head
```
* **API Endpunkt:** `http://127.0.0.1:8000`
* **Healthcheck:** `http://127.0.0.1:8000/health`
* **Interaktive Swagger-Dokumentation:** `http://127.0.0.1:8000/docs`

---

### Option B: Manuelle lokale Installation (SQLite)

#### 1. Virtuelle Umgebung einrichten & installieren
```bash
cd dnd-backend/backend

# Virtuelle Umgebung erstellen
python -m venv .venv

# Aktivieren unter Linux / macOS:
source .venv/bin/activate

# Aktivieren unter Windows (Git Bash):
source .venv/Scripts/activate

# Aktivieren unter Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Packages installieren
pip install -r requirements.txt
```

#### 2. Konfiguration & Datenbank-Migrationen
```bash
cp .env.example .env
alembic upgrade head
```

#### 3. Server & Tests starten
```bash
# Server starten
uvicorn app.main:app --reload

# Tests ausführen
pytest
```

---

## 📌 Wichtigste API-Endpunkte

| Methode | Endpunkt | Beschreibung | Auth-Schutz / Rate Limit |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | DB-Ping (`SELECT 1`) & System-Status abrufen | ❌ Öffentlich |
| `POST` | `/auth/register` | Einen neuen Benutzer registrieren | ❌ Öffentlich |
| `POST` | `/auth/login` | Einloggen: Gibt Access Token zurück & setzt HttpOnly Cookie | ⏱️ 5 Req/Min (Rate Limited) |
| `POST` | `/auth/refresh` | Liest Refresh-Cookie aus & stellt neues Access Token aus | 🍪 Cookie |
| `GET` | `/auth/me` | Profil des aktuell eingeloggten Benutzers abrufen | 🔒 Bearer Token |
| `GET` | `/characters/` | Alle Charaktere inkl. Items & gelernter Zaubersprüche abrufen | ❌ Öffentlich |
| `GET` | `/characters/{id}` | Einzelnen Charakter anhand der ID abrufen | ❌ Öffentlich |
| `POST` | `/characters/` | Einen neuen Charakter erstellen | ❌ Öffentlich |
| `POST` | `/characters/{id}/spells/{spell_id}` | Zauberspruch für Charakter freischalten | ❌ Öffentlich |
| `GET` | `/items/` | Alle Items abrufen | ❌ Öffentlich |
| `POST` | `/items/` | Neues Item erstellen | 🔒 DM / Admin |
| `GET` | `/spells/` | Alle Zaubersprüche abrufen | ❌ Öffentlich |
| `POST` | `/spells/` | Einen neuen Zauberspruch erstellen | 🔒 DM / Admin |

---

## 🛣️ Roadmap

### Phase 1: Domain-Architektur, Service Layer & Datenmodelle 🟢 (Abgeschlossen)
<details>
  <summary>🔍 Details & umgesetzte Features anzeigen</summary>

  - [x] Modulares Grundgerüst & Eager Loading für Relationen
  - [x] **Business Logic Validation:** Level-Regelprüfung (Charakter-Level vs. Spell-Level) vor dem Lernen
  - [x] **Database Integrity:** `UniqueConstraint` auf der Link-Tabelle gegen doppelt gelernte Zauber
  - [x] **Custom Domain Exceptions:** Zentrale Fehlerbehandlung für D&D-Regelverstöße
  - [x] **Service Layer Pattern:** Isolierte Fachlogik entkoppelt von der Transport-Schicht
  - [x] **Automated Testing:** Integrationstests mit `pytest` und In-Memory Test-Datenbank
  - [x] **Alembic Database Migrations:** Schema-Änderungen sauber verwalten und versionieren
</details>

### Phase 2: Authentication, Security & RBAC 🟢 (Abgeschlossen)
<details>
  <summary>🔍 Details & umgesetzte Features anzeigen</summary>

  - [x] **Authentication & Security:** JWT-Token basierte Benutzerverwaltung & Passwort-Hashing (Argon2id)
  - [x] **Authorization Dependency:** Geschützte Routen via `get_current_user`
  - [x] **Role-Based Access Control (RBAC):** Routen-Schutz nach Benutzerrollen (z. B. nur Dungeon Master darf Spells anlegen)
</details>

---

### Phase 3: Cybersecurity Hardening, Containerisierung & Cloud 🟢 (Abgeschlossen)

<details>
  <summary>🔍 1. 🛡️ Advanced Cybersecurity & Auth Hardening 🟢 (Abgeschlossen)</summary>

- [x] **Dual-Token System (Refresh Tokens):** Implementierung von kurzlebigen Access-Tokens + langlebigen Refresh-Tokens.
- [x] **Argon2 Password Hashing:** Upgrade des Hashing-Algorithmus von Bcrypt auf **Argon2id** (OWASP-Empfehlung) via `argon2-cffi` / `pwdlib`.
- [x] **Secret Management & Config:** Auslagern aller Secrets und Schlüssel aus dem Code in `.env`-Dateien mit `pydantic-settings`.
- [x] **Rate Limiting & Brute-Force Protection:** Schutz sensitiver Endpunkte (`/auth/login`) gegen Brute-Force-Angriffe via `slowapi`.
- [x] **Security Headers & CORS Hardening:** Granulare CORS-Policies und OWASP-Sicherheitsheader.
- [x] **Passwort-Komplexitäts-Validierung:** Pydantic Field-Validator für Mindestanforderungen bei Passwörtern.
</details>

<details>
  <summary>🔍 2. 🐳 Containerisierung & Datenbank-Upgrade (Docker & PostgreSQL) 🟢 (Abgeschlossen)</summary>

- [x] **Multi-Stage Dockerfile:** Erstellung eines schlanken, gehärteten Container-Images für FastAPI (Non-Root User).
- [x] **Docker Compose:** Lokales Orchestrieren von FastAPI und PostgreSQL mit einem einzigen Befehl (`docker compose up`).
- [x] **PostgreSQL Migration:** Umstieg von SQLite auf PostgreSQL via `asyncpg` für Produktionstauglichkeit.
</details>

<details>
  <summary>🔍 3. 🔄 Automated CI/CD Pipelines (GitHub Actions) 🟢 (Abgeschlossen)</summary>

- [x] **Automatisierte Qualitätskontrolle (CI):** Linter (`Ruff`), Typ-Checks (`Mypy`) und `pytest`-Suite laufen automatisch bei jedem Pull Request.
- [x] **Continuous Delivery & Deployment (CD):** Build & Push des Docker Multi-Stage Images in die GitHub Container Registry (`ghcr.io`) inklusive automatisiertem SSH-Rollout und Container-Swap auf dem VPS bei Push auf `main`.
</details>

<details>
  <summary>🔍 4. ☁️ Production Hosting, Reverse Proxy & Security 🟢 (Abgeschlossen)</summary>

- [x] **Cloud Deployment:** VPS-Setup auf Contabo mit UFW-Firewalling, SSH-Hardening und dediziertem Non-Root Deployment User.
- [x] **Reverse Proxy & TLS:** Caddy Reverse Proxy Konfiguration für automatisches SSL/TLS-Zertifikatsmanagement via Let's Encrypt.
- [ ] **Observability:** Structured JSON-Logging (`structlog`) & Error Tracking via Sentry.
</details>

---

### Phase 4: ⚡ Realtime & Advanced D&D Features 🟡 (In Planung)
- [ ] **WebSockets Integration:** Live-Synchronisation von Würfelergebnissen und Initiative-Tracker für die gesamte Spielgruppe in Echtzeit.
- [ ] **Background Tasks & Caching:** Redis-Caching für Spieldaten und asynchrone Hintergrundaufgaben (z. B. PDF-Charakterbogen-Generierung).