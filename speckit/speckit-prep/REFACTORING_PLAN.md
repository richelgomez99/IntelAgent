# 🔨 REFACTORING PLAN
## IntelAgent Competitive Intelligence Platform

**Generated:** November 17, 2025  
**Audit Phase:** Code Quality & Architecture Improvement

---

## 🎯 EXECUTIVE SUMMARY

This document provides a **comprehensive refactoring roadmap** to transform the current prototype into a production-grade codebase. The plan addresses code quality, architecture, maintainability, and scalability concerns identified in the audit.

**Current State:** ⚠️ Functional prototype with significant technical debt  
**Target State:** ✅ Production-grade, maintainable, scalable system

**Refactoring Scope:**
- **12 major refactorings** across all components
- **Estimated Total Effort:** 15 days (3 sprints)
- **Risk Level:** 🟡 Medium (extensive test coverage required)

---

## 📊 REFACTORING CATEGORIES

| Category | Issues | Priority | Effort |
|----------|--------|----------|--------|
| **Architecture** | 4 | 🔴 Critical | 6 days |
| **Code Organization** | 3 | 🟡 High | 4 days |
| **Code Quality** | 5 | 🟡 High | 3 days |
| **Performance** | 2 | 🟢 Medium | 2 days |

---

## 🏗️ ARCHITECTURE REFACTORINGS

### RF-001: Extract Business Logic from UI Layer

**Current Problem:**
- All business logic embedded in `streamlit-app/app.py` (500+ lines)
- Gemini agent logic mixed with UI rendering
- Impossible to test without Streamlit runtime
- Cannot reuse logic in other contexts (CLI, API)

**Target Architecture:**

```
streamlit-app/
  ├── app.py                    # UI ONLY (150 lines)
  ├── core/
  │   ├── __init__.py
  │   ├── agent.py              # Agent orchestration
  │   ├── data_fetchers.py      # Data source abstraction
  │   ├── analyzers.py          # Analysis logic
  │   └── formatters.py         # Response formatting
  ├── ui/
  │   ├── __init__.py
  │   ├── components.py         # Reusable UI components
  │   ├── pages.py              # Page layouts
  │   └── state.py              # Session state management
  └── tests/
      ├── unit/
      │   ├── test_agent.py
      │   ├── test_data_fetchers.py
      │   └── test_analyzers.py
      └── integration/
          └── test_streamlit_ui.py
```

**Implementation Plan:**

**Step 1: Extract Agent Logic (Day 1-2)**

```python
# streamlit-app/core/agent.py
from typing import Dict, List, Any
from dataclasses import dataclass
from .data_fetchers import DataFetcher

@dataclass
class AgentConfig:
    """Configuration for Gemini agent"""
    model: str = "gemini-2.0-flash-exp"
    project_id: str
    location: str = "us-central1"
    max_retries: int = 3
    temperature: float = 0.2

class CompetitiveIntelligenceAgent:
    """
    Orchestrates competitive intelligence analysis.
    Pure business logic - no UI dependencies.
    """
    
    def __init__(self, config: AgentConfig, data_fetcher: DataFetcher):
        self.config = config
        self.data_fetcher = data_fetcher
        self.model = self._initialize_model()
    
    def analyze(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze competitive landscape based on query.
        
        Args:
            query: User's question/analysis request
            context: Optional context (previous analyses, user preferences)
        
        Returns:
            {
                "analysis": str,
                "sources": Dict[str, Any],
                "confidence": float,
                "reasoning_steps": List[str],
                "follow_up_questions": List[str]
            }
        """
        # Pure business logic here
        pass
    
    def _execute_tool_call(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute tool call via data fetcher"""
        return self.data_fetcher.fetch(tool_name, parameters)

# Usage in app.py becomes:
# agent = CompetitiveIntelligenceAgent(config, data_fetcher)
# result = agent.analyze(user_query)
# display_result(result)  # UI rendering separate
```

**Step 2: Create Data Fetcher Abstraction (Day 2)**

```python
# streamlit-app/core/data_fetchers.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import requests

class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def fetch(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from source"""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict) -> bool:
        """Validate parameters before fetch"""
        pass

class CloudFunctionDataSource(DataSource):
    """Fetch data from Cloud Functions"""
    
    def __init__(self, function_url: str, api_key: str):
        self.function_url = function_url
        self.api_key = api_key
    
    def fetch(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(
            self.function_url,
            params=parameters,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def validate_parameters(self, parameters: Dict) -> bool:
        # Validation logic
        return True

class BigQueryDataSource(DataSource):
    """Fetch data from BigQuery"""
    
    def __init__(self, project_id: str, dataset_id: str):
        from google.cloud import bigquery
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = dataset_id
    
    def fetch(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        query = self._build_query(parameters)
        results = self.client.query(query).result()
        return [dict(row) for row in results]

class DataFetcher:
    """Unified interface for all data sources"""
    
    def __init__(self):
        self.sources = {}
    
    def register_source(self, name: str, source: DataSource):
        """Register a data source"""
        self.sources[name] = source
    
    def fetch(self, source_name: str, parameters: Dict) -> Dict[str, Any]:
        """Fetch data from registered source"""
        if source_name not in self.sources:
            raise ValueError(f"Unknown data source: {source_name}")
        
        source = self.sources[source_name]
        
        if not source.validate_parameters(parameters):
            raise ValueError(f"Invalid parameters for {source_name}")
        
        return source.fetch(parameters)
```

**Benefits:**
- ✅ Testable without UI runtime
- ✅ Reusable in CLI, API, Jupyter notebooks
- ✅ Clear separation of concerns
- ✅ Mockable data sources for testing

**Testing:**

```python
# tests/unit/test_agent.py
import pytest
from streamlit-app.core.agent import CompetitiveIntelligenceAgent, AgentConfig
from streamlit-app.core.data_fetchers import DataFetcher

class MockDataFetcher(DataFetcher):
    """Mock data fetcher for testing"""
    def fetch(self, source, params):
        return {"mock": "data"}

def test_agent_analyze():
    """Test agent analysis without Streamlit"""
    config = AgentConfig(
        project_id="test-project",
        model="gemini-2.0-flash-exp"
    )
    fetcher = MockDataFetcher()
    agent = CompetitiveIntelligenceAgent(config, fetcher)
    
    result = agent.analyze("analyze Anthropic")
    
    assert "analysis" in result
    assert "sources" in result
    assert result["confidence"] > 0
```

**Effort:** 2 days  
**Risk:** 🟡 Medium (requires extensive testing)

---

### RF-002: Consolidate Cloud Functions into Microservices

**Current Problem:**
- 3 separate Cloud Functions with 90% duplicated code
- Each function: 200-300 lines
- Shared logic copied (retry logic, Firestore writes, error handling)
- Difficult to maintain consistency

**Target Architecture:**

```
cloud-services/
  ├── shared/
  │   ├── __init__.py
  │   ├── firestore_client.py    # Unified Firestore operations
  │   ├── http_client.py          # Retry logic, timeouts
  │   ├── logging_config.py       # Structured logging
  │   └── error_handlers.py       # Common error handling
  ├── services/
  │   ├── __init__.py
  │   ├── job_scraper_service.py
  │   ├── news_search_service.py
  │   └── github_service.py
  ├── functions/
  │   ├── job_scraper/            # Thin wrapper
  │   │   └── main.py             # 50 lines
  │   ├── news_search/
  │   │   └── main.py
  │   └── github_activity/
  │       └── main.py
  └── tests/
      ├── unit/
      └── integration/
```

**Implementation:**

**Step 1: Extract Shared Firestore Client (Day 1)**

```python
# cloud-services/shared/firestore_client.py
from google.cloud import firestore
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FirestoreClient:
    """Unified Firestore operations with best practices"""
    
    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
    
    def batch_write(
        self, 
        collection: str, 
        documents: List[Dict[str, Any]],
        merge: bool = True
    ) -> int:
        """
        Write multiple documents in batches (500 per batch).
        
        Args:
            collection: Collection name
            documents: List of documents to write
            merge: If True, merge with existing; if False, overwrite
        
        Returns:
            Number of documents written
        """
        batch = self.db.batch()
        count = 0
        
        for i, doc in enumerate(documents):
            doc_ref = self.db.collection(collection).document(doc['id'])
            
            # Add metadata
            doc['updated_at'] = datetime.utcnow()
            if 'created_at' not in doc:
                doc['created_at'] = datetime.utcnow()
            
            if merge:
                batch.set(doc_ref, doc, merge=True)
            else:
                batch.set(doc_ref, doc)
            
            count += 1
            
            # Commit batch every 500 documents
            if (i + 1) % 500 == 0:
                batch.commit()
                logger.info(f"Committed batch: {count} documents")
                batch = self.db.batch()
        
        # Commit remaining
        if count % 500 != 0:
            batch.commit()
        
        logger.info(f"✅ Wrote {count} documents to {collection}")
        return count
    
    def query_recent(
        self, 
        collection: str, 
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query recent documents"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        query = (
            self.db.collection(collection)
            .where('created_at', '>=', cutoff)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        return [doc.to_dict() for doc in query.stream()]
```

**Step 2: Extract Shared HTTP Client (Day 1)**

```python
# cloud-services/shared/http_client.py
import requests
from typing import Dict, Any, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import logging

logger = logging.getLogger(__name__)

class HTTPClient:
    """HTTP client with built-in retry logic and error handling"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
        reraise=True
    )
    def get(
        self, 
        url: str, 
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """GET request with retry logic"""
        logger.info(f"GET {url} (params: {params})")
        
        response = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        logger.info(f"✅ GET {url} succeeded (status: {response.status_code})")
        
        return response
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
        reraise=True
    )
    def post(
        self,
        url: str,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """POST request with retry logic"""
        logger.info(f"POST {url}")
        
        response = self.session.post(
            url,
            json=json,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        logger.info(f"✅ POST {url} succeeded (status: {response.status_code})")
        
        return response
```

**Step 3: Refactor Job Scraper to Use Shared Code (Day 2)**

```python
# cloud-services/services/job_scraper_service.py
from ..shared.firestore_client import FirestoreClient
from ..shared.http_client import HTTPClient
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class JobScraperService:
    """Job scraping business logic (framework-agnostic)"""
    
    def __init__(
        self, 
        firestore_client: FirestoreClient,
        http_client: HTTPClient
    ):
        self.firestore = firestore_client
        self.http = http_client
    
    def scrape_jobs(self, company: str, days: int = 30) -> Dict[str, Any]:
        """
        Scrape jobs for company.
        
        Returns:
            {
                "jobs": List[Dict],
                "total_count": int,
                "competitive_score": float,
                "insights": List[str]
            }
        """
        # Business logic here
        greenhouse_url = self._get_greenhouse_url(company)
        
        # Fetch jobs
        response = self.http.get(greenhouse_url)
        jobs_data = response.json()
        
        # Filter recent
        recent_jobs = self._filter_recent(jobs_data['jobs'], days)
        
        # Calculate insights
        insights = self._extract_insights(recent_jobs)
        competitive_score = self._calculate_score(recent_jobs)
        
        # Store in Firestore
        documents = [self._job_to_document(job, company) for job in recent_jobs]
        self.firestore.batch_write(f'jobs_{company.lower()}', documents)
        
        return {
            "jobs": recent_jobs,
            "total_count": len(recent_jobs),
            "competitive_score": competitive_score,
            "insights": insights
        }

# cloud-functions/job-scraper/main.py (now just 50 lines)
import functions_framework
from cloud_services.services.job_scraper_service import JobScraperService
from cloud_services.shared.firestore_client import FirestoreClient
from cloud_services.shared.http_client import HTTPClient
import os

# Initialize once (stays warm)
firestore_client = FirestoreClient(os.environ['GCP_PROJECT_ID'])
http_client = HTTPClient()
service = JobScraperService(firestore_client, http_client)

@functions_framework.http
def job_scraper(request):
    """Thin wrapper around service"""
    company = request.args.get('company')
    
    if not company:
        return {"error": "Missing parameter: company"}, 400
    
    result = service.scrape_jobs(company)
    return result, 200
```

**Benefits:**
- ✅ Eliminate 90% code duplication
- ✅ Single source of truth for common logic
- ✅ Easier to test (pure functions)
- ✅ Consistent error handling across all functions

**Effort:** 2 days  
**Risk:** 🟡 Medium (requires deployment coordination)

---

### RF-003: Implement Repository Pattern for Data Access

**Current Problem:**
- Direct BigQuery/Firestore calls scattered throughout codebase
- Hardcoded queries in business logic
- Difficult to test (requires actual databases)
- Cannot switch data sources easily

**Target Architecture:**

```python
# streamlit-app/core/repositories.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Patent:
    """Domain model for patent"""
    id: str
    title: str
    assignee: str
    filing_date: datetime
    publication_date: datetime
    inventors: List[str]
    abstract: str
    claims_count: int

class PatentRepository(ABC):
    """Abstract repository for patents"""
    
    @abstractmethod
    def find_by_company(
        self, 
        company: str, 
        start_date: datetime,
        end_date: datetime
    ) -> List[Patent]:
        """Find patents by company and date range"""
        pass
    
    @abstractmethod
    def find_by_id(self, patent_id: str) -> Optional[Patent]:
        """Find patent by ID"""
        pass
    
    @abstractmethod
    def count_by_company(self, company: str) -> int:
        """Count patents for company"""
        pass

class BigQueryPatentRepository(PatentRepository):
    """BigQuery implementation"""
    
    def __init__(self, client, dataset_id: str):
        self.client = client
        self.dataset_id = dataset_id
    
    def find_by_company(
        self, 
        company: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Patent]:
        """Query BigQuery for patents"""
        query = """
            SELECT
                publication_number AS id,
                title,
                assignee,
                filing_date,
                publication_date,
                inventor_names AS inventors,
                abstract,
                claims_count
            FROM `{dataset}.fivetran_uspto`
            WHERE LOWER(assignee) LIKE LOWER(@company)
              AND publication_date BETWEEN @start_date AND @end_date
            ORDER BY publication_date DESC
            LIMIT 1000
        """.format(dataset=self.dataset_id)
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("company", "STRING", f"%{company}%"),
                bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", start_date),
                bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", end_date),
            ]
        )
        
        results = self.client.query(query, job_config=job_config).result()
        
        return [
            Patent(
                id=row.id,
                title=row.title,
                assignee=row.assignee,
                filing_date=row.filing_date,
                publication_date=row.publication_date,
                inventors=row.inventors or [],
                abstract=row.abstract or "",
                claims_count=row.claims_count or 0
            )
            for row in results
        ]

class MockPatentRepository(PatentRepository):
    """In-memory implementation for testing"""
    
    def __init__(self):
        self.patents = []
    
    def find_by_company(self, company, start_date, end_date):
        return [
            p for p in self.patents
            if company.lower() in p.assignee.lower()
            and start_date <= p.publication_date <= end_date
        ]
    
    def add_patent(self, patent: Patent):
        """Helper for tests"""
        self.patents.append(patent)

# Usage in business logic:
class CompetitorAnalyzer:
    def __init__(self, patent_repo: PatentRepository):
        self.patent_repo = patent_repo  # Dependency injection
    
    def analyze_innovation_pace(self, company: str) -> Dict:
        """Analyze patent filings over time"""
        patents = self.patent_repo.find_by_company(
            company,
            start_date=datetime(2023, 1, 1),
            end_date=datetime.now()
        )
        # Analysis logic here
        return {"pace": len(patents) / 24}  # per month

# In tests:
def test_innovation_pace():
    mock_repo = MockPatentRepository()
    mock_repo.add_patent(Patent(...))
    
    analyzer = CompetitorAnalyzer(mock_repo)
    result = analyzer.analyze_innovation_pace("Anthropic")
    
    assert result["pace"] > 0
```

**Benefits:**
- ✅ Testable without real databases
- ✅ Swap implementations (BigQuery → Firestore → Mock)
- ✅ Centralized query logic
- ✅ Type-safe domain models

**Effort:** 2 days  
**Risk:** 🟢 Low (doesn't change external behavior)

---

### RF-004: Add Configuration Management System

**Current Problem:**
- Environment variables scattered in Dockerfiles, Cloud Function manifests
- Hardcoded values (URLs, thresholds, company lists)
- No validation of configuration
- Different configs for dev/staging/prod mixed together

**Target Solution:**

```
config/
  ├── __init__.py
  ├── base.py                # Base configuration
  ├── development.py         # Dev overrides
  ├── staging.py             # Staging overrides
  ├── production.py          # Production overrides
  └── schemas.py             # Pydantic validation schemas
```

**Implementation:**

```python
# config/schemas.py
from pydantic import BaseSettings, Field, validator, AnyHttpUrl
from typing import List, Optional

class AppConfig(BaseSettings):
    """Application configuration with validation"""
    
    # GCP
    gcp_project_id: str = Field(..., min_length=1)
    gcp_location: str = Field(default="us-central1")
    
    # Gemini
    gemini_model: str = Field(default="gemini-2.0-flash-exp")
    gemini_temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    gemini_max_retries: int = Field(default=3, ge=1, le=10)
    
    # Cloud Functions
    job_scraper_url: AnyHttpUrl
    news_search_url: AnyHttpUrl
    github_activity_url: AnyHttpUrl
    cloud_function_api_key: str = Field(..., min_length=20)
    
    # BigQuery
    bigquery_dataset_id: str = Field(..., min_length=1)
    bigquery_timeout_seconds: int = Field(default=30, ge=5, le=300)
    
    # Firestore
    firestore_collection_prefix: str = Field(default="prod")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=10, ge=1, le=1000)
    rate_limit_per_hour: int = Field(default=100, ge=10, le=10000)
    
    # Session
    session_timeout_hours: int = Field(default=8, ge=1, le=72)
    
    # Feature Flags
    feature_flag_auth_required: bool = Field(default=True)
    feature_flag_rate_limiting: bool = Field(default=True)
    
    # Monitored Companies (default list)
    default_companies: List[str] = Field(
        default=["Anthropic", "OpenAI", "Google DeepMind", "Meta AI"]
    )
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    
    @validator('gemini_model')
    def validate_model(cls, v):
        allowed_models = ["gemini-2.0-flash-exp", "gemini-1.5-pro"]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of {allowed_models}")
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False

# config/base.py
from .schemas import AppConfig

def load_config() -> AppConfig:
    """Load and validate configuration"""
    config = AppConfig()
    
    # Log loaded config (mask secrets)
    logger.info(f"Loaded config: project={config.gcp_project_id}, model={config.gemini_model}")
    logger.debug(f"API Key: {config.cloud_function_api_key[:10]}***")
    
    return config

# config/development.py
class DevelopmentConfig(AppConfig):
    """Development-specific overrides"""
    log_level: str = "DEBUG"
    feature_flag_auth_required: bool = False  # No auth in dev
    gemini_max_retries: int = 1  # Fail fast in dev

# Usage in app:
from config.base import load_config

config = load_config()
agent = CompetitiveIntelligenceAgent(
    model=config.gemini_model,
    temperature=config.gemini_temperature,
    max_retries=config.gemini_max_retries
)
```

**Benefits:**
- ✅ Single source of truth for all config
- ✅ Automatic validation (catch errors early)
- ✅ Environment-specific overrides
- ✅ Type-safe configuration access

**Effort:** 1 day  
**Risk:** 🟢 Low

---

## 📦 CODE ORGANIZATION REFACTORINGS

### RF-005: Split Monolithic `app.py` into Modules

**Current Problem:**
- `streamlit-app/app.py`: 500+ lines
- Mixes concerns: UI, business logic, data fetching, formatting
- Difficult to navigate and understand

**Target Structure:**

```
streamlit-app/
  ├── app.py                        # Entry point (100 lines)
  ├── ui/
  │   ├── pages/
  │   │   ├── home.py               # Home page
  │   │   ├── analysis.py           # Analysis page
  │   │   └── history.py            # Query history page
  │   ├── components/
  │   │   ├── chat.py               # Chat interface
  │   │   ├── metrics.py            # Metric displays
  │   │   ├── visualizations.py    # Charts
  │   │   └── exports.py            # Export buttons
  │   └── layouts/
  │       ├── sidebar.py            # Sidebar layout
  │       └── header.py             # Header layout
  └── core/
      # (business logic as per RF-001)
```

**app.py becomes:**

```python
# streamlit-app/app.py
import streamlit as st
from auth.authenticator import AuthManager
from ui.layouts.sidebar import render_sidebar
from ui.layouts.header import render_header
from ui.pages import home, analysis, history
from config.base import load_config

# Initialize
config = load_config()
auth = AuthManager()

# Require authentication
user = auth.require_auth()

# Page routing
st.set_page_config(
    page_title="IntelAgent",
    page_icon="🧠",
    layout="wide"
)

# Header
render_header(user)

# Sidebar
page = render_sidebar()

# Route to page
if page == "Home":
    home.render()
elif page == "Analysis":
    analysis.render(user, config)
elif page == "History":
    history.render(user)
```

**Effort:** 1 day  
**Risk:** 🟢 Low (mostly moving code)

---

### RF-006: Organize Cloud Functions as Monorepo

**Current Problem:**
- Each function in separate folder with duplicate `requirements.txt`
- Shared code copied between functions
- Version drift (one function uses `requests==2.31`, another uses `2.28`)

**Target Structure:**

```
cloud-services/                      # Monorepo root
  ├── pyproject.toml                 # Shared dependencies
  ├── setup.py                       # Package definition
  ├── shared/                        # Shared code
  │   ├── firestore_client.py
  │   ├── http_client.py
  │   └── logging_config.py
  ├── services/                      # Business logic
  │   ├── job_scraper_service.py
  │   ├── news_search_service.py
  │   └── github_service.py
  ├── functions/                     # Cloud Function entry points
  │   ├── job-scraper/
  │   │   ├── main.py
  │   │   └── requirements.txt      # Minimal (just cloud-services package)
  │   ├── news-search/
  │   │   ├── main.py
  │   │   └── requirements.txt
  │   └── github-activity/
  │       ├── main.py
  │       └── requirements.txt
  └── tests/
      ├── unit/
      └── integration/

# pyproject.toml
[project]
name = "cloud-services"
version = "1.0.0"
dependencies = [
    "google-cloud-firestore==2.13.1",
    "google-cloud-bigquery==3.13.0",
    "requests==2.31.0",
    "tenacity==8.2.3",
    "pydantic==2.5.0"
]

[project.optional-dependencies]
dev = [
    "pytest==7.4.3",
    "pytest-cov==4.1.0",
    "ruff==0.1.6",
    "mypy==1.7.0"
]

# functions/job-scraper/requirements.txt (now minimal)
cloud-services==1.0.0
functions-framework==3.5.0
```

**Benefits:**
- ✅ Single dependency specification
- ✅ No version drift
- ✅ Easy to add new functions
- ✅ Shared code automatically available

**Effort:** 1 day  
**Risk:** 🟡 Medium (requires deployment pipeline update)

---

### RF-007: Create Proper Python Package Structure

**Current Problem:**
- No `__init__.py` files
- Cannot import modules properly
- No package versioning
- No installable package

**Target Structure:**

```
intelagent/                          # Package root
  ├── pyproject.toml                 # PEP 517/518 metadata
  ├── setup.py                       # Backwards compatibility
  ├── README.md
  ├── LICENSE
  ├── src/
  │   └── intelagent/
  │       ├── __init__.py
  │       ├── __version__.py
  │       ├── core/
  │       │   ├── __init__.py
  │       │   └── agent.py
  │       ├── data/
  │       │   ├── __init__.py
  │       │   └── repositories.py
  │       └── ui/
  │           ├── __init__.py
  │           └── components.py
  ├── tests/
  │   ├── __init__.py
  │   ├── unit/
  │   └── integration/
  └── docs/
      └── api/

# pyproject.toml
[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "intelagent"
version = "0.1.0"
description = "Competitive Intelligence Platform powered by Gemini AI"
authors = [{name = "Your Team", email = "team@intelagent.ai"}]
license = {text = "MIT"}
dependencies = [
    "streamlit>=1.28.0",
    "google-cloud-aiplatform>=1.38.0",
    # ... other deps
]

[tool.setuptools.packages.find]
where = ["src"]

# Now installable:
# pip install -e .
# import intelagent
# from intelagent.core import CompetitiveIntelligenceAgent
```

**Effort:** 1 day  
**Risk:** 🟢 Low

---

## 🎨 CODE QUALITY REFACTORINGS

### RF-008: Add Type Hints Everywhere

**Current Coverage:** ~30%  
**Target Coverage:** 100%

**Implementation:**

```python
# BEFORE (No type hints)
def fetch_patents(company, date_range):
    results = query_bigquery(company, date_range)
    return process_results(results)

# AFTER (Full type hints)
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dataclasses import dataclass

@dataclass
class DateRange:
    """Date range for queries"""
    start: date
    end: date

@dataclass
class Patent:
    """Patent domain model"""
    id: str
    title: str
    assignee: str
    filing_date: datetime
    publication_date: datetime
    inventors: List[str]
    abstract: Optional[str] = None

def fetch_patents(
    company: str,
    date_range: DateRange
) -> List[Patent]:
    """
    Fetch patents for company in date range.
    
    Args:
        company: Company name (case-insensitive)
        date_range: Date range to query
    
    Returns:
        List of Patent objects
    
    Raises:
        ValueError: If company is empty
        QueryError: If BigQuery query fails
    """
    if not company:
        raise ValueError("Company cannot be empty")
    
    results: List[Dict[str, Any]] = query_bigquery(company, date_range)
    patents: List[Patent] = process_results(results)
    
    return patents
```

**Tooling:**

```bash
# Add to pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_calls = true
strict = true

# Run type checker
mypy src/ --strict
```

**Effort:** 2 days  
**Risk:** 🟢 Low (doesn't change behavior)

---

### RF-009: Eliminate Code Duplication (DRY)

**Current Issues:**
- Retry logic duplicated in 5 places
- Firestore write logic duplicated in 3 functions
- Date formatting duplicated in 10 places
- Company name normalization duplicated in 8 places

**Refactoring:**

```python
# shared/utils.py
from typing import Callable, TypeVar, Any
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential
import re
from datetime import datetime

T = TypeVar('T')

def retry_on_failure(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10
) -> Callable:
    """
    Decorator to retry function on failure.
    
    Usage:
        @retry_on_failure(max_attempts=5)
        def fetch_data():
            ...
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait)
    )

def normalize_company_name(company: str) -> str:
    """
    Normalize company name for consistent querying.
    
    Examples:
        "Anthropic, Inc." -> "anthropic"
        "  OpenAI  " -> "openai"
        "Google DeepMind (UK)" -> "google deepmind"
    """
    # Remove common suffixes
    company = re.sub(r'\s+(Inc|LLC|Ltd|Corporation|Corp)\.?$', '', company, flags=re.IGNORECASE)
    
    # Remove parenthetical content
    company = re.sub(r'\([^)]*\)', '', company)
    
    # Lowercase and strip
    company = company.lower().strip()
    
    # Normalize whitespace
    company = re.sub(r'\s+', ' ', company)
    
    return company

def format_timestamp(dt: datetime, format: str = "iso") -> str:
    """
    Format datetime consistently.
    
    Args:
        dt: Datetime to format
        format: One of "iso", "human", "short"
    
    Returns:
        Formatted string
    """
    if format == "iso":
        return dt.isoformat()
    elif format == "human":
        return dt.strftime("%B %d, %Y at %I:%M %p")
    elif format == "short":
        return dt.strftime("%Y-%m-%d")
    else:
        raise ValueError(f"Unknown format: {format}")

# Replace all duplicates with these shared utilities
```

**Effort:** 1 day  
**Risk:** 🟢 Low

---

### RF-010: Add Comprehensive Error Handling

**Current Problem:**
- Bare `except:` blocks (catch everything, including Ctrl+C)
- No error context (what was being processed?)
- No structured error logging
- Users see raw Python exceptions

**Target Implementation:**

```python
# shared/errors.py
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ErrorContext:
    """Context for better error messages"""
    operation: str
    user_id: Optional[str] = None
    company: Optional[str] = None
    query: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

class IntelAgentError(Exception):
    """Base exception for all application errors"""
    
    def __init__(
        self, 
        message: str, 
        context: Optional[ErrorContext] = None,
        original_exception: Optional[Exception] = None
    ):
        self.message = message
        self.context = context
        self.original_exception = original_exception
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to structured format for logging"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "context": self.context.__dict__ if self.context else None,
            "original_error": str(self.original_exception) if self.original_exception else None
        }

class DataFetchError(IntelAgentError):
    """Error fetching data from external source"""
    pass

class AnalysisError(IntelAgentError):
    """Error during AI analysis"""
    pass

class AuthenticationError(IntelAgentError):
    """Authentication failed"""
    pass

# Usage:
def fetch_patents(company: str) -> List[Patent]:
    """Fetch patents with proper error handling"""
    context = ErrorContext(
        operation="fetch_patents",
        company=company
    )
    
    try:
        results = query_bigquery(company)
        return process_results(results)
    
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise DataFetchError(
            f"Invalid company name: {company}",
            context=context,
            original_exception=e
        )
    
    except QueryError as e:
        logger.error(f"BigQuery failed: {e}")
        raise DataFetchError(
            f"Failed to fetch patents for {company}",
            context=context,
            original_exception=e
        )
    
    except Exception as e:
        # Unexpected error - log and raise
        logger.exception("Unexpected error fetching patents")
        raise IntelAgentError(
            f"Unexpected error: {str(e)}",
            context=context,
            original_exception=e
        )

# In UI layer:
try:
    patents = fetch_patents(company)
except DataFetchError as e:
    st.error(f"❌ {e.message}")
    st.info("💡 Try a different company name or check if it exists in our database.")
    logger.error(e.to_dict())
except IntelAgentError as e:
    st.error(f"❌ Something went wrong: {e.message}")
    st.info("Please try again or contact support if the issue persists.")
    logger.error(e.to_dict())
```

**Effort:** 1 day  
**Risk:** 🟢 Low

---

### RF-011: Add Docstrings to All Public Functions

**Current Coverage:** ~20%  
**Target Coverage:** 100%

**Standard:**

```python
def fetch_competitive_intelligence(
    company: str,
    include_patents: bool = True,
    include_jobs: bool = True,
    include_news: bool = True
) -> Dict[str, Any]:
    """
    Fetch comprehensive competitive intelligence for a company.
    
    Aggregates data from multiple sources (patents, jobs, news, GitHub) and
    provides a unified intelligence report.
    
    Args:
        company: Company name (e.g., "Anthropic", "OpenAI"). Case-insensitive.
        include_patents: If True, fetch patent data from BigQuery. Default: True.
        include_jobs: If True, fetch job postings. Default: True.
        include_news: If True, fetch recent news articles. Default: True.
    
    Returns:
        Dictionary with structure:
        {
            "company": str,
            "summary": str,
            "patents": List[Patent],
            "jobs": List[Job],
            "news": List[NewsArticle],
            "github_repos": List[Repo],
            "competitive_score": float,
            "insights": List[str],
            "generated_at": str (ISO 8601 timestamp)
        }
    
    Raises:
        ValueError: If company name is empty or invalid.
        DataFetchError: If data fetching from any source fails.
        AnalysisError: If intelligence analysis fails.
    
    Examples:
        >>> intel = fetch_competitive_intelligence("Anthropic")
        >>> print(f"Found {len(intel['patents'])} patents")
        Found 42 patents
        
        >>> intel = fetch_competitive_intelligence(
        ...     "OpenAI",
        ...     include_patents=True,
        ...     include_jobs=False
        ... )
    
    Note:
        This function makes multiple external API calls and may take 5-10 seconds
        to complete. Consider using caching for frequently requested companies.
    
    See Also:
        - fetch_patents: Fetch only patent data
        - fetch_jobs: Fetch only job postings
        - CompetitiveIntelligenceAgent.analyze: Full AI-powered analysis
    """
    # Implementation...
```

**Tooling:**

```bash
# Check docstring coverage
interrogate src/ --fail-under=100 --verbose
```

**Effort:** 1 day  
**Risk:** 🟢 Low

---

### RF-012: Remove Dead Code and TODOs

**Current Issues:**
- 15+ TODO comments (some >6 months old)
- Commented-out code blocks
- Unused imports
- Unreachable code

**Process:**

1. **Find all TODOs:**

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX" src/
```

2. **Categorize:**
   - **Do now:** Critical items (security, bugs)
   - **Create ticket:** Feature requests
   - **Remove:** Obsolete/invalid

3. **Remove commented code:**

```bash
# Find commented code blocks
grep -rn "^# def \|^#.*return" src/
```

4. **Remove unused imports:**

```bash
# Use autoflake
autoflake --remove-all-unused-imports --recursive --in-place src/
```

5. **Find unreachable code:**

```bash
# Use vulture
vulture src/ --min-confidence 80
```

**Effort:** 0.5 days  
**Risk:** 🟢 Low (remove only, no new code)

---

## 🚀 PERFORMANCE REFACTORINGS

### RF-013: Implement Caching Layer

**Current Problem:**
- Same BigQuery queries run repeatedly
- Gemini calls for identical queries (expensive)
- No response caching

**Solution:**

```python
# shared/cache.py
from typing import Optional, Any, Callable
from functools import wraps
import hashlib
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheBackend:
    """Abstract cache backend"""
    
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: int):
        raise NotImplementedError
    
    def delete(self, key: str):
        raise NotImplementedError

class MemoryCache(CacheBackend):
    """In-memory cache (for Cloud Run)"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        # Check expiry
        if key in self._expiry and datetime.utcnow() > self._expiry[key]:
            self.delete(key)
            return None
        
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int):
        self._cache[key] = value
        self._expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)
    
    def delete(self, key: str):
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

# Global cache instance
cache = MemoryCache()

def cached(ttl: int = 300):
    """
    Cache function results for TTL seconds.
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
    
    Usage:
        @cached(ttl=600)
        def expensive_query(company: str) -> List[Patent]:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            key = hashlib.md5(
                json.dumps(key_data, sort_keys=True).encode()
            ).hexdigest()
            
            # Check cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.info(f"Cache HIT: {func.__name__} (key={key[:8]})")
                return cached_value
            
            # Cache miss - call function
            logger.info(f"Cache MISS: {func.__name__} (key={key[:8]})")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Usage:
@cached(ttl=3600)  # Cache for 1 hour
def fetch_patents(company: str) -> List[Patent]:
    """Fetch patents (cached)"""
    # Expensive BigQuery call
    return query_bigquery(company)

@cached(ttl=1800)  # Cache for 30 minutes
def run_gemini_analysis(query: str, context: Dict) -> str:
    """Run Gemini analysis (cached)"""
    # Expensive Gemini API call
    return gemini_model.generate(query, context)
```

**Benefits:**
- ✅ Reduce BigQuery costs (100+ queries → 10)
- ✅ Reduce Gemini costs ($100/day → $10/day)
- ✅ Faster response times (5s → 500ms for cached)

**Effort:** 1 day  
**Risk:** 🟡 Medium (must handle cache invalidation)

---

### RF-014: Optimize Database Queries

**Current Problems:**
- No indexes on Firestore queries
- BigQuery queries missing LIMIT clauses
- N+1 query problem (fetch 100 jobs, then query each for details)

**Optimizations:**

**1. Add Firestore Indexes:**

```yaml
# firestore.indexes.json
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
    }
  ]
}
```

**2. Add LIMIT to BigQuery:**

```sql
-- BEFORE (Scans entire table - expensive)
SELECT * FROM `patents.fivetran_uspto`
WHERE LOWER(assignee) LIKE '%anthropic%'

-- AFTER (Limit results)
SELECT * FROM `patents.fivetran_uspto`
WHERE LOWER(assignee) LIKE '%anthropic%'
ORDER BY publication_date DESC
LIMIT 1000
```

**3. Fix N+1 Queries:**

```python
# BEFORE (N+1 problem)
job_ids = [job['id'] for job in jobs]
details = []
for job_id in job_ids:
    # 100 separate Firestore queries!
    detail = db.collection('job_details').document(job_id).get()
    details.append(detail)

# AFTER (Batch query)
job_ids = [job['id'] for job in jobs]
# Single batch query
details = db.get_all([
    db.collection('job_details').document(job_id)
    for job_id in job_ids
])
```

**Performance Impact:**
- Firestore queries: 2-3s → 200-300ms
- BigQuery cost: $5/query → $0.50/query
- N+1 fix: 100 queries → 1 query

**Effort:** 1 day  
**Risk:** 🟢 Low

---

## 📅 REFACTORING ROADMAP

### Sprint 1 (5 days)

**Week 1:**
- [x] RF-001: Extract Business Logic (2 days)
- [x] RF-009: Eliminate Code Duplication (1 day)
- [x] RF-012: Remove Dead Code (0.5 days)
- [x] RF-004: Configuration Management (1 day)
- [x] RF-008: Add Type Hints (0.5 days - start)

**Deliverables:**
- Business logic separated from UI
- Zero code duplication
- Clean codebase (no TODOs/dead code)
- Centralized configuration

---

### Sprint 2 (5 days)

**Week 2:**
- [x] RF-002: Consolidate Cloud Functions (2 days)
- [x] RF-006: Organize as Monorepo (1 day)
- [x] RF-003: Repository Pattern (2 days)

**Deliverables:**
- Cloud Functions refactored with shared code
- Monorepo structure
- Data access abstracted

---

### Sprint 3 (5 days)

**Week 3:**
- [x] RF-005: Split app.py (1 day)
- [x] RF-007: Package Structure (1 day)
- [x] RF-008: Type Hints (1.5 days - complete)
- [x] RF-010: Error Handling (1 day)
- [x] RF-011: Docstrings (0.5 days)

**Deliverables:**
- Modular codebase
- Installable package
- 100% type coverage
- Production-ready error handling

---

### Sprint 4 (Performance) (Optional - Post-MVP)

**Week 4:**
- [x] RF-013: Caching Layer (1 day)
- [x] RF-014: Optimize Queries (1 day)
- [x] Load testing and optimization
- [x] Performance benchmarking

---

## ✅ SUCCESS CRITERIA

**Code Quality Metrics:**

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| **Type Coverage** | 30% | → 100% | ✅ 100% |
| **Docstring Coverage** | 20% | → 100% | ✅ 100% |
| **Test Coverage** | 0% | → 80% | ✅ 80% |
| **Code Duplication** | 15% | → 2% | ✅ <5% |
| **Cyclomatic Complexity** | 18 (max) | → 8 (max) | ✅ <10 |
| **File Size** | 500 lines (max) | → 200 lines (max) | ✅ <250 |
| **Function Size** | 100 lines (max) | → 30 lines (max) | ✅ <50 |

**Architecture Metrics:**

| Metric | Before | After |
|--------|--------|-------|
| **Modularity** | ⚠️ Monolithic | ✅ Modular |
| **Testability** | ❌ No unit tests | ✅ 200+ tests |
| **Reusability** | ❌ UI-coupled | ✅ Framework-agnostic |
| **Maintainability** | ⚠️ Medium | ✅ High |

---

## 🚨 RISKS & MITIGATION

### Risk 1: Breaking Changes

**Likelihood:** 🟡 Medium  
**Impact:** 🔴 High

**Mitigation:**
- Extensive test coverage before refactoring
- Feature flags for gradual rollout
- Parallel run old/new implementations

---

### Risk 2: Refactoring Takes Too Long

**Likelihood:** 🟡 Medium  
**Impact:** 🟡 Medium

**Mitigation:**
- Time-box each refactoring (if over estimate, stop and reassess)
- Focus on high-value refactorings first (RF-001, RF-002, RF-009)
- Can skip low-priority refactorings (RF-013, RF-014)

---

### Risk 3: Regressions

**Likelihood:** 🟡 Medium  
**Impact:** 🔴 High

**Mitigation:**
- Write tests BEFORE refactoring
- Automated regression testing
- Manual QA checklist

---

## 📚 REFERENCES

- **Clean Code** by Robert C. Martin
- **Refactoring** by Martin Fowler
- **Python Design Patterns** (repository pattern, dependency injection)
- **Streamlit Best Practices** (component organization)

---

**Total Estimated Effort:** 15 days (3 sprints)  
**Priority:** 🟡 High (blocks production deployment)  
**Dependencies:** Test suite must be in place first

---

**Next Steps:**
1. Review and approve this refactoring plan
2. Set up test infrastructure (RF-000 - not in this doc)
3. Begin Sprint 1 refactorings
4. Monitor progress weekly


