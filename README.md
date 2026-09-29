# Credit Card Payment System

Full Stack Junior Application Task implementation based on the supplied requirements.

## Architecture

React + Tailwind CSS → Django REST API → MySQL
                         ↓
                   FastAPI Payment Service

Django handles registration, JWT login, cards, transaction history and admin operations. FastAPI simulates payment success/failure. Django calls FastAPI over the Docker network and stores the returned final status.

## Services

- Frontend: http://localhost:3000
- Django API: http://localhost:8000/api/
- Django Swagger: http://localhost:8000/api/docs/
- Django Admin: http://localhost:8000/admin/
- FastAPI Swagger: http://localhost:8001/docs
- MySQL: localhost:3306

## Run with Docker

1. Install Docker Desktop.
2. From this folder run:

```bash
docker compose up --build
```

3. Open http://localhost:3000.
4. Register a normal user.
5. Add a test card such as `4111111111111111`. The backend stores only a masked value and last four digits; it does not store the actual number or CVV.
6. Make a payment. Django creates `PENDING`, calls FastAPI, then updates the transaction to `SUCCESS` or `FAILED`.

Admin login:
- Username: `admin`
- Password: `Admin@12345`

Change these credentials before any real deployment.

## API connection flow

`POST /api/payments/` → Django validates user/card → creates PENDING transaction → POST `http://payment-service:8000/simulate-payment` → FastAPI returns status → Django updates transaction → React displays result.

## Security notes

This is a development/demo payment simulator. Do not connect it to real card processing as-is. Never store CVV or full card numbers. Production payment handling should use a PCI-compliant payment provider/tokenization.
