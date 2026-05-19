# Data Governance & Privacy Policy

## Overview

Railway Work Access Port is committed to protecting the privacy and security of all data processed through our platform. This policy outlines our governance framework, data protection practices, and compliance standards.

## Data Classification

### Public Data
- General company information (company name, contact information)
- Publicly available opportunity listings (title, type, location)

### Internal Data
- Company certifications and capabilities
- Service areas and operational regions
- API token names and metadata

### Confidential Data
- API tokens (fully hashed and never exposed after creation)
- Opportunity details (requirements, budget, specific locations)
- Assignment history and company performance data
- Company-specific notifications and preferences

### Sensitive Personal Data
- Contact person names and direct contact information
- IP addresses from API requests
- User agent information

## Data Protection Standards

### GDPR Compliance
- **Data Subject Rights**: Right to access, correction, deletion, portability
- **Privacy by Design**: Data protection integrated into all systems
- **Data Minimization**: Collect only necessary data
- **Purpose Limitation**: Data used only for stated purposes
- **Storage Limitation**: Data retained only as long as necessary

### UK Data Protection Act 2018
- Implements GDPR in UK law
- Extends GDPR principles to non-EU data
- Enhanced protections for British citizens

### Railway Industry Data Standards
- Compliance with Network Rail data requirements
- Following industry-standard data classification
- Alignment with railway safety and operational needs

## Data Retention

### Policy
- **Completed Opportunities**: 7 years (regulatory requirement)
- **Active Opportunities**: Duration of assignment plus 2 years
- **Company Profiles**: While company is active, plus 2 years
- **API Tokens**: Life of token plus 1 year after revocation
- **Audit Logs**: 3 years (compliance requirement)
- **Notifications**: 90 days after read or creation

### Deletion Procedures
- Automated deletion for expired data
- Manual deletion requests processed within 30 days
- Secure deletion methods (multiple-pass overwrite)
- Deletion verification and audit trail

## Access Control

### Role-Based Access Control (RBAC)
- **Company Users**: Access their own profile and assigned opportunities
- **Administrators**: Full system access
- **Auditors**: Read-only access to audit logs and anonymized data

### Data Access Restrictions
- Companies can only see opportunities they're eligible for
- Companies cannot see other companies' data
- API tokens are immediately revoked upon company inactivation

### Authorization Levels
1. **Public**: No authentication required (health checks only)
2. **Authenticated**: Valid API token required
3. **Company**: Access to company's own data
4. **Admin**: Full system access

## Security Measures

### Infrastructure Security
- HTTPS encryption for all data in transit
- TLS 1.2+ minimum for connections
- SSL certificate pinning (future implementation)
- VPN access for administrative functions

### Data Encryption
- Encryption at rest using AES-256
- Database encryption with transparent data encryption (TDE)
- Hashed API tokens (SHA-256 with salt)
- Encrypted backups

### Access Monitoring
- All API requests logged with timestamp, company, endpoint, status
- Unusual access patterns detected and flagged
- IP-based threat detection (future implementation)
- Rate limiting to prevent abuse (1000 req/hour/token)

### Incident Response
- Security incidents logged and tracked
- 24-hour notification requirement for breaches
- Root cause analysis for all incidents
- Remediation tracking and verification

## Audit & Compliance

### Audit Logging
All API access is logged including:
- Timestamp (UTC)
- Company ID
- API endpoint
- HTTP method
- Status code
- Request/response size
- Client IP address
- User agent

### Audit Retention
- Audit logs retained for 3 years
- Immutable audit log storage (append-only)
- Regular audit log reviews
- Compliance audits quarterly

### Compliance Certifications
- ISO 27001 (information security management) - planned
- SOC 2 Type II - planned
- GDPR compliance verified annually
- Data Protection Impact Assessments (DPIA) conducted

## Data Subject Rights

### Right to Access
- Companies can request their data via API
- Export functionality available (future)
- Response within 30 days

### Right to Rectification
- Companies can update their profile information
- Data corrections logged for audit trail

### Right to Erasure
- Companies can request data deletion
- Data deleted according to retention policy
- Immediate deletion possible for unneeded data

### Right to Restrict Processing
- Temporarily restrict certain data processing
- Notification to company of restrictions

### Right to Data Portability
- Export data in machine-readable format (future)
- Transfer data to another platform (future)

### Right to Object
- Companies can object to data processing
- Legitimate interest assessment available

## Third-Party Data Sharing

### No Selling of Data
- Railway Work Access Port does not sell user data
- No sharing with marketing companies
- No data sharing with brokers

### Limited Sharing
- Sharing only with:
  - Service providers (under data processing agreements)
  - Legal authorities (with proper authorization)
  - Audit firms (anonymized data)
  - Security vendors (for threat detection)

### Data Processing Agreements
- All third parties execute Data Processing Agreements (DPA)
- Sub-processor list maintained and updated
- DPA compliance audited annually

## Cookies & Tracking

### No Tracking
- Railway Work Access Port API does not use cookies
- No tracking pixels or analytics
- API-only, no web-based tracking
- No third-party analytics

### Minimal Logging
- Logs limited to necessary operational data
- No session tracking beyond API requests
- Logs do not track user behavior

## Policy Updates

### Change Management
- Policy updates announced 30 days in advance
- Companies notified of material changes
- Opportunity to opt-out of service

### Version History
- Current Version: 1.0 (May 2026)
- Previous versions available upon request
- All changes documented with dates

## Contact & Support

### Data Protection Officer
- Email: dpo@railway-access-port.com
- Phone: +44 (0)20 XXXX XXXX
- Response time: 5 business days

### Data Subject Rights Requests
- Email: privacy@railway-access-port.com
- Include: Request type, company ID, specific data
- Response time: 30 days

### Complaints
- To Railway Work Access Port: compliance@railway-access-port.com
- To Data Protection Authority: [Your local DPA website]

## Additional Resources

- [Privacy Policy](./PRIVACY.md) - Full privacy policy
- [Security Guidelines](./SECURITY.md) - Security best practices
- [GDPR Compliance Guide](./GDPR.md) - GDPR-specific information

---

**Version**: 1.0
**Last Updated**: May 2026
**Next Review**: May 2027
