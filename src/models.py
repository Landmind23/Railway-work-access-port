"""
Database models for Railway Work Access Port
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

db = SQLAlchemy()


class BaseModel(db.Model):
    """Base model with common fields"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Company(BaseModel):
    """Company/Contractor profile"""
    __tablename__ = 'companies'
    
    name = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    description = db.Column(db.Text)
    
    # Certifications and qualifications
    certifications = db.Column(db.JSON, default=list)  # ["ISO9001", "ADIPS-H", ...]
    
    # Service areas - locations where company operates
    service_areas = db.Column(db.JSON, default=list)  # [{"region": "London", "areas": [...]}]
    
    # Company capabilities
    capabilities = db.Column(db.JSON, default=list)  # ["track_maintenance", "rail_inspection", ...]
    
    # Contact information
    contact_person = db.Column(db.String(255))
    address = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    api_tokens = db.relationship('APIToken', backref='company', lazy=True, cascade='all, delete-orphan')
    assigned_opportunities = db.relationship('WorkOpportunity', backref='assigned_company', lazy=True, 
                                           foreign_keys='WorkOpportunity.assigned_company_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'description': self.description,
            'certifications': self.certifications,
            'service_areas': self.service_areas,
            'capabilities': self.capabilities,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class APIToken(BaseModel):
    """API authentication tokens"""
    __tablename__ = 'api_tokens'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    
    # Token lifecycle
    expires_at = db.Column(db.DateTime)
    is_revoked = db.Column(db.Boolean, default=False)
    last_used_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_revoked': self.is_revoked,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WorkOpportunity(BaseModel):
    """Railway work opportunities and maintenance windows"""
    __tablename__ = 'work_opportunities'
    
    # Basic information
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Classification
    type = db.Column(db.String(50), nullable=False)  # maintenance, construction, inspection, urgent_repair
    category = db.Column(db.String(100))
    
    # Location information
    railway_line = db.Column(db.String(100))
    station = db.Column(db.String(100))
    region = db.Column(db.String(100))
    location_coordinates = db.Column(db.JSON)  # {"latitude": ..., "longitude": ...}
    
    # Scheduling
    scheduled_start = db.Column(db.DateTime, nullable=False)
    scheduled_end = db.Column(db.DateTime, nullable=False)
    duration_hours = db.Column(db.Float)
    
    # Requirements
    required_skills = db.Column(db.JSON, default=list)  # ["track_maintenance", "signaling", ...]
    required_certifications = db.Column(db.JSON, default=list)
    required_equipment = db.Column(db.JSON, default=list)
    
    # Assignment and status
    status = db.Column(db.String(50), default='open')  # open, assigned, in_progress, completed, cancelled
    assigned_company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    
    # Priority and importance
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Additional metadata
    budget = db.Column(db.Float)  # Estimated budget if available
    notes = db.Column(db.Text)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_railway_line', 'railway_line'),
        Index('idx_region', 'region'),
        Index('idx_scheduled_start', 'scheduled_start'),
        Index('idx_type', 'type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'category': self.category,
            'railway_line': self.railway_line,
            'station': self.station,
            'region': self.region,
            'location_coordinates': self.location_coordinates,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'scheduled_end': self.scheduled_end.isoformat() if self.scheduled_end else None,
            'duration_hours': self.duration_hours,
            'required_skills': self.required_skills,
            'required_certifications': self.required_certifications,
            'required_equipment': self.required_equipment,
            'status': self.status,
            'assigned_company_id': self.assigned_company_id,
            'priority': self.priority,
            'budget': self.budget,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Notification(BaseModel):
    """Notifications for opportunities matching company capabilities"""
    __tablename__ = 'notifications'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('work_opportunities.id'), nullable=False)
    
    # Notification state
    notification_type = db.Column(db.String(50))  # match, deadline, assignment
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Relationships
    company = db.relationship('Company', backref='notifications')
    opportunity = db.relationship('WorkOpportunity', backref='notifications')
    
    __table_args__ = (
        Index('idx_company_id', 'company_id'),
        Index('idx_is_read', 'is_read'),
        Index('idx_created_at', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'opportunity_id': self.opportunity_id,
            'notification_type': self.notification_type,
            'message': self.message,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(BaseModel):
    """Audit trail for all API operations"""
    __tablename__ = 'audit_logs'
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer)
    
    # Request/Response details
    request_data = db.Column(db.JSON)
    response_data = db.Column(db.JSON)
    
    # IP and user agent
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    __table_args__ = (
        Index('idx_company_id_audit', 'company_id'),
        Index('idx_created_at_audit', 'created_at'),
        Index('idx_endpoint', 'endpoint'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
