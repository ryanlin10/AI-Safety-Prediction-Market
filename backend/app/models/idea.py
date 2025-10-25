from datetime import datetime
from app import db
from pgvector.sqlalchemy import Vector

class Idea(db.Model):
    __tablename__ = 'ideas'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.ARRAY(db.String), default=[])
    embedding = db.Column(Vector(1536))  # OpenAI embedding dimension
    extracted_claim = db.Column(db.Text)
    confidence_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    markets = db.relationship('Market', backref='idea', lazy='dynamic')
    
    def to_dict(self, include_embedding=False):
        data = {
            'id': self.id,
            'source_id': self.source_id,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'extracted_claim': self.extracted_claim,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat()
        }
        if include_embedding and self.embedding:
            data['embedding'] = self.embedding
        return data
    
    def __repr__(self):
        return f'<Idea {self.id}: {self.title[:50]}>'

