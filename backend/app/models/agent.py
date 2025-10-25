from datetime import datetime
from app import db
import json

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    agent_type = db.Column(db.String(50), nullable=False)  # bettor, researcher, trader, analyst
    config = db.Column(db.Text)  # Configuration as JSON string for SQLite
    description = db.Column(db.Text)  # Agent description
    balance = db.Column(db.Float, default=1000.0)  # Available balance for betting
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    bets = db.relationship('Bet', backref='agent', lazy='dynamic')
    experiments = db.relationship('Experiment', backref='agent', lazy='dynamic')
    
    def to_dict(self):
        # Parse config from JSON string
        try:
            config = json.loads(self.config) if isinstance(self.config, str) else self.config
        except:
            config = self.config
        
        return {
            'id': self.id,
            'name': self.name,
            'agent_type': self.agent_type,
            'config': config,
            'description': self.description,
            'balance': self.balance,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Agent {self.id}: {self.name} ({self.agent_type})>'

