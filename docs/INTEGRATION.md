# Integration Guide

## Overview

This guide helps companies integrate Railway Work Access Port into their systems.

## Quick Start Integration

### 1. Setup Your Development Environment

```bash
# Clone repository
git clone https://github.com/Landmind23/Railway-work-access-port.git
cd Railway-work-access-port

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install SDK/Dependencies
pip install -r requirements.txt

# Get API credentials
# - Company ID
# - API Token
```

### 2. Authenticate

```python
import os
os.environ['RAILWAY_API_TOKEN'] = 'your_token_here'
os.environ['API_BASE_URL'] = 'https://api.railway-access-port.com'
```

### 3. Make Your First Request

```python
import requests
import os

token = os.getenv('RAILWAY_API_TOKEN')
base_url = os.getenv('API_BASE_URL', 'http://localhost:5000')

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Get available opportunities
response = requests.get(
    f'{base_url}/api/v1/opportunities',
    headers=headers
)

opportunities = response.json()
print(opportunities)
```

## Common Integration Patterns

### Polling for New Opportunities

```python
import requests
import time
from datetime import datetime, timedelta

def poll_new_opportunities(interval_seconds=300):
    """Poll for new opportunities every 5 minutes"""
    token = os.getenv('RAILWAY_API_TOKEN')
    base_url = os.getenv('API_BASE_URL')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    while True:
        try:
            # Get opportunities from the last 5 minutes
            response = requests.get(
                f'{base_url}/api/v1/opportunities',
                headers=headers,
                params={'status': 'open'}
            )
            
            opportunities = response.json()
            
            # Process each opportunity
            for opp in opportunities['opportunities']:
                process_opportunity(opp)
            
            time.sleep(interval_seconds)
            
        except Exception as e:
            print(f'Error polling: {e}')
            time.sleep(60)

def process_opportunity(opportunity):
    """Your custom logic to process opportunities"""
    print(f"Found opportunity: {opportunity['title']}")
    # Your implementation here
```

### Batch Assignment

```python
def batch_assign_opportunities(opportunity_ids):
    """Assign multiple opportunities"""
    token = os.getenv('RAILWAY_API_TOKEN')
    base_url = os.getenv('API_BASE_URL')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    for opp_id in opportunity_ids:
        try:
            response = requests.post(
                f'{base_url}/api/v1/opportunities/{opp_id}/assign',
                headers=headers,
                json={'notes': f'Batch assigned at {datetime.now()}'}
            )
            
            if response.status_code == 200:
                print(f'✓ Assigned opportunity {opp_id}')
            else:
                print(f'✗ Failed to assign {opp_id}: {response.json()}')
                
        except Exception as e:
            print(f'Error assigning {opp_id}: {e}')
```

### Advanced Search Integration

```python
def search_for_matching_opportunities(skills, regions):
    """Search for opportunities matching company capabilities"""
    token = os.getenv('RAILWAY_API_TOKEN')
    base_url = os.getenv('API_BASE_URL')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    search_body = {
        'required_skills': skills,
        'regions': regions,
        'date_from': (datetime.now()).isoformat(),
        'date_to': (datetime.now() + timedelta(days=90)).isoformat(),
        'page': 1,
        'per_page': 50
    }
    
    response = requests.post(
        f'{base_url}/api/v1/opportunities/search',
        headers=headers,
        json=search_body
    )
    
    return response.json()['opportunities']
```

## Framework-Specific Examples

### Django Integration

```python
# django_app/utils/railway.py
import requests
from django.conf import settings

class RailwayClient:
    def __init__(self):
        self.token = settings.RAILWAY_API_TOKEN
        self.base_url = settings.RAILWAY_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def get_opportunities(self, **filters):
        response = requests.get(
            f'{self.base_url}/api/v1/opportunities',
            headers=self.headers,
            params=filters
        )
        response.raise_for_status()
        return response.json()

# In your Django view
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .utils.railway import RailwayClient

@require_http_methods(["GET"])
def list_opportunities(request):
    client = RailwayClient()
    opportunities = client.get_opportunities(
        status='open',
        region=request.GET.get('region')
    )
    return JsonResponse(opportunities)
```

### FastAPI Integration

```python
# fastapi_app/railway_client.py
import httpx
from typing import List, Optional
from datetime import datetime

class RailwayAsyncClient:
    def __init__(self, token: str, base_url: str):
        self.token = token
        self.base_url = base_url
    
    async def get_opportunities(self, **filters) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.base_url}/api/v1/opportunities',
                headers={'Authorization': f'Bearer {self.token}'},
                params=filters
            )
            response.raise_for_status()
            return response.json()

# In your FastAPI route
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/opportunities")
async def list_opportunities(region: Optional[str] = None):
    client = RailwayAsyncClient(
        token='YOUR_TOKEN',
        base_url='https://api.railway-access-port.com'
    )
    
    try:
        return await client.get_opportunities(region=region, status='open')
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Error Handling

### Retry Logic

```python
import time
from requests.exceptions import RequestException

def make_request_with_retry(url, headers, max_retries=3, backoff_factor=2):
    """Make HTTP request with exponential backoff retry"""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
            
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = backoff_factor ** attempt
            print(f'Attempt {attempt + 1} failed. Retrying in {wait_time}s...')
            time.sleep(wait_time)

# Usage
response = make_request_with_retry(
    'http://localhost:5000/api/v1/opportunities',
    headers={'Authorization': f'Bearer {token}'}
)
```

## Webhook Integration (Future)

When webhooks are available, integrate notifications:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhooks/railway-opportunities', methods=['POST'])
def handle_railway_webhook():
    """Handle incoming opportunity notifications"""
    
    data = request.get_json()
    
    # Verify webhook signature (when implemented)
    verify_webhook_signature(request)
    
    # Process opportunity notification
    event_type = data.get('event_type')  # 'opportunity.created', 'opportunity.assigned'
    opportunity = data.get('opportunity')
    
    if event_type == 'opportunity.created':
        notify_team(opportunity)
    
    return {'status': 'received'}, 200
```

## Testing Your Integration

```python
# test_integration.py
import unittest
import os
from railway_client import RailwayClient

class TestRailwayIntegration(unittest.TestCase):
    
    def setUp(self):
        self.client = RailwayClient(
            token=os.getenv('RAILWAY_API_TOKEN'),
            base_url='http://localhost:5000'
        )
    
    def test_api_health(self):
        """Test API is accessible"""
        response = requests.get(f'{self.client.base_url}/api/v1/health')
        self.assertEqual(response.status_code, 200)
    
    def test_list_opportunities(self):
        """Test listing opportunities"""
        opps = self.client.get_opportunities()
        self.assertIn('opportunities', opps)
    
    def test_authentication(self):
        """Test invalid token handling"""
        response = requests.get(
            f'{self.client.base_url}/api/v1/opportunities',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        self.assertEqual(response.status_code, 401)
```

## Best Practices

1. **Always Use HTTPS in Production**
   - SSL/TLS encryption for all traffic
   - Certificate pinning for extra security

2. **Handle Rate Limits**
   - Implement backoff strategies
   - Monitor rate limit headers
   - Cache when possible

3. **Secure Token Management**
   - Store tokens in secure vaults
   - Rotate tokens regularly
   - Never commit tokens to version control

4. **Error Handling**
   - Implement proper error handling
   - Log errors for debugging
   - Use exponential backoff for retries

5. **Monitoring & Logging**
   - Log all API calls
   - Monitor success/failure rates
   - Alert on anomalies

6. **Documentation**
   - Document your integration
   - Keep API client code version-controlled
   - Maintain integration tests

---

**Last Updated**: May 2026
