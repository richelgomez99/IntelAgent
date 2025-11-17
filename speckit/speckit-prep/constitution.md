# INTELAGENT PLATFORM CONSTITUTION
## Immutable Architectural Principles

**Project:** IntelAgent Competitive Intelligence Platform  
**Generated:** November 17, 2025  
**Version:** 1.0  
**Status:** ACTIVE

---

## PREAMBLE

This constitution defines the **immutable architectural principles** that govern all development on the IntelAgent platform. These principles are **NON-NEGOTIABLE** and must be followed by all team members.

**Purpose:** Transform a hackathon prototype into a production-grade, portfolio-quality system.

**Scope:** All code, all features, all changes - no exceptions.

---

## I. SECURITY FIRST
### "Security is not optional. Every feature must pass security review before deployment."

**Principle:** Security is the foundation. A single vulnerability can destroy trust, cause financial loss, and end the project.

### 1.1 Authentication Required
**Rule:** Every endpoint, every API, every data access MUST require authentication.

**Implementation:**
- ✅ No public Cloud Functions
- ✅ No public Firestore access
- ✅ OAuth for UI (Google Sign-In)
- ✅ API keys for programmatic access
- ✅ Service account authentication for backend services

**Violations:**
- ❌ Deploying endpoints without auth
- ❌ Bypassing auth "temporarily"
- ❌ Hardcoding default credentials

**Test Gate:** Every PR must include authentication checks in tests.

---

### 1.2 Input Validation Mandatory
**Rule:** All user input MUST be validated and sanitized before processing.

**Implementation:**
- ✅ Regex checks for injection patterns
- ✅ Length limits enforced (min 3, max 500 chars)
- ✅ Whitelist validation where possible
- ✅ HTML entity escaping
- ✅ SQL parameterized queries

**Violations:**
- ❌ Passing user input directly to AI/database
- ❌ Using f-strings for SQL queries
- ❌ Skipping validation "for quick testing"

**Test Gate:** 100% coverage required for validation code.

---

### 1.3 Secrets in Secret Manager
**Rule:** NO secrets in environment variables or code. Ever.

**Implementation:**
- ✅ GitHub tokens → Secret Manager
- ✅ API keys → Secret Manager
- ✅ Configuration → Secret Manager
- ✅ Automatic token rotation every 90 days

**Violations:**
- ❌ Committing secrets to git
- ❌ Putting secrets in environment variables
- ❌ Hardcoding API keys "temporarily"

**Test Gate:** CI checks for hardcoded secrets (gitleaks, trufflehog).

---

### 1.4 Security Audits Regular
**Rule:** Monthly security audits, penetration testing before major releases.

**Implementation:**
- ✅ OWASP ZAP automated scans weekly
- ✅ Dependency vulnerability scanning (Snyk/Dependabot)
- ✅ Manual penetration testing quarterly
- ✅ Bug bounty program for production

---

## II. TEST-DRIVEN DEVELOPMENT (TDD)
### "No code merges without tests. No exceptions."

**Principle:** Untested code is broken code. We just haven't discovered how yet.

### 2.1 80% Coverage Minimum
**Rule:** All new code must have 80%+ test coverage.

**Implementation:**
- ✅ Unit tests for business logic (70% of tests)
- ✅ Integration tests for API interactions (20%)
- ✅ E2E tests for critical user flows (10%)
- ✅ Coverage reports generated on every PR

**Violations:**
- ❌ Merging PRs that drop coverage
- ❌ Merging code without tests
- ❌ Writing tests after code (should be before)

**Test Gate:** CI blocks PR merge if coverage < 80%.

---

### 2.2 Write Tests First (TDD Cycle)
**Rule:** Follow Red → Green → Refactor cycle.

**Process:**
1. 🔴 **Red:** Write failing test
2. 🟢 **Green:** Implement minimum code to pass
3. 🔵 **Refactor:** Clean up with confidence

**Why:** Tests define requirements, prevent over-engineering, enable safe refactoring.

**Violations:**
- ❌ Writing code before tests
- ❌ Writing tests just to pass CI
- ❌ Mocking everything (write real tests)

---

### 2.3 Test Pyramid Balance
**Rule:** Balance test types appropriately.

**Ratio:**
- 70% Unit Tests (fast, isolated, high-value)
- 20% Integration Tests (API contracts)
- 10% E2E Tests (critical paths only)

**Why:**
- Unit tests are fast, catch bugs early
- Too many E2E tests are slow, flaky, expensive

**Anti-Pattern:**
- ❌ All E2E tests (slow, brittle)
- ❌ All mocked tests (false confidence)

---

### 2.4 No Flaky Tests
**Rule:** Tests must pass consistently. Flaky tests erode trust.

**Implementation:**
- ✅ Use `pytest-timeout` to prevent hanging
- ✅ Use `pytest-xdist` for parallel execution
- ✅ Mock external APIs (don't call real APIs in tests)
- ✅ Use `freezegun` to mock time
- ✅ Set random seeds for reproducibility

**Process for Flaky Tests:**
1. Quarantine immediately (mark as `@pytest.mark.flaky`)
2. Fix within 48 hours
3. If unfixable, delete (better no test than flaky test)

---

## III. OBSERVABILITY REQUIRED
### "If you can't measure it, you can't improve it."

**Principle:** Visibility into system behavior is essential for production operations.

### 3.1 Structured Logging
**Rule:** All operations log structured JSON with context.

**Required Fields:**
- `timestamp` (ISO 8601)
- `level` (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `user_id` (who triggered action)
- `request_id` (trace requests end-to-end)
- `operation` (what happened)
- `latency_ms` (how long it took)
- `cost_usd` (API costs)
- `error` (if applicable, with stack trace)

**Example:**
```python
logger.info(
    "agent_query_executed",
    user_id="user123",
    request_id="req-abc",
    query="Analyze Anthropic",
    tool_calls=4,
    response_time_ms=3200,
    tokens_used=8500,
    cost_usd=0.034
)
```

**Violations:**
- ❌ `print()` statements
- ❌ Unstructured logs ("User did thing")
- ❌ Logging sensitive data (passwords, tokens)

---

### 3.2 Custom Metrics
**Rule:** Track business metrics in Cloud Monitoring.

**Required Metrics:**
- Query latency (P50/P95/P99)
- API quota consumption (% of limit)
- Cost per query (USD)
- Error rate (% of requests)
- Cache hit rate (% cached)
- User engagement (queries per user)

**Dashboards:**
- ✅ Real-time ops dashboard (latency, errors, quota)
- ✅ Business metrics dashboard (usage, cost, growth)
- ✅ Security dashboard (auth failures, rate limits)

---

### 3.3 Alerting Configured
**Rule:** Critical issues trigger immediate alerts.

**Alert Thresholds:**
- Error rate > 5% → Page on-call (PagerDuty)
- API quota > 80% → Notify team (Slack)
- Response time > 10s → Investigate
- Cost per day > $100 → Notify team
- No traffic for 1 hour → Check deployment
- 5 failed logins → Security alert

**Notification Channels:**
- 🔴 Critical → PagerDuty (24/7 on-call)
- 🟠 High → Slack #incidents channel
- 🟡 Medium → Email to team
- 🟢 Low → Log to dashboard

---

### 3.4 Distributed Tracing
**Rule:** Trace requests end-to-end across services.

**Implementation:**
- ✅ Use OpenTelemetry for instrumentation
- ✅ Propagate trace context across services
- ✅ Store traces in Cloud Trace
- ✅ Visualize request paths

**Use Cases:**
- Debug slow queries (which service is bottleneck?)
- Track errors across services
- Optimize performance (identify hotspots)

---

## IV. PERFORMANCE BUDGETS
### "Fast by default. Optimize for speed and cost."

**Principle:** Performance is a feature. Slow apps lose users. Expensive apps lose money.

### 4.1 Response Time Targets
**Rule:** Meet performance SLOs or explain why not.

**Targets:**
- P50: < 1 second (50% of requests)
- P95: < 2 seconds (95% of requests)
- P99: < 5 seconds (99% of requests)
- P99.9: < 10 seconds (99.9% of requests)

**Measurement:**
- Monitor with Cloud Monitoring
- Track weekly in team dashboard
- Alert if P95 > 3 seconds for 5 minutes

**Response if Exceeded:**
1. Identify bottleneck (Cloud Trace)
2. Optimize (caching, query optimization, parallelization)
3. If unavoidable, document and set new baseline

---

### 4.2 Cost Budgets
**Rule:** Stay within cost budgets or request increase.

**Budgets:**
- Cost per query: < $0.10
- Daily cost: < $100
- Monthly cost: < $3,000

**Optimization Strategies:**
- ✅ Cache frequently accessed data (Redis)
- ✅ Use cheapest tier that meets SLOs
- ✅ Optimize BigQuery queries (avoid full scans)
- ✅ Batch operations where possible
- ✅ Use Cloud Functions Gen 2 (cheaper)

**Monthly Review:**
- Review cost dashboard
- Identify cost spikes
- Optimize highest-cost operations
- Forecast next month's cost

---

### 4.3 Caching Strategy
**Rule:** Cache aggressively, invalidate smartly.

**What to Cache:**
- Patents (TTL: 24 hours) - rarely change
- Jobs (TTL: 1 hour) - change daily
- News (TTL: 1 hour) - change frequently
- GitHub (TTL: 1 hour) - change frequently
- Agent responses (TTL: 1 hour, keyed by query hash)

**Cache Invalidation:**
- ✅ Time-based (TTL)
- ✅ Manual (admin trigger)
- ✅ Event-based (new data arrives)

**Monitoring:**
- Cache hit rate (target: > 80%)
- Cache size (prevent unbounded growth)
- Cache latency (should be < 10ms)

---

### 4.4 Database Optimization
**Rule:** All queries use indexed fields.

**Implementation:**
- ✅ Firestore composite indexes for common queries
- ✅ BigQuery partitioned tables (by date)
- ✅ BigQuery clustered tables (by company)
- ✅ Regular query analysis (`EXPLAIN` plans)

---

## V. CODE QUALITY STANDARDS
### "Clean code is maintainable code."

**Principle:** Code is read 10x more than written. Optimize for readability.

### 5.1 Single Responsibility Principle
**Rule:** Functions do ONE thing. Files < 300 lines.

**Implementation:**
- ✅ Extract helper functions
- ✅ Break God files into modules
- ✅ Clear separation of concerns

**Violations:**
- ❌ Functions > 50 lines
- ❌ Files > 300 lines
- ❌ Classes > 500 lines

**Enforcement:** Linter warns if exceeded.

---

### 5.2 DRY (Don't Repeat Yourself)
**Rule:** No copy-paste code.

**Implementation:**
- ✅ Extract shared utilities
- ✅ Use inheritance/composition
- ✅ Centralize configuration

**Violations:**
- ❌ Duplicated CORS handling
- ❌ Repeated error handling patterns
- ❌ Multiple similar functions

**Process:** If you copy-paste, refactor into shared module.

---

### 5.3 Type Hints Required
**Rule:** All Python functions have full type annotations.

**Example:**
```python
def get_patents(company: str, limit: int = 50) -> Dict[str, Any]:
    """Fetch patents with type safety"""
    ...
```

**Why:**
- Catches bugs at dev time
- Enables IDE autocomplete
- Self-documenting code

**Enforcement:** `mypy` type checker runs in CI.

---

### 5.4 Code Review Required
**Rule:** 2 approvals before merge.

**Reviewer Checklist:**
- [ ] Tests written and passing
- [ ] Code follows style guide
- [ ] Security considerations addressed
- [ ] Performance implications considered
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Error handling appropriate

**No Merge If:**
- ❌ Tests failing
- ❌ Coverage dropped
- ❌ Linter errors
- ❌ Security concerns unaddressed

---

### 5.5 Consistent Style
**Rule:** Use automated formatters. Don't debate style.

**Tools:**
- `ruff format` - Code formatting
- `ruff check` - Linting
- `mypy` - Type checking

**Configuration:**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B"]
```

**Enforcement:** Pre-commit hooks run formatters automatically.

---

## VI. GRACEFUL DEGRADATION
### "Failures are inevitable. Handle them gracefully."

**Principle:** System should degrade gracefully, not crash catastrophically.

### 6.1 No Cascading Failures
**Rule:** One component failure doesn't crash the app.

**Implementation:**
- ✅ If BigQuery fails → Use fallback data
- ✅ If Gemini rate-limited → Queue + retry
- ✅ If Firestore slow → Show cached data
- ✅ If Cloud Function fails → Skip that data source

**Pattern:**
```python
try:
    patents = get_patents(company)
except Exception as e:
    logger.error(f"Patent fetch failed: {e}")
    patents = {
        "count": 0,
        "summary": "Patent data temporarily unavailable",
        "fallback": True
    }
```

---

### 6.2 Circuit Breakers
**Rule:** Stop calling failing services.

**Implementation:**
- After 5 failures → Open circuit (stop calling)
- Wait 30 seconds → Try again (half-open)
- If success → Close circuit (resume)
- If fails → Open circuit again

**Libraries:** Use `pybreaker` for circuit breaker pattern.

---

### 6.3 Meaningful Error Messages
**Rule:** Users get helpful errors, not stack traces.

**Good Error:**
```
⚠️ Patent data temporarily unavailable

We're having trouble connecting to the patent database. 
Showing cached results from 1 hour ago.

If this persists, contact support@intelagent.ai
```

**Bad Error:**
```
Exception: 'NoneType' object has no attribute 'get'
Traceback (most recent call last):
  File "gemini_agent.py", line 574, in get_patents
    ...
```

---

### 6.4 Retry with Backoff
**Rule:** Retry transient failures with exponential backoff.

**Implementation:**
```python
@retry.Retry(
    predicate=retry.if_exception_type(ResourceExhausted),
    initial=2.0,
    maximum=60.0,
    multiplier=2.0,
    deadline=300.0
)
def call_gemini_api(query):
    return gemini.generate_content(query)
```

---

## VII. SCALABILITY BY DESIGN
### "Design for 10x growth."

**Principle:** Plan for success. Design systems that can scale.

### 7.1 Stateless Architecture
**Rule:** No server-side state. Scale horizontally.

**Implementation:**
- ✅ Use Firestore for session data
- ✅ Use Redis for shared cache
- ✅ Cloud Run auto-scales to 1000 instances

**Violations:**
- ❌ Storing state in instance memory
- ❌ Assuming single instance
- ❌ File-based state

---

### 7.2 Async Where Possible
**Rule:** Parallelize independent operations.

**Implementation:**
- ✅ Fetch all data sources concurrently
- ✅ Use async/await for I/O
- ✅ Background jobs for heavy processing (Cloud Tasks)

**Expected Improvement:**
- Sequential: 8 seconds (4 sources × 2s each)
- Parallel: 2 seconds (max of all sources)
- 4x faster!

---

### 7.3 Database Indexing
**Rule:** All queries use indexed fields.

**Firestore Indexes:**
```javascript
// firestore.indexes.json
{
  "indexes": [
    {
      "collectionGroup": "jobs",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "company", "order": "ASCENDING" },
        { "fieldPath": "scraped_at", "order": "DESCENDING" }
      ]
    }
  ]
}
```

---

### 7.4 Horizontal Scaling
**Rule:** Add capacity by adding instances, not upgrading instances.

**Why:** More flexible, better fault tolerance, cheaper.

**Cloud Run Benefits:**
- Scales to 1000 instances automatically
- Scales to zero (no cost when idle)
- Pay per request

---

## VIII. DOCUMENTATION STANDARDS
### "Code is read 10x more than written. Document accordingly."

**Principle:** Good docs enable self-service, reduce interruptions, onboard faster.

### 8.1 API Documentation
**Rule:** Every endpoint documented with OpenAPI/Swagger.

**Required:**
- Request/response schemas
- Example requests/responses
- Error codes and meanings
- Authentication requirements
- Rate limits

---

### 8.2 Architecture Diagrams
**Rule:** Keep diagrams updated.

**Required Diagrams:**
- System architecture (high-level)
- Data flow diagrams
- Sequence diagrams for complex flows
- Infrastructure diagram (GCP resources)

**Tools:** Draw.io, Mermaid, PlantUML

---

### 8.3 Runbooks for Ops
**Rule:** Document common incident responses.

**Required Runbooks:**
- "What to do if Gemini API down"
- "How to increase quota"
- "How to roll back deployment"
- "How to investigate slow queries"
- "How to rotate secrets"

---

### 8.4 Code Comments
**Rule:** Comment WHY, not WHAT.

**Good Comment:**
```python
# Use exponential backoff to avoid hitting Gemini rate limits
# which can cause 5-minute delays before retry succeeds
@retry.Retry(initial=2.0, multiplier=2.0)
def call_api():
    ...
```

**Bad Comment:**
```python
# Call the API
def call_api():
    ...
```

---

## IX. CONTINUOUS IMPROVEMENT
### "Always be learning. Always be improving."

**Principle:** Stagnation is death. Iterate, measure, improve, repeat.

### 9.1 Post-Mortems Required
**Rule:** Every incident gets a blameless post-mortem.

**Template:**
1. **What happened?** (timeline of events)
2. **Why did it happen?** (root cause analysis)
3. **How do we prevent it?** (action items)
4. **Who owns action items?** (assign owners)
5. **Follow-up date** (verify items completed)

**Blameless Culture:**
- ✅ Focus on systems, not people
- ✅ "How can we prevent this?" not "Who did this?"
- ✅ Share learnings with team

---

### 9.2 Weekly Metrics Review
**Rule:** Review dashboards every week.

**Questions:**
- What's trending up/down?
- Any anomalies?
- Opportunities to optimize?
- Are we meeting SLOs?

**Attendees:** Engineering team, product, leadership

---

### 9.3 Tech Debt Sprints
**Rule:** 20% time for refactoring/cleanup.

**Schedule:** One week per month

**Focus:**
- Pay down accumulated tech debt
- Improve existing code quality
- Update dependencies
- Refactor God files
- Add missing tests

**Goal:** Prevent tech debt bankruptcy.

---

### 9.4 Quarterly Architecture Review
**Rule:** Assess system health every quarter.

**Review:**
- Is architecture still appropriate?
- Are we following principles?
- Where did we deviate and why?
- What should we change?
- Update constitution if needed

---

## X. ENFORCEMENT

### Principle Violations
**First offense:** Warning + coaching  
**Second offense:** Required training  
**Third offense:** Escalate to management

### Constitution Updates
**Frequency:** Quarterly review  
**Approval:** 75% team consensus required  
**Effective:** Immediately after approval

### Exceptions
**Process:**
1. Document reason for exception
2. Get approval from 2 senior engineers
3. Create ticket to fix exception
4. Review in next architecture meeting

**Valid Reasons:**
- Technical blocker (API limitation)
- Time-critical fix (production down)
- Proof-of-concept (not production code)

**Invalid Reasons:**
- "Too hard"
- "Takes too long"
- "Just this once"

---

## SIGNATURES

This constitution is adopted by the IntelAgent engineering team:

**Effective Date:** November 17, 2025  
**Next Review:** February 17, 2026  
**Status:** ACTIVE

---

**Remember:** These principles exist to build a system that is:
- **Secure** (can't be hacked)
- **Reliable** (doesn't crash)
- **Fast** (responds quickly)
- **Maintainable** (can be changed safely)
- **Cost-effective** (doesn't burn money)

**When in doubt:** Security first, test everything, measure everything.

**Questions?** Refer to specification documents for implementation details.

---

*"Excellence is not an act, but a habit." - Aristotle*

*"The code you write today is the technical debt of tomorrow." - Unknown*

*"Quality is not an act, it is a habit." - Aristotle*


