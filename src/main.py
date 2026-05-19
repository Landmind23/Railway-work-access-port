"""
Railway Work Access Port - Main Application
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import models and blueprints
from src.models import db
from src.api.opportunities import opportunities_bp


def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///railway_access.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    # CORS
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
    CORS(app, resources={r'/api/*': {'origins': cors_origins}})
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(opportunities_bp)
    
    # Health check endpoint
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '0.1.0'
        }), 200
    
    # API documentation endpoint
    @app.route('/api/v1', methods=['GET'])
    def api_info():
        return jsonify({
            'name': 'Railway Work Access Port API',
            'version': '0.1.0',
            'description': 'API for accessing railway work opportunities and scheduling information',
            'endpoints': {
                'health': '/api/v1/health',
                'opportunities': {
                    'list': 'GET /api/v1/opportunities',
                    'get': 'GET /api/v1/opportunities/{id}',
                    'create': 'POST /api/v1/opportunities',
                    'assign': 'POST /api/v1/opportunities/{id}/assign',
                    'search': 'POST /api/v1/opportunities/search'
                },
                'documentation': '/api/v1/docs'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Internal server error: {str(error)}')
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create tables
    with app.app_context():
        db.create_all()
        logger.info('Database tables created')
    
    logger.info('Application initialized successfully')
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f'Starting Railway Work Access Port on {host}:{port}')
    app.run(host=host, port=port, debug=debug)
