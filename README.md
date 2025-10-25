# AI Safety Prediction Market

A prediction market platform for niche AI-safety questions with automated LLM agent market makers and researchers that automatically test technical hypotheses.

## 🎯 Overview

This platform combines prediction markets with automated research validation:

1. **Scrapes** research sources (arXiv, conferences) for candidate ideas
2. **Auto-generates** prediction markets from testable claims
3. **LLM agents** place initial bets with reasoning
4. **Automated researchers** execute experiments to validate claims

## 🏗️ Architecture

### Tech Stack

- **Backend**: Python, Flask, PostgreSQL (pgvector), Redis, Celery
- **Frontend**: React, TypeScript, React Query, Recharts
- **ML/NLP**: Hugging Face Transformers, Sentence Transformers, OpenAI API
- **Infrastructure**: Docker, Docker Compose

### Components

```
├── backend/
│   ├── app/                    # Flask application
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routes/            # API endpoints
│   │   └── services/          # Business logic
│   ├── scraper/               # arXiv scraper
│   ├── agents/                # LLM agents
│   └── experiments/           # Experiment runners
├── frontend/                  # React application
└── docker-compose.yml         # Container orchestration
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (for LLM agents)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/ryanlin10/AI-Safety-Prediction-Market.git
cd AI-Safety-Prediction-Market
```

2. **Configure environment**
```bash
cd backend
cp env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Start services**
```bash
docker-compose up --build
```

This will start:
- PostgreSQL with pgvector (port 5432)
- Redis (port 6379)
- Flask API (port 5000)
- Celery worker
- React frontend (port 3000)

4. **Initialize database**
```bash
# In a new terminal
docker-compose exec backend flask db upgrade
```

5. **Seed initial data**
```bash
docker-compose exec backend python scraper/run.py --seed
```

6. **Run the scraper**
```bash
docker-compose exec backend python scraper/run.py
```

7. **Access the application**
- Frontend: http://localhost:3000
- API: http://localhost:5000

## 📊 Database Schema

### Core Tables

- **users**: User accounts
- **sources**: Research paper sources (arXiv, conferences)
- **ideas**: Extracted research ideas with embeddings
- **markets**: Prediction markets with resolution rules
- **bets**: User and agent bets on markets
- **agents**: LLM agents (bettors and researchers)
- **experiments**: Automated experiment runs

## 🤖 Agent System

### Bettor Agents

LLM-based agents that:
- Analyze research claims
- Search for similar historical results
- Estimate probabilities
- Place bets with rationale

### Researcher Agents

Automated agents that:
- Execute experiments based on market resolution rules
- Run fine-tuning tests on small models
- Report results with metrics and logs

## 🔬 Experiment System

Experiments validate market claims through:

1. **Configuration**: Dataset, model, metrics, thresholds
2. **Execution**: Baseline evaluation → Fine-tuning → Re-evaluation
3. **Results**: Pass/fail determination with detailed logs

Example experiment config:
```json
{
  "dataset": "tiny-sst2-subset",
  "metric": "accuracy",
  "baseline_model": "distilbert-base-uncased",
  "fine_tune_recipe": {"epochs": 1, "lr": 5e-5},
  "success_threshold_delta": 0.03
}
```

## 📡 API Endpoints

### Ideas
- `GET /api/ideas` - List ideas with search
- `GET /api/ideas/{id}` - Get specific idea
- `POST /api/ideas/search/semantic` - Semantic search

### Markets
- `GET /api/markets` - List markets
- `GET /api/markets/{id}` - Get market details
- `POST /api/markets` - Create market
- `POST /api/markets/{id}/bets` - Place bet

### Agents
- `GET /api/agents` - List agents
- `POST /api/agents/{id}/place_initial_bet` - Agent places bet

### Experiments
- `POST /api/markets/{id}/run_experiment` - Run experiment
- `GET /api/experiments/{id}/status` - Check experiment status

## 🎮 Demo Workflow

1. **Scrape Papers**: Run scraper to fetch recent AI safety papers from arXiv
2. **View Ideas**: Browse extracted research ideas with testable claims
3. **Create Markets**: Auto-generate prediction markets from high-confidence claims
4. **Agent Bets**: Have bettor agents analyze and place initial bets
5. **Run Experiments**: Execute automated experiments to validate claims
6. **View Results**: See experiment outcomes and market resolution

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run Flask dev server
flask run

# Run Celery worker
celery -A app.celery worker --loglevel=info

# Run tests
pytest
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm run build
```

## 🔐 Security & Safety

- **Content filtering**: Blocks harmful or non-evaluable claims
- **Rate limiting**: Caps agent stake amounts
- **Human review**: Required for sensitive markets
- **Audit logs**: All LLM outputs logged for review
- **Sandboxing**: Experiments run in isolated containers

## 📈 Scaling Considerations

- Use GPU instances for experiment execution
- Implement caching for embedding searches
- Add horizontal scaling for Celery workers
- Use CDN for frontend assets
- Implement rate limiting on API endpoints

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 Configuration

Key environment variables:

- `OPENAI_API_KEY`: OpenAI API key for LLM agents
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `AGENT_MAX_STAKE`: Maximum stake per agent bet
- `EXPERIMENT_TIMEOUT_MINUTES`: Max experiment runtime

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔮 Future Enhancements

- [ ] Human-in-the-loop market resolution UI
- [ ] Continuous agent calibration monitoring
- [ ] Auto-resolution with verification pipeline
- [ ] Expand to Semantic Scholar, OpenReview
- [ ] Real-time WebSocket updates
- [ ] Advanced market analytics dashboard
- [ ] Multi-model ensemble experiments
- [ ] Reputation system for agents

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/ryanlin10/AI-Safety-Prediction-Market/issues)
- Documentation: See `/docs` folder

## 🙏 Acknowledgments

Built for the OAISI Hackathon to advance AI safety research through prediction markets and automated validation.

---

**Note**: This is a prototype for demonstration purposes. Use appropriate safety measures and human oversight before deploying to production.

