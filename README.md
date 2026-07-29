# 🐉 D&D Campaign Manager API

Eine asynchrone, modulare REST-API für Dungeons & Dragons Kampagnen. Das Backend ermöglicht die Verwaltung von Charakteren, Inventar-Items und Zaubersprüchen inklusive relationaler Verknüpfungen (1:N und N:M) sowie ein vollständiges **Authentifizierungs-, Autorisierungs- und Rollensystem (JWT, Bcrypt & RBAC)**.

---

## 🛠️ Tech Stack & Werkzeuge

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
* **ORM & Validierung:** [SQLModel](https://sqlmodel.tiangolo.com/) (Kombination aus SQLAlchemy 2.0 & Pydantic)
* **Sicherheit & Auth:** [PyJWT](https://pyjwt.readthedocs.io/) (JWT Access Tokens) & [passlib](https://passlib.readthedocs.io/) mit `bcrypt==4.0.1`
* **Datenbank-Migrationen:** [Alembic](https://alembic.sqlalchemy.org/)
* **Asynchrone Datenbank:** [SQLite](https://www.sqlite.org/) via `aiosqlite` & `AsyncSession`
* **Automated Testing:** `pytest`, `pytest-asyncio` & `httpx`
* **ASGI Server:** Uvicorn

---

## 🚀 Key Features & Highlights

* **Authentifizierung & Autorisierung (AuthN/AuthZ):** Sichere Benutzerregistrierung, Login mit **JWT Access Tokens** (HS256) und Passworthashing via **Bcrypt**.
* **Role-Based Access Control (RBAC):** Granulare Rechtevergabe über die `RoleChecker`-Dependency. Bestimmte Aktionen (z. B. Erstellen neuer Items oder Zaubersprüche) sind exklusiv Nutzern mit den Rollen `DUNGEON_MASTER` oder `ADMIN` vorbehalten.
* **Geschützte Routen via Dependency Injection:** Wiederverwendbare `get_current_user`-Dependency zur Absicherung von Endpunkten über den HTTP `Authorization: Bearer <token>` Header.
* **Asynchrone Datenbank-Architektur:** Vollständig asynchrone DB-Zugriffe via `AsyncSession` für hohe Performance und Skalierbarkeit.
* **Schema-Migrationen via Alembic:** Nahtlose Versionierung von Datenbank-Strukturänderungen ohne Datenverlust, vorbereitet für Cloud-Deployments und PostgreSQL.
* **Automatisierte Test-Suite (In-Memory DB):** Vollständige Integrationstests mit `pytest-asyncio` über eine temporäre SQLite-In-Memory-Datenbank (`:memory:`) und FastAPI Dependency Overrides.
* **Eager Loading via `selectinload`:** Vermeidung von N+1-Problemen und Asynchronous Lazy Loading Errors beim Abfragen von Relationen (`items` & `spells`).
* **Service Layer & Domain Logic:** Entkopplung der Business-Logik (D&D-Regeln) vom API-Router in dedizierte Service-Module (`app/services/`).
* **Custom Domain Exceptions & Global Handler:** Strukturierte Fehlerbehandlung über eine benutzerdefinierte Exception-Hierarchie (`DNDGameException`), die von einem zentralen FastAPI Exception Handler in einheitliche JSON-Fehlermeldungen übersetzt wird.
* **Modulare Architektur (Separation of Concerns):** Strikte Trennung zwischen API-Routern (`app/api/`) und Datenmodellen (`app/models/`).
* **Circular Import Defense:** Nutzung von Pythons `TYPE_CHECKING` und entkoppelten Pydantic-Response-Schemas zur Vermeidung von zirkulären Importabhängigkeiten zur Laufzeit.

---

## 📁 Projektstruktur

```text
DND-BACKEND/
├── alembic/                    # Alembic Migrations-Ordner
│   ├── versions/               # Versionierte Migrations-Skripte
│   ├── env.py                  # Async Migrations-Konfiguration & Model-Importe
│   └── script.py.mako          # Jinja-Template für neue Migrationen
├── .gitignore                  # Ausschluss lokaler Laufzeit-Dateien & DBs
├── alembic.ini                 # Hauptkonfiguration für DB-Migrationen
├── README.md                   # Dokumentation
├── app/
│   ├── api/                    # FastAPI Router (Endpoints)
│   │   └──v1/                  # Versionierte API v1
│   │       ├── auth.py         # Auth-Router (/register, /login, /me)
│   │       ├── characters.py   # Router für Charaktere & Lern-Logik
│   │       ├── items.py        # Router für Inventar-Gegenstände
│   │       └── spells.py       # Router für Zaubersprüche
│   ├── core/                   # Anwendungsweite Kern-Komponenten
│   │   └── exceptions.py       # Custom Domain Exceptions (DNDGameException)
│   │   └── security.py         # Hashing, JWT-Generierung & get_current_user Dependency
│   ├── models/                 # SQLModel / Pydantic Datenmodelle
│   │   ├── characters.py       # Character-Modelle & Stat-Validation
│   │   ├── items.py            # Item-Modelle & Enums (ItemRarity)
│   │   └── spells.py           # Spell-Modelle, Enums & Link-Tabelle
│   │   └── users.py            # User-Modelle, Rollen-Enums & Token-DTOs
│   ├── services/               # Business Logic & Service Layer
│   │   └── spell_service.py    # D&D-Regelprüfungen (Level & Duplikate)
│   ├── database.py             # Async Engine & Session Dependency Injector
│   └── main.py                 # App-Einstiegspunkt & Global Exception Handler
└── tests/                      # Automatisierte Integrationstests
    ├── conftest.py             # Pytest Fixtures (In-Memory DB & Async Client)
    ├── test_auth.py            # Integrationstests für AuthN & AuthZ
    ├── test_characters.py      # Tests für Charakter-Endpunkte & Regelvalidierungen
    └── test_rbac.py            # Tests für Rollenrechte (Player vs. DM)
```

---

## ⚡ Quickstart / Lokale Installation

### 1. Repository klonen & Abhängigkeiten installieren
```bash
git clone https://github.com/DimitrovMikh/dnd-backend.git
cd dnd-backend

# Virtuelle Umgebung erstellen & aktivieren
python -m venv .venv
source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate

# Packages installieren
pip install fastapi sqlmodel uvicorn aiosqlite alembic pytest pytest-asyncio httpx pyjwt passlib "bcrypt==4.0.1"
```

### 2. Datenbank-Migrationen ausführen
```bash
alembic upgrade head
```

### 3. Server starten
```bash
uvicorn app.main:app --reload
```
* **API Endpunkt:** `[http://127.0.0.1:8000](http://127.0.0.1:8000)`
* **Interaktive Swagger-Dokumentation:** `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`

### 4. Automatisierte Tests ausführen
```bash
pytest
```

---

## 📌 Wichtigste API-Endpunkte

| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Einen neuen Benutzer registrieren | ❌ Öffentlich |
| `POST` | `/auth/login` | Benutzer einloggen & JWT Access Token erhalten | ❌ Öffentlich |
| `GET` | `/auth/me` | Profil des aktuell eingeloggten Benutzers abrufen | 🔒 Bearer Token |
| `GET` | `/characters/` | Alle Charaktere inkl. Items & gelernter Zaubersprüche abrufen | ❌ Öffentlich |
| `GET` | `/characters/{id}` | Einzelnen Charakter anhand der ID abrufen | ❌ Öffentlich |
| `POST` | `/characters/` | Einen neuen Charakter erstellen | ❌ Öffentlich |
| `POST` | `/characters/{id}/spells/{spell_id}` | Zauberspruch für Charakter freischalten (N:M Link) | ❌ Öffentlich |
| `GET` | `/items/` | Alle Items abrufen | ❌ Öffentlich |
| `POST` | `/items/` | Neues Item erstellen |🔒 DM / Admin |
| `GET` | `/spells/` | Alle Zaubersprüche abrufen | ❌ Öffentlich |
| `POST` | `/spells/` | Neuen Zauberspruch erstellen |🔒 DM / Admin |

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

### Phase 3: Cloud, Security Hardening & Advanced Backend Architecture 🟡 (Geplant)

#### 1. 🛡️ Advanced Cybersecurity & Auth Hardening
- [ ] **Dual-Token System (Refresh Tokens):** Implementierung von kurzlebigen Access-Tokens + langlebigen Refresh-Tokens inkl. Token-Blacklisting/Rotation.
- [ ] **Argon2 Password Hashing:** Upgrade des Hashing-Algorithmus von Bcrypt auf **Argon2id** (OWASP-Empfehlung) via `argon2-cffi` / `pwdlib`.
- [ ] **Secret Management & Config:** Auslagern aller Secrets und Schlüssel aus dem Code in `.env`-Dateien mit `pydantic-settings`.
- [ ] **Rate Limiting & Brute-Force Protection:** Schutz sensitiver Endpunkte (`/auth/login`) gegen Brute-Force-Angriffe (z. B. via `slowapi` / Redis).
- [ ] **Security Headers & CORS Hardening:** Granulare CORS-Policies und OWASP-Sicherheitsheader.

#### 2. 🐳 Containerisierung & Datenbank-Upgrade (Docker & PostgreSQL)
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