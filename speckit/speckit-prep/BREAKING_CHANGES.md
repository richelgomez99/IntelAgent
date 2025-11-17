# 💥 BREAKING CHANGES FORECAST
## IntelAgent Competitive Intelligence Platform

**Generated:** November 17, 2025  
**Audit Phase:** Pre-Production Security Hardening

---

## 🎯 EXECUTIVE SUMMARY

This document forecasts **all breaking changes** that will be introduced during the production-grade transformation. Breaking changes are categorized by severity and user impact.

**Total Breaking Changes:** 15  
**Critical (API/Integration):** 5  
**Major (Feature Changes):** 7  
**Minor (Configuration):** 3

---

## 🔴 CRITICAL BREAKING CHANGES

### BC-001: Authentication Required (IMMEDIATE)

**Impact:** ⚠️ **ALL USERS** - 100% breakage  
**Timeline:** Sprint 1 (Week 1)  
**Reversible:** No

**What's Breaking:**
- Current: Open access to all app functionality
- Future: **Login required** before any access

**User Impact:**
```
BEFORE:
1. Visit URL
2. Use app immediately

AFTER:
1. Visit URL
2. See login screen
3. Enter credentials
4. Use app
```

**Migration Path:**
1. **Week 0 (Now):** Email all current users
   - Announce authentication coming
   - Provide timeline
   - Share credential request form
2. **Week 1 (Deploy Day):** Send credentials via secure channel
3. **Week 1 (Deploy Day+1):** Support office hours for login issues

**API Impact:**
- None (no public API exists yet)

**Rollback Plan:**
- Feature flag `REQUIRE_AUTH=false` can disable (emergency only)
- Full rollback: Redeploy previous version (< 5 minutes)

---

### BC-002: Cloud Function Authentication Required

**Impact:** ⚠️ **ALL INTEGRATIONS** - Breaks external callers  
**Timeline:** Sprint 1 (Week 1)  
**Reversible:** No

**What's Breaking:**
- Current: Cloud Functions accept all requests (no auth header)
- Future: **API key required** in `Authorization: Bearer <key>` header

**Breaking API Calls:**

```python
# BEFORE (Works)
requests.get("https://job-scraper-abc.run.app", params={"company": "Anthropic"})

# AFTER (Breaks - Returns 401 Unauthorized)
requests.get("https://job-scraper-abc.run.app", params={"company": "Anthropic"})

# FIXED
headers = {"Authorization": "Bearer YOUR_API_KEY"}
requests.get("https://job-scraper-abc.run.app", 
             params={"company": "Anthropic"},
             headers=headers)
```

**Who's Affected:**
- Internal Streamlit app (will be updated automatically)
- **Any external scripts/tests calling these endpoints**
- **Monitoring/healthcheck systems**

**Migration Checklist:**
- [ ] Identify all external callers (grep for function URLs)
- [ ] Generate API keys for each caller
- [ ] Update all calls to include `Authorization` header
- [ ] Update monitoring systems
- [ ] Test thoroughly before deploy

---

### BC-003: Firestore Collection Structure Change

**Impact:** ⚠️ **DATA QUERIES** - Existing queries will fail  
**Timeline:** Sprint 2 (Week 2)  
**Reversible:** Yes (with data migration)

**What's Breaking:**
- Current flat structure: `jobs/`, `news/`, `github_repos/`
- Future namespaced: `tenants/{tenant_id}/jobs/`, `tenants/{tenant_id}/news/`

**Breaking Queries:**

```python
# BEFORE (Works)
db.collection('jobs').where('company', '==', 'Anthropic').get()

# AFTER (Breaks - Returns 0 results)
db.collection('jobs').where('company', '==', 'Anthropic').get()

# FIXED
tenant_id = get_current_tenant_id()
db.collection('tenants').document(tenant_id).collection('jobs')\
  .where('company', '==', 'Anthropic').get()
```

**Data Migration Required:**
1. **Copy** existing data to new structure (idempotent)
2. **Run both** old and new paths for 7 days (dual-write)
3. **Verify** data parity
4. **Switch** reads to new path
5. **Archive** old collections (keep for 30 days)

**Rollback Plan:**
- Old collections remain intact for 30 days
- Can revert to old path with config change

---

### BC-004: BigQuery Schema Update (Fivetran Connector)

**Impact:** ⚠️ **EXISTING DASHBOARDS/QUERIES** - Looker/Tableau reports break  
**Timeline:** Sprint 2 (Week 3)  
**Reversible:** Yes (via views)

**What's Breaking:**
- Column renames for consistency:
  - `publication_date` → `published_at` (TIMESTAMP)
  - `inventors` → `inventor_names` (STRING[])
  - `filing_country` → `country_code` (STRING)

**Breaking SQL:**

```sql
-- BEFORE (Works)
SELECT publication_date, inventors, filing_country
FROM `patents.fivetran_uspto`
WHERE publication_date > '2024-01-01'

-- AFTER (Breaks - Columns don't exist)
SELECT publication_date, inventors, filing_country
FROM `patents.fivetran_uspto`
WHERE publication_date > '2024-01-01'
-- ERROR: Column publication_date not found

-- FIXED
SELECT published_at, inventor_names, country_code
FROM `patents.fivetran_uspto`
WHERE published_at > '2024-01-01'
```

**Migration Strategy:**
1. **Create backwards-compatible view:**

```sql
CREATE OR REPLACE VIEW `patents.fivetran_uspto_v1` AS
SELECT
  published_at AS publication_date,
  inventor_names AS inventors,
  country_code AS filing_country,
  *
FROM `patents.fivetran_uspto`;
```

2. **Update queries gradually** (no deadline pressure)
3. **Deprecate view** after 90 days

---

### BC-005: Environment Variable Changes

**Impact:** ⚠️ **DEPLOYMENT PIPELINES** - CI/CD breaks  
**Timeline:** Sprint 1 (Week 1)  
**Reversible:** No

**What's Breaking:**
- Renamed for consistency:
  - `GCP_PROJECT` → `GCP_PROJECT_ID`
  - `BIGQUERY_DATASET` → `BIGQUERY_DATASET_ID`
  - `FIRESTORE_COLLECTION` → removed (no longer used)

**Breaking Deployment Scripts:**

```bash
# BEFORE (Works)
gcloud run deploy intelagent-app \
  --set-env-vars GCP_PROJECT=my-project,BIGQUERY_DATASET=patents

# AFTER (Breaks - App fails to start)
# ERROR: Required env var GCP_PROJECT_ID not found

# FIXED
gcloud run deploy intelagent-app \
  --set-env-vars GCP_PROJECT_ID=my-project,BIGQUERY_DATASET_ID=patents
```

**Who's Affected:**
- CI/CD pipelines (GitHub Actions, Cloud Build)
- Terraform/IaC configurations
- Local development `.env` files
- Documentation

**Migration Checklist:**
- [ ] Update CI/CD pipeline files
- [ ] Update Terraform variables
- [ ] Update `.env.example`
- [ ] Update deployment documentation
- [ ] Send team notification

---

## 🟡 MAJOR BREAKING CHANGES

### BC-006: Session State Structure Change

**Impact:** 🟠 **SESSIONS INVALIDATED** - Users logged out once  
**Timeline:** Sprint 1 (Week 2)  
**Reversible:** No

**What's Breaking:**
- Session state keys renamed for namespacing:
  - `messages` → `chat_session.messages`
  - `context` → `chat_session.context`
  - `analysis_history` → `user_data.analysis_history`

**User Impact:**
- On deployment: All active sessions cleared
- Users must re-enter any in-progress queries
- Chat history lost (not persisted yet)

**Mitigation:**
1. **Deploy during low-traffic window** (3am PST)
2. **Show banner 24h before:** "Maintenance window scheduled"
3. **Add session migration helper** (best-effort recovery)

---

### BC-007: Response Format Change

**Impact:** 🟠 **EXPORT/INTEGRATION** - JSON format changes  
**Timeline:** Sprint 3 (Week 4)  
**Reversible:** Yes (via versioned API)

**What's Breaking:**
- JSON export structure changes to match industry standards:

```json
// BEFORE
{
  "response": "...",
  "metadata": {
    "patents_found": 10
  }
}

// AFTER
{
  "version": "2.0",
  "data": {
    "analysis": "...",
    "sources": {
      "patents": 10
    }
  },
  "meta": {
    "generated_at": "2025-11-17T...",
    "model": "gemini-2.5-pro"
  }
}
```

**Mitigation:**
- Add `?format_version=1` query param to get old format (90 day deprecation)
- Update all internal consumers immediately

---

### BC-008: CSS Class Name Changes

**Impact:** 🟠 **CUSTOM STYLING** - User-added CSS breaks  
**Timeline:** Sprint 3 (Week 5)  
**Reversible:** No

**What's Breaking:**
- CSS classes renamed for BEM convention:
  - `.metric-card` → `.metric-card__container`
  - `.insight` → `.insight-card__wrapper`
  - `.badge-high` → `.priority-badge--high`

**Who's Affected:**
- Users with custom CSS overrides (if any)
- Browser extensions modifying the UI
- Screenshot/testing tools with CSS selectors

**Mitigation:**
- Unlikely to affect anyone (no public custom CSS feature)
- Add deprecation aliases for 30 days

---

### BC-009: Gemini Function Call Schema Change

**Impact:** 🟠 **CACHED FUNCTION SIGNATURES** - Cache invalidated  
**Timeline:** Sprint 2 (Week 2)  
**Reversible:** No

**What's Breaking:**
- Function schemas restructured (better validation):

```python
# BEFORE
{
  "name": "get_patents",
  "parameters": {
    "company": "string"
  }
}

# AFTER
{
  "name": "get_patents",
  "description": "Fetch patent data...",
  "parameters": {
    "type": "object",
    "properties": {
      "company": {
        "type": "string",
        "description": "Company name",
        "minLength": 1
      }
    },
    "required": ["company"]
  }
}
```

**Impact:**
- All cached Gemini responses invalidated (one-time)
- First queries after deploy ~3x slower (no cache)
- Performance returns to normal after cache warms up

---

### BC-010: Rate Limiting Introduced

**Impact:** 🟠 **HIGH-FREQUENCY USERS** - Requests throttled  
**Timeline:** Sprint 1 (Week 2)  
**Reversible:** Yes (via config)

**What's Breaking:**
- New rate limits enforced:
  - **Per user:** 10 queries/minute, 100 queries/hour
  - **Per IP:** 30 queries/minute, 300 queries/hour
  - **Cloud Functions:** 100 requests/minute/function

**Error Response:**

```json
HTTP 429 Too Many Requests
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded: 10 requests per minute",
  "retry_after": 45
}
```

**Who's Affected:**
- Automated scripts making rapid requests
- Power users doing batch analysis
- Integration tests (need to add delays)

**Mitigation:**
- Add clear error messages
- Show rate limit in UI ("9/10 queries used")
- Offer "request limit increase" form

---

### BC-011: GitHub Token Scope Requirements

**Impact:** 🟠 **GITHUB FUNCTION** - May need token regeneration  
**Timeline:** Sprint 2 (Week 2)  
**Reversible:** No

**What's Breaking:**
- Token now requires additional scopes:
  - `public_repo` → `repo` (full access needed for READMEs)
  - Add: `read:org` (for organization verification)

**Impact:**
- If current token lacks scopes: GitHub function returns 403 errors
- Must regenerate token with new scopes

**Migration:**
1. Generate new token with correct scopes
2. Update Cloud Function env var: `GITHUB_TOKEN`
3. Redeploy function

---

### BC-012: Firestore Security Rules Enforced

**Impact:** 🟠 **DIRECT DATABASE ACCESS** - Manual queries fail  
**Timeline:** Sprint 1 (Week 1)  
**Reversible:** Yes (revert rules)

**What's Breaking:**
- Current: Open Firestore (test mode)
- Future: Strict security rules

**Breaking Access:**

```javascript
// BEFORE (Works)
// Any client-side read/write from console
db.collection('jobs').get()

// AFTER (Breaks - Returns permission denied)
db.collection('jobs').get()
// ERROR: Missing or insufficient permissions

// FIXED
// Use service account or authenticated requests only
```

**Who's Affected:**
- Direct Firebase console queries (developers)
- Any scripts using Firebase client SDK without auth

**Migration:**
- All access must go through Cloud Functions (authenticated)
- Developers: Use service account for admin operations

---

## 🟢 MINOR BREAKING CHANGES

### BC-013: Log Format Change

**Impact:** 🟢 **LOG PARSERS** - Custom log parsing breaks  
**Timeline:** Sprint 2 (Week 3)  
**Reversible:** Yes (configure structured logging)

**What's Breaking:**
- Switch from plain text to structured JSON logs:

```
BEFORE:
INFO: User query processed: "analyze Anthropic"

AFTER:
{"severity":"INFO","message":"User query processed","query":"analyze Anthropic","timestamp":"2025-11-17T..."}
```

**Who's Affected:**
- Custom log aggregation scripts
- Log alerting regex patterns

**Migration:**
- Update log parsing to handle JSON
- Cloud Logging already supports both formats

---

### BC-014: Default Company List Change

**Impact:** 🟢 **AUTOCOMPLETE** - Suggestion list updated  
**Timeline:** Sprint 3 (Week 4)  
**Reversible:** Yes (config file)

**What's Breaking:**
- Default companies in autocomplete expanded:
  - Added: 15 new companies (Mistral, Cohere, etc.)
  - Removed: 3 defunct companies
  - Updated: 2 company name changes (rebrands)

**User Impact:**
- Users typing old company names see different suggestions
- Minimal impact (can still enter any company name)

---

### BC-015: Dockerfile Base Image Update

**Impact:** 🟢 **CUSTOM BUILDS** - Must update custom Dockerfiles  
**Timeline:** Sprint 2 (Week 2)  
**Reversible:** No

**What's Breaking:**
- Base image upgrade:
  - `python:3.11-slim` → `python:3.11-slim-bookworm`
  - Debian version: Bullseye → Bookworm

**Impact:**
- Breaks custom Dockerfiles extending the base image
- Some apt packages renamed (rare)

---

## 📋 BREAKING CHANGE TIMELINE

### Week 1 (Sprint 1)
- ✅ BC-001: Authentication Required
- ✅ BC-002: Cloud Function Auth
- ✅ BC-005: Environment Variables
- ✅ BC-012: Firestore Security Rules

### Week 2 (Sprint 1)
- ✅ BC-006: Session State Structure
- ✅ BC-010: Rate Limiting
- ✅ BC-011: GitHub Token Scopes
- ✅ BC-015: Dockerfile Base Image

### Week 3 (Sprint 2)
- ✅ BC-003: Firestore Structure
- ✅ BC-009: Gemini Function Schema
- ✅ BC-013: Log Format

### Week 4 (Sprint 3)
- ✅ BC-004: BigQuery Schema
- ✅ BC-007: Response Format
- ✅ BC-014: Default Company List

### Week 5 (Sprint 3)
- ✅ BC-008: CSS Class Names

---

## 🛡️ RISK MITIGATION STRATEGIES

### Pre-Deployment

**1. Feature Flags:**
```python
# All breaking changes behind flags
if config.FEATURE_FLAG_AUTH_REQUIRED:
    require_authentication()
else:
    logger.warning("Running without auth (dev mode)")
```

**2. Gradual Rollout:**
- Week 1: 10% of traffic
- Week 1 (Day 3): 50% of traffic
- Week 2: 100% of traffic

**3. Automated Testing:**
- 200+ integration tests covering all API contracts
- Backward compatibility tests for all JSON responses
- Smoke tests run every 15 minutes in production

---

### During Deployment

**1. Dual-Write Period:**
- Write to both old and new Firestore structures for 7 days
- Allows instant rollback without data loss

**2. Canary Deployment:**
- Deploy to 1 instance first
- Monitor error rates for 30 minutes
- Auto-rollback if error rate > 1%

**3. Real-Time Monitoring:**
- Dashboard showing:
  - Login success rate
  - API error rate by endpoint
  - Session creation/failure
  - Database query failures

---

### Post-Deployment

**1. Backwards Compatibility Views:**
- SQL views for old BigQuery schema (90 days)
- API versioning for JSON exports (90 days)
- Legacy endpoints with deprecation warnings

**2. User Communication:**
- **T-7 days:** Email announcing changes
- **T-1 day:** In-app banner warning
- **T-0 (deploy):** In-app changelog modal
- **T+1 day:** Email recap with support links

**3. Support Readiness:**
- Office hours for first 3 days post-deploy
- FAQ document published before deploy
- Support team trained on all breaking changes

---

## 📊 USER IMPACT ASSESSMENT

### Impact by User Type

| User Type | Affected Changes | Severity | Mitigation |
|-----------|------------------|----------|------------|
| **End Users** | BC-001, BC-006, BC-010 | 🔴 High | Email notification, support hours |
| **Developers** | BC-002, BC-003, BC-005, BC-012 | 🔴 High | Migration guide, code examples |
| **Data Analysts** | BC-004, BC-007 | 🟡 Medium | Backwards-compatible views |
| **DevOps** | BC-005, BC-015 | 🟡 Medium | Updated deployment docs |
| **Integrations** | BC-002, BC-007 | 🔴 High | API versioning, 90-day notice |

---

### Communication Plan

**T-30 Days:**
- [ ] Publish this breaking changes document
- [ ] Email all users about upcoming changes
- [ ] Post announcement on status page

**T-14 Days:**
- [ ] Send detailed migration guide
- [ ] Offer migration support calls
- [ ] Update all documentation

**T-7 Days:**
- [ ] Send final reminder email
- [ ] Show in-app banner about changes
- [ ] Freeze new features (bug fixes only)

**T-1 Day:**
- [ ] Send "tomorrow is the day" email
- [ ] Prepare support team
- [ ] Final verification of rollback procedures

**T-0 (Deploy Day):**
- [ ] Deploy during low-traffic window (3am PST)
- [ ] Monitor closely for 4 hours
- [ ] Send "deployment complete" email
- [ ] Update status page

**T+1 Day:**
- [ ] Send recap email with any issues/fixes
- [ ] Gather user feedback
- [ ] Plan hotfixes if needed

---

## 🔄 ROLLBACK PROCEDURES

### Emergency Rollback (< 5 minutes)

```bash
# Revert to previous Cloud Run revision
gcloud run services update-traffic intelagent-app \
  --to-revisions=intelagent-app-previous=100

# Revert Cloud Functions
gcloud functions deploy job-scraper \
  --source=gs://backups/job-scraper-v1.0.0.zip

# Revert Firestore rules
firebase deploy --only firestore:rules --config firebase.backup.json

# Disable feature flags
gcloud run services update intelagent-app \
  --set-env-vars FEATURE_FLAG_AUTH_REQUIRED=false
```

### Partial Rollback (Specific Feature)

```bash
# Disable just authentication (keep other changes)
gcloud run services update intelagent-app \
  --set-env-vars FEATURE_FLAG_AUTH_REQUIRED=false

# Revert to old Firestore structure (keep new security rules)
gcloud run services update intelagent-app \
  --set-env-vars USE_LEGACY_FIRESTORE_STRUCTURE=true
```

---

## ✅ ACCEPTANCE CRITERIA

**This document is complete when:**

- [x] All 15 breaking changes documented
- [x] Migration path defined for each critical change
- [x] Rollback procedures tested
- [x] User communication plan finalized
- [x] Timeline with clear milestones
- [x] Risk mitigation strategies defined
- [x] Impact assessment completed
- [ ] Reviewed by engineering team
- [ ] Reviewed by product team
- [ ] Approved by stakeholders
- [ ] Published to documentation site

---

## 📞 ESCALATION CONTACTS

**During Deployment:**
- **Engineering Lead:** [Your Name]
- **DevOps Lead:** [DevOps Contact]
- **Product Owner:** [Product Contact]

**Escalation Procedure:**
1. Error rate > 1% → Alert engineering lead
2. Error rate > 5% → Trigger rollback
3. Data loss detected → Immediate escalation to CTO

---

**Document Version:** 1.0  
**Last Updated:** November 17, 2025  
**Next Review:** Before each sprint deployment


