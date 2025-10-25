from datetime import datetime
from app import db

class Bet(db.Model):
    __tablename__ = 'bets'
    
    id = db.Column(db.Integer, primary_key=True)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=True)
    outcome = db.Column(db.String(50), nullable=False)
    stake = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    rationale = db.Column(db.Text)  # For agent bets, store LLM reasoning
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'market_id': self.market_id,
            'user_id': self.user_id,
            'agent_id': self.agent_id,
            'outcome': self.outcome,
            'stake': self.stake,
            'odds': self.odds,
            'rationale': self.rationale,
            'created_at': self.created_at.isoformat(),
            'is_agent_bet': self.agent_id is not None
        }
    
    def __repr__(self):
        bettor = f'Agent {self.agent_id}' if self.agent_id else f'User {self.user_id}'
        return f'<Bet {self.id}: {bettor} on Market {self.market_id}>'

