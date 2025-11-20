# Life Harness - Complete Onboarding Guide

Welcome to Life Harness! This guide will walk you through every step of setting up and using the system to document your life story.

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [First Time User Journey](#first-time-user-journey)
3. [Creating Your First Thread](#creating-your-first-thread)
4. [Answering Questions](#answering-questions)
5. [Managing Your Entries](#managing-your-entries)
6. [Understanding the Coverage Heatmap](#understanding-the-coverage-heatmap)
7. [Generating Your Autobiography](#generating-your-autobiography)
8. [Tips for Best Results](#tips-for-best-results)
9. [Troubleshooting](#troubleshooting)

---

## Installation & Setup

### Prerequisites

Choose one of the following options:

**Option A: Docker (Recommended)**
- Docker Desktop or Docker Engine
- Docker Compose

**Option B: Manual Installation**
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite works for development)

### Step 1: Get a Vultr API Key

Life Harness uses AI to generate personalized questions and distill your answers. You'll need a Vultr Inference API key:

1. Visit [Vultr.com](https://www.vultr.com/) and create an account
2. Navigate to **Account** → **API** → **Inference API**
3. Click **Generate API Key**
4. Copy the key (you'll need it in the next step)

**Cost estimate:** Vultr Inference API is pay-as-you-go. Typical usage for daily sessions costs $1-5/month.

### Step 2: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/CrazyDubya/LifeHarness.git
cd LifeHarness

# Copy environment configuration
cp .env.example .env

# Edit .env and add your Vultr API key
nano .env  # or use your preferred editor
```

In the `.env` file, set:
```env
VULTR_API_KEY=your-actual-api-key-here
SECRET_KEY=generate-a-random-secret-here
```

**Security tip:** Generate a strong SECRET_KEY using:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Start the Application

**Using Docker:**
```bash
docker-compose up -d
```

Wait 30-60 seconds for services to start, then verify:
```bash
docker-compose ps
# All services should show "Up"
```

**Using Manual Setup:**

Terminal 1 (Backend):
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm install
npm run dev
```

### Step 4: Access the Application

Open your browser and navigate to:
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs (interactive API testing)

---

## First Time User Journey

### Screen 1: Login / Register

**What you'll see:**
- A simple login form
- Link to switch to registration

**What to do:**
1. Click "Don't have an account? Register"
2. Enter your email (used for login only, not shared)
3. Create a strong password
4. Click "Register"

**Note:** Your data is stored locally on your system. Life Harness doesn't send your personal information to any external service except Vultr's AI for processing questions and answers.

### Screen 2: Onboarding Wizard - Basic Information

After registration, you'll be guided through a 3-step onboarding process.

**Step 1 fields:**

- **Year of Birth** (e.g., 1990)
  - Used to adapt questions to your age
  - Won't ask about retirement if you're 25

- **Country** (optional)
  - Helps with cultural context

- **Primary Language** (optional)
  - Currently English only, but noted for future

- **Relationship Status**
  - Single / Partnered / Married / Divorced / Widowed / Complicated
  - Helps tailor questions about relationships

- **Do you have children?** (checkbox)
  - If checked, you'll be asked:
    - Number of children
    - Age brackets (for more specific questions)
  - If unchecked, the system won't ask about kids unless you explicitly create a "children" thread

**Why this matters:** Life Harness adapts questions based on your actual life circumstances. If you don't have children, it won't waste your time asking about them.

Click **Next** when done.

### Screen 3: Onboarding Wizard - Work & Preferences

**Step 2 fields:**

- **Main Role**
  - Student / Employee / Self-employed / Unemployed / Retired / Caregiver / Other
  - Helps focus career-related questions

- **Field or Industry** (optional)
  - E.g., "Technology", "Healthcare", "Education"
  - Adds specificity to work questions

- **Intensity**
  - **Light:** Casual questions, easier to answer, less emotional depth
  - **Balanced:** Mix of easy and profound questions (recommended)
  - **Deep:** Thorough exploration, emotionally intense, detailed

**Tip:** Start with "Balanced" and adjust later if needed.

Click **Next** when done.

### Screen 4: Onboarding Wizard - Life Snapshot

**Step 3:**

Write a brief (5-10 lines) sketch of your life so far. This helps the AI understand your story arc.

**Example:**
```
I was born in Seattle and grew up in the suburbs. I studied
computer science at UW and worked at Microsoft for 5 years
before starting my own company. I got married in 2015 and
have two kids. Now I'm focusing on work-life balance and
documenting my journey for my family.
```

**Why this matters:** This snapshot gives the AI context to ask better, more relevant questions. It's like giving a biographer a head start.

Click **Complete Setup** when done.

---

## Creating Your First Thread

After onboarding, you'll land on the **Dashboard**.

### What is a Thread?

A thread is a themed conversation about a specific period or aspect of your life. Think of it as a chapter in your biography that you'll explore through questions.

**Good thread examples:**
- "My College Years" (time-focused)
- "Career Journey" (topic-focused)
- "Relationship with My Parents" (relationship-focused)
- "Starting My Business" (event-focused)
- "Life in New York" (place-focused)

### Creating a Thread

1. Click the **"New Thread"** button on the Dashboard
2. Fill in the form:

**Title:** Short, memorable name
```
Example: "My College Years"
```

**Root Prompt:** Detailed description of what you want to explore
```
Example: "I want to document my college experience from
2010-2014 at the University of Washington. This includes
academics, friendships, personal growth, and the transition
from teenager to adult. I want to capture both the struggles
and triumphs of this formative period."
```

**Optional: Time Focus** (advanced)
- Select specific age ranges: 10s, 20s, 30s, etc.
- Leave blank to let the AI decide

**Optional: Topic Focus** (advanced)
- Select specific topics: friendships, work, family, etc.
- Leave blank for a broad exploration

3. Click **Create**

You'll be immediately taken to the thread to start answering questions.

---

## Answering Questions

### The Question Flow

Life Harness presents **one question at a time**. This keeps you focused and prevents overwhelm.

### Types of Questions

**1. Multiple Choice**

Example:
```
In your twenties, how central were your friendships to your
sense of identity?

○ They were my whole world
○ Very important, but not everything
○ Nice to have, but secondary
○ I mostly kept to myself
○ None of these fit (I'll explain)
```

**How to answer:**
1. Read the question carefully
2. Select the option that best fits
3. If you select "None of these fit", a text box appears
4. Optionally, add elaboration in the text box even if you picked an option
5. Click **Continue**

**Tip:** The elaboration text is where the magic happens! Even if you pick an option, add a sentence or two with specifics. The AI uses this to create your life entries.

**2. Short Answer (Freeform)**

Every 5-10 questions, you'll get a freeform prompt:

Example:
```
Take a moment to write about a memory that stands out
from this period of your life.
```

**How to answer:**
1. Write as much or as little as you want (minimum ~20 words)
2. Be specific: names, places, dates, feelings
3. Write naturally - it's your story
4. Click **Continue** when done

**Example answer:**
```
The night before my organic chemistry final, I was studying
in the library with Sarah and Tom. We were exhausted and
stressed, but around midnight we started laughing about
something stupid and couldn't stop. We got shushed by
the librarian three times. I failed the final, but that
friendship sustained me through a really hard semester.
```

### The Infinite Loop

Questions will keep coming as long as you want. There's no end - you control when to stop.

**To take a break:**
- Click **"Stop for Today"** at any time
- Your progress is saved
- Resume the thread anytime from the Dashboard

### Behind the Scenes

When you answer:
1. Your response is saved immediately
2. If you provided meaningful text (freeform or elaboration), the AI:
   - Distills it into a structured "Life Entry"
   - Extracts: headline, time period, topics, people, places, emotional tone
   - Updates your coverage grid
3. The AI generates the next question based on:
   - Your profile (age, children, etc.)
   - This thread's theme
   - Your recent answers
   - Your coverage gaps (asks about under-explored areas)

---

## Managing Your Entries

Click **"My Entries"** in the navigation to view all your life entries.

### What's in an Entry?

Each entry contains:
- **Headline:** AI-generated title (e.g., "Late night study session friendship")
- **Timeframe:** When this happened (e.g., "20s", "2012")
- **Distilled:** AI summary of your story
- **Raw Text:** Your original answer
- **Tags:** Keywords extracted by AI (e.g., "college", "friendship", "stress")
- **Topics:** Categories (e.g., "friendships", "education")
- **Visibility:** Who can see this (default: self only)
- **Seal:** When this becomes visible to others (default: no seal)

### Filtering Entries

Use the sidebar to filter by:
- **Time Period:** pre10, 10s, 20s, 30s, 40s, 50+
- **Topic:** family, work, love, health, etc.

### Editing Visibility & Seals

Click on any entry to open the detail modal.

**Visibility Levels:**
1. **Self:** Only you can see this (default)
2. **Trusted:** Close friends/family you explicitly grant access
3. **Heirs:** Your children/descendants (for posthumous release)
4. **Public:** Anyone

**Seal Types:**
1. **None:** Visible now (based on visibility level)
2. **Until Date:** Hidden until a specific date
3. **Until Event:** Hidden until an event occurs (e.g., "my death", "my 50th birthday")
4. **Manual:** Hidden until you manually unseal

**Example use cases:**
- Write about current struggles, seal until you've overcome them
- Document family secrets to be revealed after you pass
- Save embarrassing stories to share at your own retirement party

**To update:**
1. Click an entry to open the modal
2. Change the "Visibility Level" dropdown
3. Optionally add a seal
4. Changes save automatically
5. Click "Close"

---

## Understanding the Coverage Heatmap

The Dashboard shows a **Coverage Heatmap** - a grid showing which areas of your life you've documented.

### How to Read It

**Rows:** Life topics
- Family of Origin
- Friendships
- Romantic Love
- Children
- Work/Career
- Money/Status
- Health/Body
- Creativity/Play
- Beliefs/Values
- Crises/Turning Points

**Columns:** Life periods
- pre10 (before age 10)
- 10s (ages 10-19)
- 20s (ages 20-29)
- 30s (ages 30-39)
- 40s (ages 40-49)
- 50+ (age 50+)

**Colors:**
- **Light gray:** No coverage (0 points)
- **Light blue:** Minimal coverage (1-20 points)
- **Medium blue:** Some coverage (21-40 points)
- **Blue:** Good coverage (41-60 points)
- **Dark blue:** Strong coverage (61-80 points)
- **Darkest blue:** Comprehensive coverage (81-100 points)

### What the Scores Mean

You earn points by creating life entries in each time × topic cell:
- Each entry typically adds 10 points
- Maximum 100 points per cell
- The AI preferentially asks about low-coverage areas

### How to Use It

**Strategy 1: Fill the gaps**
Look for gray or light blue cells and create threads targeting those areas.

Example: See that "Friendships × 30s" is low? Create a thread called "Friends in My Thirties".

**Strategy 2: Deep dive**
Pick one period (e.g., your 20s) and systematically cover all topics.

**Strategy 3: Organic exploration**
Just answer questions naturally - the AI will guide you toward gaps automatically.

---

## Generating Your Autobiography

When you're ready to see your story as a cohesive narrative, generate an autobiography.

Click **"Autobiography"** in the navigation.

### Configuration Options

**1. Audience**
Who will read this?
- **Self:** Private reflection, full honesty
- **Trusted:** Close friends/family, mostly open
- **Heirs:** Future generations, curated
- **Public:** Anyone, heavily filtered

**Effect:** Only entries with matching or lower visibility are included. Sealed entries are excluded unless their seal has expired.

**2. Tone**
- **Light:** Casual, easier reading, glosses over pain
- **Balanced:** Honest but not overwhelming (recommended)
- **Deep:** Unflinching, emotionally intense, thorough

**3. Scope**

**Full Life:**
Includes all visible entries from all time periods.

**Time Range:**
Focus on specific years (e.g., 1995-2005 for your "Starting My Career" autobiography).

### Generating

1. Configure your settings
2. Click **"Generate"**
3. Wait 30-60 seconds (depends on number of entries)
4. Review the output

### What You Get

**Outline:**
Chapter structure with sections. Example:
```
Chapter 1: Early Years
  - Childhood Memories
  - Family Dynamics
  - School Days

Chapter 2: Coming of Age
  - High School
  - First Love
  - College Applications
```

**Markdown Text:**
A full narrative synthesized from your entries. The AI:
- Organizes chronologically
- Creates narrative flow
- Maintains your voice
- Adds transitions between entries
- Structures into chapters/sections

### Downloading

Click **"Download Markdown"** to save as a .md file.

**What to do with it:**
- Convert to PDF using tools like [Pandoc](https://pandoc.org/)
- Convert to EPUB for e-readers
- Edit in any text editor or Markdown app
- Share with family
- Print and bind

### Regenerating

You can generate multiple autobiographies:
- Different audiences (one for kids, one for yourself)
- Different time ranges (one per decade)
- Different tones (light for social media, deep for therapy)

Each generation is fresh - not saved in the system. Download what you want to keep.

---

## Tips for Best Results

### 1. Be Specific

**Bad answer:**
"I was happy."

**Good answer:**
"I was so happy I literally jumped up and down in the parking lot, then called my mom crying tears of joy."

**Why:** Specificity creates vivid, memorable entries. The AI has more to work with.

### 2. Include Context

**Bad answer:**
"We broke up."

**Good answer:**
"Sarah and I broke up after 3 years together. It was mutual but painful. This was February 2015, right before I moved to Boston."

**Why:** Context (names, dates, places) helps the AI organize your timeline and makes your autobiography richer.

### 3. Write Freely on Freeform Prompts

Don't overthink it. Write like you're talking to a trusted friend. Grammar doesn't matter. Just capture the memory.

### 4. Use Multiple Threads

Don't try to document everything in one thread. Create multiple:
- One per decade
- One per major life event
- One per relationship
- One per location you lived

This keeps sessions focused and prevents "thread fatigue".

### 5. Short Daily Sessions

**Better:** 10-15 minutes per day, answer 5-10 questions
**Worse:** 2 hours once a month, answer 50 questions

Why: Daily sessions keep memories fresh and prevent burnout. It becomes a habit like journaling.

### 6. Review Your Entries

Periodically browse your entries to:
- Remind yourself what you've covered
- Spark new memories
- Update visibility/seals as your life evolves

### 7. Don't Seal Everything

It's tempting to seal painful memories, but remember: your future self needs honesty. Seal truly private things, but don't rob yourself of your full story.

### 8. Use "Stop for Today" Liberally

If a question triggers strong emotions, it's okay to stop. Come back tomorrow. This isn't a race.

---

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError" or similar Python errors**

Solution:
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**"Database connection failed"**

Solution: Check your `.env` file. For development, use:
```
DATABASE_URL=sqlite:///./lifeharness.db
```

**"Port 8000 already in use"**

Solution: Either stop the other process using port 8000, or run on a different port:
```bash
uvicorn app.main:app --reload --port 8001
```
(Then update frontend to point to 8001)

### Frontend Issues

**"npm install" fails**

Solution: Ensure Node.js 18+ is installed:
```bash
node --version  # Should be v18.x or higher
npm --version   # Should be v9.x or higher
```

If not, install from [nodejs.org](https://nodejs.org/).

**Frontend won't connect to backend**

Solution: Check frontend/.env:
```
VITE_API_URL=http://localhost:8000/api
```

Make sure backend is running on port 8000.

**"Network Error" when clicking buttons**

Solution:
1. Check browser console (F12) for errors
2. Verify backend is running: visit http://localhost:8000/docs
3. Check CORS: backend should show your frontend origin in logs

### LLM Issues

**"Failed to generate question"**

Causes:
1. Vultr API key invalid or expired
2. Vultr API rate limit hit
3. Network issues

Solutions:
1. Verify API key in `.env`
2. Check Vultr dashboard for usage/limits
3. Wait a minute and try again

**Fallback:** If LLM fails, the system will show a freeform prompt instead.

**Questions don't make sense / are off-topic**

The AI is learning from your answers. After 5-10 questions, it should improve. If not:
1. Provide more context in your freeform answers
2. Ensure your profile is accurate
3. Try creating more focused threads (specific time periods)

### Data Issues

**"I answered a question but no entry was created"**

This is normal if:
- You only selected a multiple-choice option without adding text
- Your text was very short (< 20 words)

The system only creates entries from substantive text responses.

**"My entry has the wrong time period"**

The AI infers time from your text. To fix:
- Be explicit about dates in answers: "This was in 2015..." or "When I was 23..."
- The more context you provide, the more accurate it gets

**"I want to delete an entry"**

Currently not implemented (to preserve memories). Workaround:
- Set visibility to "Self"
- Add seal: "Manual" with audiences blocked: "All"

This effectively hides it from all outputs.

### Docker Issues

**"docker-compose up" fails**

Common fixes:
```bash
# Pull latest images
docker-compose pull

# Rebuild
docker-compose build --no-cache

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

**"Postgres won't start"**

Solution: Check if port 5432 is already in use:
```bash
# Stop other Postgres instances
# OR change port in docker-compose.yml
```

---

## Advanced Usage

### Custom Threads for Specific Coverage

If you notice a gap in your heatmap (e.g., "Health × 40s" is empty), create a targeted thread:

**Title:** "Health Journey in My Forties"

**Root Prompt:**
```
Document my health experiences from ages 40-49, including
physical changes, medical issues, fitness efforts, mental
health, and how my relationship with my body evolved.
```

**Time Focus:** Select "40s"
**Topic Focus:** Select "health_body"

The AI will laser-focus on this area.

### Collaborative Storytelling

Have a parent, sibling, or old friend answer questions about YOU in a shared thread:

1. Create a thread: "Mom's Memories of My Childhood"
2. Have them answer questions
3. Their answers create entries in your timeline
4. Great for filling gaps you don't remember

**Note:** Currently requires sharing your account. Multi-user support planned for future.

### Exporting for Backup

**Database backup (Docker):**
```bash
docker-compose exec postgres pg_dump -U lifeharness lifeharness > backup.sql
```

**SQLite backup (manual setup):**
```bash
cp backend/lifeharness.db lifeharness_backup_$(date +%Y%m%d).db
```

**Entry export:**
Visit http://localhost:8000/docs, use the `GET /api/entries` endpoint, save the JSON.

---

## Next Steps

Now that you're set up:

1. **Complete onboarding** if you haven't
2. **Create your first thread** - start with something recent and easy
3. **Answer 5-10 questions** - get a feel for the flow
4. **Check your entries** - see how the AI distills your answers
5. **Look at the heatmap** - identify what to explore next
6. **Make it a habit** - 10 minutes per day

Your life story is worth documenting. Start today, one question at a time.

---

**Questions or issues?** Open an issue on [GitHub](https://github.com/CrazyDubya/LifeHarness/issues).
