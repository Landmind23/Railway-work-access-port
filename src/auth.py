"""
Authentication and authorization module
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models import db, Company, APIToken


def hash_token(token: str) -> str:
    """Hash a token for secure storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_api_token() -> str:
    """Generate a secure random API token"""
    return secrets.token_urlsafe(32)


def create_company_token(company_id: int, token_name: str, expires_in_days: int = 365) -> dict:
    """
    Create a new API token for a company
    
    Args:
        company_id: ID of the company
        token_name: Human-readable name for the token
        expires_in_days: Token expiration time in days
        
    Returns:
        Dictionary with token and token_id
    """
    token = generate_api_token()
    token_hash = hash_token(token)
    
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    api_token = APIToken(
        company_id=company_id,
        token_hash=token_hash,
        name=token_name,
        expires_at=expires_at
    )
    
    db.session.add(api_token)
    db.session.commit()
    
    return {
        'token_id': api_token.id,
        'token': token,  # Only shown once at creation
        'name': token_name,
        'expires_at': expires_at.isoformat()
    }


def verify_api_token(token: str) -> dict:
    """
    Verify an API token and return company information
    
    Args:
        token: The API token to verify
        
    Returns:
        Dictionary with company info if valid, None otherwise
    """
    token_hash = hash_token(token)
    
    api_token = APIToken.query.filter_by(
        token_hash=token_hash,
        is_revoked=False
    ).first()
    
    if not api_token:
        return None
    
    # Check expiration
    if api_token.expires_at and api_token.expires_at < datetime.utcnow():
        return None
    
    # Update last used timestamp
    api_token.last_used_at = datetime.utcnow()
    db.session.commit()
    
    company = Company.query.get(api_token.company_id)
    
    if not company or not company.is_active:
        return None
    
    return {
        'company_id': company.id,
        'company_name': company.name,
        'token_id': api_token.id
    }


def revoke_token(token_id: int) -> bool:
    """Revoke an API token"""
    api_token = APIToken.query.get(token_id)
    if api_token:
        api_token.is_revoked = True
        db.session.commit()
        return True
    return False


def api_key_required(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid Authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'Missing API token'}), 401
        
        company_info = verify_api_token(token)
        
        if not company_info:
            return jsonify({'error': 'Invalid or expired API token'}), 401
        
        # Store company info in request context
        request.company_id = company_info['company_id']
        request.company_name = company_info['company_name']
        request.token_id = company_info['token_id']
        
        return f(*args, **kwargs)
    
    return decorated_function
