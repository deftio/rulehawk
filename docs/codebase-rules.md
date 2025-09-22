# Codebase Rules - For Automated Agents and Humans too

Quality standards and enforcement checkpoints to ensure consistent, maintainable code across all contributors.

**Purpose:** These rules define quality gates that prevent common issues, enforce consistency, and enable reliable automation. Unlike task-specific instructions, these are persistent standards that apply to all development work.

**Rules vs Tasks:** Rules are quality constraints (what must be true), while tasks are implementation steps (what to do for a given project). Rules remain constant across projects; tasks change based on specific work.

## Always-Active Rules (Continuous Enforcement)
Standards that apply continuously during development and must be enforced automatically at each stage of development.

### A1 — Code Formatting
Enforce consistent code style automatically across all files to eliminate style debates and reduce diff noise.

**Details:**
- **What:** Automatic code style consistency across all files  
- **Why:** Eliminates style debates, improves readability, reduces diff noise  
- **Action:** Configure auto-format on save in your editor/IDE or via a script
- **Trigger:** Every file save
- **Tools:** Auto-format on save with project standards
  - **Python:** `ruff format`
  - **JS/TS:** `biome check --write` 
  - **C/C++:** `clang-format -i`
  - **Go:** `gofmt -w`

### A2 — Organize Experimental and Temporary Files  
Use designated directories for debug files, experiments, and temporary artifacts to keep the main codebase clean.

**Details:**
- **What:** Direct all experimental and temporary files to appropriate directories  
- **Why:** Keeps main codebase clean, makes it obvious what's experimental vs production code  
- **Action:** Create temporary/debug files only in designated directories
- **Trigger:** When creating any experimental, debug, or temporary files
- **Designated directories:**
  - `scratch/` - Quick experiments and throwaway code
  - `debug/` - Debug scripts and diagnostic tools  
  - `test-*/` - Named test directories (e.g., `test-auth`, `test-performance`)
  - `temp/` - Temporary files and outputs
- **Forbidden in main codebase:**
  - Debug files in `src/`, root directory, or alongside production code
  - Files named `debug.*`, `test.*`, `scratch.*` outside designated areas
  - Build outputs mixed with source code

### A3 — Branch Protection
Never commit directly to protected branches (`main`, `master`, `develop`, `staging`, `production`) - always use feature branches.

**Details:**
- **What:** Prevent direct commits to protected branches
- **Why:** Maintains branch stability, enforces code review process, enables safe rollbacks
- **Action:** Always create feature branches for any changes, never commit directly to protected branches
- **Trigger:** Every commit attempt
- **Protected branches:** `main`, `master`, `develop`, `staging`, `production`, `release/*`
- **Required branch naming:**
  - `feature/description` - New functionality
  - `fix/bug-description` - Bug fixes
  - `chore/task-description` - Maintenance, refactoring, dependencies
  - `hotfix/critical-issue` - Emergency production fixes

---

## Security Rules (Continuous Enforcement)
Critical security practices that must be followed at all times to protect sensitive data and prevent vulnerabilities.

### S1 — No Hardcoded Secrets
Never commit credentials, API keys, tokens, or sensitive data directly in code or configuration files.

**Details:**
- **What:** Prevent secrets from being hardcoded in any file
- **Why:** Exposed credentials lead to security breaches, API abuse, and data theft
- **Action:** Use environment variables, secret management systems, or configuration services
- **Trigger:** Every file save and commit
- **Forbidden patterns:**
  - API keys: `api_key = "sk-..."`
  - Passwords: `password = "admin123"`
  - Tokens: `token = "ghp_..."`
  - Private keys: `-----BEGIN RSA PRIVATE KEY-----`
  - Connection strings with embedded credentials
- **Acceptable alternatives:**
  ```python
  # Good - using environment variables
  api_key = os.environ.get('API_KEY')

  # Good - using secret manager
  api_key = secret_manager.get_secret('api-key')

  # Good - using config file (not in repo)
  config = load_config('.env.local')  # .env.local in .gitignore
  ```
- **Detection tools:**
  - Pre-commit: `detect-secrets`, `gitleaks`
  - CI/CD: Secret scanning in GitHub/GitLab
  - IDE: Security plugins that highlight potential secrets

### S2 — Secure Credential Storage
Store credentials and sensitive configuration using approved secure methods only.

**Details:**
- **What:** Use proper credential storage mechanisms based on environment
- **Why:** Centralized secure storage prevents leaks and enables rotation
- **Action:** Choose appropriate storage method for each environment
- **Development environments:**
  - `.env` files (must be in `.gitignore`)
  - Local secret managers (e.g., 1Password CLI, HashiCorp Vault)
  - Docker secrets for containerized apps
- **Production environments:**
  - Cloud provider secret managers (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager)
  - Kubernetes secrets (with encryption at rest)
  - Environment-specific configuration services
- **Required `.gitignore` entries:**
  ```
  .env
  .env.*
  *.pem
  *.key
  *.cert
  *_rsa
  *_dsa
  *_ed25519
  credentials/
  secrets/
  ```

### S3 — Authentication & Authorization Best Practices
Implement authentication and authorization using industry-standard patterns and libraries.

**Details:**
- **What:** Use proven auth patterns instead of custom implementations
- **Why:** Custom auth is error-prone; established patterns have been security-tested
- **Action:** Implement auth using standard protocols and maintained libraries
- **Required practices:**
  - **Never store plaintext passwords** - use bcrypt, scrypt, or Argon2
  - **Use established auth libraries** - don't roll your own crypto
  - **Implement proper session management** - secure cookies, CSRF tokens
  - **Follow OAuth2/OIDC standards** for third-party auth
  - **Use JWT correctly** - short expiry, proper validation, no sensitive data
- **Password requirements:**
  ```python
  # Good - using bcrypt
  import bcrypt
  hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

  # Bad - custom hashing
  import hashlib
  hashed = hashlib.md5(password.encode()).hexdigest()  # NEVER DO THIS
  ```
- **Session security:**
  - HTTPOnly cookies for session tokens
  - Secure flag for HTTPS environments
  - SameSite attribute for CSRF protection
  - Regular session rotation

### S4 — Input Validation & Sanitization
Validate and sanitize all external input to prevent injection attacks.

**Details:**
- **What:** Validate all input from users, APIs, and external systems
- **Why:** Prevents SQL injection, XSS, command injection, and other attacks
- **Action:** Apply validation at boundaries and use parameterized queries
- **Required validations:**
  - **SQL:** Use parameterized queries or ORMs
    ```python
    # Good - parameterized query
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

    # Bad - string concatenation
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # VULNERABLE
    ```
  - **HTML/JavaScript:** Escape output, use Content Security Policy
    ```javascript
    // Good - using template literals with escaping
    element.textContent = userInput;  // Auto-escaped

    // Bad - innerHTML with user data
    element.innerHTML = userInput;  // XSS VULNERABLE
    ```
  - **OS Commands:** Avoid shell=True, use subprocess with lists
    ```python
    # Good - subprocess with list
    subprocess.run(['ls', '-l', user_path], check=True)

    # Bad - shell command with user input
    os.system(f"ls -l {user_path}")  # COMMAND INJECTION
    ```
  - **File paths:** Validate against directory traversal
    ```python
    # Good - path validation
    safe_path = os.path.normpath(os.path.join(base_dir, user_input))
    if not safe_path.startswith(base_dir):
        raise ValueError("Invalid path")
    ```

### S5 — Dependency Security
Keep dependencies updated and scan for known vulnerabilities.

**Details:**
- **What:** Regularly update and audit third-party dependencies
- **Why:** Outdated dependencies often contain known security vulnerabilities
- **Action:** Automate dependency scanning and updates
- **Required practices:**
  - Run vulnerability scans in CI/CD pipeline
  - Update dependencies at least monthly
  - Review and approve major version updates
  - Pin dependency versions in production
- **Scanning tools:**
  - **Python:** `pip-audit`, `safety check`
  - **JavaScript:** `npm audit`, `yarn audit`
  - **General:** Snyk, OWASP Dependency-Check, GitHub Dependabot
- **Update strategy:**
  ```json
  // package.json - use exact versions in production
  {
    "dependencies": {
      "express": "4.18.2",  // Not ^4.18.2
      "lodash": "4.17.21"
    }
  }
  ```

### S6 — Secure Communication
Enforce encrypted communication for all sensitive data transmission.

**Details:**
- **What:** Use TLS/HTTPS for all network communication with sensitive data
- **Why:** Prevents man-in-the-middle attacks and data interception
- **Action:** Configure proper TLS and validate certificates
- **Required practices:**
  - **Always use HTTPS** in production
  - **Validate SSL certificates** - don't disable verification
  - **Use TLS 1.2 or higher** - disable older protocols
  - **Implement HSTS** headers for web applications
- **Configuration examples:**
  ```python
  # Good - verify certificates
  response = requests.get('https://api.example.com', verify=True)

  # Bad - disabled verification
  response = requests.get('https://api.example.com', verify=False)  # INSECURE
  ```
  ```javascript
  // Good - HSTS header
  app.use((req, res, next) => {
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    next();
  });
  ```

### S7 — Logging & Error Handling Security
Implement secure logging practices that don't expose sensitive information.

**Details:**
- **What:** Log security events without exposing sensitive data
- **Why:** Logs are often less protected but critical for security monitoring
- **Action:** Sanitize logs and implement proper error handling
- **Forbidden in logs:**
  - Passwords (even hashed)
  - API keys and tokens
  - Credit card numbers
  - Social security numbers
  - Personal health information
  - Full request/response bodies with sensitive data
- **Required logging:**
  - Authentication attempts (success/failure)
  - Authorization failures
  - Input validation failures
  - System errors (sanitized)
- **Error handling:**
  ```python
  # Good - generic error to user, detailed log
  try:
      process_payment(card_number)
  except PaymentError as e:
      logger.error(f"Payment failed for user {user_id}: {e.code}")
      return {"error": "Payment processing failed. Please try again."}

  # Bad - exposing internal error
  except Exception as e:
      return {"error": str(e)}  # May leak sensitive info
  ```

### S8 — Security Testing Requirements
Include security testing as part of the development process.

**Details:**
- **What:** Integrate security testing into development and CI/CD
- **Why:** Catches vulnerabilities before they reach production
- **Action:** Run automated security tests and conduct code reviews
- **Required tests:**
  - **Static analysis (SAST):** Run on every commit
    - Python: `bandit`, `semgrep`
    - JavaScript: `eslint-plugin-security`, `NodeJsScan`
  - **Dependency scanning:** Daily in CI/CD
  - **Dynamic testing (DAST):** Before major releases
  - **Penetration testing:** For public-facing APIs
- **Code review checklist:**
  - [ ] No hardcoded secrets
  - [ ] Input validation present
  - [ ] Proper auth checks
  - [ ] Secure session handling
  - [ ] Safe error messages
  - [ ] Logging sanitized

---

## Pre-Flight Checklist (Before Development Session)
Validation steps to complete before starting any significant development work to ensure your environment is ready.

### P1 — Environment Validation
Verify your development environment is ready and tests pass before starting any coding work.

**Details:**
- **What:** Verify your development environment is ready for work  
- **Why:** Catches environment issues early before you waste time coding  
- **Action:** Run environment check script before starting any development

- [ ] Working directory is clean (`git status`)
- [ ] On correct feature branch (not main/master)
- [ ] Dependencies up to date (`npm install`, `pip install -r requirements.txt`)
- [ ] Local tests pass (`npm test`, `pytest`)

### P2 — Task Planning Documentation
Create a written plan with clear steps and current status to enable progress tracking and agent recovery.

**Details:**
- **What:** Document your implementation plan before coding  
- **Why:** Prevents scope creep, enables agent recovery, tracks progress  
- **Action:** Create/update `TASK-PLAN.md` with clear steps and current status

Create/update `TASK-PLAN.md` in feature branch:
```markdown
## Objective
Brief description of what we're building

## Implementation Steps
- [ ] Step 1: Setup X
- [ ] Step 2: Implement Y  
- [ ] Step 3: Test Z

## Current Status
What's been completed, what's next

## Blockers/Questions
Issues that need resolution
```

---

## In-Flight Rules (During Development)
Quality standards that guide ongoing development work to maintain consistency and documentation as you code.

### F1 — Document Public APIs
**What:** Add comprehensive documentation for any public-facing code  
**Why:** Enables other developers to use your code correctly without reading implementation  
**Action:** Write docstrings/comments immediately after creating public functions/classes

**Trigger:** When creating/modifying public functions/classes
**Requirement:** Add documentation before moving to next task
- Purpose, parameters, return values, examples
- **Python:** Google-style docstrings
- **JS/TS:** JSDoc with `@param`, `@returns`, `@example`

### F2 — Update Task Plan
**What:** Keep your implementation plan current as work progresses  
**Why:** Enables seamless handoffs and agent recovery after crashes  
**Action:** Update status immediately after completing any implementation step

**Trigger:** Completing any implementation step
**Action:** Update `TASK-PLAN.md` current status
- Mark completed steps
- Add new steps discovered
- Document decisions/changes

### F3 — Test as You Go
**What:** Write tests immediately after implementing functionality  
**Why:** Catches bugs early when context is fresh, prevents test debt accumulation  
**Action:** Write corresponding tests before moving to next feature

**Trigger:** After implementing any new function/feature
**Requirement:** Write corresponding test before continuing
- Unit test for the specific function
- Integration test if it touches other components

---

## Post-Flight Checklist (Before Considering Work Complete)
Final validation gates that must all pass before marking work "done" or creating a pull request.

### C1 — Zero Warnings Policy
Eliminate all compiler and linter warnings from your code before considering work complete.

**Details:**
- **What:** Eliminate all compiler/linter warnings from your code  
- **Why:** Warnings often indicate real bugs, clean builds prevent warning fatigue  
- **Action:** Fix warnings or explicitly suppress with documented justification

**Check:** `pytest -W error`, lint with warnings-as-errors
**Fix:** Resolve all warnings or suppress with justification
```python
# noqa: E501 - long URL required for API compatibility
# type: ignore[attr-defined] - dynamic attribute from plugin
```

### C2 — Test Coverage Requirements  
Ensure comprehensive test coverage for all new and changed code with measurable before/after comparison.

**Details:**
- **What:** Ensure comprehensive test coverage for all new/changed code  
- **Why:** Prevents regressions, documents expected behavior, enables confident refactoring  
- **Action:** Measure coverage before/after and ensure thresholds are met

**Check:** Coverage before/after comparison
**Requirements:**
- New/changed code: 100% coverage (with documented exceptions)
- Overall project: ≥80% coverage maintained
- All tests deterministic and complete in <10 minutes

### C3 — CI Must Be Green
All automated checks and tests must pass in the CI environment before work can be considered complete.

**Details:**
- **What:** All automated checks and tests must pass in CI environment  
- **Why:** Ensures changes work in clean environment, prevents breaking main branch  
- **Action:** Fix any CI failures before proceeding; document infrastructure issues

**Check:** All automated checks pass
**Action:** If CI fails due to infrastructure, document and stop
**Fix:** Code issues before proceeding

### C4 — Documentation Complete
Verify all documentation requirements are satisfied and reflect the final implementation.

**Details:**
- **What:** Verify all documentation requirements are satisfied  
- **Why:** Ensures future maintainers understand your changes and decisions  
- **Action:** Review and update all relevant documentation before submission

**Check:** All public APIs documented per F1
**Check:** `TASK-PLAN.md` reflects final implementation
**Update:** `RELEASE-NOTES.md` if user-facing changes

### C5 — Security Review
Verify all security rules (S1-S8) are followed for changes touching sensitive systems or data.

**Details:**
- **What:** Comprehensive security validation against all security rules
- **Why:** Prevents security vulnerabilities from reaching production
- **Action:** Run security scans and verify compliance with security rules S1-S8

**Required validation:**
- [ ] No hardcoded secrets (S1)
- [ ] Proper credential storage (S2)
- [ ] Auth best practices followed (S3)
- [ ] Input validation present (S4)
- [ ] Dependencies scanned (S5)
- [ ] Secure communication enforced (S6)
- [ ] Logging sanitized (S7)
- [ ] Security tests passing (S8)

**High-risk changes requiring extra review:**
- Authentication/authorization changes
- External API integrations
- Data encryption/handling
- Database schema changes
- Payment processing
- Personal data handling

**Automated checks:** Secret detection, SAST, dependency scanning

---

## Commit/PR Standards (Final Submission)
Formatting and documentation requirements for submitting completed work for review.

### S1 — Conventional Commits
Use standardized commit message format to enable automated tooling and clear change history.

**Details:**
- **What:** Standardized commit message format for automated tooling  
- **Why:** Enables automatic changelog generation and semantic versioning  
- **Action:** Use structured commit messages following conventional format

```
type(scope): description

feat(auth): add OAuth2 integration
fix(api): handle null user responses
```

### S2 — PR Description Template
Provide comprehensive pull request documentation to help reviewers understand context and validation.

**Details:**
- **What:** Comprehensive pull request documentation  
- **Why:** Helps reviewers understand context, risks, and validation performed  
- **Action:** Fill out complete PR template before requesting review

```markdown
## Problem & Approach
What you solved and how

## Validation
- [ ] All post-flight checks completed
- [ ] Coverage: before X% → after Y%  
- [ ] Manual testing performed

## Risks & Rollout
Breaking changes, deployment notes
```

---

## Agent Recovery Protocol
Structured approach for agents to resume work after crashes or interruptions.
If agent crashes during development:

1. **Check `TASK-PLAN.md`** - resume from current status
2. **Review last commits** - understand what was completed  
3. **Run post-flight checks** - verify current state
4. **Continue from next uncompleted step** in task plan

---

## Rule Enforcement CLI Tool
Automated tooling to monitor compliance, provide feedback, and guide corrections.

### `rules` Command Interface
```bash
# Audit current state against all rules
rules audit

# Enforce specific phase rules
rules enforce --phase=preflight
rules enforce --phase=inflight
rules enforce --phase=postflight
rules enforce --phase=security

# Auto-fix what can be fixed
rules fix --auto

# Check specific rules
rules check A1 A2 C1
rules check S1 S2 S3 S4 S5 S6 S7 S8  # Security rules

# Generate compliance report
rules report --format=json --output=compliance.json
```

### Audit & Logging
**Purpose:** Track rule violations to improve rules and agent behavior
**Logs to:** `.rules/audit.log` with structured entries
```json
{
  "timestamp": "2025-09-20T10:30:00Z",
  "rule": "C1",
  "violation": "pytest warnings detected", 
  "file": "src/auth.py:45",
  "severity": "error",
  "auto_fixable": false,
  "context": "agent_session_123"
}
```

**Violation Actions:**
- **Block:** Stop operation until fixed (C1, C3)
- **Warn:** Log and continue with notification (F2)
- **Auto-fix:** Attempt automatic correction (A1, A2)

---

## Enforcement Automation
Integration points for automated rule checking across different development phases and tools.

**Always-Active:** `rules enforce --watch` (continuous monitoring)
**Pre-Flight:** `rules enforce --phase=preflight` (before session)
**In-Flight:** `rules enforce --phase=inflight` (on file changes)
**Post-Flight:** `rules enforce --phase=postflight` (before PR)
**Agent Integration:** Each phase maps to specific CLI commands