from datetime import datetime
from app import db
import json

class Idea(db.Model):
    __tablename__ = 'ideas'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False)
    title = db.Column(db.Text, nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, default='')  # Store as comma-separated string for SQLite
    embedding = db.Column(db.Text)  # Store as JSON string for SQLite
    extracted_claim = db.Column(db.Text)
    confidence_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    markets = db.relationship('Market', backref='idea', lazy='dynamic')
    
    def to_dict(self, include_embedding=False):
        # Parse keywords from comma-separated string
        keywords = [k.strip() for k in self.keywords.split(',')] if self.keywords else []
        
        data = {
            'id': self.id,
            'source_id': self.source_id,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': keywords,
            'extracted_claim': self.extracted_claim,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat()
        }
        if include_embedding and self.embedding:
            try:
                data['embedding'] = json.loads(self.embedding)
            except:
                data['embedding'] = self.embedding
        return data
    
    def __repr__(self):
        return f'<Idea {self.id}: {self.title[:50]}>'

