# TASK PRIORITIES - IMPACT vs EFFORT MATRIX
## IntelAgent Competitive Intelligence Platform

**Ordered by:** Business Impact / Implementation Effort  
**Time Estimates:** Conservative (includes testing, docs, review)  
**Priority Scale:** P0 (Critical) → P1 (High) → P2 (Medium) → P3 (Low)

---

## 🔴 P0: CRITICAL (Fix Within 48 Hours)

### P0-001: Implement Basic Authentication
**Impact:** 🔴 CRITICAL - Prevents unlimited API abuse  
**Effort:** 🟡 Medium (2 days)  
**Dependencies:** None  
**Blocks:** P0-002, P0-003

**Why Critical:** App is currently wide open. Anyone can consume your Gemini API quota ($$$).

**Tasks:**
1. Install `streamlit-authenticator` package
2. Create `config/credentials.yaml` with user accounts
3. Add login screen at app entry point
4. Implement session management
5. Add logout functionality
6. Test authentication flow

**Files Changed:**
- `streamlit-app/requirements.txt` (+1 line)
- `streamlit-app/app.py` (~30 lines added)
- `config/credentials.yaml` (new file)

**Success Criteria:**
- [ ] Unauthenticated users see login screen
- [ ] Invalid credentials are rejected
- [ ] Authenticated users can use app
- [ ] Sessions persist across page refreshes
- [ ] Logout clears session

**Spec:** See `spec-001-authentication-system.md`

---

### P0-002: Secure Cloud Functions
**Impact:** 🔴 CRITICAL - Prevents database pollution & cost explosion  
**Effort:** 🟢 Low (4 hours)  
**Dependencies:** None

**Why Critical:** Public Cloud Functions allow anyone to write to Firestore, drain API quota.

**Tasks:**
1. Deploy functions with `--no-allow-unauthenticated`
2. Add service account verification
3. Restrict CORS to specific origins
4. Update Cloud Scheduler with OIDC authentication
5. Test authenticated function calls

**Files Changed:**
- `cloud-functions/*/main.py` (~20 lines per function)
- `cloud-functions/shared/auth_utils.py` (new file)

**Success Criteria:**
- [ ] Unauthenticated requests return 401
- [ ] Cloud Scheduler successfully triggers functions
- [ ] Cross-origin requests blocked
- [ ] Firestore only accepts writes from functions

---

### P0-003: Add Input Validation
**Impact:** 🔴 CRITICAL - Prevents SQL injection & prompt injection  
**Effort:** 🟢 Low (4 hours)  
**Dependencies:** None

**Why Critical:** User input goes directly to Gemini and BigQuery without sanitization.

**Tasks:**
1. Create `utils/validation.py` module
2. Add length checks (min 3, max 500 chars)
3. Add injection pattern detection
4. Add special character filtering
5. Add rate limiting per session (10/hour)
6. Test with OWASP injection test cases

**Files Changed:**
- `streamlit-app/utils/validation.py` (new file, ~100 lines)
- `streamlit-app/app.py` (~10 lines added)

**Success Criteria:**
- [ ] Long queries (>500 chars) blocked
- [ ] Short queries (<3 chars) blocked
- [ ] Injection patterns detected and blocked
- [ ] Rate limit enforced (11th query/hour fails)
- [ ] Legitimate queries still work

---

### P0-004: Deploy Firestore Security Rules
**Impact:** 🔴 CRITICAL - Prevents data breach  
**Effort:** 🟢 Low (2 hours)  
**Dependencies:** P0-001 (authentication)

**Why Critical:** Firestore is wide open. Anyone can read/write/delete all data.

**Tasks:**
1. Create `firestore.rules` file
2. Require authentication for all reads
3. Restrict writes to admin users only
4. Test rules with Firebase emulator
5. Deploy rules to production
6. Verify with security audit

**Files Changed:**
- `firestore.rules` (new file, ~50 lines)

**Success Criteria:**
- [ ] Unauthenticated reads fail
- [ ] Unauthenticated writes fail
- [ ] Authenticated users can read
- [ ] Only admins can write
- [ ] Cloud Functions can still write (service account)

---

## 🟠 P1: HIGH (Fix Within 1 Week)

### P1-001: Migrate Secrets to Secret Manager
**Impact:** 🟠 HIGH - Reduces token compromise risk  
**Effort:** 🟢 Low (3 hours)  
**Dependencies:** None

**Tasks:**
1. Create secrets in Secret Manager (GitHub token)
2. Grant Cloud Functions access to secrets
3. Update functions to fetch from Secret Manager
4. Remove environment variables
5. Test token rotation

**Files Changed:**
- `cloud-functions/github-activity/main.py` (~15 lines)

---

### P1-002: Add Structured Logging
**Impact:** 🟠 HIGH - Enables debugging & monitoring  
**Effort:** 🟢 Low (4 hours)  
**Dependencies:** None

**Tasks:**
1. Configure Cloud Logging integration
2. Replace `logger.info()` with structured logs
3. Add request/response logging
4. Add error logging with stack traces
5. Set up log-based metrics

**Files Changed:**
- All Python files (~5 lines per file)

---

### P1-003: Implement Rate Limiting
**Impact:** 🟠 HIGH - Prevents DoS & cost explosion  
**Effort:** 🟡 Medium (1 day)  
**Dependencies:** P0-001 (authentication)

**Tasks:**
1. Set up Redis for distributed rate limiting
2. Implement sliding window counter
3. Add rate limit middleware
4. Configure limits (10/hour, 100/day)
5. Add rate limit headers to responses
6. Test with load testing tool

**Files Changed:**
- `streamlit-app/middleware/rate_limit.py` (new file)
- `streamlit-app/requirements.txt` (+1 line: redis)
- `streamlit-app/app.py` (~10 lines)

---

### P1-004: Fix SQL Injection Vulnerability
**Impact:** 🟠 HIGH - Prevents data breach  
**Effort:** 🟢 Low (2 hours)  
**Dependencies:** None

**Tasks:**
1. Replace f-string queries with parameterized queries
2. Use BigQuery query parameters
3. Add input sanitization
4. Test with SQL injection payloads

**Files Changed:**
- `streamlit-app/gemini_agent.py` (~20 lines in `get_patents()`)

---

### P1-005: Add Basic Monitoring Dashboard
**Impact:** 🟠 HIGH - Detect outages & abuse  
**Effort:** 🟡 Medium (1 day)  
**Dependencies:** P1-002 (logging)

**Tasks:**
1. Create Cloud Monitoring dashboard
2. Add metrics (requests, errors, latency, cost)
3. Set up alerting (error rate, quota, cost)
4. Configure notifications (email/Slack)
5. Test alerts with synthetic errors

**No Code Changes** (configuration only)

---

### P1-006: Add Unit Testing Framework
**Impact:** 🟠 HIGH - Enables safe iteration  
**Effort:** 🔴 High (2 days)  
**Dependencies:** None

**Tasks:**
1. Set up pytest with pytest-cov
2. Write 20 unit tests for critical functions
3. Configure CI/CD pipeline (GitHub Actions)
4. Add test coverage report
5. Set minimum coverage threshold (60%)

**Files Changed:**
- `tests/` (new directory, ~500 lines of tests)
- `.github/workflows/test.yml` (new file)
- `pyproject.toml` (test config)

---

## 🟡 P2: MEDIUM (Fix Within 2 Weeks)

### P2-001: Implement Redis Caching Layer
**Impact:** 🟡 MEDIUM - Reduces cost & improves speed  
**Effort:** 🟡 Medium (1.5 days)  
**Dependencies:** None

**Tasks:**
1. Deploy Cloud Memorystore (Redis)
2. Implement cache wrapper for data fetch functions
3. Set TTLs (patents: 24h, jobs: 1h, news: 1h, github: 1h)
4. Add cache invalidation logic
5. Monitor cache hit rate

**Files Changed:**
- `streamlit-app/cache/redis_client.py` (new file)
- `streamlit-app/gemini_agent.py` (~50 lines added)
- `streamlit-app/requirements.txt` (+1 line)

**Expected Impact:**
- 90% cache hit rate → 90% cost reduction
- Response time: 8s → 0.5s (cached queries)

---

### P2-002: Optimize BigQuery Queries
**Impact:** 🟡 MEDIUM - Reduces cost & latency  
**Effort:** 🟢 Low (4 hours)  
**Dependencies:** None

**Tasks:**
1. Create materialized view for common companies
2. Add table partitioning (by publication_date)
3. Create composite indexes
4. Analyze query plans
5. Benchmark before/after

**No Code Changes** (SQL/config only)

**Expected Impact:**
- Query time: 3-5s → 0.5-1s
- Query cost: $0.05 → $0.01 per query

---

### P2-003: Add Loading Skeletons & States
**Impact:** 🟡 MEDIUM - Improves perceived performance  
**Effort:** 🟢 Low (4 hours)  
**Dependencies:** None

**Tasks:**
1. Create skeleton UI components
2. Add to agent execution flow
3. Add progress indicators
4. Add estimated time display
5. Test on slow connections

**Files Changed:**
- `streamlit-app/components.py` (~50 lines)
- `streamlit-app/app.py` (~20 lines)

---

### P2-004: Implement Error Boundaries
**Impact:** 🟡 MEDIUM - Prevents app crashes  
**Effort:** 🟢 Low (3 hours)  
**Dependencies:** None

**Tasks:**
1. Create error boundary decorator
2. Wrap all major UI components
3. Add user-friendly error messages
4. Add retry buttons
5. Test with synthetic errors

**Files Changed:**
- `streamlit-app/utils/error_handling.py` (new file)
- `streamlit-app/app.py` (~15 lines)

---

### P2-005: Add Integration Tests
**Impact:** 🟡 MEDIUM - Validates API contracts  
**Effort:** 🟡 Medium (1.5 days)  
**Dependencies:** P1-006 (test framework)

**Tasks:**
1. Write 15 integration tests
2. Mock external APIs (BigQuery, Firestore, Gemini)
3. Test end-to-end workflows
4. Add to CI/CD pipeline

**Files Changed:**
- `tests/integration/` (new directory, ~400 lines)

---

### P2-006: Parallelize Data Fetching
**Impact:** 🟡 MEDIUM - 4x faster data collection  
**Effort:** 🟡 Medium (1 day)  
**Dependencies:** None

**Tasks:**
1. Convert tool execution to async/await
2. Use `asyncio.gather()` for parallel calls
3. Handle partial failures gracefully
4. Benchmark before/after

**Files Changed:**
- `streamlit-app/gemini_agent.py` (~100 lines refactored)

**Expected Impact:**
- Data collection: 8s → 2s (4 sources in parallel)

---

## 🟢 P3: LOW (Fix Within 1 Month)

### P3-001: Add WCAG AA Accessibility
**Impact:** 🟢 LOW - Improves inclusivity  
**Effort:** 🟡 Medium (1 day)

**Tasks:**
1. Add ARIA labels
2. Improve color contrast (4.5:1)
3. Add keyboard navigation
4. Add alt text for images
5. Run Lighthouse accessibility audit

---

### P3-002: Mobile Optimization
**Impact:** 🟢 LOW - Better mobile UX  
**Effort:** 🟡 Medium (1 day)

**Tasks:**
1. Test on mobile devices
2. Enlarge touch targets (min 48px)
3. Stack metrics vertically
4. Optimize font sizes
5. Test landscape/portrait modes

---

### P3-003: Add E2E Testing
**Impact:** 🟢 LOW - Validates user flows  
**Effort:** 🔴 High (2 days)

**Tasks:**
1. Set up Selenium/Playwright
2. Write 10 E2E test scenarios
3. Add to CI/CD pipeline
4. Run on staging before prod

---

### P3-004: Add User Accounts & Profiles
**Impact:** 🟢 LOW - Enhanced UX  
**Effort:** 🔴 High (3 days)

**Tasks:**
1. Create users collection in Firestore
2. Add profile management UI
3. Store user preferences
4. Add saved searches
5. Add query history

---

### P3-005: Implement Comparative Analysis
**Impact:** 🟢 LOW - New feature  
**Effort:** 🔴 High (3 days)

**Tasks:**
1. Design side-by-side comparison UI
2. Add comparison logic to agent
3. Generate comparison tables/charts
4. Test with multiple companies

---

## 📊 SUMMARY METRICS

### By Priority
| Priority | Tasks | Total Effort | Business Impact |
|----------|-------|--------------|-----------------|
| P0 | 4 | 3 days | Prevents abuse ($$$) |
| P1 | 6 | 7 days | Hardens security & reliability |
| P2 | 6 | 6 days | Improves performance & UX |
| P3 | 5 | 10 days | Nice-to-have features |
| **TOTAL** | **21** | **26 days** | Production-ready system |

### By Effort
| Effort | Count | Examples |
|--------|-------|----------|
| 🟢 Low (< 1 day) | 11 | Input validation, SQL fix, logging |
| 🟡 Medium (1-2 days) | 8 | Rate limiting, caching, mobile |
| 🔴 High (2+ days) | 2 | Testing framework, E2E tests |

### By Impact
| Impact | Count | Examples |
|--------|-------|----------|
| 🔴 CRITICAL | 4 | Auth, Cloud Function security, Firestore rules |
| 🟠 HIGH | 6 | Secrets, logging, rate limiting, monitoring |
| 🟡 MEDIUM | 6 | Caching, query optimization, error boundaries |
| 🟢 LOW | 5 | Accessibility, mobile, user accounts |

---

## 🎯 RECOMMENDED EXECUTION PLAN

### Week 1: Security Lockdown
- Day 1-2: P0-001 (Authentication)
- Day 2: P0-002 (Cloud Function security)
- Day 2: P0-003 (Input validation)
- Day 3: P0-004 (Firestore rules)
- Day 3: P1-001 (Secret Manager)
- Day 4: P1-004 (SQL injection fix)
- Day 5: P1-002 (Structured logging)

**Outcome:** App is secure, no longer wide open to abuse

### Week 2: Reliability & Testing
- Day 1-2: P1-006 (Unit testing framework)
- Day 2: P1-003 (Rate limiting)
- Day 3: P1-005 (Monitoring dashboard)
- Day 4: P2-004 (Error boundaries)
- Day 5: P2-005 (Integration tests)

**Outcome:** App is reliable, tested, monitored

### Week 3: Performance & UX
- Day 1-2: P2-001 (Redis caching)
- Day 2: P2-002 (BigQuery optimization)
- Day 3: P2-006 (Parallel data fetching)
- Day 4: P2-003 (Loading states)
- Day 5: Buffer/catch-up day

**Outcome:** App is fast, cost-optimized, good UX

### Week 4: Polish & Features
- Day 1: P3-001 (Accessibility)
- Day 2: P3-002 (Mobile optimization)
- Day 3-5: P3-004 (User accounts) OR P3-003 (E2E testing)

**Outcome:** App is production-grade, ready for launch

---

## 📋 TASK SELECTION GUIDE

**Choose tasks based on:**

1. **Security First:** Always prioritize P0/P1 security tasks
2. **Impact/Effort Ratio:** High impact + low effort = do first
3. **Dependencies:** Do prerequisite tasks before dependent ones
4. **Team Capacity:** Balance junior/senior tasks
5. **Quick Wins:** Sprinkle in easy wins for morale

**Decision Matrix:**

| Scenario | Recommended Tasks |
|----------|-------------------|
| **"We're launching next week!"** | P0-001 through P0-004 only (minimum viable security) |
| **"We have 2 weeks"** | All P0 + P1-001,002,003,004 (secure & monitored) |
| **"We have 1 month"** | All P0 + all P1 + P2-001,002,004,006 (production-ready) |
| **"We have 2 months"** | Everything except P3-003,004,005 (portfolio-quality) |

---

## ✅ PROGRESS TRACKING

**Use this checklist:**

```markdown
## Sprint 1: Security (Week 1)
- [ ] P0-001: Authentication implemented
- [ ] P0-002: Cloud Functions secured
- [ ] P0-003: Input validation added
- [ ] P0-004: Firestore rules deployed
- [ ] P1-001: Secrets in Secret Manager
- [ ] P1-002: Structured logging configured
- [ ] P1-004: SQL injection fixed

## Sprint 2: Reliability (Week 2)
- [ ] P1-003: Rate limiting active
- [ ] P1-005: Monitoring dashboard live
- [ ] P1-006: 20+ unit tests passing
- [ ] P2-004: Error boundaries added
- [ ] P2-005: 15+ integration tests passing

## Sprint 3: Performance (Week 3)
- [ ] P2-001: Redis caching deployed (90%+ hit rate)
- [ ] P2-002: BigQuery queries 5x faster
- [ ] P2-003: Loading states added
- [ ] P2-006: Parallel data fetching (4x faster)

## Sprint 4: Polish (Week 4)
- [ ] P3-001: Accessibility score 90+
- [ ] P3-002: Mobile-responsive UI
- [ ] P3-003: E2E tests passing
```

---

## 🚀 SUCCESS METRICS

**Track these to measure progress:**

| Metric | Before | After P0/P1 | After P2 | After P3 |
|--------|--------|-------------|----------|----------|
| **Security Score** | 2/10 | 8/10 | 9/10 | 10/10 |
| **Test Coverage** | 0% | 60% | 75% | 85% |
| **Response Time (P95)** | 8s | 8s | 2s | 1.5s |
| **Error Rate** | Unknown | <5% | <2% | <1% |
| **Cost per Query** | Unknown | $0.20 | $0.05 | $0.03 |
| **Accessibility Score** | Unknown | Unknown | Unknown | 90+ |

---

**Next Steps:**
1. Review with team
2. Assign tasks to sprint backlog
3. Start with P0-001 (Authentication)
4. Track progress weekly
5. Celebrate wins!

**Questions?** Refer to individual specification documents in `speckit-prep/`.


