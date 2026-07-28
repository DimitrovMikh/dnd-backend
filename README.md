# 🐉 D&D Campaign Manager API

Eine asynchrone, modulare REST-API für Dungeons & Dragons Kampagnen. Das Backend ermöglicht die Verwaltung von Charakteren, Inventar-Items und Zaubersprüchen inklusive relationaler Verknüpfungen (1:N und N:M) über ein asynchrones ORM.

---

## 🛠️ Tech Stack & Werkzeuge

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
* **ORM & Validierung:** [SQLModel](https://sqlmodel.tiangolo.com/) (Kombination aus SQLAlchemy 2.0 & Pydantic)
* **Datenbank-Migrationen:** [Alembic](https://alembic.sqlalchemy.org/)
* **Asynchrone Datenbank:** [SQLite](https://www.sqlite.org/) via `aiosqlite` & `AsyncSession`
* **Automated Testing:** `pytest`, `pytest-asyncio` & `httpx`
* **ASGI Server:** Uvicorn

---

## 🚀 Key Features & Highlights

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
├── alembic/                 # Alembic Migrations-Ordner
│   ├── versions/            # Versionierte Migrations-Skripte
│   ├── env.py               # Async Migrations-Konfiguration & Model-Importe
│   └── script.py.mako       # Jinja-Template für neue Migrationen
├── .gitignore               # Ausschluss lokaler Laufzeit-Dateien & DBs
├── alembic.ini              # Hauptkonfiguration für DB-Migrationen
├── README.md                # Dokumentation
├── app/
│   ├── api/                 # FastAPI Router (Endpoints)
│   │   ├── characters.py    # Router für Charaktere & Lern-Logik
│   │   ├── items.py         # Router für Inventar-Gegenstände
│   │   └── spells.py        # Router für Zaubersprüche
│   ├── core/                # Anwendungsweite Kern-Komponenten
│   │   └── exceptions.py    # Custom Domain Exceptions (DNDGameException)
│   ├── models/              # SQLModel / Pydantic Datenmodelle
│   │   ├── characters.py    # Character-Modelle & Stat-Validation
│   │   ├── items.py         # Item-Modelle & Enums (ItemRarity)
│   │   └── spells.py        # Spell-Modelle, Enums & Link-Tabelle
│   ├── services/            # Business Logic & Service Layer
│   │   └── spell_service.py # D&D-Regelprüfungen (Level & Duplikate)
│   ├── database.py          # Async Engine & Session Dependency Injector
│   └── main.py              # App-Einstiegspunkt & Global Exception Handler
└── tests/                   # Automatisierte Integrationstests
    ├── conftest.py          # Pytest Fixtures (In-Memory DB & Async Client)
    └── test_characters.py   # Tests für Charakter-Endpunkte & Regelvalidierungen
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
pip install fastapi sqlmodel uvicorn aiosqlite alembic pytest pytest-asyncio httpx
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
| `GET` | `/characters/` | Alle Charaktere inkl. Items & gelernter Zaubersprüche abrufen |
| `GET` | `/characters/{id}` | Einzelnen Charakter anhand der ID abrufen |
| `POST` | `/characters/` | Einen neuen Charakter erstellen |
| `POST` | `/characters/{id}/spells/{spell_id}` | Zauberspruch für Charakter freischalten (N:M Link) |
| `GET` | `/items/` | Alle Items abrufen |
| `POST` | `/items/` | Neues Item erstellen |
| `GET` | `/spells/` | Alle Zaubersprüche abrufen |
| `POST` | `/spells/` | Neuen Zauberspruch erstellen |

---

## 🛣️ Roadmap / Anstehende Erweiterungen (Phase 2)

- [x] Modulares Grundgerüst & Eager Loading für Relationen
- [x] **Business Logic Validation:** Level-Regelprüfung (Charakter-Level vs. Spell-Level) vor dem Lernen
- [x] **Database Integrity:** `UniqueConstraint` auf der Link-Tabelle gegen doppelt gelernte Zauber
- [x] **Custom Domain Exceptions:** Zentrale Fehlerbehandlung für D&D-Regelverstöße
- [x] **Service Layer Pattern:** Isolierte Fachlogik entkoppelt von der Transport-Schicht
- [x] **Automated Testing:** Integrationstests mit `pytest` und In-Memory Test-Datenbank
- [x] **Alembic Database Migrations:** Schema-Änderungen sauber verwalten und versionieren
- [ ] **Authentication & Security:** JWT-Token basierte Benutzerverwaltung