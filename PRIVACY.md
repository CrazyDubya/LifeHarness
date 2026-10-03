# LifeHarness Privacy & Data Controls

What the app stores, where it goes, and how you get it back. Written for the
person whose life story is in the database.

## What is stored

| Data | Where | Notes |
|---|---|---|
| Email + password hash (bcrypt) | `users` | Passwords are never stored in plain text |
| Onboarding profile: year of birth, country, language, relationship status, children info, role/industry, topics to avoid, intensity, free-text life snapshot | `user_profiles` | All optional |
| Conversation threads: titles, prompts, chosen persona | `threads` | |
| Questions asked and your answers (including free text) | `questions`, `answers` | |
| Freeform writings | `thread_freeforms` | |
| Life entries: headline, your raw text, distilled summary, tags, people, locations, emotional tone | `life_entries` | The autobiographical core |
| Coverage heatmap scores | `coverage_grid` | Derived, not personal content |

## Where your words travel

Your life-story content leaves your server in two places. Both are configured
by environment variables and both are third parties:

1. **Inference provider** (`VULTR_API_BASE_URL`, default Vultr Inference API)
   — generates interview questions and question candidates, distills your
   freeform writings into structured memories, and drafts autobiographies.
   It receives thread content, profile summaries, freeform texts, recent
   questions and answers, and distilled life entries.
2. **TypeSafe Jev** (`TYPESAFE_API_BASE_URL`) — ranks candidate questions each
   interview step. It receives a thread state summary: thread title and
   persona, profile facts (age, children status, topics you avoid), recent
   question/answer exchanges (truncated), candidate question texts, coverage
   gaps, and engagement signals.

There is currently no local-only mode and no opt-out short of not using those
features — that is a product decision still open (see the punchlist).

Error tracking via Sentry is optional and off unless `SENTRY_DSN` is set; it is
configured to never send personal data (`send_default_pii=False`).

## Your controls

- **Visibility & seals** — every life entry has a visibility level
  (`self` → `trusted` → `heirs` → `public`) and an optional seal (until a
  date, until an event, or until you release it manually). Autobiography
  generation only includes entries visible to the requested audience.
- **Export** — `GET /api/account/export` returns everything stored about you
  as JSON (password hashes excluded).
- **Delete** — `DELETE /api/account` with your password as confirmation
  permanently removes your account and every related row. Nothing is retained.

## Deployment notes

- Never run with the default `SECRET_KEY` — the app refuses to start in
  production with it. Set a unique `SECRET_KEY`.
- Set `POSTGRES_PASSWORD` in your environment; the compose file default is
  for local development only.
- Logs: failed LLM responses are never written to logs (content omitted).
