# AI Safety Prediction Market - Setup Guide

A prediction market platform for AI safety research questions with automated LLM agents.

## 📋 Prerequisites

### Backend Requirements
- **Python 3.10+** (tested with 3.13)
- **pip** (Python package manager)

### Frontend Requirements
- **Node.js 16+** (tested with latest LTS)
- **npm** (comes with Node.js)

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
# Make scripts executable
chmod +x setup.sh start.sh stop.sh

# Run setup (installs all dependencies)
./setup.sh

# Start both frontend and backend
./start.sh

# When done, stop all services
./stop.sh
```

### Manual Setup

#### 1. Backend Setup

```bash
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed database with test data
python seed_data.py

# Start backend server
python run_local.py
```

Backend will run on: `http://localhost:5001`

#### 2. Frontend Setup

```bash
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm start
```

Frontend will run on: `http://localhost:3000`

## 📦 Dependencies

### Backend (Python - requirements.txt)
- **Flask 3.0+** - Web framework
- **SQLAlchemy** - Database ORM
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-JWT-Extended** - Authentication
- **OpenAI** - LLM integration
- **Celery** - Task queue (optional)
- **Redis** - Caching/queue backend (optional)
- See `backend/requirements.txt` for full list

### Frontend (Node.js - package.json)
- **React 19** - UI framework
- **TypeScript** - Type safety
- **React Router** - Navigation
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **TanStack Query** - Data fetching
- See `frontend/package.json` for full list

## 🗄️ Database

The application uses **SQLite** for local development (stored in `backend/prediction_market.db`).

### Resetting Database

```bash
cd backend
source venv/bin/activate
python seed_data.py  # Drops and recreates all tables with test data
```

## 🔧 Configuration

### Backend Configuration

Create `backend/.env` (optional):
```bash
FLASK_ENV=development
OPENAI_API_KEY=your_key_here  # Optional: for LLM features
DATABASE_URL=sqlite:///prediction_market.db
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:5001` for the API.

To change this, update `frontend/src/api/client.ts`:
```typescript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';
```

## 🧪 Test Data

The seed script creates:
- **6 Research Ideas** - AI safety topics from areas like debate, interpretability, constitutional AI
- **6 Prediction Markets** - Active markets for betting on research outcomes
- **3 AI Agents** - Automated agents with different betting strategies

## 📁 Project Structure

```
OAISI_Hackathon/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   └── services/        # Business logic
│   ├── venv/                # Python virtual environment
│   ├── requirements.txt     # Python dependencies
│   ├── run_local.py        # Development server
│   └── seed_data.py        # Database seed script
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   └── api/            # API client
│   ├── node_modules/        # Node.js dependencies
│   ├── package.json        # Node.js dependencies
│   └── package-lock.json   # Locked versions
├── setup.sh                 # Automated setup script
├── start.sh                 # Start both services
├── stop.sh                  # Stop both services
└── SETUP.md                # This file
```

## 🌐 API Endpoints

- `GET /health` - Health check
- `GET /api/markets` - List prediction markets
- `GET /api/markets/:id` - Get market details
- `GET /api/ideas` - List research ideas
- `GET /api/agents` - List AI agents
- `POST /api/markets` - Create new market
- `POST /api/markets/:id/bets` - Place a bet

## 🐛 Troubleshooting

### Backend Issues

**Port 5000 already in use:**
- macOS AirPlay uses port 5000
- Backend is configured to use port 5001 instead
- Or disable AirPlay: System Settings → General → AirDrop & Handoff

**Module not found errors:**
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Database errors:**
- Reset database: `python seed_data.py`
- Delete `prediction_market.db` and recreate

### Frontend Issues

**npm install fails:**
- Clear cache: `npm cache clean --force`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

**Port 3000 already in use:**
- Kill existing process: `lsof -ti:3000 | xargs kill`
- Or use different port: `PORT=3001 npm start`

## 📝 Development Notes

- Backend uses SQLite (not PostgreSQL) for simplicity
- Some ML features (spacy, transformers) are disabled due to Python 3.13 compatibility
- Frontend hot-reloads on file changes
- Backend auto-reloads in debug mode
- Logs are stored in `backend.log` and `frontend.log` when using start script

## 🔐 Security Notes

- This is a **development setup** - not production-ready
- JWT secrets are hardcoded - change for production
- No authentication implemented yet
- CORS is wide open for development

## 📞 Support

For issues or questions:
1. Check logs: `backend/backend.log` or `frontend/frontend.log`
2. Verify services are running: `lsof -i :3000` and `lsof -i :5001`
3. Reset everything: `./stop.sh && ./setup.sh && ./start.sh`

