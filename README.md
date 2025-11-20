# Life Harness

**Autobiography one question at a time**

A system that helps you continuously document your life through infinite, guided questioning, periodic freeform reflections, and then generates audience-appropriate autobiographical outputs.

## Features

- **Infinite Question Loops**: Answer questions organized into themed "threads" that continue as long as you want
- **Adaptive Intelligence**: Questions adapt to your age, life stage, and avoid topics you don't want to discuss
- **Coverage Tracking**: Visual heatmap shows which areas of your life (time × topic) have been explored
- **Freeform Prompts**: Every 5-10 questions, you'll get a chance to write freely about what matters
- **Smart Distillation**: AI automatically organizes your answers into structured life entries
- **Seal & Privacy**: Control who can see each entry and when (self, trusted, heirs, public)
- **Autobiography Generation**: Create comprehensive autobiographies tailored to different audiences

## Architecture

### Backend
- **FastAPI** (Python) - RESTful API
- **PostgreSQL** (or SQLite for dev) - Database
- **SQLAlchemy** - ORM
- **Vultr Inference API** - LLM integration (OpenAI-compatible)

### Frontend
- **Vite** - Build tool
- **React** - UI framework
- **TypeScript** - Type safety
- **React Router** - Navigation

## Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Python 3.11+, Node.js 18+, PostgreSQL

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/your-username/LifeHarness.git
cd LifeHarness
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your Vultr API key
```

3. **Start the services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the backend**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.example .env
```

4. **Run the frontend**
```bash
npm run dev
```

## Configuration

### Vultr API Key

This system uses Vultr Inference API for LLM capabilities. To get your API key:

1. Sign up at [Vultr](https://www.vultr.com/)
2. Navigate to the Inference API section
3. Generate an API key
4. Add it to your `.env` file:
```
VULTR_API_KEY=your-api-key-here
```

### Database

**Development**: SQLite (default)
```
DATABASE_URL=sqlite:///./lifeharness.db
```

**Production**: PostgreSQL (recommended)
```
DATABASE_URL=postgresql://user:password@localhost:5432/lifeharness
```

## Documentation

Comprehensive guides are available to help you get started and use the system effectively:

- **[Onboarding Guide](ONBOARDING_GUIDE.md)** - Complete walkthrough for new users, from installation to generating your first autobiography
- **[Testing Guide](TESTING_GUIDE.md)** - Instructions for testing the system, including manual tests, API testing, and bug reporting
- **[Screen Flows](SCREEN_FLOWS.md)** - Detailed UI specifications and screen descriptions for each page

## Usage Guide

### 1. Registration & Onboarding

- Create an account with email/password
- Complete the onboarding wizard:
  - Basic information (age, country, language)
  - Relationship status and family details
  - Work and role
  - Topics to avoid
  - Intensity preference (light, balanced, deep)
  - Life snapshot (5-10 line summary)

### 2. Create a Thread

Threads are themed question sessions. Examples:
- "My College Years"
- "Career Journey"
- "Family Relationships"
- "Pivotal Moments"

Each thread has:
- **Title**: What this thread is about
- **Root Prompt**: Detailed description
- **Optional Focus**: Specific time periods or topics

### 3. Answer Questions

The system will:
- Present one question at a time (multiple choice or short answer)
- Inject freeform prompts every 5-10 questions
- Adapt based on your profile (won't ask about kids if you don't have any)
- Focus on under-explored areas shown in the coverage heatmap

### 4. Manage Entries

Your answers are distilled into **Life Entries**:
- View all entries organized by time period
- Set visibility levels (self, trusted, heirs, public)
- Add seals (release on certain dates or events)
- Filter by time bucket or topic

### 5. Generate Autobiography

Create polished autobiographies:
- Choose audience (self, trusted, heirs, public)
- Select tone (light, balanced, deep)
- Set scope (full life or specific time range)
- Download as Markdown

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

**Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login

**Profile**
- `GET /api/profile` - Get user profile
- `POST /api/profile` - Create/update profile

**Threads**
- `GET /api/threads` - List all threads
- `POST /api/threads` - Create new thread
- `POST /api/threads/{id}/step` - Execute one Q&A step

**Entries**
- `GET /api/entries` - List life entries
- `PATCH /api/entries/{id}/seal` - Update entry seal
- `GET /api/entries/coverage/grid` - Get coverage heatmap data

**Autobiography**
- `POST /api/autobiography/generate` - Generate autobiography

## Data Model

### Core Entities

**Users & Profiles**
- User account (email, password)
- Profile (demographics, preferences, life snapshot)

**Threads**
- Themed question sessions
- Track questions asked and last activity

**Questions & Answers**
- Multiple choice or short answer
- Tagged with time/topic focus
- Age/children constraints

**Life Entries**
- Distilled memories from answers
- Time bucket (pre10, 10s, 20s, etc.)
- Topic buckets (family, work, love, etc.)
- Visibility and seal settings

**Coverage Grid**
- Tracks exploration of time × topic combinations
- Scores from 0-100

## Development

### Project Structure

```
LifeHarness/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   ├── types/        # TypeScript types
│   │   ├── hooks/        # React hooks
│   │   └── App.tsx       # Main app
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

### Code Style

**Backend**: Follow PEP 8
```bash
black app/
flake8 app/
```

**Frontend**: ESLint + Prettier
```bash
npm run lint
```

## Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure proper CORS origins
- [ ] Use HTTPS
- [ ] Set up backup strategy for database
- [ ] Configure rate limiting
- [ ] Monitor LLM API usage and costs

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- CORS configured for allowed origins
- SQL injection protection via SQLAlchemy
- Input validation with Pydantic
- Seal system for privacy control

## Roadmap

- [ ] Email verification
- [ ] Password reset
- [ ] Social authentication (Google, etc.)
- [ ] Mobile app
- [ ] Voice input for answers
- [ ] Multi-language support
- [ ] Export to PDF, EPUB
- [ ] Collaborative features (family trees)
- [ ] Media attachments (photos, videos)
- [ ] Advanced analytics

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Issues: https://github.com/CrazyDubya/LifeHarness/issues
- Documentation: See this README

## Acknowledgments

- Built with Vultr Inference API
- Inspired by the human need to preserve and share our stories
- Thanks to all contributors and users

---

**Remember**: Your life story matters. Start documenting it today, one question at a time
