# Bus AgentUB Backend

FastAPI-based backend for the Bus AgentUB booking system with real-time tracking and Google Maps integration.

## Quick Start

### Prerequisites
- Python 3.8+
- SQLite (development) or PostgreSQL (production)
- Google Maps API key (optional)

### Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see configuration guide for details)
cp .env.example .env

# Initialize database
python -m app.database.init_db

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at `http://localhost:8000`

## Documentation

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Detailed Configuration**: See `docs/BACKEND_CONFIG.md`
- **API Reference**: See `docs/API_REFERENCE.md`
- **Authentication**: See `docs/AUTHENTICATION.md`
- **Database Schema**: See `docs/DATABASE.md`

## Key Features

- JWT-based authentication with role-based access
- Real-time WebSocket updates for bookings and bus locations
- Complete booking workflow (request → confirmation → ticket)
- Google Maps integration for routing and ETAs
- Owner dashboard with analytics
- Supervisor tools for booking management

## Development

```bash
# Format code
black .
isort .

# Run tests
pytest

# Create database migration
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Deployment

For production setup, see `docs/DEPLOYMENT.md`

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── database/         # DB configuration
│   └── main.py          # FastAPI app
├── tests/               # Test suite
├── requirements.txt     # Dependencies
└── .env.example        # Environment template
```
