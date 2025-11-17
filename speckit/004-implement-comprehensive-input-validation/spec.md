# Feature Specification: Input Validation & SQL Injection Prevention

**Feature Branch**: `004-implement-comprehensive-input-validation`  
**Created**: 2025-11-17  
**Status**: Draft  
**Specification Version**: 0.0.52  
**Priority**: P0 (Critical Security Issue)

## Constitutional Alignment

This specification adheres to the project constitution established in `.specify-mcp/constitution.yaml`. All requirements and design decisions comply with constitutional principles including:

- **Security**: IMMUTABLE requirement for parameterized queries only (prevent SQL injection)
- **Security**: IMMUTABLE requirement for input validation on all user-facing endpoints
- **Architecture**: Separation of concerns (validation layer before business logic)
- **Security**: No unvalidated inputs in database queries or logs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

**As a** platform operator and application user  
**I want** all user inputs validated and sanitized before processing  
**So that** malicious inputs cannot exploit SQL injection, XSS, or other injection vulnerabilities, protecting data integrity and user safety

### Acceptance Scenarios

**Scenario 1: Valid Company Name Input**
- **Given** a user enters a legitimate company name "OpenAI" in the Streamlit app
- **When** the app validates the input before sending to Gemini agent or database queries
- **Then** the input passes validation (alphanumeric, spaces, hyphens allowed; max 100 characters)
- **And** the query uses parameterized SQL with the validated input
- **And** the results are returned successfully

**Scenario 2: SQL Injection Attempt**
- **Given** a malicious user enters `"Microsoft'; DROP TABLE job_postings; --"` as company name
- **When** the app validates the input
- **Then** the input is rejected with error message "Invalid company name format"
- **And** the malicious SQL is never executed
- **And** the rejection is logged with source IP and input (truncated)
- **And** the user receives a safe error message without technical details

**Scenario 3: XSS Attack Attempt**
- **Given** a malicious user enters `"<script>alert('XSS')</script>"` as company name
- **When** the app validates the input
- **Then** the input is rejected with error message "Invalid company name format"
- **And** the script is never rendered or stored
- **And** the rejection is logged

**Scenario 4: Parameterized BigQuery Query**
- **Given** a validated company name needs to be queried from BigQuery patents data
- **When** the Gemini agent constructs the BigQuery query
- **Then** the query uses parameterized syntax with placeholder `@company_name`
- **And** the company name is passed as a query parameter (not concatenated)
- **And** BigQuery SQL injection is prevented by parameter binding

**Scenario 5: Excessive Input Length**
- **Given** a user enters a company name exceeding 100 characters
- **When** the app validates the input
- **Then** the input is rejected with error message "Company name too long (max 100 characters)"
- **And** the oversized input is not processed or logged in full

**Scenario 6: Special Characters in Company Name**
- **Given** a user enters a company name with special characters like "AT&T" or "O'Reilly"
- **When** the app validates the input
- **Then** the input passes validation (apostrophes and ampersands allowed in controlled manner)
- **And** the special characters are properly escaped for SQL queries
- **And** the query executes safely

### Edge Cases and Error Conditions

- **Empty Input**: Rejected with "Company name is required"
- **Whitespace Only**: Trimmed and rejected if empty after trimming
- **Unicode Characters**: Validated for allowed character set (Latin alphabet, basic punctuation)
- **Null Bytes**: Rejected immediately to prevent injection attacks
- **Path Traversal Attempts**: Input like `"../../etc/passwd"` rejected
- **Command Injection**: Input like `"; ls -la"` rejected
- **Encoding Attacks**: URL-encoded or hex-encoded attacks detected and rejected

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate all user inputs (company names, search queries) before processing using allowlist-based validation
- **FR-002**: System MUST use parameterized queries for ALL BigQuery operations (no string concatenation in SQL)
- **FR-003**: System MUST reject inputs containing SQL keywords (SELECT, DROP, INSERT, UPDATE, DELETE, etc.) in company names
- **FR-004**: System MUST reject inputs containing script tags, HTML tags, or JavaScript code
- **FR-005**: System MUST enforce maximum input length limits (company name: 100 chars, search query: 500 chars)
- **FR-006**: System MUST trim whitespace from inputs and reject empty/whitespace-only inputs
- **FR-007**: System MUST escape special characters (quotes, semicolons, backslashes) before passing to any system
- **FR-008**: System MUST log all validation failures with truncated input (first 50 characters) and source information
- **FR-009**: System MUST display user-friendly error messages for validation failures without exposing system internals
- **FR-010**: System MUST implement input validation at the earliest point (Streamlit UI) before any processing

### Non-Functional Requirements

- **NFR-001**: **Performance** - Input validation MUST complete within 50ms (P95) to avoid noticeable UI latency
- **NFR-002**: **Security** - All validation failures MUST be logged; validation logic MUST be centralized and testable; no inputs bypass validation
- **NFR-003**: **Usability** - Error messages MUST be clear and helpful (e.g., "Company name can only contain letters, numbers, spaces, and basic punctuation"); validation MUST provide immediate feedback in UI
- **NFR-004**: **Maintainability** - Validation rules MUST be centralized in a single module; validation logic MUST be documented with examples of allowed/rejected inputs
- **NFR-005**: **Reliability** - Validation MUST fail closed (reject ambiguous inputs rather than allowing them); validation MUST not crash or raise unhandled exceptions

### Business Rules

- **BR-001**: Company names can contain: letters (A-Z, a-z), numbers (0-9), spaces, hyphens (-), apostrophes ('), ampersands (&), periods (.), commas (,)
- **BR-002**: Company names cannot contain: SQL keywords, script tags, path separators (/, \), control characters, null bytes
- **BR-003**: All BigQuery queries must use parameterized syntax (e.g., `WHERE company_name = @company_name`)
- **BR-004**: Validation failures are logged but do not expose full input in logs (truncate to 50 chars, mask sensitive patterns)
- **BR-005**: Input validation applies to all sources: Streamlit UI, API requests, Cloud Function parameters

### Key Entities

- **Input Validation Rule**: Specification for validating specific input types
  - **Attributes**: input_type (company_name/search_query/url), pattern (regex or allowlist), max_length, error_message
  - **Lifecycle**: Defined → Tested → Deployed → Monitored for false positives
  - **Storage**: Centralized validation module

- **Validated Input**: User-provided data that has passed validation
  - **Attributes**: original_value, sanitized_value, input_type, validation_timestamp, source (user/API)
  - **Lifecycle**: Received → Validated → Sanitized → Processed → Logged (if failed)
  - **Guarantees**: Safe for SQL queries, API calls, display

- **Validation Failure Event**: Record of rejected input
  - **Attributes**: timestamp, input_type, truncated_input (first 50 chars), rejection_reason, source_ip, user_agent
  - **Retention**: 90 days in Cloud Logging
  - **Purpose**: Security monitoring and validation tuning

### Integration Points

- **Streamlit App**: Primary entry point for user inputs
  - **Purpose**: Validate all user inputs before processing
  - **Interface**: Validation module called on form submission and input change events
  - **Dependencies**: Centralized validation library

- **BigQuery Client**: Database query execution
  - **Purpose**: Execute parameterized queries safely
  - **Interface**: Use query parameters instead of string formatting
  - **Dependencies**: `google-cloud-bigquery` library with parameterized query support

- **Gemini Agent**: AI model integration
  - **Purpose**: Pass validated inputs to AI agent for analysis
  - **Interface**: Validate inputs before constructing prompts
  - **Dependencies**: Validated company names used in prompt templates

- **Cloud Logging**: Audit log destination
  - **Purpose**: Record all validation failures for security monitoring
  - **Interface**: Structured log entries with validation context
  - **Dependencies**: Logging API enabled

## Success Criteria *(mandatory)*

### Definition of Done

- [ ] Input validation implemented for all user-facing inputs (company names, search queries)
- [ ] All BigQuery queries use parameterized syntax (no string concatenation)
- [ ] SQL injection attempts are blocked and logged
- [ ] XSS attempts are blocked and logged
- [ ] Input length limits enforced (company: 100 chars, query: 500 chars)
- [ ] User-friendly error messages displayed for validation failures
- [ ] Validation failures logged to Cloud Logging
- [ ] Zero SQL injection or XSS vulnerabilities in security scan
- [ ] Documentation complete (validation rules, error handling)

### Acceptance Tests

**Test Suite 1: SQL Injection Prevention**
- Verify `' OR '1'='1` is rejected
- Verify `'; DROP TABLE job_postings; --` is rejected
- Verify `1'; SELECT * FROM users; --` is rejected
- Verify parameterized queries prevent injection even with malicious input

**Test Suite 2: XSS Prevention**
- Verify `<script>alert('XSS')</script>` is rejected
- Verify `<img src=x onerror=alert(1)>` is rejected
- Verify JavaScript event handlers (`onclick`, `onerror`) are rejected

**Test Suite 3: Valid Input Acceptance**
- Verify "OpenAI" passes validation
- Verify "Microsoft Corporation" passes validation
- Verify "AT&T" passes validation
- Verify "O'Reilly Media" passes validation
- Verify "Salesforce.com" passes validation

**Test Suite 4: Input Length Limits**
- Verify 100-character company name passes
- Verify 101-character company name is rejected
- Verify empty input is rejected
- Verify whitespace-only input is rejected after trimming

**Test Suite 5: Special Characters**
- Verify allowed special characters pass (-, ', &, ., ,)
- Verify disallowed characters are rejected (/, \, ;, <, >, ", `)
- Verify unicode characters are handled correctly
- Verify control characters are rejected

**Test Suite 6: Error Handling**
- Verify clear error messages for validation failures
- Verify no technical details exposed in error messages
- Verify validation failures are logged
- Verify validation does not crash application

---

## Assumptions

1. **Input Sources**: Primary input source is Streamlit UI; API inputs validated same way
2. **Character Set**: Latin alphabet (A-Z, a-z) and basic punctuation; no emoji or extended unicode
3. **BigQuery Library**: Using `google-cloud-bigquery` with parameterized query support
4. **Validation Library**: Using Python `re` (regex) module for pattern matching
5. **Error Handling**: Validation errors return immediately without processing
6. **Performance**: Regex validation completes in microseconds; negligible latency impact

## Dependencies

- **Prerequisite**: Streamlit app structure supports input validation hooks
- **Prerequisite**: BigQuery client library supports parameterized queries
- **Blocker**: None - can implement independently
- **Upstream**: Security audit identified SQL injection risks
- **Downstream**: All user inputs pass through validation before processing

## Out of Scope

- Advanced input sanitization (HTML purification, Markdown parsing)
- Content Security Policy (CSP) headers (handled at deployment level)
- Rate limiting on validation failures (covered in separate feature)
- CAPTCHA or bot detection (not required for authenticated app)
- Input normalization (case-insensitive matching, unicode normalization)

---

## Review & Acceptance Checklist (v0.0.52)

### Constitutional Compliance

- [x] Aligns with security principles (parameterized queries, input validation)
- [x] Follows architectural governance (separation of concerns)
- [x] Supports data privacy requirements (no sensitive data in logs)

### Content Quality

- [x] No implementation details (validation approach abstracted)
- [x] Focused on user value (security, data integrity)
- [x] All mandatory sections completed

### Requirement Quality

- [x] All requirements testable and unambiguous
- [x] Success criteria measurable and verifiable
- [x] Acceptance scenarios comprehensive

### Specification Completeness

- [x] User scenarios defined (legitimate users, attackers)
- [x] Business rules documented (allowed characters, query patterns)
- [x] Integration points identified (Streamlit, BigQuery, Gemini)
- [x] Edge cases addressed (SQL injection, XSS, length limits)
- [x] 6 test suites specified

### Clarification Assessment

- [x] **No [NEEDS CLARIFICATION] markers**: Ready for planning

---

## Next Phase Readiness

- [x] Ready for planning phase (`/speckit.plan`)

---

*Priority: P0 (Critical Security Issue) - Must be completed before production deployment.*
