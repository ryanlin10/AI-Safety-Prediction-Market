from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Agent, Market, Bet
from app.services.agent_bettor import AgentBettor

bp = Blueprint('agents', __name__, url_prefix='/api/agents')

@bp.route('', methods=['GET'])
def get_agents():
    """Get all agents"""
    agents = Agent.query.all()
    return jsonify({
        'agents': [agent.to_dict() for agent in agents]
    }), 200

@bp.route('/<int:agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get a specific agent"""
    agent = Agent.query.get_or_404(agent_id)
    return jsonify(agent.to_dict()), 200

@bp.route('', methods=['POST'])
def create_agent():
    """Create a new agent"""
    data = request.get_json()
    
    required_fields = ['name', 'type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if data['type'] not in ['bettor', 'researcher']:
        return jsonify({'error': 'Invalid agent type'}), 400
    
    agent = Agent(
        name=data['name'],
        type=data['type'],
        creds=data.get('creds', {}),
        meta=data.get('meta', {}),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(agent)
    db.session.commit()
    
    return jsonify(agent.to_dict()), 201

@bp.route('/<int:agent_id>/place_initial_bet', methods=['POST'])
def place_initial_bet(agent_id):
    """Agent places an initial bet on a market"""
    agent = Agent.query.get_or_404(agent_id)
    
    if agent.type != 'bettor':
        return jsonify({'error': 'Agent is not a bettor'}), 400
    
    if not agent.is_active:
        return jsonify({'error': 'Agent is not active'}), 400
    
    data = request.get_json()
    market_id = data.get('market_id')
    
    if not market_id:
        return jsonify({'error': 'market_id required'}), 400
    
    market = Market.query.get_or_404(market_id)
    
    if market.status != 'active':
        return jsonify({'error': 'Market is not active'}), 400
    
    # Use AgentBettor service to generate bet
    try:
        bettor = AgentBettor(agent, current_app.config)
        bet_recommendation = bettor.generate_bet(market)
        
        # Validate stake against max
        max_stake = current_app.config['AGENT_MAX_STAKE']
        if bet_recommendation['stake'] > max_stake:
            bet_recommendation['stake'] = max_stake
        
        # Place the bet
        bet = Bet(
            market_id=market_id,
            agent_id=agent_id,
            outcome=bet_recommendation['outcome'],
            stake=bet_recommendation['stake'],
            odds=bet_recommendation['odds'],
            rationale=bet_recommendation['rationale']
        )
        
        db.session.add(bet)
        db.session.commit()
        
        return jsonify(bet.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:agent_id>/bets', methods=['GET'])
def get_agent_bets(agent_id):
    """Get all bets placed by an agent"""
    agent = Agent.query.get_or_404(agent_id)
    bets = agent.bets.order_by(Bet.created_at.desc()).all()
    
    return jsonify({
        'agent_id': agent_id,
        'bets': [bet.to_dict() for bet in bets]
    }), 200

