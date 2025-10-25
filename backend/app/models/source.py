from datetime import datetime
from app import db

class Source(db.Model):
    __tablename__ = 'sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    url = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # arxiv, conference, rss
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_scraped = db.Column(db.DateTime)
    
    # Relationships
    ideas = db.relationship('Idea', backref='source', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'type': self.type,
            'created_at': self.created_at.isoformat(),
            'last_scraped': self.last_scraped.isoformat() if self.last_scraped else None
        }
    
    def __repr__(self):
        return f'<Source {self.name}>'

