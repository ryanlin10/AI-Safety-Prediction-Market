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
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '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')
    
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

