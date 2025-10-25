from datetime import datetime
from app import db

class Market(db.Model):
    __tablename__ = 'markets'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    outcomes = db.Column(db.JSON, nullable=False)  # e.g., ["True", "False"] or numeric buckets
    resolution_rule = db.Column(db.JSON)  # Contains dataset, metric, threshold, etc.
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, active, closed, resolved
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    close_date = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    resolution_outcome = db.Column(db.String(50))
    
    # Relationships
    bets = db.relationship('Bet', backref='market', lazy='dynamic')
    experiments = db.relationship('Experiment', backref='market', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'idea_id': self.idea_id,
            'question_text': self.question_text,
            'outcomes': self.outcomes,
            'resolution_rule': self.resolution_rule,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'close_date': self.close_date.isoformat() if self.close_date else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_outcome': self.resolution_outcome
        }
    
    def get_current_odds(self):
        """Calculate current odds based on bets"""
        # Simple implementation: count bets per outcome
        outcome_stakes = {}
        for bet in self.bets:
            outcome_stakes[bet.outcome] = outcome_stakes.get(bet.outcome, 0) + bet.stake
        
        total_stake = sum(outcome_stakes.values())
        if total_stake == 0:
            return {outcome: 0.5 for outcome in self.outcomes}
        
        return {outcome: outcome_stakes.get(outcome, 0) / total_stake for outcome in self.outcomes}
    
    def __repr__(self):
        return f'<Market {self.id}: {self.question_text[:50]}>'

