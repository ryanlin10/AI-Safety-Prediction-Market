from app import db
from datetime import datetime
import json

class Run(db.Model):
    __tablename__ = 'runs'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    
    code_hash = db.Column(db.String(64))  # Hash of code snapshot
    status = db.Column(db.String(50), default='queued')  # queued, running, completed, failed, failed_static_check
    
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    
    stdout = db.Column(db.Text)
    stderr = db.Column(db.Text)
    exit_code = db.Column(db.Integer)
    
    # Store additional metadata as JSON
    _meta = db.Column('meta', db.Text, default='{}')
    
    # Resource usage
    cpu_time_ms = db.Column(db.Integer)
    memory_mb = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def meta(self):
        """Get meta as dict"""
        if self._meta:
            return json.loads(self._meta)
        return {}
    
    @meta.setter
    def meta(self, value):
        """Set meta from dict"""
        self._meta = json.dumps(value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'workspace_id': self.workspace_id,
            'code_hash': self.code_hash,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'exit_code': self.exit_code,
            'meta': self.meta,
            'cpu_time_ms': self.cpu_time_ms,
            'memory_mb': self.memory_mb,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_ms': int((self.finished_at - self.started_at).total_seconds() * 1000) if self.finished_at and self.started_at else None
        }

