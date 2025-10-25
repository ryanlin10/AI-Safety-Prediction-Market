from flask import Blueprint, request, jsonify
from app import db
from app.models import Idea
from sqlalchemy import func

bp = Blueprint('ideas', __name__, url_prefix='/api/ideas')

@bp.route('', methods=['GET'])
def get_ideas():
    """Get all ideas with optional filtering"""
    query = request.args.get('query', '')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    ideas_query = Idea.query
    
    # Simple text search
    if query:
        search_pattern = f'%{query}%'
        ideas_query = ideas_query.filter(
            db.or_(
                Idea.title.ilike(search_pattern),
                Idea.abstract.ilike(search_pattern),
                Idea.extracted_claim.ilike(search_pattern)
            )
        )
    
    # Order by confidence and recency
    ideas_query = ideas_query.order_by(
        Idea.confidence_score.desc(),
        Idea.created_at.desc()
    )
    
    total = ideas_query.count()
    ideas = ideas_query.limit(limit).offset(offset).all()
    
    return jsonify({
        'ideas': [idea.to_dict() for idea in ideas],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200

@bp.route('/<int:idea_id>', methods=['GET'])
def get_idea(idea_id):
    """Get a specific idea by ID"""
    idea = Idea.query.get_or_404(idea_id)
    return jsonify(idea.to_dict()), 200

@bp.route('/search/semantic', methods=['POST'])
def semantic_search():
    """Semantic search using embeddings"""
    data = request.get_json()
    query_embedding = data.get('embedding')
    limit = data.get('limit', 10)
    
    if not query_embedding:
        return jsonify({'error': 'embedding required'}), 400
    
    # Use pgvector for similarity search
    # This requires the embedding to be in the correct format
    similar_ideas = Idea.query.filter(
        Idea.embedding.isnot(None)
    ).order_by(
        Idea.embedding.cosine_distance(query_embedding)
    ).limit(limit).all()
    
    return jsonify({
        'ideas': [idea.to_dict() for idea in similar_ideas]
    }), 200

@bp.route('', methods=['POST'])
def create_idea():
    """Create a new idea (admin/scraper only)"""
    data = request.get_json()
    
    required_fields = ['source_id', 'title', 'abstract']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    idea = Idea(
        source_id=data['source_id'],
        title=data['title'],
        abstract=data['abstract'],
        keywords=data.get('keywords', []),
        extracted_claim=data.get('extracted_claim'),
        confidence_score=data.get('confidence_score', 0.0)
    )
    
    db.session.add(idea)
    db.session.commit()
    
    return jsonify(idea.to_dict()), 201

