═══════════════════════════════════════════════════════════════════════════════
📋 COPY THIS ENTIRE PROMPT AND PASTE TO YOUR NEW IMPLEMENTATION AGENT
═══════════════════════════════════════════════════════════════════════════════

You are an expert implementation agent tasked with transforming the IntelAgent codebase from prototype to production-grade. You have been provided with a complete implementation package worth $55K-$80K in consulting deliverables.

═══════════════════════════════════════════════════════════════════════════════
📍 PROJECT CONTEXT
═══════════════════════════════════════════════════════════════════════════════

Repository: IntelAgent (Competitive Intelligence Platform on GCP)
Branch: 005-build-comprehensive-test-suite
Package Location: /speckit/
Your Mission: Execute 120 production-grade tasks across 5 critical features in 10-12 days

Current State:
- 15 critical security vulnerabilities
- 0% test coverage
- Risk: HIGH
- Production Ready: NO

Target State:
- 0 security vulnerabilities
- 80%+ test coverage (270+ tests)
- Risk: LOW
- Production Ready: YES

═══════════════════════════════════════════════════════════════════════════════
🎯 IMMEDIATE ACTION (FIRST 60 MINUTES)
═══════════════════════════════════════════════════════════════════════════════

Step 1: Read the complete initialization document
```bash
cat speckit/AGENT_INITIALIZATION_PROMPT.md
```

Step 2: Orient yourself (30 minutes)
```bash
cat speckit/START_HERE.md                           # Your primary guide
cat speckit/COMPLETE_TRANSFORMATION_JOURNEY.md      # Full scope
cat speckit/IMPLEMENTATION_READY.md                 # Execution patterns
cat speckit/CONSTITUTION_QUICK_REF.md               # 69 rules you MUST follow
```

Step 3: Understand current state (30 minutes)
```bash
cat speckit/speckit-prep/AUDIT_REPORT.md            # Current state analysis
cat speckit/speckit-prep/SECURITY_VULNERABILITIES.md # 15 vulnerabilities to fix
cat speckit/speckit-prep/TEST_COVERAGE_GAPS.md      # 270+ tests needed
cat speckit/speckit-prep/QUICK_WINS.md              # Fast improvements (start here)
```

═══════════════════════════════════════════════════════════════════════════════
🚀 EXECUTION PLAN
═══════════════════════════════════════════════════════════════════════════════

TODAY (2-4 hours): Quick Wins
```bash
cat speckit/speckit-prep/QUICK_WINS.md
# Execute 25 fast improvements (5-30 min each)
# Examples: Add type hints, remove console.logs, fix hardcoded secrets
# Mark complete: - [ ] → - [x] in the file
```

WEEK 1 (5 days): Security Hardening
- Day 1-2: Feature #001 - Secret Management (24 tasks)
- Day 2-3: Feature #002 - Cloud Function Auth (24 tasks)
- Day 4: Feature #003 - Firestore Security (24 tasks)
- Day 5: Feature #004 - Input Validation (24 tasks)
Result: Zero critical vulnerabilities, risk HIGH → MEDIUM

WEEK 2 (5 days): Testing Infrastructure
- Day 6-10: Feature #005 - Comprehensive Test Suite (24 tasks)
Result: 270+ tests passing, 80%+ coverage, risk MEDIUM → LOW

═══════════════════════════════════════════════════════════════════════════════
📦 FEATURE IMPLEMENTATION WORKFLOW (REPEAT FOR EACH FEATURE)
═══════════════════════════════════════════════════════════════════════════════

For Feature #001 (repeat for #002-#005):

1. Create feature branch
```bash
git checkout -b 001-migrate-all-hardcoded-secrets
```

2. Read implementation package
```bash
cat speckit/001-migrate-all-hardcoded-secrets/spec.md       # WHAT to build
cat speckit/001-migrate-all-hardcoded-secrets/plan.md       # HOW to build (detailed steps)
cat speckit/001-migrate-all-hardcoded-secrets/tasks.md      # 24 tasks (step-by-step)
cat speckit/001-migrate-all-hardcoded-secrets/research.md   # Technology decisions
cat speckit/001-migrate-all-hardcoded-secrets/data-model.md # Data schemas
```

3. Execute tasks T001 → T024
   - Follow plan.md for implementation details
   - Execute phases sequentially (Phase 1 → Phase 2 → Phase 3)
   - Tasks marked [P] can run in parallel (30% time savings!)
   - Mark completed: Change - [ ] to - [x] in tasks.md

4. Run quality gates BEFORE committing
```bash
# Security checks
gitleaks detect --source . --verbose    # No hardcoded secrets
pip-audit                               # No vulnerable dependencies
bandit -r .                             # No security issues

# Test checks
pytest --cov=. --cov-report=html        # 80%+ coverage required
pytest tests/ -v                        # All tests passing

# Code quality checks
mypy .                                  # Type hints present
flake8 .                                # Zero linter errors
radon cc -s .                           # No complex functions (max 50 lines)
```

5. Verify constitutional compliance (69 rules)
```bash
cat speckit/CONSTITUTION_QUICK_REF.md
# Check all categories: Security, Testing, Architecture, Performance, etc.
```

6. Commit and push
```bash
git add .
git commit -m "feat(security): Implement Feature #001 - Secret Management

- Migrated all secrets to GCP Secret Manager
- Configured IAM roles (least-privilege)
- Implemented secret rotation
- All 24 tasks completed
- Constitutional compliance: 69/69 rules
- Test coverage: 85%
- Zero security vulnerabilities

Closes: T001-T024"

git push origin 001-migrate-all-hardcoded-secrets
```

═══════════════════════════════════════════════════════════════════════════════
⚡ PARALLEL EXECUTION (SAVE 30% TIME)
═══════════════════════════════════════════════════════════════════════════════

Tasks marked with [P] can be executed simultaneously because they modify different files.

Example from Feature #001, Phase 3:
```markdown
- [ ] T013 [P] [US2] Create secret_manager_utils.py in cloud-functions/common/
- [ ] T014 [P] [US2] Update job-scraper/main.py
- [ ] T015 [P] [US2] Update news-search/main.py
- [ ] T016 [P] [US2] Update job-scraper/requirements.txt
- [ ] T017 [P] [US2] Update news-search/requirements.txt
```

How to execute:
1. Open 5 files in separate editor tabs
2. Execute T013-T017 simultaneously
3. No conflicts (different files)
4. Save 30-40% of time

═══════════════════════════════════════════════════════════════════════════════
✅ QUALITY GATES (BEFORE EVERY COMMIT)
═══════════════════════════════════════════════════════════════════════════════

Security (8 rules):
- [ ] No hardcoded secrets (gitleaks detect)
- [ ] All endpoints authenticated
- [ ] Parameterized queries (prevent SQL injection)
- [ ] Input validation everywhere
- [ ] CORS configured (no wildcards)
- [ ] Rate limiting enabled
- [ ] Firestore security rules deployed
- [ ] Dependencies audited (pip-audit)

Testing (8 rules):
- [ ] 80%+ test coverage (pytest --cov)
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance benchmarks met (<5s AI response)
- [ ] External APIs mocked

Architecture (9 rules):
- [ ] Type hints for all functions (mypy)
- [ ] Docstrings for all public APIs
- [ ] No functions >50 lines
- [ ] No files >500 lines
- [ ] DRY principle enforced
- [ ] Separation of concerns
- [ ] No circular dependencies

Performance (8 rules):
- [ ] Bundle size <500KB (gzipped)
- [ ] AI response <5s (95th percentile)
- [ ] API response <2s (95th percentile)
- [ ] DB queries indexed

(See full list of 69 rules: cat speckit/CONSTITUTION_QUICK_REF.md)

═══════════════════════════════════════════════════════════════════════════════
🚨 CRITICAL RULES (NON-NEGOTIABLE)
═══════════════════════════════════════════════════════════════════════════════

ALWAYS:
✅ Read spec.md, plan.md, tasks.md BEFORE implementing
✅ Execute tasks in order (respect phase dependencies)
✅ Mark tasks complete in tasks.md as you go (- [ ] → - [x])
✅ Run quality gates BEFORE every commit
✅ Verify constitutional compliance (69 rules)
✅ Test as you go (don't wait until the end)
✅ Use [P] parallel markers to save 30% time
✅ Document learnings in research.md

NEVER:
❌ Skip reading implementation plans
❌ Execute tasks out of order
❌ Commit without running quality gates
❌ Merge without constitutional compliance
❌ Hardcode secrets (use GCP Secret Manager)
❌ Skip tests (80%+ coverage required)
❌ Ignore [P] parallel opportunities
❌ Write functions >50 lines

═══════════════════════════════════════════════════════════════════════════════
📖 COMPLETE FILE REFERENCE
═══════════════════════════════════════════════════════════════════════════════

Your Implementation Package (63 files, 22,328+ lines):

Primary Guides:
- speckit/AGENT_INITIALIZATION_PROMPT.md     # Complete briefing (THIS FILE)
- speckit/START_HERE.md                      # Your main guide
- speckit/COMPLETE_TRANSFORMATION_JOURNEY.md # Full overview
- speckit/IMPLEMENTATION_READY.md            # Execution patterns
- speckit/CONSTITUTION_QUICK_REF.md          # 69 rules (daily checklist)

Audit Documents (Current State):
- speckit/speckit-prep/AUDIT_REPORT.md            # Comprehensive findings
- speckit/speckit-prep/SECURITY_VULNERABILITIES.md # 15 vulnerabilities + fixes
- speckit/speckit-prep/TEST_COVERAGE_GAPS.md      # 270+ test specs
- speckit/speckit-prep/QUICK_WINS.md              # 25 fast improvements
- speckit/speckit-prep/REFACTORING_PLAN.md        # Technical debt
- speckit/speckit-prep/UI_UX_IMPROVEMENTS.md      # UI enhancements
- speckit/speckit-prep/BREAKING_CHANGES.md        # Breaking changes
- speckit/speckit-prep/TASK_PRIORITIES.md         # Prioritization

Constitutional Framework:
- speckit/.specify-mcp/constitution.yaml     # 69 production rules
- speckit/CONSTITUTION_QUICK_REF.md          # Quick reference

Feature Packages (5 features × 6-7 files each):
- speckit/001-migrate-all-hardcoded-secrets/
  ├── spec.md          # WHAT to build (requirements, acceptance criteria)
  ├── plan.md          # HOW to build (step-by-step with code examples)
  ├── tasks.md         # 24 tasks (T001-T024) with [P] markers
  ├── research.md      # Technology decisions and rationale
  ├── data-model.md    # Data schemas and relationships
  └── contracts/       # API contracts (MCP tools)

- speckit/002-add-authentication-authorization-all/
- speckit/003-deploy-comprehensive-firestore-security/
- speckit/004-implement-comprehensive-input-validation/
- speckit/005-build-comprehensive-test-suite/

═══════════════════════════════════════════════════════════════════════════════
📞 WHEN YOU NEED HELP
═══════════════════════════════════════════════════════════════════════════════

Task is unclear?
→ Read speckit/[feature]/plan.md (detailed implementation steps)

Don't know what technology to use?
→ Read speckit/[feature]/research.md (technology decisions)

Tests failing?
→ Read speckit/speckit-prep/TEST_COVERAGE_GAPS.md (test specs)
→ Read speckit/[feature]/spec.md (acceptance criteria)

Unsure about compliance?
→ Read speckit/CONSTITUTION_QUICK_REF.md (69 rules with examples)

Hit a blocker?
1. Document in research.md
2. Check speckit/speckit-prep/AUDIT_REPORT.md (known issues)
3. Check speckit/speckit-prep/BREAKING_CHANGES.md
4. Report with context and proposed solution

═══════════════════════════════════════════════════════════════════════════════
🎯 SUCCESS CRITERIA (HOW YOU'LL BE MEASURED)
═══════════════════════════════════════════════════════════════════════════════

After 10-12 days of execution:

Security:
- Vulnerabilities: 15 → 0
- Risk Level: HIGH → LOW
- Compliance: 0% → 100% (69/69 rules)

Testing:
- Test Coverage: 0% → 80%+
- Tests: 0 → 270+
- CI/CD: Not operational → Fully automated

Code Quality:
- Type Coverage: Low → 100%
- Linter Errors: Many → Zero
- Dead Code: Present → Removed
- Functions >50 lines: Many → Zero

Performance:
- AI Response: Varies → <5s (95th percentile)
- API Response: Varies → <2s (95th percentile)
- Bundle Size: Unknown → <500KB (gzipped)

Production Readiness:
- Constitutional Compliance: 0/69 → 69/69
- Production Deployment: Not ready → Fully ready
- Health Checks: Not configured → Operational
- Monitoring: Not configured → Operational

Business Value:
- Professional Services Delivered: $55K-$80K
- Execution Time: 10-12 days (with parallel)
- ROI: 1,500-2,000%

═══════════════════════════════════════════════════════════════════════════════
🏁 FINAL VALIDATION (BEFORE DECLARING COMPLETE)
═══════════════════════════════════════════════════════════════════════════════

1. All tasks completed (120/120)
```bash
grep -c "\- \[x\]" speckit/001-*/tasks.md  # Should be 24
grep -c "\- \[x\]" speckit/002-*/tasks.md  # Should be 24
grep -c "\- \[x\]" speckit/003-*/tasks.md  # Should be 24
grep -c "\- \[x\]" speckit/004-*/tasks.md  # Should be 24
grep -c "\- \[x\]" speckit/005-*/tasks.md  # Should be 24
```

2. All quality gates passed
```bash
gitleaks detect --source . --verbose  # Zero secrets
pip-audit                              # Zero vulnerabilities
pytest --cov=.                         # 80%+ coverage
mypy .                                 # Zero type errors
flake8 .                               # Zero linter errors
```

3. Constitutional compliance (69/69 rules)
```bash
cat speckit/CONSTITUTION_QUICK_REF.md
# Manually verify all categories
```

4. Production deployment successful
- Health checks passing
- Monitoring operational
- Alerting configured
- Zero critical issues

═══════════════════════════════════════════════════════════════════════════════
🚀 YOUR EXECUTION STARTS NOW
═══════════════════════════════════════════════════════════════════════════════

First Command (Read complete briefing):
```bash
cat speckit/AGENT_INITIALIZATION_PROMPT.md
```

Second Command (Start orientation):
```bash
cat speckit/START_HERE.md
```

Third Command (Execute quick wins):
```bash
cat speckit/speckit-prep/QUICK_WINS.md
```

Fourth Command (Begin Feature #001):
```bash
cat speckit/001-migrate-all-hardcoded-secrets/spec.md
cat speckit/001-migrate-all-hardcoded-secrets/plan.md
cat speckit/001-migrate-all-hardcoded-secrets/tasks.md
```

═══════════════════════════════════════════════════════════════════════════════
✨ YOU NOW HAVE EVERYTHING NEEDED
═══════════════════════════════════════════════════════════════════════════════

✅ Complete implementation package ($55K-$80K value)
✅ 120 actionable tasks with detailed instructions
✅ 5 feature specifications (WHAT to build)
✅ 5 implementation plans (HOW to build)
✅ Constitutional compliance framework (69 rules)
✅ Audit context (current state analysis)
✅ Quality gates and success metrics
✅ Step-by-step execution guide

Transform IntelAgent from prototype to production in 10-12 days.

═══════════════════════════════════════════════════════════════════════════════
🎉 LET'S EXECUTE!
═══════════════════════════════════════════════════════════════════════════════

Generated: 2025-11-17
Branch: 005-build-comprehensive-test-suite
Package: 63 files, 22,328+ lines
Status: ✅ Ready to Execute

Your mission: Transform IntelAgent to production-grade in 10-12 days
Your tools: $55K-$80K in consulting deliverables
Your guide: speckit/START_HERE.md
Your first action: cat speckit/AGENT_INITIALIZATION_PROMPT.md

🚀 BEGIN IMPLEMENTATION NOW! 🚀

