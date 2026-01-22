# API Documentation

## Overview

The LifeHarness API provides endpoints for managing user autobiographical documentation through an intelligent questioning system.

**Base URL**: `http://localhost:8000`
**API Prefix**: `/api`

## Authentication

All protected endpoints require a JWT Bearer token in the Authorization header:

```
Authorization: Bearer <token>
```

Tokens are obtained via the `/api/auth/login` or `/api/auth/register` endpoints.

## Endpoints

### Authentication

#### POST /api/auth/register

Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**:
- `400 Bad Request`: Email already registered

---

#### POST /api/auth/login

Login to an existing account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors**:
- `401 Unauthorized`: Incorrect email or password

---

#### GET /api/auth/me

Get current user information.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "created_at": "2024-01-19T12:00:00"
}
```

---

### User Profile

#### GET /api/profile

Get the current user's profile.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "year_of_birth": 1990,
  "country": "USA",
  "primary_language": "English",
  "relationship_status": "single",
  "has_children": false,
  "children_count": null,
  "children_age_brackets": [],
  "main_role": "engineer",
  "field_or_industry": "Software",
  "avoid_topics": ["health"],
  "intensity": "balanced",
  "life_snapshot": "A software engineer living in San Francisco",
  "created_at": "2024-01-19T12:00:00",
  "updated_at": "2024-01-19T12:00:00"
}
```

---

#### POST /api/profile

Create or update user profile.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "year_of_birth": 1990,
  "country": "USA",
  "primary_language": "English",
  "relationship_status": "married",
  "has_children": true,
  "children_count": 2,
  "children_age_brackets": ["5-10", "10-15"],
  "main_role": "engineer",
  "field_or_industry": "Software",
  "avoid_topics": ["health", "politics"],
  "intensity": "deep",
  "life_snapshot": "A software engineer with a family"
}
```

**Response** (200 OK):
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "year_of_birth": 1990,
  ...
}
```

---

### Threads

#### GET /api/threads

List all threads for the current user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
[
  {
    "id": "thread-uuid-1",
    "user_id": "user-uuid",
    "title": "My College Years",
    "root_prompt": "Tell me about your college experience",
    "persona": "default",
    "time_focus": ["20s"],
    "topic_focus": ["education", "friendships"],
    "questions_asked": 15,
    "questions_since_last_freeform": 3,
    "created_at": "2024-01-19T12:00:00",
    "last_activity_at": "2024-01-20T14:30:00"
  }
]
```

---

#### POST /api/threads

Create a new thread.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "title": "My Career Journey",
  "root_prompt": "Tell me about your career path and professional experiences",
  "persona": "professional",
  "time_focus": ["30s", "40s"],
  "topic_focus": ["work_career", "money_status"]
}
```

**Response** (200 OK):
```json
{
  "id": "thread-uuid",
  "user_id": "user-uuid",
  "title": "My Career Journey",
  "root_prompt": "Tell me about your career path...",
  "persona": "professional",
  "time_focus": ["30s", "40s"],
  "topic_focus": ["work_career", "money_status"],
  "questions_asked": 0,
  "questions_since_last_freeform": 0,
  "created_at": "2024-01-20T15:00:00",
  "last_activity_at": "2024-01-20T15:00:00"
}
```

---

#### GET /api/threads/{thread_id}

Get a specific thread by ID.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": "thread-uuid",
  "user_id": "user-uuid",
  "title": "My Career Journey",
  ...
}
```

**Errors**:
- `404 Not Found`: Thread not found

---

#### POST /api/threads/{thread_id}/step

Execute one Q&A step in a thread (ask question, get answer, generate entry).

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "user_answer": "I graduated from MIT in 2012 with a degree in Computer Science..."
}
```

**Response** (200 OK):
```json
{
  "question": {
    "id": "question-uuid",
    "text": "What was the most challenging course you took?",
    "type": "short_answer",
    ...
  },
  "life_entry": {
    "id": "entry-uuid",
    "content": "Graduated from MIT in 2012...",
    "time_bucket": "20s",
    "topic_buckets": ["education"],
    ...
  },
  "thread": {
    "id": "thread-uuid",
    "questions_asked": 1,
    ...
  }
}
```

---

### Life Entries

#### GET /api/entries

Get all life entries for the current user.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `time_bucket` (optional): Filter by time bucket (pre10, 10s, 20s, etc.)
- `topic_bucket` (optional): Filter by topic (family_of_origin, work_career, etc.)

**Response** (200 OK):
```json
[
  {
    "id": "entry-uuid",
    "user_id": "user-uuid",
    "content": "Graduated from MIT in 2012 with honors...",
    "time_bucket": "20s",
    "topic_buckets": ["education", "achievements"],
    "seal": "self",
    "seal_date": null,
    "created_at": "2024-01-20T15:30:00"
  }
]
```

---

#### GET /api/entries/coverage/grid

Get coverage heatmap data (time × topic matrix).

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "pre10": {
    "family_of_origin": 45,
    "friendships": 20,
    ...
  },
  "10s": {
    "family_of_origin": 60,
    "friendships": 80,
    ...
  },
  ...
}
```

---

### Autobiography

#### POST /api/autobiography/generate

Generate an autobiography based on life entries.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "audience": "trusted",
  "tone": "balanced",
  "time_start": "pre10",
  "time_end": "40s",
  "include_topics": ["family_of_origin", "work_career", "romantic_love"]
}
```

**Response** (200 OK):
```json
{
  "content": "# My Life Story\n\n## Early Years\n\nI was born in...",
  "word_count": 5432,
  "generated_at": "2024-01-20T16:00:00"
}
```

---

## Data Models

### Enums

#### IntensityLevel
- `light`: Lighter, less probing questions
- `balanced`: Mix of light and deep questions
- `deep`: More introspective, emotional questions

#### TimeBucket
- `pre10`: Before age 10
- `10s`: Ages 10-19
- `20s`: Ages 20-29
- `30s`: Ages 30-39
- `40s`: Ages 40-49
- `50plus`: Age 50+

#### TopicBucket
- `family_of_origin`: Birth family, childhood home
- `friendships`: Friends throughout life
- `romantic_love`: Dating, partnerships, marriage
- `children`: Having and raising children
- `work_career`: Professional life
- `money_status`: Financial situation
- `health_body`: Physical and mental health
- `creativity_play`: Hobbies, arts, recreation
- `beliefs_values`: Religion, philosophy, ethics
- `crises_turning_points`: Major life events

#### SealLevel
- `self`: Only you can see
- `trusted`: Trusted individuals
- `heirs`: Family/heirs after your passing
- `public`: Anyone can see

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, no rate limiting is enforced. This may change in production deployments.

---

## Interactive Documentation

For interactive API documentation, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
