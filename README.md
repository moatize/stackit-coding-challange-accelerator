# STACKIT Coding-Challenge – REST-Service (Flask)

Minimaler REST-Service:
- `POST /notifications` nimmt JSON entgegen
- **Warning** → via ntfy weitergeleitet
- **Info** → nicht weitergeleitet
- Speicherung: In-Memory
- Tests: pytest (5 passed)

## Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Start
python app.py  # http://127.0.0.1:5000

## Demo
curl -X POST http://127.0.0.1:5000/notifications \
  -H "Content-Type: application/json" \
  -d '{"Type":"Warning","Name":"Backup Failure","Description":"DB issue"}'

## Tests
pytest -q  # erwartet: 5 passed

## Messenger
ntfy: https://ntfy.sonrio.eu • Topic: stackit-challenge-sonrio

## Screenshots
![Warning](./screenshots/ntfy_warning.png)
![Pytest](./screenshots/pytest_green.png)

> Produktiv-Verbesserungen sind **nur als Kommentare** im Code notiert.
