# Life Harness - Testing Guide

This guide helps you test the Life Harness system to ensure everything works correctly.

## Quick Start Testing

### 1. Installation Test

```bash
# Check Python version
python --version  # Should be 3.11+

# Check Node version
node --version    # Should be 18+

# Check Docker (if using Docker)
docker --version
docker-compose --version
```

### 2. Backend Tests

**Start the backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Test endpoints using curl:**

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# API root
curl http://localhost:8000/
# Expected: {"message":"Life Harness API","version":"0.1.0"}

# Register a test user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
# Expected: {"access_token":"...","token_type":"bearer"}

# Save the token from response
TOKEN="your-token-here"

# Get profile (should fail - not created yet)
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer $TOKEN"
# Expected: 404 error

# Create profile
curl -X POST http://localhost:8000/api/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "year_of_birth": 1990,
    "country": "USA",
    "has_children": false,
    "intensity": "balanced",
    "life_snapshot": "Test user for system validation"
  }'
# Expected: Profile object returned

# Get profile again
curl http://localhost:8000/api/profile \
  -H "Authorization: Bearer $TOKEN"
# Expected: Profile object

# Create a thread
curl -X POST http://localhost:8000/api/threads \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Thread",
    "root_prompt": "Testing the system"
  }'
# Expected: Thread object with ID

# Save thread ID
THREAD_ID="thread-id-from-response"

# Get first question
curl -X POST "http://localhost:8000/api/threads/$THREAD_ID/step" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"control":"continue"}'
# Expected: {"done":false,"question":{...}}
```

**Test with Swagger UI:**

1. Open http://localhost:8000/docs
2. Click "Authorize" button
3. Enter Bearer token
4. Try each endpoint interactively

### 3. Frontend Tests

**Start the frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Manual testing checklist:**

Open http://localhost:5173 in your browser.

- [ ] **Login Page**
  - [ ] Can switch between login and register
  - [ ] Registration with valid email/password works
  - [ ] Registration with duplicate email shows error
  - [ ] Login with correct credentials works
  - [ ] Login with wrong credentials shows error

- [ ] **Onboarding**
  - [ ] Step 1: Can enter basic information
  - [ ] Step 1: Children checkbox shows/hides children count
  - [ ] Step 2: Can select role and intensity
  - [ ] Step 3: Can enter life snapshot
  - [ ] Can navigate back/forward between steps
  - [ ] Completing onboarding redirects to dashboard

- [ ] **Dashboard**
  - [ ] Coverage heatmap displays (initially empty)
  - [ ] Thread list is empty initially
  - [ ] Can click "New Thread"
  - [ ] New thread form validates required fields
  - [ ] Creating thread navigates to thread view
  - [ ] Logout button works

- [ ] **Thread View**
  - [ ] First question appears automatically
  - [ ] Multiple choice options are selectable
  - [ ] "Other" option shows text box
  - [ ] Elaboration text box works for all options
  - [ ] Submitting answer shows next question
  - [ ] Short answer questions show large text area
  - [ ] "Stop for Today" redirects to dashboard
  - [ ] Thread counter updates after answers

- [ ] **Entries View**
  - [ ] Initially empty
  - [ ] After answering freeform, entries appear
  - [ ] Clicking entry opens modal
  - [ ] Modal shows full raw text
  - [ ] Can change visibility level
  - [ ] Changes save and modal closes

- [ ] **Autobiography View**
  - [ ] Configuration form works
  - [ ] Scope dropdown shows/hides year inputs
  - [ ] Generate button starts loading
  - [ ] After generation, outline displays
  - [ ] Markdown text displays
  - [ ] Download button creates .md file

### 4. Integration Tests

**Full user journey:**

1. **Registration → Onboarding → First Thread**
   ```
   Register → Complete 3-step onboarding → Create "My Test Thread" →
   Answer 3 MC questions → Answer 1 freeform question → Stop
   ```

   Expected results:
   - Thread shows "Questions answered: 4"
   - Entries view shows 1 entry (from freeform)
   - Coverage heatmap has at least one non-zero cell

2. **Continue Thread → See Coverage Update**
   ```
   Return to dashboard → Click thread → Answer 3 more questions
   (include 1 freeform) → Stop → Check heatmap
   ```

   Expected results:
   - Thread shows "Questions answered: 7"
   - Entries view shows 2 entries
   - Coverage scores increased

3. **Generate Autobiography**
   ```
   Go to Autobiography → Select "Self" audience → "Balanced" tone →
   "Full Life" scope → Generate
   ```

   Expected results:
   - Outline with at least 1 chapter
   - Markdown text includes content from your entries
   - Download works

### 5. Error Handling Tests

**Test error scenarios:**

- [ ] **Backend down**
  - Stop backend server
  - Try to login on frontend
  - Expected: "Authentication failed" error

- [ ] **Invalid token**
  - Manually edit localStorage token to garbage
  - Refresh page
  - Expected: Redirect to login

- [ ] **Network timeout**
  - Block network to backend
  - Try to create thread
  - Expected: Error message

- [ ] **Vultr API failure**
  - Set invalid Vultr API key in .env
  - Restart backend
  - Try to get next question in thread
  - Expected: Fallback to freeform prompt

### 6. Performance Tests

**Load testing:**

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Linux
brew install httpd  # macOS

# Test registration endpoint
ab -n 100 -c 10 -p register.json -T application/json \
  http://localhost:8000/api/auth/register

# Where register.json contains:
# {"email":"load-test@example.com","password":"testpass"}
```

**Expected performance:**
- Registration: < 500ms per request
- Profile operations: < 200ms
- Thread step (without LLM): < 1000ms
- Thread step (with LLM): < 5000ms (depends on Vultr)
- Coverage grid: < 300ms
- Autobiography generation: 10-60s (depends on entry count)

### 7. Security Tests

**Basic security checks:**

- [ ] **Password hashing**
  - Check database: passwords should be bcrypt hashes, not plaintext

- [ ] **JWT validation**
  - Try accessing protected endpoint without token
  - Expected: 401 Unauthorized

- [ ] **CORS**
  - Try accessing API from different origin
  - Expected: CORS error (unless origin in allowed list)

- [ ] **SQL injection**
  - Try email like: `' OR '1'='1`
  - Expected: Handled safely by SQLAlchemy

- [ ] **XSS**
  - Enter answer with: `<script>alert('XSS')</script>`
  - Expected: Rendered as text, not executed

### 8. Database Tests

**Verify data integrity:**

```bash
# SQLite
sqlite3 backend/lifeharness.db

# Check tables exist
.tables
# Should show: users, user_profiles, threads, questions, answers,
#              life_entries, coverage_grid

# Check user count
SELECT COUNT(*) FROM users;

# Check entries
SELECT headline, timeframe_label FROM life_entries;

# Check coverage
SELECT time_bucket, topic_bucket, score FROM coverage_grid;
```

**PostgreSQL:**
```bash
docker-compose exec postgres psql -U lifeharness

\dt  -- list tables
SELECT COUNT(*) FROM users;
SELECT * FROM life_entries LIMIT 5;
```

### 9. LLM Tests

**Test question generation:**

Create a thread and answer several questions. Verify that:
- Questions are relevant to thread theme
- Questions respect age (if you're 25, shouldn't ask about retirement)
- Questions respect children status (if no kids, shouldn't ask about them)
- Questions focus on low-coverage areas after ~5 answers
- Freeform prompts appear every 5-10 questions

**Test distillation:**

Answer a freeform question with rich detail:
```
"It was December 2015, and I was living in Brooklyn with my roommate Sarah.
We threw a huge holiday party and invited everyone we knew from our improv
class. I was nervous because I had a crush on this guy Tom who was coming.
The night was magical - we ended up talking on the fire escape for hours
while the party raged inside. He asked me out that night. We dated for
two years after that."
```

Check the resulting life entry for:
- Headline captures the essence
- Time bucket is correct (likely "20s" or "30s")
- Year detected (2015)
- Topics include "romantic_love" and possibly "friendships"
- Tags include: "Brooklyn", "Sarah", "Tom", "holiday", "improv"
- People: ["Sarah", "Tom"]
- Locations: ["Brooklyn"]
- Emotional tone: something like "nervous excitement" or "romantic"

### 10. Automated Test Suite (Future)

**Backend tests (pytest):**
```python
# tests/test_auth.py
def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_duplicate_registration(client):
    # Register once
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    # Try again
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 400
```

**Frontend tests (Jest + React Testing Library):**
```typescript
// tests/Login.test.tsx
test('switches from login to register', () => {
  render(<Login />);
  const switchButton = screen.getByText("Don't have an account? Register");
  fireEvent.click(switchButton);
  expect(screen.getByText('Register')).toBeInTheDocument();
});
```

## Test Data Sets

**Minimal test (3 entries):**
- 1 thread, 10 questions answered
- Result: Can test basic flow

**Light test (10 entries):**
- 2 threads, 30 questions answered
- Result: Can test coverage visualization

**Medium test (50 entries):**
- 5 threads, 100 questions answered
- Result: Can test autobiography generation

**Heavy test (200+ entries):**
- 10+ threads, 500+ questions answered
- Result: Can test performance, comprehensive autobiographies

## Reporting Bugs

When you find a bug, report it with:

1. **Steps to reproduce**
2. **Expected behavior**
3. **Actual behavior**
4. **Environment** (OS, Python version, Node version, Docker/manual)
5. **Logs** (from terminal or browser console)

Example:
```
Bug: Thread step returns 500 error

Steps:
1. Create thread "Test Thread"
2. Answer first question with freeform text
3. Click Continue
4. Server returns 500 error

Expected: Next question appears
Actual: Error message, no next question

Environment:
- macOS 13.5
- Python 3.11.5
- Manual setup (not Docker)
- SQLite database

Logs:
[Backend terminal shows traceback with KeyError: 'time_bucket']
```

## Success Criteria

The system passes testing if:

✅ All manual testing checklist items pass
✅ No errors in browser console during normal operation
✅ Backend logs show no errors during normal operation
✅ Database is populated correctly after use
✅ Coverage heatmap updates based on answers
✅ Entries are created from freeform responses
✅ Autobiography generates successfully with 10+ entries
✅ Seal/visibility controls work correctly
✅ System survives backend restart (data persists)
✅ Multiple threads can exist simultaneously
✅ LLM integration works (questions generated, entries distilled)

---

Happy testing! Report issues on [GitHub](https://github.com/CrazyDubya/LifeHarness/issues).
