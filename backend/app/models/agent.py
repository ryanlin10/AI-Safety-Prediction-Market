from datetime import datetime
from app import db

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # bettor, researcher
    creds = db.Column(db.JSON)  # API keys, credentials
    meta = db.Column(db.JSON)  # Configuration, parameters
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    bets = db.relationship('Bet', backref='agent', lazy='dynamic')
    experiments = db.relationship('Experiment', backref='agent', lazy='dynamic')
    
    def to_dict(self, include_creds=False):
        data = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'meta': self.meta,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
        if include_creds:
            data['creds'] = self.creds
        return data
    
    def __repr__(self):
        return f'<Agent {self.id}: {self.name} ({self.type})>'

