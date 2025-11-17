# Feature Specification: Migrate Hardcoded Secrets to GCP Secret Manager

**Feature Branch**: `001-migrate-all-hardcoded-secrets`  
**Created**: 2025-11-17  
**Status**: Draft  
**Specification Version**: 0.0.52  
**Priority**: P0 (Critical Security Issue)

## Constitutional Alignment

This specification adheres to the project constitution established in `.specify-mcp/constitution.yaml`. All requirements and design decisions comply with constitutional principles including:

- **Security**: IMMUTABLE requirement to eliminate all hardcoded secrets
- **Architecture**: Configuration via environment variables and secure secret management
- **Deployment**: Secure credential management for production environments
- **Data Privacy**: No sensitive data in logs or error messages

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

**As a** platform operator and security administrator  
**I want** all sensitive credentials and API keys stored securely in GCP Secret Manager  
**So that** no secrets are exposed in code, version control, or logs, reducing security vulnerabilities and enabling secure credential rotation without code deployments

### Acceptance Scenarios

**Scenario 1: Cloud Function Retrieves Secret at Runtime**
- **Given** a Cloud Function (job-scraper, news-search, or github-activity) needs to access an external API
- **When** the function is invoked and requires credentials
- **Then** the function retrieves the secret from GCP Secret Manager using IAM-based authentication
- **And** the secret is never logged or exposed in error messages
- **And** the function gracefully handles secret retrieval failures

**Scenario 2: Streamlit App Accesses Database Credentials**
- **Given** the Streamlit application needs to connect to BigQuery and Firestore
- **When** the application initializes at startup
- **Then** database credentials are retrieved from GCP Secret Manager
- **And** credentials are cached securely in memory for the session duration
- **And** credentials are never written to disk or logs

**Scenario 3: Secret Rotation Without Downtime**
- **Given** an API key needs to be rotated due to security policy or compromise
- **When** an operator updates the secret in GCP Secret Manager
- **Then** all services automatically use the new secret on next invocation
- **And** no code changes or redeployments are required
- **And** the rotation is completed within the secret TTL window (30 minutes maximum)

**Scenario 4: Unauthorized Secret Access Attempt**
- **Given** an unauthorized service or user attempts to access a secret
- **When** the access attempt is made without proper IAM permissions
- **Then** the request is denied with a clear authorization error
- **And** the failed access attempt is logged to Cloud Logging
- **And** an alert is triggered for security monitoring

**Scenario 5: Local Development Access**
- **Given** a developer needs to run services locally for testing
- **When** the developer has appropriate IAM permissions
- **Then** the local service can retrieve secrets from GCP Secret Manager
- **And** the developer can use Application Default Credentials (ADC)
- **And** local development does not require `.env` files with real secrets

### Edge Cases and Error Conditions

- **Secret Not Found**: Service gracefully handles missing secrets with informative error messages (without exposing secret names in logs)
- **Secret Manager API Unavailable**: Service implements exponential backoff retry logic (max 3 retries over 10 seconds) before failing
- **IAM Permission Denied**: Service fails fast with clear permission errors in startup logs (not runtime)
- **Secret Version Mismatch**: Service uses the latest version by default, with option to pin specific versions
- **Concurrent Access**: Multiple service instances can retrieve the same secret simultaneously without contention
- **Secret Retrieval Timeout**: Maximum 2-second timeout for secret retrieval to prevent service hangs
- **Secret Cache Expiration**: In-memory caches expire after 30 minutes to ensure fresh secrets

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST migrate all hardcoded credentials (GITHUB_TOKEN, API keys, database connection strings) to GCP Secret Manager before production deployment
- **FR-002**: System MUST provide a standardized secret retrieval function/library used by all services (Cloud Functions and Streamlit app)
- **FR-003**: System MUST implement IAM-based access control where each service has minimum required permissions (principle of least privilege)
- **FR-004**: System MUST handle secret retrieval failures gracefully without exposing secret names or values in error messages or logs
- **FR-005**: System MUST support secret rotation without requiring code changes or service redeployments
- **FR-006**: System MUST cache secrets in memory for maximum 30 minutes to balance performance and freshness
- **FR-007**: System MUST log all secret access attempts (successful and failed) to Cloud Logging for security auditing
- **FR-008**: System MUST support local development using Application Default Credentials (ADC) without requiring production secrets
- **FR-009**: System MUST validate that no secrets exist in code, configuration files, or version control before allowing deployment
- **FR-010**: System MUST provide documentation for operators on secret creation, rotation, and access management procedures

### Non-Functional Requirements

- **NFR-001**: **Performance** - Secret retrieval MUST complete within 2 seconds (P95) to prevent service delays; cached secrets MUST be retrieved in <10ms
- **NFR-002**: **Security** - All secret access MUST use IAM authentication; secrets MUST never be logged, displayed, or included in error messages; failed access attempts MUST trigger security alerts
- **NFR-003**: **Reliability** - Service MUST implement retry logic with exponential backoff (3 retries over 10 seconds); service MUST fail fast on startup if required secrets are inaccessible
- **NFR-004**: **Maintainability** - Secret names MUST follow consistent naming convention (`PROJECT_NAME/SERVICE_NAME/SECRET_NAME`); documentation MUST include runbooks for secret rotation and troubleshooting
- **NFR-005**: **Auditability** - All secret operations (create, read, update, delete) MUST be logged with service account, timestamp, and outcome; audit logs MUST be retained for 90 days

### Business Rules

- **BR-001**: Each service (Cloud Function or Streamlit app) MUST have its own service account with minimum required secret access permissions
- **BR-002**: Secrets MUST be versioned in GCP Secret Manager with automatic versioning enabled for audit trail
- **BR-003**: Production secrets MUST never be used in development or testing environments
- **BR-004**: Secret rotation MUST be completed within 30 minutes to ensure all cached values expire
- **BR-005**: Any commit containing secrets (detected by pre-commit hooks or scanning) MUST be rejected and secrets immediately rotated

### Key Entities

- **Secret**: Sensitive credential stored in GCP Secret Manager
  - **Attributes**: name (project/service/credential), value (encrypted), version, creation_time, last_accessed
  - **Lifecycle**: Created → Active → Rotated (new version) → Deprecated (old version) → Deleted (after 90 days)
  - **Access Control**: IAM policy with specific service account permissions

- **Service Account**: GCP identity used by each service to access secrets
  - **Attributes**: account_email, display_name, secret_access_permissions
  - **Relationships**: One service account per service; multiple secrets per service account
  - **Constraints**: Must have minimum required permissions (least privilege)

- **Secret Access Log**: Audit record of secret operations
  - **Attributes**: timestamp, service_account, secret_name, operation (read/update), outcome (success/failure), source_ip
  - **Retention**: 90 days in Cloud Logging

### Integration Points

- **GCP Secret Manager API**: Primary integration for secret storage and retrieval
  - **Purpose**: Centralized, secure secret management
  - **Data Exchange**: Secret create, read, update operations via REST API
  - **Dependencies**: Requires IAM permissions and network connectivity

- **Cloud Functions (job-scraper, news-search, github-activity)**: Services requiring secret access
  - **Purpose**: Retrieve API keys at runtime
  - **Interface**: Standardized secret retrieval function injected at startup
  - **Dependencies**: Service account with Secret Manager read permissions

- **Streamlit App (streamlit-app)**: Frontend application requiring database credentials
  - **Purpose**: Retrieve BigQuery and Firestore credentials
  - **Interface**: Standardized secret retrieval function in initialization code
  - **Dependencies**: Cloud Run service account with Secret Manager read permissions

- **Cloud Logging**: Audit logging destination
  - **Purpose**: Record all secret access attempts for security monitoring
  - **Data Exchange**: Structured log entries with service account, secret name, outcome
  - **Dependencies**: Logging API enabled and accessible

## Success Criteria *(mandatory)*

### Definition of Done

- [ ] All hardcoded secrets removed from all code files (verified by grep/scan)
- [ ] All secrets migrated to GCP Secret Manager with proper IAM policies
- [ ] All services (3 Cloud Functions + Streamlit app) successfully retrieve secrets at runtime
- [ ] Secret retrieval completes within 2 seconds (P95) with caching enabled
- [ ] Zero secrets exposed in logs, error messages, or monitoring dashboards
- [ ] Secret rotation tested and verified to work without redeployment
- [ ] Documentation complete (operator runbook, developer guide)
- [ ] Pre-commit hooks installed to prevent future secret commits
- [ ] Security audit passed (no secrets in code, version control, or logs)

### Acceptance Tests

**Test Suite 1: Secret Migration**
- Verify all hardcoded secrets identified in audit are removed from code
- Verify all secrets exist in GCP Secret Manager with correct naming convention
- Verify IAM policies grant minimum required permissions to each service
- Verify no secrets remain in environment variables or configuration files
- Verify pre-commit hooks reject commits containing potential secrets

**Test Suite 2: Secret Retrieval**
- Verify each service successfully retrieves secrets at startup
- Verify secret retrieval completes within 2-second timeout
- Verify secret caching works correctly (30-minute TTL)
- Verify exponential backoff retry logic (3 retries over 10 seconds)
- Verify graceful failure handling when secrets are unavailable

**Test Suite 3: Security Validation**
- Verify unauthorized access attempts are blocked with IAM errors
- Verify no secret values appear in logs or error messages
- Verify failed access attempts generate security alerts
- Verify audit logs capture all secret operations correctly
- Verify secret names are not exposed in public-facing errors

**Test Suite 4: Secret Rotation**
- Verify updating a secret in Secret Manager works without downtime
- Verify cached secrets expire after 30 minutes
- Verify services pick up new secret versions automatically
- Verify old secret versions remain accessible during rotation window
- Verify documentation procedures for secret rotation are accurate

**Test Suite 5: Local Development**
- Verify developers can use Application Default Credentials locally
- Verify local services retrieve secrets from GCP Secret Manager
- Verify local development does not require `.env` files with real secrets
- Verify clear error messages when ADC is not configured

---

## Assumptions

1. **GCP Project Setup**: GCP Secret Manager API is enabled in the project
2. **IAM Permissions**: Operator has permissions to create secrets and assign IAM roles
3. **Service Accounts**: Each service already has a service account configured
4. **Network Connectivity**: All services have outbound internet access to GCP APIs
5. **Secret Names**: Existing secret names follow pattern: `GITHUB_TOKEN`, `OPENAI_API_KEY`, etc.
6. **Rotation Policy**: Secrets should be rotated every 90 days per security policy
7. **Development Environment**: Developers have `gcloud` CLI installed and configured with ADC

## Dependencies

- **Prerequisite**: GCP Secret Manager API enabled in project
- **Prerequisite**: Service accounts created for each service
- **Blocker**: IAM permissions required to create secrets and assign roles
- **Upstream**: Security audit identified all hardcoded secrets to migrate
- **Downstream**: Once secrets are in Secret Manager, services can be deployed to production

## Out of Scope

- Automatic secret rotation (rotate secrets manually via Secret Manager console)
- Secret encryption with customer-managed keys (CMEK) - using Google-managed encryption
- Multi-region secret replication (using single region for now)
- Secret access from non-GCP environments (focus on Cloud Run and Cloud Functions)
- Secrets for external third-party services not yet integrated

---

## Review & Acceptance Checklist (v0.0.52)

### Constitutional Compliance

- [x] Aligns with security principles (no hardcoded secrets)
- [x] Follows architectural governance (configuration via secure secret management)
- [x] Supports deployment standards (secure credential management)
- [x] Adheres to data privacy requirements (no PII/secrets in logs)

### Content Quality

- [x] No implementation details (technology-agnostic, focuses on WHAT not HOW)
- [x] Focused on user value (operator security, developer productivity)
- [x] Written for business stakeholders (clear security value proposition)
- [x] All mandatory sections completed with substantive content

### Requirement Quality

- [x] All functional requirements follow FR-xxx format and are testable
- [x] Requirements are measurable and unambiguous
- [x] Success criteria are clearly defined and verifiable
- [x] Acceptance scenarios cover happy path, alternatives, and errors
- [x] Non-functional requirements address performance, security, reliability

### Specification Completeness

- [x] User personas and scenarios clearly defined (operators, developers)
- [x] Business rules and constraints documented (IAM, rotation, audit)
- [x] Integration points identified (Secret Manager, Cloud Functions, Streamlit)
- [x] Edge cases and error conditions addressed (failures, timeouts, unauthorized access)
- [x] Success criteria and acceptance tests specified (5 test suites)

### Clarification Assessment

- [x] **No [NEEDS CLARIFICATION] markers present**: Ready for planning phase
- [x] All ambiguous areas have been resolved with reasonable defaults
- [x] Scope is clearly bounded (in scope: GCP services; out of scope: non-GCP, CMEK)

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

*This specification follows GitHub spec-kit v0.0.52 enhanced methodology with constitution-driven development. Priority: P0 (Critical Security Issue) - Must be completed before production deployment.*
