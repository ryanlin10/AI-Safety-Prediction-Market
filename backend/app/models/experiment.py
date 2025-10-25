from datetime import datetime
from app import db

class Experiment(db.Model):
    __tablename__ = 'experiments'
    
    id = db.Column(db.Integer, primary_key=True)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    config = db.Column(db.JSON, nullable=False)  # Experiment configuration
    result = db.Column(db.JSON)  # Experiment results
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, running, completed, failed
    logs = db.Column(db.Text)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'market_id': self.market_id,
            'agent_id': self.agent_id,
            'config': self.config,
            'result': self.result,
            'status': self.status,
            'logs': self.logs,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Experiment {self.id}: Market {self.market_id} - {self.status}>'

