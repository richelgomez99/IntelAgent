# SpecKit Configuration for IntelAgent

## 🎯 Overview

This directory contains the SpecKit constitution and templates for the IntelAgent project.

**Constitution Status:** ✅ Active  
**Last Updated:** 2025-11-17  
**Total Rules:** 69 production-grade standards  
**Categories:** 9 (Security, Testing, UI/UX, Architecture, Performance, Documentation, Deployment, Observability, Privacy)

---

## 📁 Directory Structure

```
.specify-mcp/
├── constitution.yaml    📜 69 production-grade rules (IMMUTABLE principles)
├── templates/
│   ├── spec-template.md      (Feature specifications)
│   ├── plan-template.md      (Implementation plans)
│   └── tasks-template.md     (Task breakdowns)
└── README.md           📖 This file
```

---

## 📜 Constitution Summary

### 🔒 Security (8 IMMUTABLE rules)
- No hardcoded secrets → GCP Secret Manager
- All endpoints require authentication
- Parameterized queries only (SQL injection prevention)
- Input validation everywhere
- Firestore security rules deployed
- CORS configured properly (no wildcards)
- Rate limiting on public endpoints
- Regular dependency audits

### 🧪 Testing (8 IMMUTABLE rules)
- 80%+ test coverage required before merge
- Unit tests for all business logic
- Integration tests for Cloud Functions
- E2E tests for critical flows
- Performance benchmarks (<5s AI responses)
- Mock external APIs (BigQuery, Firestore, Gemini)
- Test data factory for fixtures
- Snapshot tests for AI responses

### 🎨 UI/UX (9 IMMUTABLE rules)
- WCAG 2.1 AA accessibility compliance
- Mobile-responsive (320px-4K)
- Loading states for all async operations
- Error boundaries with user-friendly messages
- Skeleton loaders (no blank screens)
- Keyboard navigation support
- Streamlit custom components
- Consistent design system
- Progressive enhancement

### 🏗️ Architecture (9 IMMUTABLE rules)
- Separation of concerns (UI / Business Logic / Data)
- Type hints on all function signatures
- Comprehensive docstrings (Google style)
- Max 50 lines per function, 500 per file
- DRY principle (max 2 similar blocks)
- Configuration via environment variables
- Single Responsibility Principle
- Dependency injection for testability
- Repository pattern for data access

### ⚡ Performance (9 IMMUTABLE rules)
- AI agent response time <5s (P95)
- Cloud Function cold start <3s
- Firestore queries <500ms
- BigQuery queries <2s
- Streamlit page load <2s
- Response caching (30 min TTL)
- Pagination (50 items/page)
- Lazy loading for heavy components
- Optimized Gemini prompts

### 📚 Documentation (8 IMMUTABLE rules)
- README.md for every deployable component
- API documentation (OpenAPI/Swagger)
- Architecture diagrams (C4 model)
- Deployment runbook with rollback
- Inline comments for complex logic
- User guide with screenshots
- Developer onboarding guide
- Incident response playbook

### 🚀 Deployment (8 IMMUTABLE rules)
- Automated deployments (Cloud Build)
- Zero-downtime deployments
- Health checks on all services
- Monitoring and alerting (Cloud Monitoring)
- Centralized logging (Cloud Logging)
- Blue-green deployment for Streamlit
- Feature flags for gradual rollouts
- Automated rollback on failure

### 🔍 Observability (8 IMMUTABLE rules)
- Structured logging (JSON format)
- Request tracing (correlation IDs)
- Error tracking (log with context)
- Performance metrics (Cloud Monitoring)
- Cost monitoring alerts
- Dashboard for business metrics
- SLO/SLA tracking (99.5% uptime)
- User analytics (privacy-respecting)

### 🛡️ Data Privacy (8 IMMUTABLE rules)
- No PII in logs or error messages
- Data retention policies (90 days)
- User consent for analytics
- Data encryption at rest (Firestore default)
- Data encryption in transit (HTTPS only)
- GDPR compliance considerations
- Right to deletion implementation
- Data minimization (collect only needed)

---

## 🔧 Quality Thresholds

```yaml
quality:
  test_coverage_minimum: 80
  documentation_required: true
  linting_enabled: true
  type_checking: true
  code_review_required: true
  max_function_lines: 50
  max_file_lines: 500
  max_complexity: 10
```

---

## 🚀 SpecKit Workflow

### 1️⃣ SPECIFY
**Input:** Natural language feature description  
**Output:** `specs/spec-NNN-{feature}.md`  
**Contains:** User stories, acceptance criteria, success metrics, dependencies

**Tool:** `mcp_speckit_specify_tool` or use template

### 2️⃣ PLAN
**Input:** `specs/spec-NNN-{feature}.md`  
**Output:** `specs/plan-NNN.md`  
**Contains:** Step-by-step implementation, files to modify, technical decisions

**Tool:** `mcp_speckit_plan_tool`

### 3️⃣ TASKS
**Input:** `specs/plan-NNN.md`  
**Output:** `specs/tasks-NNN.md`  
**Contains:** Numbered tasks, dependencies, parallel groups, estimates

**Tool:** `mcp_speckit_tasks_tool`

### 4️⃣ EXECUTE
**Input:** Constitution + Plan + Tasks  
**Output:** Production-ready feature  
**Requirement:** All 69 constitution rules must be followed

**Validation:** Every commit must pass constitution compliance checks

---

## 📖 Using Templates

### Creating a Feature Specification

```bash
# Copy template
cp .specify-mcp/templates/spec-template.md specs/spec-002-my-feature.md

# Edit the spec
# Fill in: Overview, User Story, Acceptance Criteria, Technical Requirements

# Generate plan
# Use: mcp_speckit_plan_tool with specs/spec-002-my-feature.md

# Generate tasks
# Use: mcp_speckit_tasks_tool with specs/plan-002.md

# Execute tasks
# Follow tasks one by one, ensuring constitution compliance
```

---

## ✅ Pre-Commit Checklist

Before committing any code, verify:

### Security ✅
- [ ] No hardcoded secrets
- [ ] Authentication implemented
- [ ] Input validation present
- [ ] CORS configured

### Testing ✅
- [ ] 80%+ test coverage
- [ ] All tests passing
- [ ] Performance benchmarks met
- [ ] External APIs mocked

### Code Quality ✅
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] No functions >50 lines
- [ ] No code duplication

### UI/UX ✅ (if applicable)
- [ ] WCAG 2.1 AA compliant
- [ ] Mobile responsive
- [ ] Loading states present
- [ ] Error boundaries implemented

---

## 🎓 Getting Started

### 1. Read the Constitution
```bash
cat .specify-mcp/constitution.yaml
```

### 2. Read the Full Guide
```bash
cat ../SPECKIT_GUIDE.md
```

### 3. Read Quick Reference
```bash
cat ../CONSTITUTION_QUICK_REF.md
```

### 4. Review Audit Deliverables
```bash
ls -lh ../speckit-prep/
```

### 5. Start with Quick Wins
```bash
cat ../speckit-prep/QUICK_WINS.md
```

### 6. Implement First Spec (Authentication)
```bash
cat ../speckit-prep/spec-001-authentication-system.md
cp ../speckit-prep/spec-001-authentication-system.md ../specs/
```

---

## 📊 Success Metrics

**Your code is production-ready when:**

✅ All 15 security vulnerabilities fixed  
✅ 80%+ test coverage achieved  
✅ WCAG 2.1 AA compliance verified  
✅ All endpoints authenticated  
✅ Zero hardcoded secrets  
✅ Mobile-responsive (320px-4K)  
✅ AI responses <5s (P95)  
✅ Monitoring configured  
✅ Documentation complete  
✅ Production deployed successfully  

---

## 🔗 Additional Resources

### In Project Root
- `SPECKIT_GUIDE.md` - Complete workflow guide
- `CONSTITUTION_QUICK_REF.md` - Quick reference card
- `README.md` - Project overview

### In speckit-prep/
- `AUDIT_REPORT.md` - Comprehensive audit findings
- `SECURITY_VULNERABILITIES.md` - 15 vulnerabilities + fixes
- `QUICK_WINS.md` - 25 fast improvements (2-4 hours)
- `claude-execution.md` - Step-by-step execution plan
- `UI_UX_IMPROVEMENTS.md` - 18 UI enhancements
- `REFACTORING_PLAN.md` - 14 refactorings
- `TEST_COVERAGE_GAPS.md` - 270+ test specs
- Plus 7 more comprehensive documents

---

## 🏆 Project Standards

**Language:** Python 3.11  
**Framework:** Streamlit + Cloud Functions  
**Testing:** pytest  
**Build Tool:** pip  
**Branch Prefix:** feature/  
**Version:** 0.1.0  

---

## 🤝 Contributing

All code contributions must:
1. Follow the 69-rule constitution
2. Include comprehensive tests (80%+ coverage)
3. Have complete documentation
4. Pass security audits
5. Meet performance budgets
6. Be WCAG 2.1 AA compliant (for UI changes)

**No exceptions to IMMUTABLE principles!**

---

## 📞 Support

For questions about:
- **Constitution rules:** See `constitution.yaml` or `../CONSTITUTION_QUICK_REF.md`
- **Workflow:** See `../SPECKIT_GUIDE.md`
- **Security:** See `../speckit-prep/SECURITY_VULNERABILITIES.md`
- **Testing:** See `../speckit-prep/TEST_COVERAGE_GAPS.md`
- **Execution:** See `../speckit-prep/claude-execution.md`

---

**🎉 This constitution enforces production-grade standards on every commit! 🎉**

**Last Updated:** 2025-11-17  
**Status:** ✅ Active  
**Enforcement:** Mandatory for all code changes

