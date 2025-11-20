# Life Harness - Screen Flows & UI Guide

This document describes each screen in detail for screenshot documentation and UI reference.

---

## Navigation Structure

```
Public Routes:
└── /login - Login/Register page

Protected Routes:
├── /onboarding - 3-step onboarding wizard (one-time)
├── /dashboard - Main landing page
├── /thread/:id - Question/answer conversation
├── /entries - Life entries library
└── /autobiography - Autobiography generator
```

---

## Screen 1: Login / Register

**Route:** `/login`

**Purpose:** User authentication

### Layout

```
┌─────────────────────────────────────┐
│                                     │
│         LIFE HARNESS                │
│   Autobiography one question        │
│          at a time                  │
│                                     │
│  ┌───────────────────────────────┐ │
│  │         Login                 │ │
│  │                               │ │
│  │  Email                        │ │
│  │  [________________]           │ │
│  │                               │ │
│  │  Password                     │ │
│  │  [________________]           │ │
│  │                               │ │
│  │  [      Login      ]          │ │
│  │                               │ │
│  │  Don't have an account?       │ │
│  │       Register                │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

**Elements:**
- Centered card with white background
- App title and tagline at top
- Email input (type: email)
- Password input (type: password)
- Primary button: "Login" or "Register" (blue)
- Text link to switch modes

**States:**
- Login mode (default)
- Register mode (click link to switch)
- Error state: Red text above form showing error message
- Loading state: Button disabled with "Logging in..." text

**Validation:**
- Email must be valid format
- Password must be 8+ characters (could be added)
- Show errors inline below inputs

**Screenshot notes:**
- Capture both login and register views
- Capture error state with sample error

---

## Screen 2-4: Onboarding Wizard

**Route:** `/onboarding`

**Purpose:** Collect user profile information

### Common Layout

```
┌─────────────────────────────────────────────────┐
│  Welcome to Life Harness                        │
│  Let's set up your profile...                   │
│                                                  │
│  ┌─────────────────────────────────────────────┐│
│  │  [Step Content Here]                        ││
│  │                                             ││
│  │  [Form fields]                              ││
│  │                                             ││
│  │  [Back] [Next/Complete]                     ││
│  └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

### Step 1: Basic Information

**Elements:**
- Header: "Basic Information"
- Year of Birth (number input)
- Country (text input)
- Primary Language (text input)
- Relationship Status (dropdown)
  - Options: Single, Partnered, Married, Divorced, Widowed, Complicated
- "I have children" (checkbox)
- If checked:
  - Number of Children (number input)
- Navigation: [Next] button (blue)

**Screenshot notes:**
- Capture with checkbox unchecked
- Capture with checkbox checked (showing children fields)

### Step 2: Work & Preferences

**Elements:**
- Header: "Work & Preferences"
- Main Role (dropdown)
  - Options: Student, Employee, Self-employed, Unemployed, Retired, Caregiver, Other
- Field or Industry (text input, labeled optional)
- Intensity (dropdown)
  - Light: Casual questions
  - Balanced: Mix of depth and ease (default)
  - Deep: Thorough exploration
- Navigation: [Back] [Next] buttons

**Screenshot notes:**
- Show all three intensity options in dropdown
- Show balanced selected

### Step 3: Life Snapshot

**Elements:**
- Header: "Life Snapshot"
- Description text: "Write a brief (5-10 lines) sketch of your life so far..."
- Large textarea (8 rows)
- Placeholder: "I was born in... grew up in... studied... worked as..."
- Navigation: [Back] [Complete Setup] buttons

**Screenshot notes:**
- Show with example text filled in
- Button should say "Complete Setup" not "Next"

---

## Screen 5: Dashboard

**Route:** `/dashboard`

**Purpose:** Overview of threads, coverage, and quick actions

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  [Dashboard] [My Entries] [Autobiography]    [Logout]   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Life Harness Dashboard                                  │
│  Welcome back! Continue documenting your life story.     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Coverage Heatmap                                        │
│  Visual representation of which life areas...            │
│                                                          │
│  [Heatmap Grid: 10 rows × 6 columns with colors]        │
│                                                          │
│  Legend: Darker blue = more coverage                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Your Threads                        [New Thread]        │
│                                                          │
│  ┌────────────────────┐  ┌────────────────────┐        │
│  │ My College Years   │  │ Career Journey     │        │
│  │                    │  │                    │        │
│  │ Exploring college  │  │ From first job to  │        │
│  │ experiences...     │  │ current role...    │        │
│  │                    │  │                    │        │
│  │ Questions: 23      │  │ Questions: 45      │        │
│  │ Last: 2 days ago   │  │ Last: 1 hour ago   │        │
│  └────────────────────┘  └────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

**Elements:**

**Top Navigation Bar:**
- Links: Dashboard, My Entries, Autobiography
- Logout button (right-aligned, gray)

**Welcome Card:**
- Heading: "Life Harness Dashboard"
- Subtitle text

**Coverage Heatmap Card:**
- Title: "Coverage Heatmap"
- Description
- Heatmap table:
  - Headers: pre10, 10s, 20s, 30s, 40s, 50+
  - Rows: Family, Friendships, Love, Children, Career, Money, Health, Creativity, Beliefs, Turning Points
  - Cells colored: Gray (0), Light blue (1-20), Medium blue (21-40), Blue (41-60), Dark blue (61-80), Darkest blue (81-100)
  - Numbers shown in cells when > 0
- Legend text

**Threads Card:**
- Title: "Your Threads" with [New Thread] button
- Grid of thread cards (2 columns on desktop, 1 on mobile)
- Each thread card:
  - Title (bold)
  - Root prompt (truncated, gray text)
  - Questions answered count
  - Last activity timestamp
  - Hover effect: slight shadow
  - Click to open thread

**Empty State (no threads):**
- Centered text: "No threads yet. Create your first thread..."

**New Thread Form (when clicked):**
- Title input
- Root Prompt textarea
- [Create] [Cancel] buttons

**Screenshot notes:**
- Capture with 0 threads (empty state)
- Capture with 2-3 threads
- Capture with "New Thread" form open
- Capture heatmap with varied coverage (some cells filled)

---

## Screen 6: Thread View

**Route:** `/thread/:id`

**Purpose:** Interactive Q&A session

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  [Dashboard]                                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  My College Years                                        │
│  Exploring college experiences from 2010-2014...         │
│  Questions answered: 12                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  In your twenties, how central were your friendships    │
│  to your sense of identity?                             │
│                                                          │
│  ○ They were my whole world                             │
│  ○ Very important, but not everything                   │
│  ⦿ Nice to have, but secondary                          │
│  ○ I mostly kept to myself                              │
│  ○ None of these fit (I'll explain)                     │
│                                                          │
│  Want to elaborate? (optional)                          │
│  ┌─────────────────────────────────────────────┐       │
│  │                                             │       │
│  │                                             │       │
│  └─────────────────────────────────────────────┘       │
│                                                          │
│  [Continue]  [Stop for Today]                           │
└─────────────────────────────────────────────────────────┘
```

### Multiple Choice Question

**Elements:**
- Thread title (bold, large)
- Root prompt (gray, smaller)
- Questions answered count
- Question text (large, clear)
- Radio button options:
  - Each option in a box with border
  - Selected option has blue background
  - Last option typically "None of these fit" or "Other"
- If "Other" selected:
  - Text area appears: "Please explain:"
- If any option selected:
  - Optional elaboration text area appears below
- Buttons:
  - [Continue] (blue, primary) - disabled until option selected
  - [Stop for Today] (gray, secondary)

**States:**
- No selection: Continue button disabled
- Option selected: Continue button enabled
- "Other" selected: Required text area appears
- Loading: "Generating next question..." message

### Short Answer Question

**Elements:**
- Thread info (same as above)
- Freeform prompt text
  - Examples:
    - "Take a moment to write about a memory..."
    - "Describe a turning point..."
    - "What's something you want to remember forever?"
- Large textarea (8 rows)
- Character count (optional)
- Buttons: [Continue] [Stop for Today]

**Screenshot notes:**
- Capture MC question with no selection
- Capture MC question with selection (no "Other")
- Capture MC question with "Other" selected (showing explain box)
- Capture MC question with elaboration filled in
- Capture short answer question
- Capture loading state

---

## Screen 7: Entries View

**Route:** `/entries`

**Purpose:** Browse and manage life entries

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  [Dashboard] [My Entries] [Autobiography]    [Logout]   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Life Entries                                            │
│  All your documented memories and experiences            │
└─────────────────────────────────────────────────────────┘

┌─────────┬───────────────────────────────────────────────┐
│ Filters │ ┌─────────────────────────────────────────┐   │
│         │ │ Late night study session friendship     │   │
│ Time:   │ │ 2012 • 20s                       [self] │   │
│ [All ▾] │ │ ────────────────────────────────────────│   │
│         │ │ I was studying with Sarah and Tom in    │   │
│         │ │ the library when we couldn't stop       │   │
│         │ │ laughing about something...             │   │
│ Topic:  │ │                                         │   │
│ [All ▾] │ │ [college] [friendship] [stress]         │   │
│         │ └─────────────────────────────────────────┘   │
│ [Apply] │                                               │
│         │ ┌─────────────────────────────────────────┐   │
│         │ │ First day at Microsoft                  │   │
│         │ │ 2015 • 20s                    [trusted] │   │
│         │ │ ────────────────────────────────────────│   │
│         │ │ Walking into the Redmond campus on my   │   │
│         │ │ first day, nervous and excited...       │   │
│         │ │                                         │   │
│         │ │ [Microsoft] [career] [new beginnings]   │   │
│         │ └─────────────────────────────────────────┘   │
└─────────┴───────────────────────────────────────────────┘
```

**Elements:**

**Left Sidebar (Filters):**
- Time Period dropdown (pre10, 10s, 20s, etc.)
- Topic dropdown (family, work, etc.)
- [Apply Filters] button

**Main Area:**
- Entry cards (list)
- Each entry card:
  - Headline (bold)
  - Timeframe label and time bucket
  - Visibility level badge (top right)
  - Distilled text (truncated to ~3 lines)
  - Tags as pills/chips (blue background)
  - Click to open detail modal

**Empty State:**
- "No entries yet. Start a thread to create your first entry!"

### Entry Detail Modal

```
┌─────────────────────────────────────────────────────────┐
│  Late night study session friendship              [×]   │
├─────────────────────────────────────────────────────────┤
│  2012                                                    │
│                                                          │
│  Full Text                                              │
│  The night before my organic chemistry final, I was     │
│  studying in the library with Sarah and Tom. We were    │
│  exhausted and stressed, but around midnight we         │
│  started laughing about something stupid and couldn't   │
│  stop. We got shushed by the librarian three times.     │
│  I failed the final, but that friendship sustained me   │
│  through a really hard semester.                        │
│                                                          │
│  Visibility Settings                                    │
│  Visibility Level  [Self ▾]                             │
│                                                          │
│  [Close]                                                │
└─────────────────────────────────────────────────────────┘
```

**Elements:**
- Modal overlay (dark background)
- Modal card (centered, white)
- Close button (top right)
- Headline
- Timeframe
- Full raw text (scrollable if long)
- Visibility dropdown
- [Close] button

**Screenshot notes:**
- Capture with 5-6 entries showing
- Capture with filters applied
- Capture modal open for one entry
- Capture empty state

---

## Screen 8: Autobiography View

**Route:** `/autobiography`

**Purpose:** Generate autobiographies

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  [Dashboard] [My Entries] [Autobiography]    [Logout]   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Generate Autobiography                                  │
│  Create a comprehensive autobiography from your entries  │
└─────────────────────────────────────────────────────────┘

┌─────────┬───────────────────────────────────────────────┐
│ Config  │                                               │
│         │  [Empty state placeholder text]               │
│ Audience│                                               │
│ [Self▾] │  "Configure your autobiography and click      │
│         │   Generate to begin"                          │
│ Tone    │                                               │
│ [Bal.▾] │                                               │
│         │                                               │
│ Scope   │                                               │
│ [Full▾] │                                               │
│         │                                               │
│[Generate]│                                               │
│         │                                               │
│[Download]│                                               │
└─────────┴───────────────────────────────────────────────┘
```

### After Generation

```
┌─────────┬───────────────────────────────────────────────┐
│ Config  │  Outline                                      │
│         │  ─────────────────────────────────────────────│
│ Audience│  Chapter 1: Early Years                       │
│ [Self▾] │    - Childhood Memories                       │
│         │    - School Days                              │
│ Tone    │                                               │
│ [Bal.▾] │  Chapter 2: Coming of Age                     │
│         │    - High School                              │
│ Scope   │    - College                                  │
│ [Full▾] │                                               │
│         │  ─────────────────────────────────────────────│
│[Generate]│  # Chapter 1: Early Years                     │
│         │                                               │
│[Download]│  ## Childhood Memories                        │
│         │                                               │
│         │  I grew up in a small town where everyone...  │
│         │  ...                                          │
└─────────┴───────────────────────────────────────────────┘
```

**Elements:**

**Left Sidebar (Config):**
- Audience dropdown (Self, Trusted, Heirs, Public)
- Tone dropdown (Light, Balanced, Deep)
- Scope dropdown (Full Life, Time Range)
- If Time Range:
  - From Year input
  - To Year input
- [Generate] button (blue)
- [Download Markdown] button (gray) - only shows after generation

**Main Area:**

**Before generation:**
- Centered placeholder text

**During generation:**
- "Generating your autobiography..."
- "This may take a minute..."

**After generation:**
- Outline section:
  - List of chapters with sections
  - Indented hierarchy
- Markdown preview:
  - Scrollable box with gray background
  - Raw markdown text shown
  - Formatted preview

**Screenshot notes:**
- Capture empty state
- Capture during generation (loading)
- Capture after generation with outline and markdown
- Capture time range scope showing year inputs

---

## Responsive Considerations

**Mobile (< 768px):**
- Navigation collapses to hamburger menu
- Coverage heatmap scrolls horizontally
- Thread grid becomes single column
- Entry sidebar becomes dropdown
- Config sidebar in autobiography moves above content

**Tablet (768-1024px):**
- Thread grid stays 2 columns
- Most layouts similar to desktop

**Desktop (> 1024px):**
- All features as described above
- Maximum content width: 1200px (centered)

---

## Color Scheme

**Primary:** #007bff (blue)
**Secondary:** #6c757d (gray)
**Background:** #f5f5f5 (light gray)
**Card background:** #ffffff (white)
**Text:** #333333 (dark gray)
**Text secondary:** #666666 (medium gray)
**Border:** #dddddd (light gray)
**Error:** #dc3545 (red)
**Success:** #28a745 (green)

**Coverage Heatmap:**
- No coverage: #f5f5f5
- Minimal (1-20): #e3f2fd
- Some (21-40): #90caf9
- Good (41-60): #42a5f5
- Strong (61-80): #1e88e5
- Comprehensive (81-100): #1565c0

---

## Typography

**Headings:**
- H1: 32px, bold
- H2: 24px, bold
- H3: 20px, bold

**Body:**
- Regular: 16px
- Small: 14px
- Tiny: 12px

**Font:**
- System font stack: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", etc.

---

## Animations

**Smooth transitions:**
- Button hover: background color change (0.2s)
- Card hover: box-shadow change (0.2s)
- Modal appear: fade in (0.3s)
- Navigation: slide or fade (0.3s)

---

This document provides the visual reference needed to create screenshots, wireframes, or implement the UI. Each screen is fully specified with layout, elements, states, and styling.
