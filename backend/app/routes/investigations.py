from flask import Blueprint, request, jsonify
from app import db
from app.models import Investigation, Idea, Agent
from app.services.investigation_service import get_investigation_service
from datetime import datetime
import json

bp = Blueprint('investigations', __name__, url_prefix='/api')

@bp.route('/investigations', methods=['GET'])
def get_investigations():
    """Get all investigations"""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    status = request.args.get('status')
    
    query = Investigation.query
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Investigation.created_at.desc())
    
    total = query.count()
    investigations = query.limit(limit).offset(offset).all()
    
    # Include idea information
    results = []
    for inv in investigations:
        inv_dict = inv.to_dict()
        idea = Idea.query.get(inv.idea_id)
        if idea:
            inv_dict['idea'] = {
                'id': idea.id,
                'title': idea.title,
                'extracted_claim': idea.extracted_claim
            }
        results.append(inv_dict)
    
    return jsonify({
        'investigations': results,
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200

@bp.route('/investigations/<int:investigation_id>', methods=['GET'])
def get_investigation(investigation_id):
    """Get a specific investigation"""
    investigation = Investigation.query.get_or_404(investigation_id)
    inv_dict = investigation.to_dict()
    
    # Include idea information
    idea = Idea.query.get(investigation.idea_id)
    if idea:
        inv_dict['idea'] = idea.to_dict()
    
    return jsonify(inv_dict), 200

@bp.route('/ideas/<int:idea_id>/investigate', methods=['POST'])
def create_investigation(idea_id):
    """Create and run an investigation for an idea"""
    idea = Idea.query.get_or_404(idea_id)
    
    # Check if there's already a recent investigation
    existing = Investigation.query.filter_by(
        idea_id=idea_id
    ).order_by(Investigation.created_at.desc()).first()
    
    if existing and existing.status == 'investigating':
        return jsonify({'error': 'Investigation already in progress'}), 400
    
    # Get or create investigator agent
    agent = Agent.query.filter_by(agent_type='researcher').first()
    if not agent:
        agent = Agent(
            name='Automated Investigator',
            agent_type='researcher',
            description='AI agent that investigates research claims',
            config=json.dumps({'auto_investigate': True}),
            is_active=True
        )
        db.session.add(agent)
        db.session.commit()
    
    # Create investigation record
    investigation = Investigation(
        idea_id=idea_id,
        agent_id=agent.id,
        formalized_claim='',  # Will be filled by service
        status='investigating',
        started_at=datetime.utcnow()
    )
    db.session.add(investigation)
    db.session.commit()
    
    # Run investigation
    try:
        service = get_investigation_service()
        result = service.run_investigation(
            idea.title,
            idea.abstract,
            idea.extracted_claim or idea.title
        )
        
        # Update investigation with results
        investigation.formalized_claim = result['formalized_claim']
        investigation.test_criteria = json.dumps(result['test_criteria'])
        investigation.reasoning_steps = json.dumps(result['reasoning_steps'])
        investigation.evidence = json.dumps(result['evidence'])
        investigation.conclusion = result['conclusion']
        investigation.confidence = result['confidence']
        investigation.summary = result['summary']
        investigation.status = 'completed'
        investigation.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'investigation': investigation.to_dict()
        }), 201
        
    except Exception as e:
        investigation.status = 'failed'
        investigation.summary = f'Investigation failed: {str(e)}'
        db.session.commit()
        return jsonify({'error': str(e)}), 500

@bp.route('/ideas/<int:idea_id>/investigations', methods=['GET'])
def get_idea_investigations(idea_id):
    """Get all investigations for a specific idea"""
    idea = Idea.query.get_or_404(idea_id)
    investigations = Investigation.query.filter_by(idea_id=idea_id).order_by(Investigation.created_at.desc()).all()
    
    return jsonify({
        'idea_id': idea_id,
        'investigations': [inv.to_dict() for inv in investigations]
    }), 200


