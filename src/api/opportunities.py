"""
API endpoints for work opportunities
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import and_, or_
from src.models import db, WorkOpportunity, Notification, Company
from src.auth import api_key_required
import logging

logger = logging.getLogger(__name__)

opportunities_bp = Blueprint('opportunities', __name__, url_prefix='/api/v1/opportunities')


def serialize_opportunity(opp):
    """Convert opportunity to dict"""
    return opp.to_dict()


@opportunities_bp.route('', methods=['GET'])
@api_key_required
def list_opportunities():
    """
    Get available work opportunities with optional filtering
    
    Query parameters:
    - status: Filter by status (open, assigned, completed, cancelled)
    - type: Filter by opportunity type (maintenance, construction, etc.)
    - region: Filter by railway region
    - railway_line: Filter by railway line
    - start_date: Filter by scheduled start date (ISO format)
    - end_date: Filter by scheduled end date (ISO format)
    - priority: Filter by priority level
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    
    Returns:
        List of opportunities matching the filters
    """
    try:
        # Parse query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Build query
        query = WorkOpportunity.query
        
        # Apply filters
        if request.args.get('status'):
            query = query.filter_by(status=request.args.get('status'))
        
        if request.args.get('type'):
            query = query.filter_by(type=request.args.get('type'))
        
        if request.args.get('region'):
            query = query.filter_by(region=request.args.get('region'))
        
        if request.args.get('railway_line'):
            query = query.filter_by(railway_line=request.args.get('railway_line'))
        
        if request.args.get('priority'):
            query = query.filter_by(priority=request.args.get('priority'))
        
        # Date range filtering
        if request.args.get('start_date'):
            try:
                start_date = datetime.fromisoformat(request.args.get('start_date'))
                query = query.filter(WorkOpportunity.scheduled_end >= start_date)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        if request.args.get('end_date'):
            try:
                end_date = datetime.fromisoformat(request.args.get('end_date'))
                query = query.filter(WorkOpportunity.scheduled_start <= end_date)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format. Use ISO format (YYYY-MM-DD)'}), 400
        
        # Sort by scheduled start date
        query = query.order_by(WorkOpportunity.scheduled_start.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page)
        
        opportunities = [serialize_opportunity(opp) for opp in pagination.items]
        
        return jsonify({
            'opportunities': opportunities,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error listing opportunities: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@opportunities_bp.route('/<int:opportunity_id>', methods=['GET'])
@api_key_required
def get_opportunity(opportunity_id):
    """Get a specific work opportunity"""
    try:
        opportunity = WorkOpportunity.query.get(opportunity_id)
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        return jsonify(serialize_opportunity(opportunity)), 200
        
    except Exception as e:
        logger.error(f'Error retrieving opportunity: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@opportunities_bp.route('/<int:opportunity_id>/assign', methods=['POST'])
@api_key_required
def assign_opportunity(opportunity_id):
    """
    Assign a work opportunity to the requesting company
    
    Body:
    {
        "notes": "Optional assignment notes"
    }
    """
    try:
        opportunity = WorkOpportunity.query.get(opportunity_id)
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        if opportunity.status == 'assigned':
            return jsonify({'error': 'Opportunity already assigned'}), 400
        
        if opportunity.status == 'completed':
            return jsonify({'error': 'Completed opportunity cannot be assigned'}), 400
        
        # Get company
        company = Company.query.get(request.company_id)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Assign to company
        opportunity.assigned_company_id = request.company_id
        opportunity.status = 'assigned'
        
        data = request.get_json() or {}
        if data.get('notes'):
            opportunity.notes = data.get('notes')
        
        db.session.commit()
        
        logger.info(f'Opportunity {opportunity_id} assigned to company {request.company_id}')
        
        return jsonify({
            'message': 'Opportunity assigned successfully',
            'opportunity': serialize_opportunity(opportunity)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error assigning opportunity: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@opportunities_bp.route('/search', methods=['POST'])
@api_key_required
def search_opportunities():
    """
    Advanced search for opportunities
    
    Body:
    {
        "keywords": "search keywords",
        "required_skills": ["skill1", "skill2"],
        "regions": ["London", "Manchester"],
        "priority": "high",
        "date_from": "2026-06-01",
        "date_to": "2026-06-30"
    }
    """
    try:
        data = request.get_json() or {}
        query = WorkOpportunity.query
        
        # Keyword search in title and description
        if data.get('keywords'):
            keyword = f"%{data.get('keywords')}%"
            query = query.filter(
                or_(
                    WorkOpportunity.title.ilike(keyword),
                    WorkOpportunity.description.ilike(keyword)
                )
            )
        
        # Filter by required skills
        if data.get('required_skills'):
            # Filter opportunities where at least one required skill matches
            skills = data.get('required_skills')
            for skill in skills:
                query = query.filter(WorkOpportunity.required_skills.contains(skill))
        
        # Filter by regions
        if data.get('regions'):
            query = query.filter(WorkOpportunity.region.in_(data.get('regions')))
        
        # Filter by priority
        if data.get('priority'):
            query = query.filter_by(priority=data.get('priority'))
        
        # Date range
        if data.get('date_from'):
            try:
                date_from = datetime.fromisoformat(data.get('date_from'))
                query = query.filter(WorkOpportunity.scheduled_end >= date_from)
            except ValueError:
                return jsonify({'error': 'Invalid date_from format'}), 400
        
        if data.get('date_to'):
            try:
                date_to = datetime.fromisoformat(data.get('date_to'))
                query = query.filter(WorkOpportunity.scheduled_start <= date_to)
            except ValueError:
                return jsonify({'error': 'Invalid date_to format'}), 400
        
        # Pagination
        page = data.get('page', 1)
        per_page = min(data.get('per_page', 20), 100)
        
        pagination = query.order_by(
            WorkOpportunity.priority.desc(),
            WorkOpportunity.scheduled_start.asc()
        ).paginate(page=page, per_page=per_page)
        
        opportunities = [serialize_opportunity(opp) for opp in pagination.items]
        
        return jsonify({
            'opportunities': opportunities,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error searching opportunities: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500


@opportunities_bp.route('', methods=['POST'])
@api_key_required
def create_opportunity():
    """Create a new work opportunity (admin only - placeholder)"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        required_fields = ['title', 'type', 'scheduled_start', 'scheduled_end']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse dates
        try:
            scheduled_start = datetime.fromisoformat(data.get('scheduled_start'))
            scheduled_end = datetime.fromisoformat(data.get('scheduled_end'))
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use ISO format'}), 400
        
        opportunity = WorkOpportunity(
            title=data.get('title'),
            description=data.get('description'),
            type=data.get('type'),
            category=data.get('category'),
            railway_line=data.get('railway_line'),
            station=data.get('station'),
            region=data.get('region'),
            location_coordinates=data.get('location_coordinates'),
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            duration_hours=data.get('duration_hours'),
            required_skills=data.get('required_skills', []),
            required_certifications=data.get('required_certifications', []),
            required_equipment=data.get('required_equipment', []),
            priority=data.get('priority', 'medium'),
            budget=data.get('budget'),
            notes=data.get('notes')
        )
        
        db.session.add(opportunity)
        db.session.commit()
        
        logger.info(f'Created opportunity {opportunity.id}')
        
        return jsonify({
            'message': 'Opportunity created successfully',
            'opportunity': serialize_opportunity(opportunity)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating opportunity: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
