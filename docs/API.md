# API Documentation - Railway Work Access Port

**Version**: 0.1.0 (MVP)

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

All API requests (except health checks) require Bearer token authentication:

```
Authorization: Bearer YOUR_API_TOKEN
```

## Response Format

All API responses are in JSON format.

### Successful Response (2xx)
```json
{
  "data": {...},
  "message": "Success message"
}
```

### Error Response (4xx/5xx)
```json
{
  "error": "Error message"
}
```

## Endpoints

### Health & Info

#### Health Check
```
GET /api/v1/health
```

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2026-05-19T05:30:00.000000",
  "version": "0.1.0"
}
```

#### API Information
```
GET /api/v1
```

**Response**: `200 OK`
```json
{
  "name": "Railway Work Access Port API",
  "version": "0.1.0",
  "description": "API for accessing railway work opportunities...",
  "endpoints": {...}
}
```

---

## Work Opportunities Endpoints

### List Opportunities

```
GET /api/v1/opportunities
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status: `open`, `assigned`, `completed`, `cancelled` |
| type | string | Filter by type: `maintenance`, `construction`, `inspection`, `urgent_repair` |
| region | string | Filter by railway region (e.g., `London`, `Manchester`) |
| railway_line | string | Filter by railway line name |
| priority | string | Filter by priority: `low`, `medium`, `high`, `critical` |
| start_date | string | Filter opportunities ending after this date (ISO format) |
| end_date | string | Filter opportunities starting before this date (ISO format) |
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |

**Example Request**:
```bash
curl -X GET "http://localhost:5000/api/v1/opportunities?region=London&status=open&page=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: `200 OK`
```json
{
  "opportunities": [
    {
      "id": 1,
      "title": "Track Maintenance - Line A",
      "description": "Routine track maintenance",
      "type": "maintenance",
      "region": "London",
      "railway_line": "Line A",
      "scheduled_start": "2026-06-01T08:00:00",
      "scheduled_end": "2026-06-01T17:00:00",
      "duration_hours": 8.0,
      "required_skills": ["track_maintenance"],
      "required_certifications": ["ADIPS-H"],
      "status": "open",
      "priority": "high",
      "budget": 5000.0,
      "created_at": "2026-05-19T05:30:00",
      "updated_at": "2026-05-19T05:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}
```

---

### Get Single Opportunity

```
GET /api/v1/opportunities/{id}
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | Work opportunity ID |

**Example Request**:
```bash
curl -X GET "http://localhost:5000/api/v1/opportunities/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**: `200 OK`
```json
{
  "id": 1,
  "title": "Track Maintenance - Line A",
  "description": "Routine track maintenance",
  "type": "maintenance",
  "category": "scheduled",
  "railway_line": "Line A",
  "station": "King's Cross",
  "region": "London",
  "location_coordinates": {
    "latitude": 51.5309,
    "longitude": -0.1231
  },
  "scheduled_start": "2026-06-01T08:00:00",
  "scheduled_end": "2026-06-01T17:00:00",
  "duration_hours": 8.0,
  "required_skills": ["track_maintenance", "signaling"],
  "required_certifications": ["ADIPS-H"],
  "required_equipment": ["track_tools", "safety_equipment"],
  "status": "open",
  "assigned_company_id": null,
  "priority": "high",
  "budget": 5000.0,
  "notes": null,
  "created_at": "2026-05-19T05:30:00",
  "updated_at": "2026-05-19T05:30:00"
}
```

**Errors**:
- `404 Not Found`: Opportunity with given ID does not exist

---

### Search Opportunities

```
POST /api/v1/opportunities/search
```

**Request Body**:
```json
{
  "keywords": "track maintenance",
  "required_skills": ["track_maintenance", "signaling"],
  "regions": ["London", "Manchester"],
  "priority": "high",
  "date_from": "2026-06-01",
  "date_to": "2026-06-30",
  "page": 1,
  "per_page": 20
}
```

**Response**: `200 OK` (same structure as list opportunities)

---

### Assign Opportunity

Assign a work opportunity to the requesting company.

```
POST /api/v1/opportunities/{id}/assign
```

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | integer | Work opportunity ID |

**Request Body**:
```json
{
  "notes": "Assignment notes or special requirements"
}
```

**Example Request**:
```bash
curl -X POST "http://localhost:5000/api/v1/opportunities/1/assign" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Ready to start on scheduled date"}'
```

**Response**: `200 OK`
```json
{
  "message": "Opportunity assigned successfully",
  "opportunity": {
    "id": 1,
    "status": "assigned",
    "assigned_company_id": 42,
    ...
  }
}
```

**Errors**:
- `404 Not Found`: Opportunity not found
- `400 Bad Request`: Opportunity already assigned or cannot be assigned (completed/cancelled)

---

### Create Opportunity

Create a new work opportunity. (Admin endpoint - placeholder for MVP)

```
POST /api/v1/opportunities
```

**Request Body**:
```json
{
  "title": "Track Maintenance - Line A",
  "type": "maintenance",
  "description": "Routine track maintenance",
  "category": "scheduled",
  "railway_line": "Line A",
  "station": "King's Cross",
  "region": "London",
  "location_coordinates": {
    "latitude": 51.5309,
    "longitude": -0.1231
  },
  "scheduled_start": "2026-06-01T08:00:00",
  "scheduled_end": "2026-06-01T17:00:00",
  "duration_hours": 8.0,
  "required_skills": ["track_maintenance"],
  "required_certifications": ["ADIPS-H"],
  "required_equipment": ["track_tools"],
  "priority": "high",
  "budget": 5000.0,
  "notes": "Additional notes"
}
```

**Required Fields**:
- `title` (string)
- `type` (string)
- `scheduled_start` (ISO datetime)
- `scheduled_end` (ISO datetime)

**Response**: `201 Created`
```json
{
  "message": "Opportunity created successfully",
  "opportunity": {...}
}
```

---

## Rate Limiting

API rate limit: **1000 requests per hour per API token**

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1621406400
```

---

## Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 404 | Not Found | Resource not found |
| 405 | Method Not Allowed | HTTP method not allowed for this endpoint |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## Data Types & Formats

### DateTime Format
All datetime values use ISO 8601 format with UTC timezone:
```
YYYY-MM-DDTHH:MM:SS.mmmmmm
Example: 2026-06-01T08:00:00.000000
```

### Coordinates Format
Geographic locations use standard latitude/longitude:
```json
{
  "latitude": 51.5309,
  "longitude": -0.1231
}
```

### Arrays
JSON arrays are used for lists of strings:
```json
{
  "required_skills": ["track_maintenance", "signaling"],
  "certifications": ["ISO9001", "ADIPS-H"]
}
```

---

## Common Use Cases

### Find All Maintenance Opportunities Next Month
```bash
curl -X GET "http://localhost:5000/api/v1/opportunities?type=maintenance&start_date=2026-06-01&end_date=2026-06-30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search by Skills and Location
```bash
curl -X POST "http://localhost:5000/api/v1/opportunities/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "required_skills": ["track_maintenance"],
    "regions": ["London", "Manchester"]
  }'
```

### Assign Opportunity
```bash
curl -X POST "http://localhost:5000/api/v1/opportunities/123/assign" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Team assigned and ready"}'
```

---

## Support

For technical support or API issues, contact: support@railway-access-port.com

**Documentation Last Updated**: May 2026
