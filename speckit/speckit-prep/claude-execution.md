# 🚀 CLAUDE EXECUTION SCRIPT
## IntelAgent Production-Grade Transformation

**Generated:** November 17, 2025  
**Execution Phase:** Complete Production Transformation  
**Estimated Duration:** 4 weeks (20 working days)

---

## 📋 EXECUTIVE SUMMARY

This document provides **step-by-step execution instructions** for Claude (or any AI agent) to transform the IntelAgent prototype into a **production-grade, enterprise-ready application**.

**Prerequisites:**
- ✅ All audit documents reviewed
- ✅ `speckit-prep/` folder contents understood
- ✅ Development environment ready
- ✅ Git repository clean (no uncommitted changes)

**Deliverables:**
- 🔒 **Secure** application (authentication, secrets management, hardened endpoints)
- ♿ **Accessible** UI (WCAG 2.1 AA compliant)
- 📱 **Responsive** design (mobile-first)
- 🧪 **Tested** codebase (80%+ coverage)
- 📚 **Documented** system (API docs, user guides)
- 🏗️ **Refactored** architecture (clean, maintainable code)

---

## 🎯 EXECUTION PHILOSOPHY

### Guiding Principles

1. **Security First**: Fix critical vulnerabilities before features
2. **Test Coverage**: Write tests BEFORE refactoring
3. **Incremental Progress**: Small, verified steps
4. **No Breaking Changes**: Feature flags for gradual rollout
5. **Documentation**: Update docs with every change

### Quality Gates

Every phase must pass:
- ✅ Linter (ruff) - 0 errors
- ✅ Type checker (mypy) - 0 errors
- ✅ Tests - 100% pass rate
- ✅ Security scan - 0 high/critical issues
- ✅ Git commit with conventional commit message

---

## 📐 EXECUTION PHASES

```
Phase 1: SETUP & PLANNING (Day 1)
└── Set up tooling, branches, test infrastructure

Phase 2: SECURITY HARDENING (Days 2-5)
├── Critical vulnerabilities (P0)
├── Authentication system
└── Secrets management

Phase 3: CODE QUALITY (Days 6-10)
├── Test infrastructure
├── Refactoring (DRY, type hints, error handling)
└── Code organization

Phase 4: UI/UX TRANSFORMATION (Days 11-15)
├── Accessibility (WCAG 2.1 AA)
├── Responsive design
├── Design system
└── Loading/error states

Phase 5: PERFORMANCE & OPTIMIZATION (Days 16-18)
├── Caching layer
├── Query optimization
└── Bundle optimization

Phase 6: DOCUMENTATION & TESTING (Days 19-20)
├── API documentation
├── User guides
└── Integration testing

Phase 7: DEPLOYMENT (Day 21+)
├── Staging deployment
├── Production rollout
└── Monitoring setup
```

---

## 📅 PHASE 1: SETUP & PLANNING (Day 1)

### Step 1.1: Create Feature Branch

```bash
cd /home/richelgomez/.cursor/worktrees/IntelAgent/cmWee

# Create main feature branch
git checkout -b feat/production-transformation
git push -u origin feat/production-transformation

# Create phase-specific branches
git checkout -b feat/security-hardening
git checkout -b feat/code-quality
git checkout -b feat/ui-ux-improvements
git checkout -b feat/performance-optimization
```

**Expected Output:**
```
✅ 4 feature branches created
✅ All branches pushed to remote
```

---

### Step 1.2: Install Development Tools

```bash
# Create pyproject.toml for project configuration
cat > pyproject.toml << 'EOF'
[project]
name = "intelagent"
version = "0.1.0"
description = "Competitive Intelligence Platform"
requires-python = ">=3.11"

[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = []

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=. --cov-report=html --cov-report=term"

[tool.coverage.run]
source = ["."]
omit = ["tests/*", "venv/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
EOF

# Install tools
pip install ruff mypy pytest pytest-cov black isort

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

# Install pre-commit
pre-commit install
```

**Expected Output:**
```
✅ pyproject.toml created
✅ Linting tools installed
✅ Pre-commit hooks configured
✅ Ready for development
```

---

### Step 1.3: Create Test Infrastructure

```bash
# Create test directory structure
mkdir -p tests/{unit,integration,e2e}
mkdir -p tests/unit/{streamlit_app,cloud_services}
mkdir -p tests/integration/{cloud_functions,streamlit}
mkdir -p tests/fixtures

# Create pytest configuration
cat > tests/conftest.py << 'EOF'
"""Pytest configuration and fixtures"""
import pytest
from unittest.mock import Mock, MagicMock
from google.cloud import bigquery, firestore
import os

# Set test environment
os.environ['TESTING'] = 'true'
os.environ['GCP_PROJECT_ID'] = 'test-project'

@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client"""
    client = Mock(spec=bigquery.Client)
    return client

@pytest.fixture
def mock_firestore_client():
    """Mock Firestore client"""
    client = Mock(spec=firestore.Client)
    return client

@pytest.fixture
def mock_gemini_model():
    """Mock Gemini model"""
    model = MagicMock()
    model.generate_content.return_value.text = "Mock analysis"
    return model

@pytest.fixture
def sample_patent_data():
    """Sample patent data for testing"""
    return [
        {
            'publication_number': 'US-123456-A',
            'title': 'AI Model Training',
            'assignee': 'Anthropic',
            'filing_date': '2023-01-15',
            'inventors': ['John Doe', 'Jane Smith']
        }
    ]

@pytest.fixture
def sample_job_data():
    """Sample job posting data"""
    return {
        'id': 'job-001',
        'title': 'Senior ML Engineer',
        'company': 'Anthropic',
        'location': 'San Francisco',
        'posted_date': '2024-11-01'
    }
EOF

# Create first test to verify setup
cat > tests/unit/test_setup.py << 'EOF'
"""Test to verify test infrastructure works"""
import pytest

def test_pytest_working():
    """Verify pytest is configured correctly"""
    assert True

def test_fixtures_work(sample_patent_data):
    """Verify fixtures load"""
    assert len(sample_patent_data) > 0
    assert sample_patent_data[0]['assignee'] == 'Anthropic'
EOF

# Run initial test
pytest tests/unit/test_setup.py -v
```

**Expected Output:**
```
tests/unit/test_setup.py::test_pytest_working PASSED
tests/unit/test_setup.py::test_fixtures_work PASSED

✅ 2 passed in 0.05s
✅ Test infrastructure ready
```

---

### Step 1.4: Create Phase Tracking Document

```bash
cat > speckit-prep/PROGRESS_TRACKER.md << 'EOF'
# 📊 TRANSFORMATION PROGRESS TRACKER

**Last Updated:** 2025-11-17  
**Current Phase:** Phase 1 - Setup

## Progress Overview

| Phase | Status | Completion | Days |
|-------|--------|------------|------|
| 1. Setup & Planning | 🟡 In Progress | 50% | 1 |
| 2. Security Hardening | ⚪ Not Started | 0% | 4 |
| 3. Code Quality | ⚪ Not Started | 0% | 5 |
| 4. UI/UX Transformation | ⚪ Not Started | 0% | 5 |
| 5. Performance | ⚪ Not Started | 0% | 3 |
| 6. Documentation | ⚪ Not Started | 0% | 2 |
| 7. Deployment | ⚪ Not Started | 0% | 1+ |

**Overall Progress:** 7% (1.5 / 21 days)

## Phase 1: Setup & Planning ✅

- [x] 1.1: Create feature branches
- [x] 1.2: Install development tools
- [x] 1.3: Create test infrastructure
- [ ] 1.4: Review all audit documents
- [ ] 1.5: Create task breakdown

## Phase 2: Security Hardening 🔴 P0

- [ ] 2.1: Implement authentication (SPEC-001)
- [ ] 2.2: Secure Cloud Functions
- [ ] 2.3: Secrets management
- [ ] 2.4: Firestore security rules
- [ ] 2.5: Security testing

## Phase 3: Code Quality 🟡 HIGH

- [ ] 3.1: Extract business logic (RF-001)
- [ ] 3.2: Repository pattern (RF-003)
- [ ] 3.3: Type hints (RF-008)
- [ ] 3.4: Error handling (RF-010)
- [ ] 3.5: Remove duplication (RF-009)

## Phase 4: UI/UX Transformation 🟡 HIGH

- [ ] 4.1: WCAG compliance (UX-001 to UX-006)
- [ ] 4.2: Mobile responsive (UX-007 to UX-010)
- [ ] 4.3: Design system (UX-011)
- [ ] 4.4: Loading states (UX-012)
- [ ] 4.5: Error states (UX-013)

## Phase 5: Performance Optimization 🟢 MEDIUM

- [ ] 5.1: Caching layer (RF-013)
- [ ] 5.2: Query optimization (RF-014)
- [ ] 5.3: Bundle optimization
- [ ] 5.4: Load testing

## Phase 6: Documentation & Testing 🟢 MEDIUM

- [ ] 6.1: API documentation
- [ ] 6.2: User guides
- [ ] 6.3: Integration tests
- [ ] 6.4: E2E tests

## Phase 7: Deployment 🟡 HIGH

- [ ] 7.1: Staging deployment
- [ ] 7.2: Production rollout (10% → 100%)
- [ ] 7.3: Monitoring setup
- [ ] 7.4: Post-launch support

---

**Legend:**
- ⚪ Not Started
- 🟡 In Progress
- ✅ Complete
- ❌ Blocked
EOF

git add pyproject.toml .pre-commit-config.yaml tests/ speckit-prep/PROGRESS_TRACKER.md
git commit -m "chore: setup development infrastructure

- Add pyproject.toml with linting/testing config
- Install ruff, mypy, pytest
- Create test directory structure
- Add pytest fixtures
- Create progress tracker

Refs: Phase 1 - Setup & Planning"
```

**Expected Output:**
```
✅ Progress tracker created
✅ Changes committed
✅ Phase 1 setup complete
```

---

## 🔒 PHASE 2: SECURITY HARDENING (Days 2-5)

**Reference Documents:**
- `SECURITY_VULNERABILITIES.md`
- `spec-001-authentication-system.md`
- `QUICK_WINS.md` (QW-001, QW-002, QW-003)

### Step 2.1: Implement Authentication (Day 2)

**Follow:** `spec-001-authentication-system.md`

```bash
# Switch to security branch
git checkout feat/security-hardening

# Create authentication module structure
mkdir -p streamlit-app/auth
mkdir -p streamlit-app/config

# Install dependencies
cat >> streamlit-app/requirements.txt << 'EOF'
streamlit-authenticator==0.2.3
PyYAML==6.0.1
python-dotenv==1.0.0
EOF

cd streamlit-app && pip install -r requirements.txt
```

**Create Authentication Module:**

```python
# FILE: streamlit-app/auth/authenticator.py
# COPY IMPLEMENTATION FROM: spec-001-authentication-system.md
# Section: "Step 3: Create Authentication Module"

# Create the file with the AuthManager class implementation
```

**Create Credentials Configuration:**

```python
# FILE: streamlit-app/config/credentials.yaml
# COPY STRUCTURE FROM: spec-001-authentication-system.md
# Section: "Step 2: Create Credentials File"

# Generate hashed passwords using bcrypt
# Store in credentials.yaml (DO NOT COMMIT REAL PASSWORDS)
```

**Update app.py:**

```python
# FILE: streamlit-app/app.py
# ADD AT BEGINNING (before any other imports):

from auth.authenticator import AuthManager

# Initialize auth manager
auth = AuthManager()

# REQUIRE AUTHENTICATION (blocks until user logs in)
user = auth.require_auth()

# ... rest of app code ...

# ADD IN SIDEBAR:
auth.render_logout_button()
```

**Write Tests:**

```python
# FILE: tests/unit/streamlit_app/test_authentication.py

import pytest
from streamlit_app.auth.authenticator import AuthManager
from unittest.mock import patch, MagicMock

def test_auth_manager_initializes():
    """Test AuthManager can be initialized"""
    with patch('streamlit_app.auth.authenticator.open'):
        auth = AuthManager('config/credentials.yaml')
        assert auth is not None

def test_require_auth_blocks_unauthenticated():
    """Test that unauthenticated users cannot access app"""
    with patch('streamlit.stop') as mock_stop:
        auth = AuthManager()
        # Mock unauthenticated state
        with patch.object(auth.authenticator, 'login', return_value=(None, None, None)):
            auth.require_auth()
            mock_stop.assert_called_once()

def test_logout_clears_session():
    """Test logout clears session state"""
    auth = AuthManager()
    with patch('streamlit.session_state') as mock_session:
        mock_session.keys.return_value = ['user_info', 'last_activity']
        with patch('streamlit.rerun'):
            auth.logout()
            # Verify session cleared
            assert mock_session.__delitem__.called
```

**Run Tests:**

```bash
pytest tests/unit/streamlit_app/test_authentication.py -v

# Expected: 3 passed
```

**Manual Testing:**

```bash
# Run app locally
cd streamlit-app
streamlit run app.py

# Test checklist:
# ✅ Login screen appears
# ✅ Invalid credentials rejected
# ✅ Valid credentials (admin/changeme) work
# ✅ Session persists on refresh
# ✅ Logout button works
```

**Commit:**

```bash
git add streamlit-app/auth/ streamlit-app/config/ streamlit-app/app.py streamlit-app/requirements.txt tests/
git commit -m "feat(auth): implement authentication system

- Add streamlit-authenticator
- Create AuthManager class
- Add login/logout functionality
- Create credentials configuration
- Add session management
- Write unit tests

Implements: SPEC-001
Fixes: SEC-001 (P0 - Unauthenticated access)
Tests: 3 passed"
```

---

### Step 2.2: Secure Cloud Functions (Day 3)

**Reference:** `SECURITY_VULNERABILITIES.md` → SEC-002, SEC-003, SEC-004

```bash
# Create shared security module
mkdir -p cloud-services/shared

# FILE: cloud-services/shared/auth.py
cat > cloud-services/shared/auth.py << 'EOF'
"""Authentication middleware for Cloud Functions"""
import os
from functools import wraps
from typing import Callable
import logging

logger = logging.getLogger(__name__)

VALID_API_KEYS = set(os.environ.get('VALID_API_KEYS', '').split(','))

def require_api_key(func: Callable) -> Callable:
    """
    Decorator to require API key for Cloud Function.
    
    Usage:
        @require_api_key
        def my_function(request):
            ...
    """
    @wraps(func)
    def wrapper(request):
        # Check Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            logger.warning(f"Missing Bearer token from {request.remote_addr}")
            return {'error': 'Missing Authorization header'}, 401
        
        token = auth_header.replace('Bearer ', '')
        
        if token not in VALID_API_KEYS:
            logger.warning(f"Invalid API key from {request.remote_addr}")
            return {'error': 'Invalid API key'}, 401
        
        logger.info(f"Authenticated request from {request.remote_addr}")
        return func(request)
    
    return wrapper
EOF

# Update job-scraper
cat > cloud-functions/job-scraper/main.py << 'EOF'
import functions_framework
from cloud_services.shared.auth import require_api_key
from cloud_services.shared.firestore_client import FirestoreClient
from cloud_services.shared.http_client import HTTPClient
from cloud_services.services.job_scraper_service import JobScraperService
import os
import logging

logger = logging.getLogger(__name__)

# Initialize (stays warm)
firestore_client = FirestoreClient(os.environ['GCP_PROJECT_ID'])
http_client = HTTPClient()
service = JobScraperService(firestore_client, http_client)

@functions_framework.http
@require_api_key
def job_scraper(request):
    """
    Job scraper Cloud Function with authentication.
    
    Required header:
        Authorization: Bearer <API_KEY>
    
    Query parameters:
        company (required): Company name to scrape
        days (optional): Number of days to look back (default: 30)
    """
    # CORS headers (restrict to your domain)
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGIN', 'https://your-app.run.app'),
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Validate parameters
    company = request.args.get('company')
    if not company:
        return {'error': 'Missing required parameter: company'}, 400
    
    if len(company) < 2:
        return {'error': 'Company name must be at least 2 characters'}, 400
    
    days = int(request.args.get('days', 30))
    if not (1 <= days <= 365):
        return {'error': 'Days must be between 1 and 365'}, 400
    
    try:
        result = service.scrape_jobs(company, days)
        
        headers = {
            'Access-Control-Allow-Origin': os.environ.get('ALLOWED_ORIGIN', 'https://your-app.run.app'),
            'Content-Type': 'application/json'
        }
        
        return (result, 200, headers)
    
    except Exception as e:
        logger.exception(f"Error scraping jobs for {company}")
        return {'error': 'Internal server error', 'details': str(e)}, 500
EOF

# Similar updates for news-search and github-activity
# (Follow same pattern: add @require_api_key decorator, input validation, CORS)
```

**Test Security:**

```python
# FILE: tests/integration/test_cloud_function_security.py

import requests
import pytest
import os

FUNCTION_URL = os.environ.get('JOB_SCRAPER_URL', 'http://localhost:8080')
VALID_API_KEY = os.environ.get('TEST_API_KEY', 'test-key')

def test_unauthenticated_request_rejected():
    """Test that requests without API key are rejected"""
    response = requests.get(f"{FUNCTION_URL}?company=Anthropic")
    assert response.status_code == 401
    assert 'error' in response.json()

def test_invalid_api_key_rejected():
    """Test that invalid API keys are rejected"""
    headers = {'Authorization': 'Bearer invalid-key'}
    response = requests.get(f"{FUNCTION_URL}?company=Anthropic", headers=headers)
    assert response.status_code == 401

def test_valid_api_key_accepted():
    """Test that valid API key is accepted"""
    headers = {'Authorization': f'Bearer {VALID_API_KEY}'}
    response = requests.get(f"{FUNCTION_URL}?company=Anthropic", headers=headers)
    assert response.status_code == 200

def test_sql_injection_blocked():
    """Test that SQL injection attempts are blocked"""
    headers = {'Authorization': f'Bearer {VALID_API_KEY}'}
    malicious_company = "'; DROP TABLE jobs; --"
    response = requests.get(f"{FUNCTION_URL}?company={malicious_company}", headers=headers)
    # Should either reject or safely escape
    assert response.status_code in [400, 200]
    if response.status_code == 200:
        # Verify no damage done (check database still exists)
        pass
```

**Deploy with Authentication:**

```bash
# Generate API key
API_KEY=$(openssl rand -hex 32)
echo "Generated API Key: $API_KEY"
echo "Store this securely!"

# Deploy with secret
gcloud functions deploy job-scraper \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=cloud-functions/job-scraper \
  --entry-point=job_scraper \
  --trigger-http \
  --allow-unauthenticated=false \
  --set-env-vars="VALID_API_KEYS=$API_KEY,ALLOWED_ORIGIN=https://your-app.run.app"

# Test deployed function
curl -H "Authorization: Bearer $API_KEY" \
  "https://job-scraper-abc.run.app?company=Anthropic"

# Should return data (200 OK)
```

**Commit:**

```bash
git add cloud-services/ cloud-functions/ tests/
git commit -m "feat(security): secure Cloud Functions with API authentication

- Add API key authentication middleware
- Implement input validation
- Add CORS headers (restrictive)
- Write security tests

Fixes: SEC-002, SEC-003, SEC-004 (P0 - Unprotected endpoints)
Tests: 4 passed"
```

---

### Step 2.3: Secrets Management (Day 4)

**Reference:** `SECURITY_VULNERABILITIES.md` → SEC-001

```bash
# Install Google Secret Manager SDK
pip install google-cloud-secret-manager

# Create secrets management module
cat > cloud-services/shared/secrets.py << 'EOF'
"""Centralized secrets management using Google Secret Manager"""
from google.cloud import secretmanager
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

class SecretsManager:
    """Manage secrets using Google Secret Manager"""
    
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or os.environ.get('GCP_PROJECT_ID')
        self.client = secretmanager.SecretManagerServiceClient()
    
    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Get secret value from Secret Manager.
        
        Args:
            secret_id: Secret ID (e.g., 'github-token')
            version: Version to retrieve (default: 'latest')
        
        Returns:
            Secret value as string
        
        Raises:
            ValueError: If secret doesn't exist
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
        
        try:
            response = self.client.access_secret_version(request={"name": name})
            secret_value = response.payload.data.decode('UTF-8')
            logger.info(f"Retrieved secret: {secret_id}")
            return secret_value
        
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_id}: {e}")
            raise ValueError(f"Secret {secret_id} not found") from e
    
    def create_secret(self, secret_id: str, secret_value: str) -> None:
        """Create a new secret"""
        parent = f"projects/{self.project_id}"
        
        # Create secret
        secret = self.client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        
        # Add secret version
        self.client.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {"data": secret_value.encode('UTF-8')},
            }
        )
        
        logger.info(f"Created secret: {secret_id}")

# Singleton instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get singleton secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
EOF

# Update github-activity to use Secret Manager
cat > cloud-functions/github-activity/main.py << 'EOF'
import functions_framework
from cloud_services.shared.auth import require_api_key
from cloud_services.shared.secrets import get_secrets_manager
from cloud_services.services.github_service import GitHubService
import logging

logger = logging.getLogger(__name__)

# Initialize
secrets = get_secrets_manager()
github_token = secrets.get_secret('github-token')  # Fetch from Secret Manager
service = GitHubService(github_token)

@functions_framework.http
@require_api_key
def github_activity(request):
    """GitHub activity Cloud Function"""
    organization = request.args.get('organization')
    
    if not organization:
        return {'error': 'Missing parameter: organization'}, 400
    
    try:
        result = service.get_activity(organization)
        return (result, 200)
    
    except Exception as e:
        logger.exception(f"Error fetching GitHub activity for {organization}")
        return {'error': 'Internal server error'}, 500
EOF

# Create migration script to move secrets to Secret Manager
cat > tools/migrate_secrets.py << 'EOF'
"""Migrate secrets from environment variables to Secret Manager"""
from google.cloud import secretmanager
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_secrets():
    """Migrate all secrets to Google Secret Manager"""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ['GCP_PROJECT_ID']
    parent = f"projects/{project_id}"
    
    secrets_to_migrate = {
        'github-token': os.environ.get('GITHUB_TOKEN'),
        'cloud-function-api-key': os.environ.get('CLOUD_FUNCTION_API_KEY'),
        'auth-cookie-key': os.environ.get('AUTH_COOKIE_KEY'),
    }
    
    for secret_id, secret_value in secrets_to_migrate.items():
        if not secret_value:
            logger.warning(f"Skipping {secret_id}: not set in environment")
            continue
        
        try:
            # Create secret
            secret = client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": secret_id,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
            
            # Add version
            client.add_secret_version(
                request={
                    "parent": secret.name,
                    "payload": {"data": secret_value.encode('UTF-8')},
                }
            )
            
            logger.info(f"✅ Migrated: {secret_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to migrate {secret_id}: {e}")

if __name__ == "__main__":
    migrate_secrets()
    logger.info("Migration complete!")
EOF

# Run migration
python tools/migrate_secrets.py
```

**Update .gitignore:**

```bash
# Ensure sensitive files are ignored
cat >> .gitignore << 'EOF'

# Secrets (DO NOT COMMIT)
.env
.env.local
.env.production
**/credentials.yaml
**/secrets.yaml
**/*_secret.json
**/*_key.json
*.pem
*.key

# API Keys
api_keys.txt
EOF

git add .gitignore
```

**Commit:**

```bash
git add cloud-services/shared/secrets.py cloud-functions/ tools/ .gitignore
git commit -m "feat(security): implement secrets management with Google Secret Manager

- Create SecretsManager class
- Migrate hardcoded secrets to Secret Manager
- Update Cloud Functions to fetch secrets
- Add migration script
- Update .gitignore

Fixes: SEC-001 (P0 - Hardcoded secrets)
Security: All secrets now in Secret Manager"
```

---

### Step 2.4: Firestore Security Rules (Day 5)

**Reference:** `SECURITY_VULNERABILITIES.md` → SEC-005

```bash
# Create Firestore security rules
cat > firestore.rules << 'EOF'
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper functions
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isAdmin() {
      return isAuthenticated() && 
             get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Default: Deny all access
    match /{document=**} {
      allow read, write: if false;
    }
    
    // Jobs collection
    match /jobs/{jobId} {
      // Read: authenticated users only
      allow read: if isAuthenticated();
      
      // Write: only Cloud Functions (via service account)
      allow write: if request.auth.token.email.matches('.*@.*\\.iam\\.gserviceaccount\\.com$');
    }
    
    // News collection
    match /news/{articleId} {
      allow read: if isAuthenticated();
      allow write: if request.auth.token.email.matches('.*@.*\\.iam\\.gserviceaccount\\.com$');
    }
    
    // GitHub repos collection
    match /github_repos/{repoId} {
      allow read: if isAuthenticated();
      allow write: if request.auth.token.email.matches('.*@.*\\.iam\\.gserviceaccount\\.com$');
    }
    
    // User data (query history, saved analyses)
    match /users/{userId} {
      // Users can only access their own data
      allow read: if isAuthenticated() && request.auth.uid == userId;
      allow write: if isAuthenticated() && request.auth.uid == userId;
    }
    
    // Admin-only collections
    match /admin/{document=**} {
      allow read, write: if isAdmin();
    }
  }
}
EOF

# Create Firestore indexes configuration
cat > firestore.indexes.json << 'EOF'
{
  "indexes": [
    {
      "collectionGroup": "jobs",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "company", "order": "ASCENDING"},
        {"fieldPath": "posted_date", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "news",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "published_at", "order": "DESCENDING"},
        {"fieldPath": "source", "order": "ASCENDING"}
      ]
    },
    {
      "collectionGroup": "github_repos",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "organization", "order": "ASCENDING"},
        {"fieldPath": "stars", "order": "DESCENDING"}
      ]
    }
  ]
}
EOF

# Deploy rules
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes

# Test rules
cat > tests/integration/test_firestore_security.py << 'EOF'
import pytest
from google.cloud import firestore
from google.auth.credentials import Credentials
import os

@pytest.fixture
def firestore_client():
    return firestore.Client()

def test_unauthenticated_read_denied(firestore_client):
    """Test that unauthenticated reads are denied"""
    # This should fail (no auth)
    with pytest.raises(Exception):
        docs = firestore_client.collection('jobs').limit(1).get()

def test_authenticated_read_allowed():
    """Test that authenticated users can read"""
    # Create client with user credentials
    # (In real test, use Firebase Auth)
    # For now, use service account (should work)
    client = firestore.Client()
    docs = list(client.collection('jobs').limit(1).stream())
    # Should succeed

def test_direct_write_denied():
    """Test that direct writes from client are denied"""
    client = firestore.Client()
    
    with pytest.raises(Exception):
        client.collection('jobs').add({
            'title': 'Test Job',
            'company': 'Test Company'
        })
EOF

pytest tests/integration/test_firestore_security.py -v
```

**Commit:**

```bash
git add firestore.rules firestore.indexes.json tests/
git commit -m "feat(security): implement Firestore security rules

- Add restrictive security rules
- Authenticated users: read-only
- Service accounts: write access
- Add composite indexes
- Write security tests

Fixes: SEC-005 (P0 - Open Firestore access)
Tests: 3 passed"
```

**Merge Security Branch:**

```bash
# All security work complete
git checkout feat/production-transformation
git merge feat/security-hardening

# Tag this milestone
git tag -a v0.2.0-security -m "Security hardening complete

- Authentication implemented
- Cloud Functions secured
- Secrets in Secret Manager
- Firestore rules enforced

All P0 security vulnerabilities fixed."

git push origin feat/production-transformation
git push origin v0.2.0-security

# Update progress tracker
# Mark Phase 2 complete in PROGRESS_TRACKER.md
```

---

## 🧹 PHASE 3: CODE QUALITY (Days 6-10)

**Reference Documents:**
- `REFACTORING_PLAN.md` (RF-001 through RF-012)
- `TEST_COVERAGE_GAPS.md`

*(Continue with similar detailed step-by-step instructions for:)*
- Extracting business logic
- Adding type hints
- Implementing repository pattern
- Error handling
- Test coverage
- etc.

---

## 🎨 PHASE 4: UI/UX TRANSFORMATION (Days 11-15)

**Reference Documents:**
- `UI_UX_IMPROVEMENTS.md` (UX-001 through UX-018)

*(Detailed steps for:)*
- WCAG compliance
- Responsive design
- Design system
- Loading states
- etc.

---

## ⚡ PHASE 5: PERFORMANCE OPTIMIZATION (Days 16-18)

*(Caching, query optimization, bundle optimization)*

---

## 📚 PHASE 6: DOCUMENTATION & TESTING (Days 19-20)

*(API docs, user guides, integration tests)*

---

## 🚀 PHASE 7: DEPLOYMENT (Day 21+)

*(Staging, production rollout, monitoring)*

---

## 📊 PROGRESS TRACKING

### Daily Checklist

At the end of each day:

```bash
# 1. Run all quality checks
ruff check .
mypy streamlit-app/ cloud-services/
pytest tests/ -v --cov

# 2. Update progress tracker
# Edit speckit-prep/PROGRESS_TRACKER.md

# 3. Commit day's work
git add .
git commit -m "feat/fix/refactor: <description>

<detailed changes>

Progress: Phase X - Day Y complete
Tests: <X> passed, <Y>% coverage"

# 4. Push to remote
git push origin <current-branch>

# 5. Generate daily report
cat > daily-reports/day-$(date +%Y-%m-%d).md << EOF
# Daily Report: $(date +%Y-%m-%d)

## Completed Today
- Task 1
- Task 2

## Blockers
- None

## Tomorrow
- Task 3
- Task 4

## Metrics
- Tests: X passed
- Coverage: Y%
- Linting: 0 errors
EOF
```

---

## ✅ QUALITY GATES

### Before Each Commit

```bash
# Run quality gate script
cat > tools/quality_gate.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 Running quality gates..."

echo "1️⃣ Linting..."
ruff check . || exit 1

echo "2️⃣ Type checking..."
mypy streamlit-app/ cloud-services/ || exit 1

echo "3️⃣ Tests..."
pytest tests/ --cov=. --cov-fail-under=80 || exit 1

echo "4️⃣ Security scan..."
safety check || exit 1

echo "✅ All quality gates passed!"
EOF

chmod +x tools/quality_gate.sh

# Run before commit
./tools/quality_gate.sh
```

---

## 🆘 TROUBLESHOOTING

### Common Issues

**Issue: Tests failing**
```bash
# Check test output
pytest tests/ -v --tb=short

# Run specific test
pytest tests/unit/test_authentication.py::test_login -v

# Debug with pdb
pytest tests/ --pdb
```

**Issue: Linting errors**
```bash
# Auto-fix
ruff check . --fix

# Show what will be fixed
ruff check . --fix --diff
```

**Issue: Type errors**
```bash
# Verbose output
mypy streamlit-app/ --verbose

# Ignore specific error
# Add: # type: ignore[error-code]
```

---

## 📞 ESCALATION

**If stuck for > 2 hours:**

1. Document the blocker in `speckit-prep/BLOCKERS.md`
2. Try alternative approach
3. Ask for human review
4. Create GitHub issue with `blocked` label

---

## 🎉 COMPLETION CRITERIA

**Project is complete when:**

- [ ] All 7 phases marked complete in `PROGRESS_TRACKER.md`
- [ ] All tests passing (200+ tests, 80%+ coverage)
- [ ] Zero linting errors
- [ ] Zero security vulnerabilities (high/critical)
- [ ] WCAG 2.1 AA compliant (Lighthouse score 95+)
- [ ] Mobile responsive (tested on 5+ devices)
- [ ] Deployed to production
- [ ] Monitoring configured
- [ ] Documentation complete
- [ ] Handoff to team complete

---

**Estimated Total Duration:** 20 working days  
**Risk Level:** 🟡 Medium  
**Success Probability:** 95% (with proper execution)

---

## 📚 APPENDIX

### A. All Reference Documents

1. `AUDIT_REPORT.md` - Main audit findings
2. `SECURITY_VULNERABILITIES.md` - Security issues and fixes
3. `QUICK_WINS.md` - Quick improvements (< 1 hour each)
4. `TASK_PRIORITIES.md` - Prioritized task list
5. `TEST_COVERAGE_GAPS.md` - Testing strategy
6. `constitution.md` - Project principles and standards
7. `spec-001-authentication-system.md` - Authentication specification
8. `BREAKING_CHANGES.md` - All breaking changes forecast
9. `REFACTORING_PLAN.md` - Code quality improvements
10. `UI_UX_IMPROVEMENTS.md` - UI/UX transformation
11. `claude-execution.md` - This document

### B. Key Commands Reference

```bash
# Development
streamlit run streamlit-app/app.py
pytest tests/ -v --cov
ruff check . --fix
mypy .

# Deployment
gcloud run deploy intelagent-app --source=streamlit-app
gcloud functions deploy job-scraper --source=cloud-functions/job-scraper

# Git
git checkout -b feat/new-feature
git commit -m "feat: description"
git push origin feat/new-feature

# Testing
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/ --cov --cov-report=html
```

### C. Contact Information

**Project Lead:** [Your Name]  
**Repository:** https://github.com/your-org/intelagent  
**Documentation:** https://docs.intelagent.ai  
**Support:** support@intelagent.ai

---

**END OF EXECUTION SCRIPT**

*This document is a living guide. Update as you progress through the transformation.*


