from flask import Blueprint, request, jsonify
from app import db
from app.models import Market, Idea
from datetime import datetime

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
    
    return jsonify({
        'markets': [market.to_dict() for market in markets],
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

