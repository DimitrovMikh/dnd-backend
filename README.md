# 🐉 D&D Campaign Manager API

Eine asynchrone, modulare REST-API für Dungeons & Dragons Kampagnen. Das Backend ermöglicht die Verwaltung von Charakteren, Inventar-Items und Zaubersprüchen inklusive relationaler Verknüpfungen (1:N und N:M) über ein asynchrones ORM.

---

## 🛠️ Tech Stack & Werkzeuge

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
* **ORM & Validierung:** [SQLModel](https://sqlmodel.tiangolo.com/) (Kombination aus SQLAlchemy 2.0 & Pydantic)
* **Asynchrone Datenbank:** [SQLite](https://www.sqlite.org/) via `aiosqlite` & `AsyncSession`
* **ASGI Server:** Uvicorn

---

## 🚀 Key Features & Highlights

* **Asynchrone Datenbank-Architektur:** Vollständig asynchrone DB-Zugriffe via `AsyncSession` für hohe Performance und Skalierbarkeit.
* **Eager Loading via `selectinload`:** Vermeidung von N+1-Problemen und Asynchronous Lazy Loading Errors beim Abfragen von Relationen (`items` & `spells`).
* **Modulare Architektur (Separation of Concerns):** Strikte Trennung zwischen API-Routern (`app/api/`) und Datenmodellen (`app/models/`).
* **Circular Import Defense:** Nutzung von Pythons `TYPE_CHECKING` und entkoppelten Pydantic-Response-Schemas zur Vermeidung von zirkulären Importabhängigkeiten zur Laufzeit.

---

## 📁 Projektstruktur

```text
DND-BACKEND/
├── .gitignore              # Ausschluss lokaler Laufzeit-Dateien & DBs
├── README.md               # Dokumentation
└── app/
    ├── api/                # FastAPI Router (Endpoints)
    │   ├── characters.py   # Router für Charaktere & Lern-Logik
    │   ├── items.py        # Router für Inventar-Gegenstände
    │   └── spells.py       # Router für Zaubersprüche
    ├── models/             # SQLModel / Pydantic Datenmodelle
    │   ├── characters.py   # Character-Modelle & Stat-Validation
    │   ├── items.py        # Item-Modelle & Enums (ItemRarity)
    │   └── spells.py       # Spell-Modelle, Enums & Link-Tabelle
    ├── database.py         # Async Engine & Session Dependency Injector
    └── main.py             # App-Einstiegspunkt & Lifespan Handler
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
pip install fastapi sqlmodel uvicorn aiosqlite
```

### 2. Server starten
```bash
uvicorn app.main:app --reload
```
* **API Endpunkt:** `[http://127.0.0.1:8000](http://127.0.0.1:8000)`
* **Interaktive Swagger-Dokumentation:** `[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)`

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
- [ ] **Business Logic Validation:** Level-Regelprüfung (Charakter-Level vs. Spell-Level) vor dem Lernen
- [ ] **Database Integrity:** `UniqueConstraint` auf der Link-Tabelle gegen doppelt gelernte Zauber
- [ ] **Custom Domain Exceptions:** Zentrale Fehlerbehandlung für D&D-Regelverstöße
- [ ] **Automated Testing:** Integrationstests mit `pytest` und In-Memory Test-Datenbank