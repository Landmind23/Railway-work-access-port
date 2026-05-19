# Authentication Guide

## Overview

Railway Work Access Port uses API token-based authentication. Every API request (except health checks) must include a valid API token in the Authorization header.

## Getting Started

### Step 1: Create a Company Account

Contact the Railway Work Access Port administration team to register your company. You'll receive:
- Company ID
- Company credentials

### Step 2: Generate an API Token

API tokens are created by authorized administrators. Each token is:
- Unique and cryptographically secure
- Associated with a specific company
- Has an expiration date
- Can be revoked at any time

### Step 3: Use the Token

Include your token in every API request:

```bash
curl -X GET "http://localhost:5000/api/v1/opportunities" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

## Token Management

### Token Format
```
Authorization: Bearer <token>
```

Where `<token>` is a 43-character alphanumeric string.

### Token Lifecycle
- **Created**: Token is generated and can be used immediately
- **Active**: Token is valid and can authenticate requests
- **Expired**: Token can no longer be used after expiration date
- **Revoked**: Token has been disabled and cannot be used

### Best Practices

1. **Secure Storage**
   - Store tokens securely (e.g., environment variables, secure vaults)
   - Never commit tokens to version control
   - Use `.env` files locally with `.gitignore`

2. **Token Rotation**
   - Rotate tokens periodically (recommended: every 90 days)
   - Revoke old tokens after rotation
   - Maintain separate tokens for different environments

3. **Access Control**
   - Use different tokens for different applications
   - Limit token permissions to what's needed
   - Monitor token usage for unusual activity

4. **Incident Response**
   - If a token is compromised, revoke it immediately
   - Generate a new token
   - Review audit logs for unauthorized access

## Error Handling

### Missing Token
```
Status: 401 Unauthorized
Response: {"error": "Missing API token"}
```

### Invalid Token
```
Status: 401 Unauthorized
Response: {"error": "Invalid or expired API token"}
```

### Expired Token
```
Status: 401 Unauthorized
Response: {"error": "Invalid or expired API token"}
```

### Revoked Token
```
Status: 401 Unauthorized
Response: {"error": "Invalid or expired API token"}
```

## Integration Examples

### Python
```python
import requests

token = "YOUR_API_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "http://localhost:5000/api/v1/opportunities",
    headers=headers
)
```

### JavaScript/Node.js
```javascript
const token = "YOUR_API_TOKEN";
const headers = {
  "Authorization": `Bearer ${token}`
};

fetch("http://localhost:5000/api/v1/opportunities", {
  method: "GET",
  headers: headers
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL
```bash
token="YOUR_API_TOKEN"
curl -X GET "http://localhost:5000/api/v1/opportunities" \
  -H "Authorization: Bearer $token"
```

### Postman
1. Open Postman
2. Create a new request
3. Go to Authorization tab
4. Select "Bearer Token" type
5. Enter your token
6. Make the request

## Environment Configuration

### Development Environment
Create a `.env` file in your project root:

```env
RAILWAY_API_TOKEN=YOUR_DEV_TOKEN
API_BASE_URL=http://localhost:5000
```

Use in your code:
```python
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('RAILWAY_API_TOKEN')
```

### Production Environment
Use a secure secrets management system:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Environment variables on your hosting platform

Never hardcode tokens in source code!

## Support

For authentication issues:
1. Check that your token is correctly formatted
2. Verify the token hasn't expired
3. Ensure the token is for an active company
4. Contact support@railway-access-port.com for assistance

---

**Last Updated**: May 2026
