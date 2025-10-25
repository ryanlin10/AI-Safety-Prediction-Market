from flask import Blueprint, request, jsonify
from app import db
from app.models import Idea, Source
from app.services.claim_generator import get_claim_generator
from sqlalchemy import func
from datetime import datetime

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

@bp.route('/generate', methods=['POST'])
def generate_claims():
    """Generate testable research claims"""
    data = request.get_json() or {}
    count = data.get('count', 5)
    categories = data.get('categories', None)
    
    # Limit count to reasonable number
    count = min(count, 20)
    
    # Get or create a "Generated Claims" source
    source = Source.query.filter_by(name="AI-Generated Research Claims").first()
    if not source:
        source = Source(
            name="AI-Generated Research Claims",
            url="internal://claim-generator",
            type="generated",
            last_scraped=datetime.utcnow()
        )
        db.session.add(source)
        db.session.commit()
    
    # Generate claims
    generator = get_claim_generator()
    generated_claims = generator.generate_batch(count=count, categories=categories)
    
    # Save to database
    ideas = []
    for claim_data in generated_claims:
        # Convert keywords list to comma-separated string for SQLite
        keywords_str = ', '.join(claim_data.get('keywords', [])) if isinstance(claim_data.get('keywords'), list) else claim_data.get('keywords', '')
        
        idea = Idea(
            source_id=source.id,
            title=claim_data['title'],
            abstract=claim_data['abstract'],
            keywords=keywords_str,
            extracted_claim=claim_data['claim'],
            confidence_score=claim_data['confidence_score'],
            created_at=datetime.utcnow()
        )
        db.session.add(idea)
        ideas.append(idea)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'generated_count': len(ideas),
        'ideas': [idea.to_dict() for idea in ideas]
    }), 201

