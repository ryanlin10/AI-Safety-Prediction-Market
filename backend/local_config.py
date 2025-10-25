import os
from datetime import timedelta

class LocalConfig:
    """Local development configuration without external services"""
    SECRET_KEY = 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///prediction_market.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Celery Configuration (disabled for local dev)
    CELERY_BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # Scraper Configuration
    ARXIV_MAX_RESULTS = 50
    SCRAPER_INTERVAL_HOURS = 24
    
    # Agent Configuration
    AGENT_MAX_STAKE = 100
    AGENT_CONFIDENCE_THRESHOLD = 0.7
    
    # Experiment Configuration
    EXPERIMENT_TIMEOUT_MINUTES = 10
    EXPERIMENT_MAX_EPOCHS = 2
    
    # Sentry Configuration
    SENTRY_DSN = ''
    
    DEBUG = True
    TESTING = False

