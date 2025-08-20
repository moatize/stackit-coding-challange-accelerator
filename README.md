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
pytest -q  

## Messenger
Für das Weiterleiten der Benachrichtigungen wird **ntfy** verwendet:  
ntfy: https://ntfy.sonrio.eu -> Topic: stackit-challenge (https://ntfy.sonrio.eu/stackit-challenge)
Der ntfy-Server läuft separat auf meinem privaten VPS in einem Docker-Container.  

## Screenshots

### Warning im ntfy-Topic
![Warning](./screenshots/ntfy.png)

### Erfolgreiche Tests mit pytest
![Pytest](./screenshots/pytest.png)

### curl-Requests (forwarded / ignored)
![cURL](./screenshots/curl.png)
