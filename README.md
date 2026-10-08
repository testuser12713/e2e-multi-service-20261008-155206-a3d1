# Auftragsverarbeitung

Eine kleine Auftragsverarbeitung aus drei einzeln startbaren Diensten. Die
FastAPI-API nimmt Aufträge entgegen (Text plus gewünschte Auswertung:
Wörter zählen, häufigste Wörter, Lesezeit schätzen) und legt sie in einer
SQLite-Datei ab. Ein eigener Python-Worker-Prozess holt offene Aufträge aus
derselben Datei, berechnet das Ergebnis und schreibt es mit dem neuen Status
zurück. Ein Vite/React/TypeScript-Frontend legt Aufträge an, zeigt die Liste
mit Status und Ergebnis und aktualisiert sich automatisch alle paar Sekunden.

## Dienste und Verzeichnisse

| Dienst     | Verzeichnis  | Beschreibung                                              |
|------------|--------------|-----------------------------------------------------------|
| `api`      | `backend/`   | FastAPI-API (Python 3.12+), nimmt Aufträge an und speichert sie in SQLite |
| `worker`   | `worker/`    | Eigener Python-Prozess, holt offene Aufträge und berechnet die Ergebnisse |
| `web`      | `frontend/`  | Vite + React + TypeScript, Auftragsformular und Live-Liste |

## Tech-Stack

- **api**: Python, FastAPI, Uvicorn, `sqlite3` aus der Standardbibliothek
- **worker**: Python, `sqlite3` aus der Standardbibliothek
- **frontend**: Vite, React, TypeScript, Vitest
- **Datenhaltung**: eine SQLite-Datei (Pfad über `JOB_DB_PATH`), kein separater Datenbankserver

## Installation

Vorausgesetzt werden Python 3.12+ und Node.js (für das Frontend).

```bash
# API
cd backend
python -m pip install -r requirements.txt

# Worker
cd ../worker
python -m pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Starten (Entwicklung)

Die exakten Startbefehle, Ports und Umgebungsvariablen stehen maschinenlesbar
in [`RUN.json`](./RUN.json) im Repo-Wurzelverzeichnis; die Test- und
CI-Werkzeuge lesen diese Datei und führen genau das aus. **RUN.json ist die
maßgebliche Quelle für die Startbefehle** — für jeden Dienst steht dort ein
Eintrag mit `dir`, `start` und `env`. Die API lässt sich damit so starten:

```bash
# API (Port 8000, siehe RUN.json)
cd backend
python -m uvicorn app.main:app --port 8000
```

Der Worker und das Frontend werden auf dieselbe Weise gestartet: aus dem
jeweiligen Dienstverzeichnis mit dem in RUN.json deklarierten `start`-Befehl
(Frontend-Entwicklung üblicherweise `npm run dev`).

Der Health-Endpunkt der API ist unter `http://localhost:8000/health`
erreichbar. Das Frontend spricht die API standardmäßig unter
`http://localhost:8000` an.

## Bauen für die Produktion

Das Frontend wird als statisches Bundle gebaut:

```bash
cd frontend
npm run build
```

Das Ergebnis liegt in `frontend/dist/` und kann von einem beliebigen
statischen Server ausgeliefert werden. API und Worker sind Python-Prozesse und
benötigen keinen separaten Build-Schritt.

## Umgebungsvariablen

| Variable             | Dienst     | Standard                 | Bedeutung                                                           |
|----------------------|------------|--------------------------|---------------------------------------------------------------------|
| `JOB_DB_PATH`        | api/worker | `jobs.db`                | Pfad der SQLite-Datei; relativ wird gegen das Repo-Wurzelverzeichnis aufgelöst |
| `FRONTEND_ORIGIN`    | api        | `http://localhost:5173`  | Erlaubter CORS-Ursprung des Frontends                               |
| `POLL_INTERVAL_SECONDS` | worker  | `2`                      | Abstand zwischen zwei Abfragen des Workers in Sekunden              |
| `VITE_API_BASE_URL`  | frontend   | `http://localhost:8000`  | Basis-URL der API für das Frontend                                  |

Alle Werte sind unkritisch und haben einen funktionierenden Standard; es werden
keine Secrets benötigt.

## HTTP-API

Jeder Fehlerrumpf hat die Form `{"detail": "<Meldung>"}`.

### `GET /health`

- Antwort `200`: `{"status": "ok"}`

### `POST /api/jobs`

- Anfrage: `{"text": "<Text>", "analysis": "word_count" | "top_words" | "reading_time"}`
- Antwort `201`: ein Auftragsobjekt mit `status: "pending"`
- Ungültige Eingabe: `422` mit `{"detail": "<Meldung>"}`

### `GET /api/jobs`

- Antwort `200`: Liste aller Aufträge, neueste zuerst

### `GET /api/jobs/{id}`

- Antwort `200`: der Auftrag
- Unbekannte ID: `404` mit `{"detail": "<Meldung>"}`

### Auftragsobjekt

```json
{
  "id": 1,
  "text": "Beispieltext",
  "analysis": "word_count",
  "status": "pending",
  "result": null,
  "error": null,
  "created_at": "2025-03-14T09:41:07Z",
  "updated_at": "2025-03-14T09:41:07Z"
}
```

`Analysis` kennt genau die Werte `word_count`, `top_words`, `reading_time`;
`JobStatus` genau `pending`, `in_progress`, `done`, `failed`. Das Feld
`result` ist `null`, solange der Auftrag nicht fertig ist.

## Tests

```bash
cd backend
PYTHONPATH=. python -m pytest

cd ../worker
PYTHONPATH=. python -m pytest

cd ../frontend
npm test
```

## Funktionsumfang

- Text einreichen und eine der drei Auswertungen wählen
- Auftragsliste mit Status, Ergebnis und Fehlermeldung
- Automatische Aktualisierung der Liste
- Verarbeitung im Hintergrund durch einen separaten Worker-Prozess
- Gemeinsame, persistente SQLite-Ablage für API und Worker
