# Quick Start Guide - AI Safety Prediction Market

## 🚀 First Time Setup (3 minutes)

```bash
# 1. Make scripts executable
chmod +x setup.sh start.sh stop.sh

# 2. Run setup (installs everything)
./setup.sh

# 3. Start the application
./start.sh
```

**That's it!** Open http://localhost:3000 in your browser.

---

## 📋 Daily Usage

### Start the application
```bash
./start.sh
```

### Stop the application
```bash
./stop.sh
```

### Check if running
```bash
# Frontend should be on port 3000
curl http://localhost:3000

# Backend should be on port 5001
curl http://localhost:5001/health
```

---

## 🔧 Common Commands

### Reset Database (clear all data)
```bash
cd backend
source venv/bin/activate
python seed_data.py
```

### View Logs
```bash
# Backend logs
tail -f backend/backend.log

# Frontend logs
tail -f frontend/frontend.log
```

### Update Dependencies
```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 📁 Important Files

- `setup.sh` - Initial setup script
- `start.sh` - Start both services
- `stop.sh` - Stop all services
- `SETUP.md` - Detailed setup guide
- `DEPENDENCIES.md` - Full dependency list
- `README.md` - Project overview

---

## 🌐 URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5001/api
- **Health Check:** http://localhost:5001/health
- **Markets:** http://localhost:5001/api/markets
- **Ideas:** http://localhost:5001/api/ideas
- **Agents:** http://localhost:5001/api/agents

---

## 📊 Test Data

After setup, you'll have:
- ✅ 6 AI Safety Research Ideas
- ✅ 6 Active Prediction Markets
- ✅ 3 AI Agents (Conservative, Aggressive, Balanced)

---

## ❗ Troubleshooting

### "Port already in use"
```bash
# Kill processes on ports
lsof -ti:3000 | xargs kill  # Frontend
lsof -ti:5001 | xargs kill  # Backend
```

### "Module not found" (Backend)
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Module not found" (Frontend)
```bash
cd frontend
rm -rf node_modules
npm install
```

### Start from scratch
```bash
./stop.sh
rm -rf backend/venv backend/*.db backend/*.log
rm -rf frontend/node_modules frontend/*.log
./setup.sh
./start.sh
```

---

## 🎯 What to Try

1. **Browse Markets** - Click "Markets" to see prediction questions
2. **Explore Ideas** - View the research ideas that generated markets
3. **Check Agents** - See the AI agents and their strategies
4. **Place Bets** - Try placing a bet on a market outcome
5. **View Details** - Click a market to see full details

---

## 💡 Tips

- Frontend auto-reloads when you edit files
- Backend auto-reloads in debug mode
- Database is SQLite (file: `backend/prediction_market.db`)
- Logs are useful for debugging
- Use `./stop.sh` before system shutdown

---

## 📚 Need More Help?

- **Detailed Setup:** See `SETUP.md`
- **Dependencies:** See `DEPENDENCIES.md`
- **Project Info:** See `README.md`
- **Issues:** Check logs in `backend.log` and `frontend.log`

---

**Happy Predicting! 🎲**


