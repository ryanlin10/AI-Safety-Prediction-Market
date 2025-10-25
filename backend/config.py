import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/prediction_market')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 1)))
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # Scraper Configuration
    ARXIV_MAX_RESULTS = int(os.environ.get('ARXIV_MAX_RESULTS', 50))
    SCRAPER_INTERVAL_HOURS = int(os.environ.get('SCRAPER_INTERVAL_HOURS', 24))
    
    # Agent Configuration
    AGENT_MAX_STAKE = float(os.environ.get('AGENT_MAX_STAKE', 100))
    AGENT_CONFIDENCE_THRESHOLD = float(os.environ.get('AGENT_CONFIDENCE_THRESHOLD', 0.7))
    
    # Experiment Configuration
    EXPERIMENT_TIMEOUT_MINUTES = int(os.environ.get('EXPERIMENT_TIMEOUT_MINUTES', 10))
    EXPERIMENT_MAX_EPOCHS = int(os.environ.get('EXPERIMENT_MAX_EPOCHS', 2))
    
    # Sentry Configuration
    SENTRY_DSN = os.environ.get('SENTRY_DSN', '')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/prediction_market_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

