# Data Model: Migrate Hardcoded Secrets to GCP Secret Manager

## Entities

### Secret

**Description**: Sensitive credential stored in GCP Secret Manager

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

**Description**: name (project/service/credential), value (encrypted), version, creation_time, last_accessed

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

**Description**: Created → Active → Rotated (new version) → Deprecated (old version) → Deleted (after 90 days)

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

### Access Control

**Description**: IAM policy with specific service account permissions

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

### Service Account

**Description**: GCP identity used by each service to access secrets

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

**Description**: account_email, display_name, secret_access_permissions

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

### Relationships

**Description**: One service account per service; multiple secrets per service account

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

### Constraints

**Description**: Must have minimum required permissions (least privilege)

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

### Secret Access Log

**Description**: Audit record of secret operations

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

**Description**: timestamp, service_account, secret_name, operation (read/update), outcome (success/failure), source_ip

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
