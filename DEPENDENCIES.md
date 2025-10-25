# Project Dependencies

Complete list of dependencies for both frontend and backend.

## Backend Dependencies (Python)

**Location:** `backend/requirements.txt`

### Core Framework
- `Flask==3.0.0` - Web framework
- `Flask-SQLAlchemy==3.1.1` - SQLAlchemy integration for Flask
- `Flask-Migrate==4.0.5` - Database migrations
- `Flask-CORS==4.0.0` - Cross-Origin Resource Sharing support
- `Flask-JWT-Extended==4.5.3` - JWT authentication

### Database
- `psycopg2-binary==2.9.9` - PostgreSQL adapter (optional, for production)
- `pgvector==0.2.4` - Vector similarity search (optional, for production)
- `redis==5.0.1` - Redis client (optional, for caching/celery)

### Task Queue (Optional)
- `celery==5.3.4` - Distributed task queue
- `celery[redis]==5.3.4` - Redis support for Celery

### Web Scraping & Parsing
- `requests==2.31.0` - HTTP library
- `aiohttp==3.9.1` - Async HTTP client
- `beautifulsoup4==4.12.2` - HTML/XML parser
- `feedparser==6.0.10` - RSS/Atom feed parser
- `arxiv==2.1.0` - arXiv API client

### AI/ML (Core)
- `openai==1.6.1` - OpenAI API client for LLM agents

### AI/ML (Optional - disabled due to Python 3.13 compatibility)
- `sentence-transformers==2.2.2` - Sentence embeddings
- `spacy==3.7.2` - NLP library
- `transformers==4.36.2` - Hugging Face transformers
- `torch==2.1.2` - PyTorch
- `datasets==2.16.1` - Datasets library

### Utilities
- `python-dotenv==1.0.0` - Environment variable management
- `gunicorn==21.2.0` - WSGI HTTP server
- `pydantic==2.5.3` - Data validation

### Monitoring
- `sentry-sdk[flask]==1.39.2` - Error tracking

### Testing
- `pytest==7.4.3` - Testing framework
- `pytest-flask==1.3.0` - Flask testing utilities

## Frontend Dependencies (Node.js)

**Location:** `frontend/package.json`

### Core Framework
- `react@^19.2.0` - React library
- `react-dom@^19.2.0` - React DOM rendering
- `react-scripts@5.0.1` - Create React App scripts
- `typescript@^4.9.5` - TypeScript language

### Routing
- `react-router-dom@^7.9.4` - React routing

### HTTP & State Management
- `axios@^1.12.2` - HTTP client
- `@tanstack/react-query@^5.90.5` - Data fetching and caching

### UI & Visualization
- `recharts@^3.3.0` - Chart library

### Testing
- `@testing-library/react@^16.3.0` - React testing utilities
- `@testing-library/jest-dom@^6.9.1` - Jest DOM matchers
- `@testing-library/user-event@^13.5.0` - User event simulation
- `@testing-library/dom@^10.4.1` - DOM testing library

### TypeScript Type Definitions
- `@types/jest@^27.5.2` - Jest types
- `@types/node@^16.18.126` - Node.js types
- `@types/react@^19.2.2` - React types
- `@types/react-dom@^19.2.2` - React DOM types
- `@types/react-router-dom@^5.3.3` - React Router types

### Utilities
- `web-vitals@^2.1.4` - Web performance metrics

## Development Environment Setup

### Backend Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Virtual environment location:** `backend/venv/`

### Frontend Node Modules

```bash
cd frontend
npm install
```

**Node modules location:** `frontend/node_modules/`

## Dependency Management

### Backend (Python)

**Update dependencies:**
```bash
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

**Add new dependency:**
```bash
pip install package_name
pip freeze > requirements.txt  # Update requirements file
```

**Check for updates:**
```bash
pip list --outdated
```

### Frontend (Node.js)

**Update dependencies:**
```bash
cd frontend
npm update
```

**Add new dependency:**
```bash
npm install package_name
# package.json and package-lock.json are automatically updated
```

**Check for updates:**
```bash
npm outdated
```

**Audit security:**
```bash
npm audit
npm audit fix  # Automatically fix vulnerabilities
```

## Platform-Specific Notes

### macOS
- Python 3.13 has compatibility issues with some ML libraries (spacy, transformers)
- Consider using Python 3.10 or 3.11 for full ML features
- Port 5000 is used by AirPlay Receiver - backend uses port 5001 instead

### Windows
- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- May need to install Visual C++ Build Tools for some Python packages
- Use Git Bash or WSL for shell scripts

### Linux
- May need to install system packages: `python3-dev`, `libpq-dev`, `build-essential`
- Use package manager (apt, yum) to install Node.js and Python

## Production Dependencies

For production deployment, additional dependencies may be needed:

### Backend
- PostgreSQL database (instead of SQLite)
- Redis server (for caching and Celery)
- Nginx or Apache (reverse proxy)
- Gunicorn or uWSGI (WSGI server)

### Frontend
- Build: `npm run build`
- Serve static files via nginx or CDN
- Environment-specific configuration

### Infrastructure
- Docker & Docker Compose
- Kubernetes (for scaling)
- Load balancer
- Monitoring tools (Prometheus, Grafana)

## Version Constraints

### Backend
- **Python:** 3.10+ (3.13 has ML library compatibility issues)
- **pip:** Latest version recommended

### Frontend
- **Node.js:** 16+ (LTS recommended)
- **npm:** 7+ (comes with Node.js)

## Troubleshooting Dependencies

### Backend Issues

**Import errors:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

**Compilation errors:**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev libpq-dev build-essential

# Install system dependencies (macOS)
brew install postgresql
```

### Frontend Issues

**Module not found:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Version conflicts:**
```bash
# Use exact versions from lock file
npm ci
```

**Build errors:**
```bash
# Clear cache
npm cache clean --force
npm install
```

## Security Considerations

- Regularly update dependencies to patch vulnerabilities
- Run `npm audit` for frontend security checks
- Use virtual environments to isolate Python dependencies
- Never commit `.env` files or API keys
- Use `pip-audit` or `safety` for Python security checks

## CI/CD Integration

Dependencies can be cached in CI/CD pipelines:

**GitHub Actions (example):**
```yaml
- uses: actions/cache@v2
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

- uses: actions/cache@v2
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

