# 🐉 D&D Campaign Manager API

Eine asynchrone, modulare REST-API für Dungeons & Dragons Kampagnen. Das Backend ermöglicht die Verwaltung von Charakteren, Inventar-Items und Zaubersprüchen inklusive relationaler Verknüpfungen (1:N und N:M) sowie ein vollumfänglich gehärtetes **Authentifizierungs-, Autorisierungs- und Rollensystem (Argon2id, Dual-Token JWT mit HttpOnly Cookies, CORS & OWASP Hardening, Rate Limiting & RBAC)**.

---

## 🛠️ Tech Stack & Werkzeuge

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
* **ORM & Validierung:** [SQLModel](https://sqlmodel.tiangolo.com/) (Kombination aus SQLAlchemy 2.0 & Pydantic)
* **Sicherheit & Auth:** [PyJWT](https://pyjwt.readthedocs.io/) (Dual-Token: Access & Refresh JWTs) & [pwdlib](https://pwdlib.readthedocs.io/) mit `argon2-cffi` (Argon2id Password Hashing)
* **Rate Limiting & Security:** [slowapi](https://github.com/laurents/slowapi) (Brute-Force Protection) & Custom OWASP Security Headers Middleware
* **Konfiguration:** [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) (Fail-Fast `.env` Validierung)
* **Datenbank-Migrationen:** [Alembic](https://alembic.sqlalchemy.org/)
* **Asynchrone Datenbank:** [SQLite](https://www.sqlite.org/) via `aiosqlite` & `AsyncSession`
* **Automated Testing:** `pytest`, `pytest-asyncio` & `httpx`
* **ASGI Server:** Uvicorn

---

## 🚀 Key Features & Highlights

* **Gehärtete Authentifizierung (Argon2id & Dual-Tokens):**
  * **Passworthashing:** Sicheres Argon2id Hashing via modernem `pwdlib`-Framework (OWASP-Standard).
  * **Passwort-Komplexität:** Pydantic Field-Validator erzwingt Mindestlänge (9 Zeichen), Groß-/Kleinbuchstaben, Zahlen und Sonderzeichen.
  * **Access Token:** Kurzlebiges JWT (15 Minuten Gültigkeit) für API-Zugriffe im `Authorization: Bearer`-Header.
  * **Refresh Token:** Langlebiges JWT (7 Tage Gültigkeit), geschützt in einem **`HttpOnly` Cookie** (`SameSite=lax`) gegen XSS-Angriffe.
* **Brute-Force Protection & Rate Limiting:** IP-basierte Begrenzung sensitiver Endpunkte (`/auth/login` auf 5 Requests/Minute) via `slowapi`.
* **OWASP Security Headers & CORS Hardening:** Granulare CORS-Policies sowie automatische Injektion von Sicherheits-Headern (`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`).
* **Role-Based Access Control (RBAC):** Granulare Rechtevergabe über die `RoleChecker`-Dependency für geschützte Aktionen (`DUNGEON_MASTER` / `ADMIN`).
* **Clean Architecture & Service Layer:** Strikte Entkopplung von Datenbank-Tabellen (`app/db/models/`), API-DTOs (`app/schemas/`) und der Business-Logik (`app/services/`).
* **Echtzeit-Healthcheck:** Dedicated `/health`-Endpoint führt eine Live-Verbindungsprüfung (`SELECT 1`) gegen die Datenbank durch.
* **Automatisierte Test-Suite:** 100 % grün durchlaufende Integrationstests (22 Tests) mit `pytest-asyncio` über eine In-Memory Test-Datenbank.

---

## 📁 Projektstruktur

```text
DND-BACKEND/
├── .vscode/                        # VS Code Projekt-Konfiguration
│   └── settings.json
├── backend/                        # 🐍 FASTAPI BACKEND SERVICE
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
│   └── requirements.txt            # Abgleicher aller Python-Pakete
│
├── .gitignore                      # Ausschluss lokaler Laufzeit-Dateien & DBs
└── README.md                       # Dokumentation
```

---

## ⚡ Quickstart / Lokale Installation

### 1. Repository klonen & Abhängigkeiten installieren
```bash
git clone https://github.com/DimitrovMikh/dnd-backend.git
cd dnd-backend/backend

# Virtuelle Umgebung erstellen & aktivieren
python -m venv .venv
source .venv/bin/activate  # Unter Windows: .venv/Scripts/activate

# Packages installieren
pip install -r requirements.txt
```

### 2. Umgebungsvariablen konfigurieren
Erstelle eine `.env`-Datei im Ordner `backend/` basierend auf der Vorlage:

```bash
cp .env.example .env
```

```env
PROJECT_NAME="D&D Campaign Manager API"
ENVIRONMENT="development"

SECRET_KEY="HIER_DEINEN_ZUFÄLLIGEN_32_CHAR_HEX_KEY_EINTRAGEN"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

DATABASE_URL="sqlite+aiosqlite:///./dnd.db"
```

### 3. Datenbank-Migrationen ausführen
```bash
alembic upgrade head
```

### 4. Server starten
```bash
uvicorn app.main:app --reload
```
* **API Endpunkt:** `http://127.0.0.1:8000`
* **Interaktive Swagger-Dokumentation:** `http://127.0.0.1:8000/docs`

### 5. Automatisierte Tests ausführen
```bash
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

### Phase 1 & 2: Core Architecture, Auth & RBAC 🟢 (Abgeschlossen)
- [x] Modulares Grundgerüst & Eager Loading für Relationen
- [x] **Business Logic Validation:** Level-Regelprüfung (Charakter-Level vs. Spell-Level) vor dem Lernen
- [x] **Database Integrity:** `UniqueConstraint` auf der Link-Tabelle gegen doppelt gelernte Zauber
- [x] **Custom Domain Exceptions:** Zentrale Fehlerbehandlung für D&D-Regelverstöße
- [x] **Service Layer Pattern:** Isolierte Fachlogik entkoppelt von der Transport-Schicht
- [x] **Automated Testing:** Integrationstests mit `pytest` und In-Memory Test-Datenbank
- [x] **Alembic Database Migrations:** Schema-Änderungen sauber verwalten und versionieren
- [x] **Authentication & Security:** JWT-Token basierte Benutzerverwaltung & Passwort-Hashing via Bcrypt
- [x] **Authorization Dependency:** Geschützte Routen via `get_current_user`
- [x] **Role-Based Access Control (RBAC):** Routen-Schutz nach Benutzerrollen (z. B. nur Dungeon Master darf Spells anlegen)

---

### Phase 3: Cybersecurity Hardening, Containerisierung & Cloud 🟡 (In Arbeit)

#### 1. 🛡️ Advanced Cybersecurity & Auth Hardening 🟢 (Abgeschlossen)
- [x] **Dual-Token System (Refresh Tokens):** Implementierung von kurzlebigen Access-Tokens + langlebigen Refresh-Tokens inkl. Token-Blacklisting/Rotation.
- [x] **Argon2 Password Hashing:** Upgrade des Hashing-Algorithmus von Bcrypt auf **Argon2id** (OWASP-Empfehlung) via `argon2-cffi` / `pwdlib`.
- [x] **Secret Management & Config:** Auslagern aller Secrets und Schlüssel aus dem Code in `.env`-Dateien mit `pydantic-settings`.
- [x] **Rate Limiting & Brute-Force Protection:** Schutz sensitiver Endpunkte (`/auth/login`) gegen Brute-Force-Angriffe (z. B. via `slowapi` / Redis).
- [x] **Security Headers & CORS Hardening:** Granulare CORS-Policies und OWASP-Sicherheitsheader.
- [x] **Passwort-Komplexitäts-Validierung:** Pydantic Field-Validator für Mindestanforderungen bei Passwörtern.

#### 2. 🐳 Containerisierung & Datenbank-Upgrade (Docker & PostgreSQL) 🟡 (Nächster Schritt)
- [ ] **Multi-Stage Dockerfile:** Erstellung eines schlanken, gehärteten Container-Images für FastAPI.
- [ ] **Docker Compose:** Lokales Orchestrieren von FastAPI, PostgreSQL und Redis mit einem einzigen Befehl (`docker compose up`).
- [ ] **PostgreSQL Migration:** Umstieg von SQLite auf PostgreSQL für Produktionstauglichkeit.

#### 3. 🔄 Automated CI/CD Pipelines (GitHub Actions)
- [ ] **Automatisierte Qualitätskontrolle:** Linter (`Ruff`), Typ-Checks (`Mypy`) und die `pytest`-Suite laufen automatisch bei jedem Pull Request.
- [ ] **Continuous Deployment (CD):** automatisierter Build und zero-downtime Rollout auf den Cloud-Server beim Merge auf `main`.

#### 4. ☁️ Production Hosting, Reverse Proxy & Monitoring
- [ ] **Cloud Deployment:** Server-Setup auf Hetzner.
- [ ] **Reverse Proxy & SSL:** NGINX / Caddy Konfiguration für automatische HTTPS-Zertifikate via Let's Encrypt.
- [ ] **Observability:** Structured JSON-Logging (`structlog`) & Error Tracking via Sentry.

#### 5. ⚡ Realtime & Advanced D&D Features
- [ ] **WebSockets Integration:** Live-Synchronisation von Würfelergebnissen und Initiative-Tracker für die gesamte Spielgruppe in Echtzeit.
- [ ] **Background Tasks & Caching:** Redis-Caching für Spieldaten und asynchrone Hintergrundaufgaben (z. B. PDF-Charakterbogen-Generierung).
