# 🐉 D&D Campaign Manager API

Eine asynchrone, modulare REST-API für Dungeons & Dragons Kampagnen. Das Backend ermöglicht die Verwaltung von Charakteren, Inventar-Items und Zaubersprüchen inklusive relationaler Verknüpfungen (1:N und N:M) über ein asynchrones ORM.

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
    └── test_characters.py      # Tests für Charakter-Endpunkte & Regelvalidierungen
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
| `POST` | `/auth/register` | Einen neuen Benutzer registrieren | ❌ |
| `POST` | `/auth/login` | Benutzer einloggen & JWT Access Token erhalten | ❌ |
| `GET` | `/auth/me` | Profil des aktuell eingeloggten Benutzers abrufen | 🔒 Bearer Token |
| `GET` | `/characters/` | Alle Charaktere inkl. Items & gelernter Zaubersprüche abrufen | ❌ |
| `GET` | `/characters/{id}` | Einzelnen Charakter anhand der ID abrufen | ❌ |
| `POST` | `/characters/` | Einen neuen Charakter erstellen | ❌ |
| `POST` | `/characters/{id}/spells/{spell_id}` | Zauberspruch für Charakter freischalten (N:M Link) | ❌ |
| `GET` | `/items/` | Alle Items abrufen | ❌ |
| `POST` | `/items/` | Neues Item erstellen | ❌ |
| `GET` | `/spells/` | Alle Zaubersprüche abrufen | ❌ |
| `POST` | `/spells/` | Neuen Zauberspruch erstellen | ❌ |

---

## 🛣️ Roadmap / Anstehende Erweiterungen (Phase 2)

- [x] Modulares Grundgerüst & Eager Loading für Relationen
- [x] **Business Logic Validation:** Level-Regelprüfung (Charakter-Level vs. Spell-Level) vor dem Lernen
- [x] **Database Integrity:** `UniqueConstraint` auf der Link-Tabelle gegen doppelt gelernte Zauber
- [x] **Custom Domain Exceptions:** Zentrale Fehlerbehandlung für D&D-Regelverstöße
- [x] **Service Layer Pattern:** Isolierte Fachlogik entkoppelt von der Transport-Schicht
- [x] **Automated Testing:** Integrationstests mit `pytest` und In-Memory Test-Datenbank
- [x] **Alembic Database Migrations:** Schema-Änderungen sauber verwalten und versionieren
- [x] **Authentication & Security:** JWT-Token basierte Benutzerverwaltung & Passwort-Hashing via Bcrypt
- [x] **Authorization Dependency:** Geschützte Routen via `get_current_user`
- [ ] **Role-Based Access Control (RBAC):** Routen-Schutz nach Benutzerrollen (z. B. nur Dungeon Master darf Spells anlegen)