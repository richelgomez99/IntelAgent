# Data Model: Cloud Function Authentication & Authorization

## Entities

### API Key

**Description**: Authentication credential for external service access

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Attributes

**Description**: key_value (hashed), created_at, expires_at, usage_count, last_used, status (active/revoked)

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Lifecycle

**Description**: Created → Active → Rotated (new key) → Grace Period (24 hours) → Revoked

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Storage

**Description**: GCP Secret Manager with versioning enabled

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Authentication Context

**Description**: Request authentication information

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Attributes

**Description**: auth_method (api_key/iam), authenticated (boolean), principal (api_key_id or service_account), source_ip, timestamp

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Lifecycle

**Description**: Created per request → Validated → Logged → Discarded

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Purpose

**Description**: Track who accessed what and when for security auditing

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Rate Limit Counter

**Description**: Track request counts per IP address

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Attributes

**Description**: ip_address, request_count, window_start, window_end (1 minute)

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Storage

**Description**: In-memory (Redis or Memorystore for production, local dict for MVP)

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Behavior

**Description**: Reset counter every minute; block requests when count > 100

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Security Event

**Description**: Authentication failure or suspicious activity

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Attributes

**Description**: timestamp, event_type (auth_failure/rate_limit_violation/ip_blocked), source_ip, user_agent, endpoint, details

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Lifecycle

**Description**: Created → Logged to Cloud Logging → Monitored → Alert triggered if threshold exceeded

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

### Retention

**Description**: 90 days in Cloud Logging

**Fields**:
- `id`: Unique identifier
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update
- [Additional fields based on requirements]

**Relationships**:
- [Define relationships with other entities]

**Validation Rules**:
- Required fields must be present
- Data types must be valid
- Business rules must be satisfied

---

## Data Flow

1. Input validation
2. Business logic processing
3. Data persistence
4. Response generation

## State Management

- Stateless operations where possible
- Clear state transitions
- Proper error states

---
*Generated by spec-kit-mcp*
