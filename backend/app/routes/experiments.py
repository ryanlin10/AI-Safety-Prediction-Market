from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Experiment, Market, Agent
from app.services.experiment_runner import run_experiment_task
from datetime import datetime

bp = Blueprint('experiments', __name__, url_prefix='/api')

@bp.route('/markets/<int:market_id>/run_experiment', methods=['POST'])
def run_experiment(market_id):
    """Trigger an experiment for a market"""
    market = Market.query.get_or_404(market_id)
    
    if not market.resolution_rule:
        return jsonify({'error': 'Market has no resolution rule defined'}), 400
    
    data = request.get_json()
    agent_id = data.get('agent_id')
    
    if not agent_id:
        return jsonify({'error': 'agent_id required'}), 400
    
    agent = Agent.query.get_or_404(agent_id)
    
    if agent.type != 'researcher':
        return jsonify({'error': 'Agent is not a researcher'}), 400
    
    # Create experiment record
    experiment = Experiment(
        market_id=market_id,
        agent_id=agent_id,
        config=market.resolution_rule,
        status='pending'
    )
    
    db.session.add(experiment)
    db.session.commit()
    
    # Queue the experiment task
    try:
        run_experiment_task.delay(experiment.id)
    except Exception as e:
        experiment.status = 'failed'
        experiment.logs = f'Failed to queue experiment: {str(e)}'
        db.session.commit()
        return jsonify({'error': str(e)}), 500
    
    return jsonify(experiment.to_dict()), 202

@bp.route('/experiments/<int:experiment_id>/status', methods=['GET'])
def get_experiment_status(experiment_id):
    """Get the status of an experiment"""
    experiment = Experiment.query.get_or_404(experiment_id)
    return jsonify(experiment.to_dict()), 200

@bp.route('/experiments/<int:experiment_id>', methods=['GET'])
def get_experiment(experiment_id):
    """Get full experiment details"""
    experiment = Experiment.query.get_or_404(experiment_id)
    
    # Include market information
    market = Market.query.get(experiment.market_id)
    experiment_dict = experiment.to_dict()
    if market:
        experiment_dict['market'] = market.to_dict()
    
    return jsonify(experiment_dict), 200

@bp.route('/markets/<int:market_id>/experiments', methods=['GET'])
def get_market_experiments(market_id):
    """Get all experiments for a market"""
    market = Market.query.get_or_404(market_id)
    experiments = market.experiments.order_by(Experiment.created_at.desc()).all()
    
    return jsonify({
        'market_id': market_id,
        'experiments': [exp.to_dict() for exp in experiments]
    }), 200

