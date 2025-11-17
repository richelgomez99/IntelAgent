# SPEC-001: Authentication System
## IntelAgent Competitive Intelligence Platform

**Status:** 🟡 DRAFT  
**Priority:** 🔴 P0 - CRITICAL  
**Effort:** 2 days  
**Dependencies:** None  
**Blocks:** All security features

---

## 📋 OVERVIEW

### Problem Statement
The application is currently **completely open** to the public with zero authentication. Anyone with the URL can:
- Consume unlimited Gemini API quota (potential $10k+ bills)
- Access all collected competitive intelligence data
- Query the system without any restrictions

This is a **CRITICAL SECURITY VULNERABILITY** that must be fixed before any production use.

### Solution Summary
Implement **Streamlit-based authentication** with:
- Username/password login (Phase 1 - Quick)
- Session management (auto-expire after 8 hours)
- Logout functionality
- Password hashing (bcrypt)
- (Future: OAuth Google Sign-In)

### Success Criteria
- [ ] Unauthenticated users see login screen
- [ ] Invalid credentials rejected with clear error
- [ ] Authenticated users can access full app
- [ ] Sessions persist across page refreshes
- [ ] Sessions expire after 8 hours of inactivity
- [ ] Logout clears session immediately
- [ ] All auth operations logged

---

## 🎯 USER STORIES

### US-001: Login Required
**As a** product owner  
**I want** all users to log in before using the app  
**So that** we can control access and prevent abuse

**Acceptance Criteria:**
- Given user visits app without session
- When page loads
- Then user sees login screen
- And cannot access any functionality until authenticated

---

### US-002: Successful Login
**As a** authorized user  
**I want** to log in with my credentials  
**So that** I can use the competitive intelligence platform

**Acceptance Criteria:**
- Given valid username and password
- When user submits login form
- Then user is redirected to main app
- And session cookie is set
- And login event is logged

---

### US-003: Failed Login
**As a** unauthorized user  
**I want** to see a clear error when credentials are wrong  
**So that** I know what to do next

**Acceptance Criteria:**
- Given invalid username or password
- When user submits login form
- Then user sees "Invalid username/password" error
- And form is cleared
- And failed attempt is logged

---

### US-004: Session Persistence
**As an** authenticated user  
**I want** my session to persist across page refreshes  
**So that** I don't have to log in repeatedly

**Acceptance Criteria:**
- Given user is logged in
- When user refreshes page
- Then user remains authenticated
- And no login screen is shown

---

### US-005: Session Expiry
**As a** security-conscious product owner  
**I want** sessions to expire after 8 hours  
**So that** unattended sessions don't remain open indefinitely

**Acceptance Criteria:**
- Given user logged in 8+ hours ago
- When user refreshes page or makes request
- Then session is invalidated
- And user sees login screen
- And expiry event is logged

---

### US-006: Logout
**As an** authenticated user  
**I want** to log out when I'm done  
**So that** others can't use my session

**Acceptance Criteria:**
- Given user is logged in
- When user clicks "Logout" button
- Then session is cleared
- And user is redirected to login screen
- And logout event is logged

---

## 🏗️ ARCHITECTURE

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit App                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────┐         │
│  │   Authentication Middleware                │         │
│  │   • Check session state                    │         │
│  │   • Validate session expiry                │         │
│  │   • Redirect to login if needed            │         │
│  └────────────────┬───────────────────────────┘         │
│                   │                                      │
│    ┌──────────────┴─────────────┐                       │
│    │                              │                      │
│    ▼                              ▼                      │
│  ┌─────────────┐          ┌─────────────┐              │
│  │ Login Screen│          │  Main App   │              │
│  │  • Form     │          │  • Dashboard│              │
│  │  • Validate │          │  • Chat UI  │              │
│  └──────┬──────┘          └─────────────┘              │
│         │                                                │
│         ▼                                                │
│  ┌─────────────────────────────────────┐               │
│  │   streamlit_authenticator           │               │
│  │   • Password hashing (bcrypt)       │               │
│  │   • Session management               │               │
│  │   • Cookie handling                  │               │
│  └──────────┬──────────────────────────┘               │
│             │                                            │
│             ▼                                            │
│  ┌─────────────────────────────────────┐               │
│  │   Credentials Storage                │               │
│  │   • config/credentials.yaml          │               │
│  │   • Hashed passwords (bcrypt)        │               │
│  │   • User metadata                    │               │
│  └─────────────────────────────────────┘               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User visits app
   ↓
2. Check session state
   ├─ Valid session → Skip to step 7
   └─ No session → Continue to step 3
   ↓
3. Show login screen
   ↓
4. User enters credentials
   ↓
5. Validate credentials
   ├─ Invalid → Show error, go to step 3
   └─ Valid → Continue to step 6
   ↓
6. Create session
   • Set session state
   • Set cookie (expires 8 hours)
   • Log login event
   ↓
7. Show main app
   ↓
8. On every page interaction:
   • Check session expiry
   • If expired → Clear session, go to step 3
   • If valid → Continue
```

---

## 📝 TECHNICAL SPECIFICATION

### File Structure

```
streamlit-app/
  ├── app.py                        # Modified: Add auth check
  ├── requirements.txt              # Modified: Add streamlit-authenticator
  ├── config/
  │   └── credentials.yaml          # NEW: User credentials
  └── auth/
      ├── __init__.py               # NEW
      ├── authenticator.py          # NEW: Auth wrapper
      └── middleware.py             # NEW: Session checks
```

---

### Implementation: Phase 1 (Basic Auth)

**Step 1: Install Dependencies**

```bash
# Add to streamlit-app/requirements.txt
streamlit-authenticator==0.2.3
PyYAML==6.0.1
```

---

**Step 2: Create Credentials File**

```yaml
# config/credentials.yaml
credentials:
  usernames:
    admin:
      email: admin@intelagent.ai
      name: Admin User
      password: $2b$12$KIXjxSomeHashedPasswordHere  # bcrypt hash of "changeme"
    demo:
      email: demo@intelagent.ai
      name: Demo User
      password: $2b$12$AnotherHashedPasswordHere      # bcrypt hash of "demo123"

cookie:
  name: intelagent_auth_cookie
  key: some_signature_key_random_string_here  # Random secret key
  expiry_days: 0.33  # 8 hours (0.33 days)

preauthorized:
  emails:
    - admin@intelagent.ai
```

**Generate hashed passwords:**

```python
# tools/generate_password.py
import bcrypt
import yaml

def hash_password(password: str) -> str:
    """Generate bcrypt hash for password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

if __name__ == "__main__":
    print("Password:", "changeme")
    print("Hash:", hash_password("changeme"))
```

---

**Step 3: Create Authentication Module**

```python
# streamlit-app/auth/authenticator.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuthManager:
    """Manage authentication for Streamlit app"""
    
    def __init__(self, credentials_path: str = "config/credentials.yaml"):
        """Initialize authenticator with credentials"""
        with open(credentials_path) as file:
            config = yaml.load(file, Loader=SafeLoader)
        
        self.authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )
    
    def require_auth(self):
        """
        Require authentication to continue.
        Renders login screen if not authenticated.
        Returns user info if authenticated.
        """
        # Render login widget
        name, authentication_status, username = self.authenticator.login(
            'Login to IntelAgent',
            'main'
        )
        
        # Handle authentication states
        if authentication_status == False:
            logger.warning(f"Failed login attempt for username: {username}")
            st.error('Username/password is incorrect')
            st.stop()
        
        elif authentication_status == None:
            st.warning('Please enter your username and password')
            st.info("Default credentials: admin / changeme")
            st.stop()
        
        elif authentication_status:
            # Successful login
            logger.info(f"User logged in: {username}")
            
            # Store user info in session
            if 'user_info' not in st.session_state:
                st.session_state.user_info = {
                    'username': username,
                    'name': name,
                    'login_time': datetime.utcnow().isoformat()
                }
            
            return {
                'username': username,
                'name': name,
                'email': st.session_state.get('email', '')
            }
    
    def render_logout_button(self):
        """Render logout button in sidebar"""
        with st.sidebar:
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                self.logout()
    
    def logout(self):
        """Log out current user"""
        username = st.session_state.get('user_info', {}).get('username', 'unknown')
        logger.info(f"User logged out: {username}")
        
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Rerun app to show login screen
        st.rerun()
```

---

**Step 4: Add Authentication Check to App**

```python
# streamlit-app/app.py (BEGINNING OF FILE)
import streamlit as st
from auth.authenticator import AuthManager

# Initialize auth manager
auth = AuthManager()

# REQUIRE AUTHENTICATION
user = auth.require_auth()

# If we get here, user is authenticated
st.write(f"Welcome, {user['name']}!")

# Original app code continues below...
st.set_page_config(...)
# ... rest of app ...
```

---

**Step 5: Add Logout Button**

```python
# streamlit-app/app.py (IN SIDEBAR SECTION)
with st.sidebar:
    # ... existing sidebar content ...
    
    # Add logout button at bottom
    auth.render_logout_button()
```

---

**Step 6: Add Session Expiry Check**

```python
# streamlit-app/auth/middleware.py
from datetime import datetime, timedelta
import streamlit as st
import logging

logger = logging.getLogger(__name__)

SESSION_TIMEOUT_HOURS = 8

def check_session_timeout():
    """
    Check if session has expired.
    Clears session and forces re-login if expired.
    """
    if 'user_info' not in st.session_state:
        return  # No session, will be caught by auth check
    
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.utcnow()
        return
    
    last_activity = st.session_state.last_activity
    now = datetime.utcnow()
    
    # Check if session expired
    if now - last_activity > timedelta(hours=SESSION_TIMEOUT_HOURS):
        username = st.session_state.get('user_info', {}).get('username', 'unknown')
        logger.warning(f"Session expired for user: {username}")
        
        # Clear session
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.warning(f"⏰ Your session expired after {SESSION_TIMEOUT_HOURS} hours of inactivity.")
        st.info("Please log in again.")
        st.stop()
    
    # Update last activity
    st.session_state.last_activity = now

# Use in app.py after authentication
# check_session_timeout()
```

---

### Configuration Management

**Environment Variables:**

```bash
# .env (DO NOT COMMIT)
AUTH_COOKIE_KEY=randomly_generated_secret_key_here
SESSION_TIMEOUT_HOURS=8
```

**Load in app:**

```python
import os
from dotenv import load_dotenv

load_dotenv()

AUTH_COOKIE_KEY = os.environ.get('AUTH_COOKIE_KEY', 'fallback_key_for_dev')
SESSION_TIMEOUT_HOURS = int(os.environ.get('SESSION_TIMEOUT_HOURS', '8'))
```

---

## 🧪 TESTING PLAN

### Unit Tests

```python
# tests/unit/test_authentication.py
import pytest
from streamlit-app.auth.authenticator import AuthManager
from streamlit-app.auth.middleware import check_session_timeout
from datetime import datetime, timedelta

class TestAuthentication:
    """Test authentication system"""
    
    def test_valid_credentials(self):
        """Valid credentials authenticate successfully"""
        auth = AuthManager('tests/fixtures/credentials.yaml')
        # Mock streamlit authentication
        result = auth.authenticate('admin', 'changeme')
        assert result['success'] == True
    
    def test_invalid_credentials(self):
        """Invalid credentials are rejected"""
        auth = AuthManager('tests/fixtures/credentials.yaml')
        result = auth.authenticate('admin', 'wrongpassword')
        assert result['success'] == False
    
    def test_session_creation(self):
        """Session is created after successful login"""
        # Test session state after login
        assert 'user_info' in st.session_state
        assert st.session_state.user_info['username'] == 'admin'
    
    def test_session_timeout(self, monkeypatch):
        """Session expires after timeout period"""
        # Mock session state
        st.session_state.last_activity = datetime.utcnow() - timedelta(hours=9)
        
        # Should raise exception or clear session
        with pytest.raises(Exception):
            check_session_timeout()
    
    def test_logout_clears_session(self):
        """Logout clears all session data"""
        auth = AuthManager()
        auth.logout()
        
        assert 'user_info' not in st.session_state
        assert 'last_activity' not in st.session_state
```

---

### Integration Tests

```python
# tests/integration/test_auth_flow.py
import pytest
from selenium import webdriver

@pytest.mark.integration
class TestAuthenticationFlow:
    """Test authentication user flows"""
    
    def test_login_flow(self):
        """User can log in and access app"""
        driver = webdriver.Chrome()
        driver.get("http://localhost:8501")
        
        # Should see login screen
        assert "Login to IntelAgent" in driver.page_source
        
        # Enter credentials
        username_input = driver.find_element_by_name("username")
        password_input = driver.find_element_by_name("password")
        
        username_input.send_keys("admin")
        password_input.send_keys("changeme")
        
        # Submit
        submit_button = driver.find_element_by_text("Login")
        submit_button.click()
        
        # Should see main app
        assert "Competitive Intelligence Platform" in driver.page_source
        assert "Login" not in driver.page_source
```

---

### Manual Test Cases

**TC-001: First-Time Login**
1. Clear browser cookies
2. Navigate to app URL
3. Verify login screen appears
4. Enter valid credentials (admin / changeme)
5. Click "Login"
6. Verify main app loads
7. Verify "Welcome, Admin User" appears

**TC-002: Invalid Credentials**
1. Clear browser cookies
2. Navigate to app URL
3. Enter invalid credentials (admin / wrongpass)
4. Click "Login"
5. Verify error message appears
6. Verify still on login screen

**TC-003: Session Persistence**
1. Log in successfully
2. Refresh browser page
3. Verify still authenticated (no login screen)
4. Verify can use app normally

**TC-004: Session Expiry**
1. Log in successfully
2. Wait 8+ hours (or mock system time)
3. Refresh browser page
4. Verify redirected to login screen
5. Verify "Session expired" message

**TC-005: Logout**
1. Log in successfully
2. Click "Logout" button in sidebar
3. Verify redirected to login screen
4. Attempt to use browser back button
5. Verify still on login screen (session cleared)

---

## 🚀 DEPLOYMENT PLAN

### Phase 1: Development (This Sprint)

**Week 1:**
- Day 1: Set up `streamlit-authenticator`
- Day 1: Create `credentials.yaml` with test users
- Day 2: Implement `AuthManager` class
- Day 2: Add auth check to `app.py`
- Day 3: Add logout functionality
- Day 3: Add session timeout check
- Day 4: Write unit tests (10 tests)
- Day 4: Write integration tests (5 tests)
- Day 5: Manual testing & bug fixes

**Deliverables:**
- [ ] Authentication working locally
- [ ] 15+ tests passing
- [ ] Documentation updated
- [ ] Ready for staging deployment

---

### Phase 2: Staging (Next Week)

- Deploy to staging environment
- Load test with 50 concurrent users
- Security audit (XSS, CSRF, session fixation)
- Performance testing (login latency < 1s)
- Bug fixes from testing

---

### Phase 3: Production (Week After)

- Deploy to production with feature flag (10% rollout)
- Monitor error rates, login success rates
- Gradually increase to 100% over 48 hours
- Announce to users (email notification)

---

## 📊 SUCCESS METRICS

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Login Success Rate** | > 95% | Cloud Logging |
| **Login Latency (P95)** | < 1 second | Cloud Monitoring |
| **Session Expiry Rate** | < 10% | Cloud Logging |
| **Failed Login Attempts** | < 5% | Cloud Logging |
| **Test Coverage** | > 80% | pytest-cov |

### Qualitative Metrics

- [ ] User feedback positive (> 4/5 rating)
- [ ] Zero security incidents related to auth
- [ ] Zero unauthorized access attempts succeed
- [ ] Support tickets related to auth < 5 per week

---

## 🔒 SECURITY CONSIDERATIONS

### Threats Mitigated

✅ **Unauthorized Access:** Users must authenticate  
✅ **Brute Force:** Rate limiting on login (10 attempts/hour)  
✅ **Session Hijacking:** Secure cookies (httpOnly, secure)  
✅ **Session Fixation:** New session ID on login  
✅ **Credential Stuffing:** Bcrypt hashing (slow, resistant to rainbow tables)

### Remaining Risks

⚠️ **Weak Passwords:** Users can set weak passwords  
**Mitigation:** Enforce password policy (Phase 2)

⚠️ **Shared Credentials:** Users may share login info  
**Mitigation:** User education, audit logs

⚠️ **Phishing:** Users could be tricked into entering credentials on fake site  
**Mitigation:** HTTPS only, clear branding

---

## 🔮 FUTURE ENHANCEMENTS (Phase 2+)

### OAuth Integration (Phase 2)

**Why:** Better UX, more secure, no password management

**Implementation:**
- Google Sign-In (OAuth 2.0)
- Use Firebase Authentication
- Store user profiles in Firestore

**Effort:** 3 days

---

### Multi-Factor Authentication (Phase 3)

**Why:** Enhanced security for sensitive data

**Implementation:**
- TOTP (Time-based One-Time Passwords)
- Use `pyotp` library
- QR code setup during first login

**Effort:** 2 days

---

### Role-Based Access Control (Phase 3)

**Why:** Limit sensitive operations to admins

**Roles:**
- `viewer` - Can query, cannot modify
- `analyst` - Can query, save searches
- `admin` - Full access, user management

**Effort:** 3 days

---

## 📚 DOCUMENTATION

### User Guide

**Login Instructions:**
1. Navigate to https://your-app.run.app
2. Enter your username and password
3. Click "Login"
4. If successful, you'll see the main dashboard

**Troubleshooting:**
- **"Username/password incorrect"** - Double-check credentials (case-sensitive)
- **"Session expired"** - Log in again (sessions expire after 8 hours)
- **Can't remember password** - Contact admin@intelagent.ai

---

### Admin Guide

**Add New User:**

```python
# tools/add_user.py
import bcrypt
import yaml

def add_user(username: str, name: str, email: str, password: str):
    """Add new user to credentials.yaml"""
    # Hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    # Load credentials
    with open('config/credentials.yaml') as f:
        config = yaml.safe_load(f)
    
    # Add user
    config['credentials']['usernames'][username] = {
        'name': name,
        'email': email,
        'password': hashed
    }
    
    # Save
    with open('config/credentials.yaml', 'w') as f:
        yaml.dump(config, f)
    
    print(f"✅ User {username} added successfully")

# Usage
add_user('jdoe', 'John Doe', 'jdoe@company.com', 'SecurePass123!')
```

---

## ✅ ACCEPTANCE CHECKLIST

Before considering this spec complete:

**Development:**
- [ ] Code implemented and reviewed
- [ ] Unit tests written (15+ tests)
- [ ] Integration tests written (5+ tests)
- [ ] Linter passing (ruff)
- [ ] Type checker passing (mypy)
- [ ] Manual testing completed

**Documentation:**
- [ ] User guide written
- [ ] Admin guide written
- [ ] Code commented
- [ ] Architecture diagram updated

**Security:**
- [ ] Security audit passed
- [ ] Passwords hashed with bcrypt
- [ ] Sessions expire after 8 hours
- [ ] HTTPS enforced in production
- [ ] OWASP Top 10 checked

**Deployment:**
- [ ] Staging deployment successful
- [ ] Performance testing passed
- [ ] Load testing passed (50 users)
- [ ] Production deployment planned

**Monitoring:**
- [ ] Login metrics tracked
- [ ] Error alerts configured
- [ ] Audit logs enabled

---

**Estimated Total Effort:** 2 days (16 hours)  
**Risk Level:** 🟡 Medium (new dependency, session management complexity)  
**Impact:** 🔴 CRITICAL (blocks all other security features)

---

**Next Specification:** spec-002-cloud-function-security.md


