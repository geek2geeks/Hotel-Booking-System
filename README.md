# Hotel-Booking-System
A Hotel Room Booking System built with Flask, HTML, Bootstrap, and SQLAlchemy.

## Requirements

- Python 3.10 (the pinned dependency set targets this interpreter)
- pip

## Local setup (Windows PowerShell)

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe run.py
```

The app is served at <http://127.0.0.1:5000>.

## Configuration

`create_app()` loads `<repo>/instance/config.py` when it exists (the directory is
git-ignored) and then applies these environment variables:

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session/cookie signing key. Required outside local development. | development-only fallback |
| `DATABASE_URL` | SQLAlchemy database URL. | `sqlite:///<repo>/site.db` |

`site.db` and `instance/` are local files and are not committed.

## Database migrations

```powershell
$env:FLASK_APP = "run.py"
& .\.venv\Scripts\python.exe -m flask db upgrade
```

## CI

`.github/workflows/ci.yml` runs on the Owner's self-hosted Windows runner with the
labels `self-hosted`, `Windows`, `X64`, `Hotel-Booking-System`. It installs the
pinned dependencies, runs `pip check`, byte-compiles the Python sources and runs a
smoke import of the app factory. It triggers on pushes to `main` and on manual
`workflow_dispatch` only; pull requests do not trigger it because the repository is
public and the runner is self-hosted.
