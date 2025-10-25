#!/usr/bin/env python3
"""
Local development entry point for the Flask application
Uses SQLite instead of PostgreSQL for simpler local development
"""
import os
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///prediction_market.db'

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

