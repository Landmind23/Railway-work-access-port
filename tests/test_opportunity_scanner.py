"""
Unit tests for opportunities endpoints
"""

import unittest
import json
from datetime import datetime, timedelta
from src.main import create_app
from src.models import db, Company, WorkOpportunity, APIToken
from src.auth import generate_api_token, hash_token


class TestOpportunitiesAPI(unittest.TestCase):
    """Test cases for opportunities API"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test company
            self.company = Company(
                name='Test Railway Services',
                email='test@railway.com',
                certifications=['ISO9001'],
                capabilities=['track_maintenance', 'inspection'],
                service_areas=['London', 'Manchester'],
                is_active=True
            )
            db.session.add(self.company)
            db.session.flush()
            
            self.company_id = self.company.id
            
            # Create test API token
            token = generate_api_token()
            token_hash = hash_token(token)
            self.api_token = APIToken(
                company_id=self.company_id,
                token_hash=token_hash,
                name='Test Token',
                expires_at=datetime.utcnow() + timedelta(days=365)
            )
            db.session.add(self.api_token)
            db.session.flush()
            
            # Create test opportunities
            self.opportunity1 = WorkOpportunity(
                title='Track Maintenance - Line A',
                type='maintenance',
                region='London',
                railway_line='Line A',
                scheduled_start=datetime.utcnow() + timedelta(days=5),
                scheduled_end=datetime.utcnow() + timedelta(days=6),
                status='open',
                priority='high',
                required_skills=['track_maintenance']
            )
            
            self.opportunity2 = WorkOpportunity(
                title='Rail Inspection - Line B',
                type='inspection',
                region='Manchester',
                railway_line='Line B',
                scheduled_start=datetime.utcnow() + timedelta(days=10),
                scheduled_end=datetime.utcnow() + timedelta(days=11),
                status='open',
                priority='medium',
                required_skills=['inspection']
            )
            
            db.session.add(self.opportunity1)
            db.session.add(self.opportunity2)
            db.session.commit()
            
            # Store IDs after commit
            self.opportunity1_id = self.opportunity1.id
            self.opportunity2_id = self.opportunity2.id
            
            self.token = token
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_list_opportunities_no_auth(self):
        """Test listing opportunities without authentication"""
        response = self.client.get('/api/v1/opportunities')
        self.assertEqual(response.status_code, 401)
    
    def test_list_opportunities_with_auth(self):
        """Test listing opportunities with authentication"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/api/v1/opportunities', headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['opportunities']), 2)
        self.assertEqual(data['pagination']['total'], 2)
    
    def test_get_single_opportunity(self):
        """Test getting a single opportunity"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get(
            f'/api/v1/opportunities/{self.opportunity1_id}',
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], 'Track Maintenance - Line A')
    
    def test_get_nonexistent_opportunity(self):
        """Test getting non-existent opportunity"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get('/api/v1/opportunities/9999', headers=headers)
        self.assertEqual(response.status_code, 404)
    
    def test_filter_by_region(self):
        """Test filtering opportunities by region"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get(
            '/api/v1/opportunities?region=London',
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['opportunities']), 1)
        self.assertEqual(data['opportunities'][0]['region'], 'London')
    
    def test_filter_by_type(self):
        """Test filtering opportunities by type"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get(
            '/api/v1/opportunities?type=maintenance',
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['opportunities']), 1)
        self.assertEqual(data['opportunities'][0]['type'], 'maintenance')
    
    def test_assign_opportunity(self):
        """Test assigning an opportunity"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post(
            f'/api/v1/opportunities/{self.opportunity1_id}/assign',
            headers=headers,
            json={'notes': 'Test assignment'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['opportunity']['status'], 'assigned')
        self.assertEqual(data['opportunity']['assigned_company_id'], self.company_id)
    
    def test_search_opportunities(self):
        """Test searching opportunities"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post(
            '/api/v1/opportunities/search',
            headers=headers,
            json={
                'keywords': 'Track',
                'regions': ['London']
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['opportunities']), 1)


class TestOpportunityScannerBasics(unittest.TestCase):
    """Basic tests for opportunity scanner"""
    
    def test_module_imports(self):
        """Test that all modules can be imported"""
        from src.models import db, Company, WorkOpportunity
        from src.auth import generate_api_token
        self.assertIsNotNone(db)
        self.assertIsNotNone(Company)
        self.assertIsNotNone(WorkOpportunity)
        self.assertIsNotNone(generate_api_token)


if __name__ == '__main__':
    unittest.main()
