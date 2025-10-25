from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(80), unique=True, nullable=False)
    email_hash = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    bets = db.relationship('Bet', backref='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'handle': self.handle,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<User {self.handle}>'

