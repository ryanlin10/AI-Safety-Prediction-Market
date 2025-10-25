#!/usr/bin/env python3
"""
Local development entry point for the Flask application
Uses SQLite instead of PostgreSQL for simpler local development
"""
import os
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///prediction_market.db'

# Load OpenAI API key from environment variable or .env file
# Set your key with: export OPENAI_API_KEY='your-key-here'
# Or create a .env file in the backend directory
if not os.environ.get('OPENAI_API_KEY'):
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  Warning: OpenAI API key not set. Set OPENAI_API_KEY environment variable.")
        print("   Example: export OPENAI_API_KEY='your-key-here'")

from app import create_app, db

app = create_app()

# Create tables if they don't exist
with app.app_context():
    try:
        db.create_all()
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"⚠ Error creating database tables: {e}")
        print("This might be OK if tables already exist or if models aren't fully set up")

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting Flask Backend Server")
    print("="*50)
    print(f"📍 Server: http://localhost:5001")
    print(f"🏥 Health: http://localhost:5001/health")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)

