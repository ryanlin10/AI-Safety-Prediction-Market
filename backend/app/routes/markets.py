from flask import Blueprint, request, jsonify
from app import db
from app.models import Market, Idea, Source, Bet
from datetime import datetime
import json
import os
import random

bp = Blueprint('markets', __name__, url_prefix='/api/markets')

@bp.route('', methods=['GET'])
def get_markets():
    """Get all markets with optional filtering"""
    status = request.args.get('status')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    markets_query = Market.query
    
    if status:
        markets_query = markets_query.filter_by(status=status)
    
    markets_query = markets_query.order_by(Market.created_at.desc())
    
    total = markets_query.count()
    markets = markets_query.limit(limit).offset(offset).all()
    
    # Include current odds for each market
    markets_data = []
    for market in markets:
        market_dict = market.to_dict()
        market_dict['current_odds'] = market.get_current_odds()
        
        # Include idea information if available
        idea = Idea.query.get(market.idea_id)
        if idea:
            market_dict['idea'] = idea.to_dict()
        
        markets_data.append(market_dict)
    
    return jsonify({
        'markets': markets_data,
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200

@bp.route('/<int:market_id>', methods=['GET'])
def get_market(market_id):
    """Get a specific market by ID"""
    market = Market.query.get_or_404(market_id)
    market_dict = market.to_dict()
    market_dict['current_odds'] = market.get_current_odds()
    market_dict['bets'] = [bet.to_dict() for bet in market.bets.all()]
    
    # Include idea information
    idea = Idea.query.get(market.idea_id)
    if idea:
        market_dict['idea'] = idea.to_dict()
    
    return jsonify(market_dict), 200

@bp.route('', methods=['POST'])
def create_market():
    """Create a new market"""
    data = request.get_json()
    
    required_fields = ['idea_id', 'question_text', 'outcomes']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify idea exists
    idea = Idea.query.get(data['idea_id'])
    if not idea:
        return jsonify({'error': 'Idea not found'}), 404
    
    market = Market(
        idea_id=data['idea_id'],
        question_text=data['question_text'],
        outcomes=data['outcomes'],
        resolution_rule=data.get('resolution_rule'),
        status=data.get('status', 'draft'),
        close_date=datetime.fromisoformat(data['close_date']) if data.get('close_date') else None
    )
    
    db.session.add(market)
    db.session.commit()
    
    return jsonify(market.to_dict()), 201

@bp.route('/<int:market_id>', methods=['PATCH'])
def update_market(market_id):
    """Update market status or details"""
    market = Market.query.get_or_404(market_id)
    data = request.get_json()
    
    allowed_fields = ['status', 'resolution_outcome', 'close_date']
    for field in allowed_fields:
        if field in data:
            if field == 'close_date' and data[field]:
                setattr(market, field, datetime.fromisoformat(data[field]))
            else:
                setattr(market, field, data[field])
    
    if data.get('status') == 'resolved':
        market.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(market.to_dict()), 200

@bp.route('/<int:market_id>/odds', methods=['GET'])
def get_market_odds(market_id):
    """Get current odds for a market"""
    market = Market.query.get_or_404(market_id)
    return jsonify({
        'market_id': market_id,
        'odds': market.get_current_odds()
    }), 200

@bp.route('/generate', methods=['POST'])
def generate_market_from_keyword():
    """Generate a new market from markets.json based on keyword"""
    data = request.get_json()
    
    if 'keyword' not in data:
        return jsonify({'error': 'Missing keyword field'}), 400
    
    keyword = data['keyword'].lower().strip()
    
    # Load markets.json from backend root directory
    # This file is at backend/app/routes/markets.py, so we go up 2 levels to backend/
    backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_file_path = os.path.join(backend_root, 'markets.json')
    
    try:
        with open(json_file_path, 'r') as f:
            markets_data = json.load(f)
    except FileNotFoundError:
        return jsonify({'error': 'markets.json not found'}), 500
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON in markets.json'}), 500
    
    # Get existing market titles to avoid duplicates
    existing_titles = {m.question_text for m in Market.query.all()}
    
    # Filter markets by keyword in keywords field or market title
    matching_markets = []
    for market_data in markets_data:
        # Skip if already exists
        if market_data['market_title'] in existing_titles:
            continue
            
        # Check if keyword matches
        keywords_str = market_data.get('keywords', '').lower()
        title_str = market_data.get('market_title', '').lower()
        
        if keyword in keywords_str or keyword in title_str:
            matching_markets.append(market_data)
    
    if not matching_markets:
        return jsonify({'error': f'No new markets found matching keyword: {keyword}'}), 404
    
    # Randomly select one matching market
    selected_market = random.choice(matching_markets)
    
    # Get or create the JSON source
    json_source = Source.query.filter_by(name='Markets JSON Import').first()
    if not json_source:
        json_source = Source(
            name='Markets JSON Import',
            url='file://markets.json',
            type='json_import'
        )
        db.session.add(json_source)
        db.session.flush()
    
    # Create Idea entry
    idea = Idea(
        source_id=json_source.id,
        title=selected_market.get('paper_title', 'Generated Market'),
        abstract=selected_market.get('safety_reasoning', ''),
        keywords=selected_market.get('keywords', ''),
        extracted_claim=selected_market['market_title'],
        confidence_score=0.9
    )
    db.session.add(idea)
    db.session.flush()
    
    # Parse the resolution date
    try:
        close_date = datetime.strptime(selected_market['resolution_date'], '%Y-%m-%d')
    except (ValueError, KeyError):
        close_date = None
    
    # Get bid/ask prices from JSON
    bid_price = selected_market.get('bid_price', 0.5)
    ask_price = selected_market.get('ask_price', 0.5)
    
    # Create Market entry
    market = Market(
        idea_id=idea.id,
        question_text=selected_market['market_title'],
        outcomes=json.dumps(['Yes', 'No']),
        resolution_rule=json.dumps({
            'type': 'date',
            'date': selected_market.get('resolution_date', ''),
            'description': 'Resolved based on the outcome by the specified date.'
        }),
        status='active',
        close_date=close_date,
        bid_price=bid_price,
        ask_price=ask_price
    )
    
    db.session.add(market)
    db.session.flush()  # Get the market ID before adding bets
    
    # Use the average of bid/ask as the initial YES price
    yes_price = (bid_price + ask_price) / 2
    no_price = 1.0 - yes_price
    
    # Create synthetic initial bets to establish market prices
    # The bet amounts determine the initial liquidity pool ratios
    # For a Kalshi-style market, we want the prices to reflect the probabilities
    initial_liquidity = 1000.0  # Starting liquidity pool
    
    # Create initial bet for YES outcome
    yes_bet = Bet(
        market_id=market.id,
        user_id=1,  # System user
        outcome='Yes',
        stake=yes_price * initial_liquidity,
        odds=yes_price,
        rationale=f'Initial market seeding at {yes_price*100:.1f}%'
    )
    
    # Create initial bet for NO outcome
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
    db.session.commit()
    
    return jsonify({
        'success': True,
        'market': market.to_dict(),
        'initial_prices': {
            'yes': yes_price,
            'no': no_price
        },
        'message': f'Generated market matching keyword: {keyword}'
    }), 201

