#!/usr/bin/env python3
"""
Migration script to add bid_price and ask_price columns to markets table
"""
import os
import sys

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for local development
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///prediction_market.db'

from app import create_app, db

def run_migration():
    """Add bid_price and ask_price columns to markets table"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Running migration: add bid_price and ask_price columns")
        
        try:
            # Check if columns already exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('markets')]
            
            if 'bid_price' in columns and 'ask_price' in columns:
                print("✓ Columns already exist. Migration not needed.")
                return
            
            # Add the columns
            with db.engine.connect() as conn:
                if 'bid_price' not in columns:
                    print("  Adding bid_price column...")
                    conn.execute(db.text("ALTER TABLE markets ADD COLUMN bid_price REAL"))
                    conn.commit()
                    print("  ✓ Added bid_price column")
                
                if 'ask_price' not in columns:
                    print("  Adding ask_price column...")
                    conn.execute(db.text("ALTER TABLE markets ADD COLUMN ask_price REAL"))
                    conn.commit()
                    print("  ✓ Added ask_price column")
            
            print("\n✅ Migration completed successfully!")
            print("\nNote: Existing markets will have NULL values for these columns.")
            print("You may want to run load_markets_from_json.py to reload markets with prices.")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            sys.exit(1)

if __name__ == '__main__':
    run_migration()

