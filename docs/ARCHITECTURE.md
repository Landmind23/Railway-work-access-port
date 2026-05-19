# Architecture Overview

## System Design

Railway Work Access Port is designed with a modular, scalable architecture that separates concerns into distinct layers.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                        │
│              (Companies accessing opportunities)                  │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────────────┐
│                       API Layer (Flask)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │Opportunities │  │  Companies   │  │ Notifications│          │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│              Authentication & Authorization                      │
│  • API Token Validation                                          │
│  • Company Verification                                          │
│  • Request Logging & Audit Trail                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│            Business Logic & Services Layer                       │
│  • Opportunity Matching                                          │
│  • Search & Filtering                                            │
│  • Notification Generation                                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    Data Access Layer                             │
│  • SQLAlchemy ORM                                               │
│  • Query Builders                                                │
│  • Validation & Serialization                                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────┐
│                    Database (PostgreSQL)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Companies   │  │ Opportunities│  │ Notifications│          │
│  │  API Tokens  │  │  Audit Logs  │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Component Description

### 1. API Layer (Flask)
- **Purpose**: Expose RESTful endpoints for client applications
- **Responsibilities**:
  - HTTP request/response handling
  - Request validation
  - Response serialization
- **Key Components**:
  - `src/api/opportunities.py` - Opportunity endpoints
  - `src/main.py` - Application factory and configuration

### 2. Authentication & Authorization
- **Purpose**: Secure API access and track usage
- **Responsibilities**:
  - API token validation
  - Company verification
  - Request logging for audit trails
- **Key Components**:
  - `src/auth.py` - Token management and decorators
  - Models: `APIToken`, `AuditLog`

### 3. Business Logic Layer
- **Purpose**: Implement business rules and operations
- **Responsibilities**:
  - Opportunity filtering and matching
  - Search operations
  - Notification generation
- **Key Components**:
  - `src/services/` - Service classes (future)
  - Database models

### 4. Data Access Layer
- **Purpose**: Interact with database
- **Responsibilities**:
  - Query building and execution
  - Data validation
  - Result serialization
- **Key Components**:
  - `src/models.py` - SQLAlchemy models
  - Flask-SQLAlchemy integration

### 5. Database
- **Purpose**: Persistent storage of application data
- **Technology**: PostgreSQL (or SQLite for development)
- **Key Tables**:
  - `companies` - Company/contractor profiles
  - `work_opportunities` - Available work opportunities
  - `api_tokens` - API authentication tokens
  - `notifications` - Opportunity notifications
  - `audit_logs` - API access audit trail

## Data Models

### Company
Represents a railway company or contractor.

**Fields**:
- Basic info: name, email, phone, description
- Qualifications: certifications, capabilities
- Location: service_areas, address
- Status: is_active

**Relationships**:
- Has many API tokens
- Has many assigned opportunities
- Has many notifications

### WorkOpportunity
Represents a railway work opportunity or maintenance window.

**Fields**:
- Metadata: title, description, type, category
- Location: railway_line, station, region, coordinates
- Schedule: scheduled_start, scheduled_end, duration_hours
- Requirements: required_skills, required_certifications, required_equipment
- Status: status, assigned_company_id, priority
- Additional: budget, notes

**Relationships**:
- Belongs to company (when assigned)
- Has many notifications

### APIToken
Represents an API authentication token.

**Fields**:
- Credentials: token_hash, name
- Lifecycle: expires_at, is_revoked, last_used_at

**Relationships**:
- Belongs to company

### Notification
Represents an opportunity notification to a company.

**Fields**:
- References: company_id, opportunity_id
- Content: notification_type, message
- State: is_read, read_at

**Relationships**:
- Belongs to company
- Belongs to opportunity

### AuditLog
Records all API access for compliance and troubleshooting.

**Fields**:
- Request info: endpoint, method, status_code
- Data: request_data, response_data
- Client: ip_address, user_agent

**Relationships**:
- References company (if applicable)

## API Design

### RESTful Principles
- Resources: opportunities, companies, notifications
- Standard HTTP methods: GET, POST, PUT, DELETE
- Status codes: 200, 201, 400, 401, 404, 500
- JSON request/response bodies

### Authentication
- Bearer token in Authorization header
- Validated on every protected request
- Company isolation (companies can only access their own data)

### Search & Filtering
- Query parameters for simple filters
- POST endpoint for advanced search
- Support for pagination, sorting, and limiting

## Security Considerations

### Authentication
- API tokens are hashed and salted before storage
- Tokens have expiration dates
- Tokens can be revoked
- Last used timestamp tracks activity

### Authorization
- Companies can only see opportunities they have access to
- Companies can only assign opportunities to themselves
- Admin-level operations are restricted

### Data Protection
- All API traffic should use HTTPS in production
- Sensitive data (tokens, credentials) are never logged
- Audit logs track all API access for compliance

### Input Validation
- All inputs are validated before processing
- SQL injection prevention through ORM
- CORS configuration restricts cross-origin requests

## Scalability Considerations

### Database Indexing
Indexes on frequently queried fields:
- `status`, `type`, `region`, `railway_line`, `scheduled_start`
- `company_id`, `is_read` on notifications
- `company_id_audit`, `created_at_audit`, `endpoint` on audit logs

### Pagination
- Default 20 items per page
- Maximum 100 items per page
- Cursor-based or offset-based options

### Caching (Future)
- Opportunity listings (short TTL)
- Company profiles (medium TTL)
- API token validation (short TTL)

### Async Operations (Future)
- Notification generation
- Audit log writing
- Report generation

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Load Balancer                   │
│         (optional)                      │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼──┐     ┌───▼──┐     ┌──▼────┐
│ API  │     │ API  │     │ API   │
│ Pod  │     │ Pod  │     │ Pod   │
│  1   │     │  2   │     │  3    │
└──────┘     └──────┘     └───────┘
    │            │            │
    └────────────┼────────────┘
                 │
         ┌───────▼────────┐
         │   Database     │
         │  (PostgreSQL)  │
         └────────────────┘
```

## Development & Production Environments

### Development
- SQLite database for local testing
- Flask development server
- Auto-reloading on code changes
- Verbose logging

### Production
- PostgreSQL database with backups
- Gunicorn/uWSGI application server
- Nginx reverse proxy
- SSL/TLS encryption
- Rate limiting and DDoS protection

---

**Last Updated**: May 2026
