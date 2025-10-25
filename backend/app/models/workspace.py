from app import db
from datetime import datetime
import json

class Workspace(db.Model):
    __tablename__ = 'workspaces'
    
    id = db.Column(db.Integer, primary_key=True)
    investigation_id = db.Column(db.Integer, db.ForeignKey('investigations.id'), nullable=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Store files as JSON: {"main.py": "content", "utils.py": "content", ...}
    _files = db.Column('files', db.Text, default='{}')
    
    snapshot_id = db.Column(db.String(64))  # For versioning
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    runs = db.relationship('Run', backref='workspace', lazy=True, cascade='all, delete-orphan')
    
    @property
    def files(self):
        """Get files as dict"""
        if self._files:
            return json.loads(self._files)
        return {}
    
    @files.setter
    def files(self, value):
        """Set files from dict"""
        self._files = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'investigation_id': self.investigation_id,
            'agent_id': self.agent_id,
            'name': self.name,
            'description': self.description,
            'files': self.files,
            'snapshot_id': self.snapshot_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'run_count': len(self.runs) if self.runs else 0
        }

