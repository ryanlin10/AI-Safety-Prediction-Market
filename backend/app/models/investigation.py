from datetime import datetime
from app import db
import json

class Investigation(db.Model):
    __tablename__ = 'investigations'
    
    id = db.Column(db.Integer, primary_key=True)
    idea_id = db.Column(db.Integer, db.ForeignKey('ideas.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=True)
    
    # Formalized claim
    formalized_claim = db.Column(db.Text, nullable=False)
    test_criteria = db.Column(db.Text)  # JSON string for SQLite
    
    # Investigation process
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, investigating, completed, failed
    reasoning_steps = db.Column(db.Text)  # JSON array of reasoning steps
    evidence = db.Column(db.Text)  # JSON array of evidence
    
    # Results
    conclusion = db.Column(db.String(20))  # true, false, inconclusive
    confidence = db.Column(db.Float)  # 0-1
    summary = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        # Parse JSON fields
        try:
            test_criteria = json.loads(self.test_criteria) if isinstance(self.test_criteria, str) else self.test_criteria
        except:
            test_criteria = self.test_criteria
        
        try:
            reasoning_steps = json.loads(self.reasoning_steps) if isinstance(self.reasoning_steps, str) else self.reasoning_steps
        except:
            reasoning_steps = self.reasoning_steps or []
        
        try:
            evidence = json.loads(self.evidence) if isinstance(self.evidence, str) else self.evidence
        except:
            evidence = self.evidence or []
        
        return {
            'id': self.id,
            'idea_id': self.idea_id,
            'agent_id': self.agent_id,
            'formalized_claim': self.formalized_claim,
            'test_criteria': test_criteria,
            'status': self.status,
            'reasoning_steps': reasoning_steps,
            'evidence': evidence,
            'conclusion': self.conclusion,
            'confidence': self.confidence,
            'summary': self.summary,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<Investigation {self.id}: {self.status} - {self.conclusion}>'

