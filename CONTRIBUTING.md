# Contributing to Railway-work-access-port

Thank you for interest in contributing to Railway Work Access Port! This document provides guidelines and instructions for contributing.

## Getting Started

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Landmind23/Railway-work-access-port.git
cd Railway-work-access-port

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest discover -s tests -v
```

### Code Style

- **Python**: Follow PEP 8
- **Formatting**: Use `black` for code formatting
- **Linting**: Use `flake8` for linting
- **Type Hints**: Add type hints to all function signatures

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Check for type errors
mypy src/ --ignore-missing-imports
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bugfix-name
```

Branch naming conventions:
- Features: `feature/feature-description`
- Bug fixes: `bugfix/bug-description`
- Documentation: `docs/doc-description`

### 2. Make Changes

- Write clean, readable code
- Add docstrings to functions and classes
- Keep functions small and focused
- Follow the existing code style

### 3. Write Tests

All new features must include tests with minimum 80% code coverage.

```python
# tests/test_new_feature.py
import unittest
from src.models import db
from src.main import create_app

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_feature(self):
        # Your test here
        self.assertTrue(True)
```

Run tests:
```bash
python -m unittest discover -s tests -v

# With coverage
pip install coverage
coverage run -m unittest discover -s tests
coverage report
```

### 4. Format and Lint

```bash
black src/ tests/
flake8 src/ tests/
```

### 5. Commit Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feature: Add search functionality for opportunities

- Implement POST /api/v1/opportunities/search endpoint
- Add keyword and skill-based filtering
- Add comprehensive tests
- Update API documentation"
```

Commit message format:
- `feature:` for new features
- `bugfix:` for bug fixes
- `docs:` for documentation
- `test:` for test additions
- `refactor:` for code refactoring

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Guidelines

### PR Description

Your PR should include:
- Clear description of changes
- Link to related issues
- Any breaking changes
- Testing performed
- Screenshots (if UI changes)

### PR Template

```markdown
## Description
Brief description of the changes.

## Related Issues
Closes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Integration tests passed
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass (`python -m unittest discover -s tests -v`)
- [ ] Linting passes (`flake8 src/ tests/`)
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Code Review Process

1. At least one maintainer reviews the PR
2. Feedback provided in comments
3. Address feedback in additional commits
4. After approval, PR is merged

## Reporting Issues

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and logs

### Feature Requests

Include:
- Description of desired feature
- Use case and motivation
- Proposed implementation (if applicable)
- Any alternatives considered

## Code Structure

```
railway-work-access-port/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application factory
│   ├── models.py               # Database models
│   ├── auth.py                 # Authentication logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── opportunities.py    # Opportunity endpoints
│   │   └── ...
│   ├── services/               # Business logic (future)
│   └── utils/                  # Utility functions (future)
├── tests/
│   ├── __init__.py
│   ├── test_opportunity_scanner.py  # API tests
│   └── ...
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── README.md                   # Project README
└── .gitignore                  # Git ignore file
```

## Documentation

### API Documentation
- Update `docs/API.md` for endpoint changes
- Include examples and error codes
- Document all parameters and response fields

### Code Comments
- Comment complex logic
- Use docstrings for functions/classes
- Keep comments up-to-date with code

### README
- Update `README.md` if you add new features
- Include setup instructions for new features

## Testing Standards

### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Aim for >80% coverage

### Integration Tests
- Test API endpoints end-to-end
- Use test database
- Clean up after tests

### Test Naming
- Use descriptive names: `test_list_opportunities_filters_by_region`
- Group related tests in classes
- Use `setUp` and `tearDown` for initialization

## Performance Considerations

- Write efficient database queries
- Avoid N+1 queries
- Use indexes appropriately
- Profile code for bottlenecks

## Security Considerations

- Never commit secrets or credentials
- Validate all inputs
- Sanitize database queries (use ORM)
- Follow OWASP top 10
- Report security issues privately

## Documentation Standards

All public functions should have docstrings:

```python
def list_opportunities(page: int = 1, per_page: int = 20) -> dict:
    """
    List available work opportunities with pagination.
    
    Args:
        page: Page number (1-indexed)
        per_page: Items per page (1-100)
        
    Returns:
        Dictionary with opportunities and pagination info
        
    Raises:
        ValueError: If parameters are invalid
    """
```

## Merge Conflicts

If your branch has conflicts:

```bash
git fetch origin
git rebase origin/main

# Resolve conflicts in your editor
git add .
git rebase --continue
git push --force origin feature/your-feature-name
```

## Questions or Need Help?

- Open an issue with your question
- Check existing issues for similar questions
- Contact maintainers: maintainers@railway-access-port.com

---

Thank you for contributing!

**Last Updated**: May 2026
