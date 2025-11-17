# Feature Specification: Cloud Function Authentication & Authorization

**Feature Branch**: `002-add-authentication-authorization-all`  
**Created**: 2025-11-17  
**Status**: Draft  
**Specification Version**: 0.0.52  
**Priority**: P0 (Critical Security Issue)

## Constitutional Alignment

This specification adheres to the project constitution established in `.specify-mcp/constitution.yaml`. All requirements and design decisions comply with constitutional principles including:

- **Security**: IMMUTABLE requirement for all endpoints to require authentication
- **Architecture**: Input validation on all user-facing endpoints
- **Security**: CORS configured with allowed origins (no wildcards)
- **Security**: Rate limiting on all public endpoints
- **Observability**: Structured logging for request tracing and security auditing

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

**As a** platform operator and security administrator  
**I want** all Cloud Functions protected with authentication and authorization  
**So that** only authorized services (Streamlit app) and administrators can invoke functions, preventing abuse, data theft, and quota exhaustion from unauthorized access

### Acceptance Scenarios

**Scenario 1: Streamlit App Makes Authenticated Request**
- **Given** the Streamlit application needs to fetch job postings for analysis
- **When** the app invokes the `job-scraper` Cloud Function with a valid API key in the request header
- **Then** the function validates the API key against Secret Manager
- **And** the function processes the request and returns job postings data
- **And** the request is logged with timestamp, source, and authentication status

**Scenario 2: Internal GCP Service Invokes Function**
- **Given** a Cloud Scheduler job needs to trigger the `news-search` function
- **When** Cloud Scheduler invokes the function using IAM authentication (service account)
- **Then** the function validates the service account has required IAM permissions
- **And** the function processes the scheduled task
- **And** no API key is required for IAM-authenticated requests

**Scenario 3: Unauthorized Access Attempt**
- **Given** an external attacker discovers a Cloud Function URL
- **When** the attacker attempts to invoke the function without authentication credentials
- **Then** the function immediately returns HTTP 401 Unauthorized
- **And** the request is blocked before any processing occurs
- **And** the failed attempt is logged with source IP and timestamp for security monitoring
- **And** no sensitive error details are exposed to the attacker

**Scenario 4: Invalid or Expired API Key**
- **Given** the Streamlit app has an outdated or invalid API key
- **When** the app attempts to invoke a Cloud Function
- **Then** the function returns HTTP 403 Forbidden with error message "Invalid API key"
- **And** the request is logged as authentication failure
- **And** an alert is triggered after 5 consecutive failures from the same source

**Scenario 5: Rate Limiting Triggered**
- **Given** a client (legitimate or malicious) makes excessive requests
- **When** the client exceeds 100 requests per minute per IP address
- **Then** subsequent requests return HTTP 429 Too Many Requests
- **And** the client receives a `Retry-After` header indicating when to retry
- **And** rate limit violations are logged for monitoring

**Scenario 6: CORS Preflight Request from Streamlit App**
- **Given** the Streamlit app (running in browser) needs to make a cross-origin request
- **When** the browser sends an OPTIONS preflight request
- **Then** the function returns HTTP 200 with appropriate CORS headers
- **And** the CORS headers allow requests only from the Streamlit app origin
- **And** authentication is not required for preflight requests (OPTIONS method)

### Edge Cases and Error Conditions

- **Missing API Key Header**: Function returns HTTP 400 Bad Request with clear error message
- **Malformed API Key**: Function returns HTTP 401 Unauthorized without exposing key format
- **API Key Retrieval Failure**: Function fails gracefully with HTTP 503 Service Unavailable
- **IAM Permission Check Timeout**: Function times out after 3 seconds with HTTP 504
- **Concurrent Rate Limit Checks**: Rate limiter handles concurrent requests correctly using atomic counters
- **Clock Skew**: Rate limit windows are based on server time, not client time
- **API Key Rotation**: New keys work immediately, old keys remain valid for 24-hour grace period

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST implement authentication middleware for all three Cloud Functions (job-scraper, news-search, github-activity) before processing any requests
- **FR-002**: System MUST support two authentication methods: API key for external calls (Streamlit app) and IAM for internal GCP services (Cloud Scheduler)
- **FR-003**: System MUST store API keys in GCP Secret Manager and retrieve them at function startup for validation
- **FR-004**: System MUST validate authentication on every request except OPTIONS (CORS preflight)
- **FR-005**: System MUST return HTTP 401 for missing/invalid authentication and HTTP 403 for valid authentication with insufficient permissions
- **FR-006**: System MUST implement rate limiting of 100 requests per minute per IP address with HTTP 429 response when exceeded
- **FR-007**: System MUST log all authentication attempts (success and failure) with timestamp, source IP, user agent, and outcome
- **FR-008**: System MUST configure CORS to allow requests only from the Streamlit app origin (no wildcard `*`)
- **FR-009**: System MUST provide clear error messages for authentication failures without exposing sensitive security details
- **FR-010**: System MUST trigger security alerts after 5 consecutive authentication failures from the same source within 5 minutes

### Non-Functional Requirements

- **NFR-001**: **Performance** - Authentication check MUST complete within 100ms (P95) to minimize function latency overhead; rate limit check MUST complete within 10ms
- **NFR-002**: **Security** - All authentication failures MUST be logged with full request details (excluding request body); API keys MUST never be logged or exposed in responses; failed auth attempts MUST trigger monitoring alerts
- **NFR-003**: **Reliability** - Authentication middleware MUST fail closed (deny access if auth check fails); function MUST fail fast at startup if API keys cannot be retrieved from Secret Manager
- **NFR-004**: **Usability** - Error responses MUST include clear messages (e.g., "Missing API key header") without exposing implementation details; documentation MUST include authentication setup guide
- **NFR-005**: **Maintainability** - Authentication logic MUST be shared across all three functions via common library; API key rotation MUST not require code changes or redeployment

### Business Rules

- **BR-001**: Streamlit app uses API key authentication; internal GCP services (Cloud Scheduler, Pub/Sub) use IAM authentication
- **BR-002**: API keys have 24-hour grace period during rotation (old and new keys both valid)
- **BR-003**: Rate limits are per IP address, not per API key, to prevent single compromised key from exhausting quotas
- **BR-004**: Failed authentication attempts from the same IP address are blocked after 10 failures within 10 minutes (lockout period: 30 minutes)
- **BR-005**: CORS is configured for Streamlit app origin only; all other origins are blocked

### Key Entities

- **API Key**: Authentication credential for external service access
  - **Attributes**: key_value (hashed), created_at, expires_at, usage_count, last_used, status (active/revoked)
  - **Lifecycle**: Created → Active → Rotated (new key) → Grace Period (24 hours) → Revoked
  - **Storage**: GCP Secret Manager with versioning enabled

- **Authentication Context**: Request authentication information
  - **Attributes**: auth_method (api_key/iam), authenticated (boolean), principal (api_key_id or service_account), source_ip, timestamp
  - **Lifecycle**: Created per request → Validated → Logged → Discarded
  - **Purpose**: Track who accessed what and when for security auditing

- **Rate Limit Counter**: Track request counts per IP address
  - **Attributes**: ip_address, request_count, window_start, window_end (1 minute)
  - **Storage**: In-memory (Redis or Memorystore for production, local dict for MVP)
  - **Behavior**: Reset counter every minute; block requests when count > 100

- **Security Event**: Authentication failure or suspicious activity
  - **Attributes**: timestamp, event_type (auth_failure/rate_limit_violation/ip_blocked), source_ip, user_agent, endpoint, details
  - **Lifecycle**: Created → Logged to Cloud Logging → Monitored → Alert triggered if threshold exceeded
  - **Retention**: 90 days in Cloud Logging

### Integration Points

- **GCP Secret Manager**: Retrieve API keys for validation
  - **Purpose**: Secure API key storage and retrieval
  - **Data Exchange**: Read API key secrets at function startup
  - **Dependencies**: IAM permissions for secret access

- **Cloud Logging**: Audit logging destination
  - **Purpose**: Record all authentication events for security monitoring
  - **Data Exchange**: Structured log entries with authentication context
  - **Dependencies**: Logging API enabled and accessible

- **Cloud Monitoring**: Alert generation for security events
  - **Purpose**: Trigger alerts on authentication failures and rate limit violations
  - **Data Exchange**: Metrics and log-based alerts
  - **Dependencies**: Monitoring API enabled with alert policies configured

- **Streamlit App**: Primary authenticated client
  - **Purpose**: Invoke Cloud Functions to fetch competitive intelligence data
  - **Interface**: Include API key in `X-API-Key` request header
  - **Dependencies**: API key stored in Secret Manager and injected at app startup

## Success Criteria *(mandatory)*

### Definition of Done

- [ ] All three Cloud Functions have authentication middleware implemented
- [ ] API key authentication works for Streamlit app requests
- [ ] IAM authentication works for Cloud Scheduler and internal services
- [ ] Unauthorized requests return HTTP 401/403 as appropriate
- [ ] Rate limiting blocks excessive requests with HTTP 429
- [ ] CORS configured for Streamlit app origin only (no wildcards)
- [ ] All authentication events logged to Cloud Logging
- [ ] Security alerts trigger on repeated authentication failures
- [ ] Documentation complete (authentication setup, API key rotation)
- [ ] Zero unauthenticated endpoints remain in production

### Acceptance Tests

**Test Suite 1: API Key Authentication**
- Verify valid API key allows request to succeed
- Verify missing API key returns HTTP 400
- Verify invalid API key returns HTTP 401
- Verify expired API key returns HTTP 401
- Verify API key validation completes within 100ms (P95)

**Test Suite 2: IAM Authentication**
- Verify valid service account can invoke function
- Verify service account without IAM permissions is denied (HTTP 403)
- Verify IAM token validation works correctly
- Verify IAM authentication does not require API key

**Test Suite 3: Rate Limiting**
- Verify 100 requests per minute per IP are allowed
- Verify 101st request within 1 minute returns HTTP 429
- Verify rate limit resets after 1 minute
- Verify different IP addresses have independent rate limits
- Verify `Retry-After` header is included in 429 responses

**Test Suite 4: CORS Configuration**
- Verify OPTIONS preflight request returns HTTP 200 with CORS headers
- Verify CORS headers allow Streamlit app origin only
- Verify requests from other origins are blocked
- Verify credentials are included in CORS headers (`Access-Control-Allow-Credentials: true`)

**Test Suite 5: Security Logging**
- Verify successful authentication is logged with principal and timestamp
- Verify failed authentication is logged with source IP and reason
- Verify API keys are never logged (even in errors)
- Verify rate limit violations are logged
- Verify repeated failures trigger security alerts (5 failures in 5 minutes)

**Test Suite 6: Error Handling**
- Verify clear error messages for authentication failures
- Verify no sensitive information exposed in error responses
- Verify function fails gracefully if Secret Manager is unavailable
- Verify authentication errors don't crash the function

---

## Assumptions

1. **API Key Format**: API keys are randomly generated 32-character alphanumeric strings
2. **Streamlit App Origin**: Known Streamlit app URL for CORS configuration
3. **IAM Setup**: Service accounts for Cloud Scheduler and other GCP services already exist
4. **Secret Manager**: API keys stored in Secret Manager under `PROJECT/cloudfunction-api-keys/*`
5. **Rate Limiting**: In-memory rate limiting sufficient for MVP; can upgrade to Redis/Memorystore for scale
6. **Logging**: Cloud Logging sufficient for security audit logs; no separate SIEM required initially
7. **Alert Policies**: Cloud Monitoring alert policies will be configured manually via console

## Dependencies

- **Prerequisite**: Feature #001 (Secret Management) completed - API keys stored in Secret Manager
- **Prerequisite**: Service accounts configured for Cloud Scheduler and internal services
- **Blocker**: IAM permissions required to validate service account tokens
- **Upstream**: Security audit identified unauthenticated endpoints
- **Downstream**: Streamlit app must be updated to include API key in requests

## Out of Scope

- OAuth 2.0 or JWT-based authentication (using simpler API key for MVP)
- User-specific authentication (API key represents Streamlit app, not individual users)
- Advanced rate limiting (per-user, per-endpoint, dynamic limits) - using simple per-IP limit
- WAF (Web Application Firewall) integration - relying on Cloud Functions built-in features
- Distributed rate limiting across multiple regions - single-region deployment initially

---

## Review & Acceptance Checklist (v0.0.52)

### Constitutional Compliance

- [x] Aligns with security principles (all endpoints require authentication)
- [x] Follows security standards (CORS configured, rate limiting, input validation)
- [x] Supports observability requirements (structured logging, request tracing)
- [x] Adheres to data privacy requirements (no sensitive data in logs)

### Content Quality

- [x] No implementation details (technology-agnostic, focuses on WHAT not HOW)
- [x] Focused on user value (security, abuse prevention, cost control)
- [x] Written for business stakeholders (clear security value proposition)
- [x] All mandatory sections completed with substantive content

### Requirement Quality

- [x] All functional requirements follow FR-xxx format and are testable
- [x] Requirements are measurable and unambiguous
- [x] Success criteria are clearly defined and verifiable
- [x] Acceptance scenarios cover happy path, alternatives, and errors
- [x] Non-functional requirements address performance, security, reliability

### Specification Completeness

- [x] User personas and scenarios clearly defined (operators, Streamlit app)
- [x] Business rules and constraints documented (rate limits, auth methods, CORS)
- [x] Integration points identified (Secret Manager, Cloud Logging, Streamlit)
- [x] Edge cases and error conditions addressed (failures, timeouts, expired keys)
- [x] Success criteria and acceptance tests specified (6 test suites)

### Clarification Assessment

- [x] **No [NEEDS CLARIFICATION] markers present**: Ready for planning phase
- [x] All ambiguous areas have been resolved with reasonable defaults
- [x] Scope is clearly bounded (in scope: API key + IAM; out of scope: OAuth, JWT, WAF)

---

## Next Phase Readiness

### Phase Transition Requirements

**To Planning Phase**:
- ✅ No [NEEDS CLARIFICATION] markers remain
- ✅ All requirements are unambiguous and testable
- ✅ Success criteria are measurable
- ✅ Constitutional alignment confirmed

### Execution Status

- [x] User description parsed and analyzed
- [x] Constitutional alignment verified
- [x] Key concepts and entities extracted
- [x] User scenarios and acceptance criteria defined
- [x] Functional and non-functional requirements specified
- [x] Business rules and constraints documented
- [x] Success criteria and acceptance tests defined
- [x] Review checklist completed
- [x] **Ready for planning phase** (`/speckit.plan`)

---

*This specification follows GitHub spec-kit v0.0.52 enhanced methodology with constitution-driven development. Priority: P0 (Critical Security Issue) - Must be completed before production deployment. Depends on Feature #001 (Secret Management).*
