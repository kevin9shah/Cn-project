from . import db
from datetime import datetime

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False, unique=True)
    priority = db.Column(db.String(20), default='low')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pings = db.relationship('Ping', backref='device', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'priority': self.priority,
            'created_at': self.created_at.isoformat()
        }

class Ping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(10), nullable=False) # UP or DOWN
    rtt_ms = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'rtt_ms': self.rtt_ms
        }
