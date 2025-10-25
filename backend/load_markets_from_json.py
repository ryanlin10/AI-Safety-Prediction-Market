#!/usr/bin/env python3
"""
Load markets from markets.json file into the database
"""
import os
import sys
import json
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for local development
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///prediction_market.db'

from app import create_app, db
from app.models import Market, Idea, Source, Bet

def load_markets_from_json():
    """Load markets from markets.json file"""
    app = create_app()
    
    with app.app_context():
        # Read the JSON file
        json_file_path = os.path.join(os.path.dirname(__file__), 'markets.json')
        
        print(f"📖 Reading markets from {json_file_path}")
        
        with open(json_file_path, 'r') as f:
            markets_data = json.load(f)
        
        print(f"✓ Found {len(markets_data)} markets in JSON file\n")
        
        # Clear existing markets (optional - comment out if you want to keep existing ones)
        print("🗑️  Clearing existing markets...")
        Market.query.delete()
        Idea.query.delete()
        Source.query.delete()
        db.session.commit()
        print("✓ Cleared existing markets\n")
        
        # Create a default source for JSON-imported markets
        print("📝 Creating source for JSON imports...")
        json_source = Source(
            name='Markets JSON Import',
            url='file://markets.json',
            type='json_import'
        )
        db.session.add(json_source)
        db.session.flush()
        print(f"✓ Created source with ID: {json_source.id}\n")
        
        # Create markets from JSON
        for idx, market_data in enumerate(markets_data, 1):
            print(f"📊 Creating market {idx}/{len(markets_data)}")
            print(f"   Title: {market_data['market_title'][:80]}...")
            
            # First, create an Idea entry for this market
            idea = Idea(
                source_id=json_source.id,
                title=market_data['paper_title'],
                abstract=market_data['safety_reasoning'],
                keywords=market_data['keywords'],
                extracted_claim=market_data['market_title'],
                confidence_score=0.9  # High confidence since these are curated
            )
            db.session.add(idea)
            db.session.flush()  # Get the idea ID
            
            # Parse the resolution date
            try:
                close_date = datetime.strptime(market_data['resolution_date'], '%Y-%m-%d')
            except:
                close_date = None
            
            # Create outcomes based on bid/ask prices
            # These are binary markets (Yes/No)
            outcomes = json.dumps(['Yes', 'No'])
            
            # Create the market
            market = Market(
                idea_id=idea.id,
                question_text=market_data['market_title'],
                outcomes=outcomes,
                resolution_rule=json.dumps({
                    'type': 'binary',
                    'source': 'paper_validation',
                    'criteria': market_data['safety_reasoning']
                }),
                status='active',
                close_date=close_date
            )
            db.session.add(market)
            db.session.flush()  # Get the market ID
            
            # Initialize market prices using bid/ask from JSON
            bid_price = market_data.get('bid_price', 0.5)
            ask_price = market_data.get('ask_price', 0.5)
            
            # Use the average of bid/ask as the initial YES price
            yes_price = (bid_price + ask_price) / 2
            no_price = 1.0 - yes_price
            
            # Create synthetic initial bets to establish market prices
            initial_liquidity = 1000.0
            
            # Create initial bet for Yes outcome
            yes_bet = Bet(
                market_id=market.id,
                user_id=1,  # System user
                outcome='Yes',
                stake=yes_price * initial_liquidity,
                odds=yes_price,
                rationale=f'Initial market seeding at {yes_price*100:.1f}%'
            )
            
            # Create initial bet for No outcome
            no_bet = Bet(
                market_id=market.id,
                user_id=1,  # System user
                outcome='No',
                stake=no_price * initial_liquidity,
                odds=no_price,
                rationale=f'Initial market seeding at {no_price*100:.1f}%'
            )
            
            db.session.add(yes_bet)
            db.session.add(no_bet)
            
            print(f"   ✓ Created market with ID: {market.id}")
            print(f"   📅 Resolution date: {market_data['resolution_date']}")
            print(f"   💰 Bid: {market_data['bid_price']}, Ask: {market_data['ask_price']}")
            print(f"   📊 Initial prices - YES: {yes_price*100:.1f}%, NO: {no_price*100:.1f}%")
            print()
        
        # Commit all changes
        db.session.commit()
        
        print("=" * 50)
        print(f"✅ Successfully loaded {len(markets_data)} markets!")
        print("=" * 50)
        
        # Display summary
        total_markets = Market.query.count()
        active_markets = Market.query.filter_by(status='active').count()
        print(f"\n📈 Database Summary:")
        print(f"   Total markets: {total_markets}")
        print(f"   Active markets: {active_markets}")
        print(f"   Total ideas: {Idea.query.count()}")

if __name__ == '__main__':
    load_markets_from_json()

