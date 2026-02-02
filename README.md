# EdgeLab v0.1

A lightweight coding assessment platform for practicing Python, SQL, and Java problems with automated testing and AI-powered feedback.

## Quick Start

```bash
docker compose up
```

Then open http://localhost:8501 in your browser.

## What This Is

EdgeLab is a coding practice environment where you can:
- Browse programming assignments in Python, SQL, and Java
- Write solutions in a web interface
- Get instant feedback from automated tests
- See AI-generated code review (optional, requires Ollama)

Think of it like a mini LeetCode for learning and assessment.

## Architecture

```
┌─────────────┐
│  Streamlit  │  (Port 8501) - Web UI
│     UI      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Flask     │  (Port 5000) - REST API
│    API      │
└──────┬──────┘
       │
       ├──────► SQLite Database (assignments, submissions, results)
       │
       └──────► Code Executor (runs user code in isolated Docker containers)
                        │
                        └──► Phi-3 AI (optional feedback)
```

## Components

### API (`/api`)
Flask-based REST API that handles:
- Assignment management
- Code submissions
- Test execution coordination
- Results storage

### UI (`/ui`)
Streamlit web interface for:
- Browsing problems
- Writing and submitting code
- Viewing test results

### Executor (`/api/executor.py`)
Sandboxed code execution engine:
- Runs Python, SQL, Java in isolated Docker containers
- Enforces time and memory limits
- Blocks network access
- Compares output against test cases

### Database (`/database`)
SQLite database storing:
- Assignment definitions
- Code submissions
- Test results
- AI feedback

## How to Use

### 1. Start the System

```bash
docker compose up
```

Wait for both services to start:
- API: http://localhost:5000
- UI: http://localhost:8501

### 2. Browse Problems

Open http://localhost:8501 and you'll see three sample problems:
- Python: Two Sum
- SQL: Top Salaries by Department  
- Java: Valid Palindrome

### 3. Submit a Solution

1. Select a problem
2. Write your code
3. Click "Run Tests"
4. See results instantly

### 4. View Results

Results include:
- Pass/fail for each public test
- Score percentage
- Hidden test summary (pass count only)
- AI feedback (if enabled)

## Sample Problems

### Python: Two Sum
Find two numbers in an array that add up to a target value.

### SQL: Top Salaries
Query the top 3 highest salaries in each department.

### Java: Palindrome Checker
Determine if a string is a valid palindrome.

## Adding New Assignments

Create a JSON file in `/assignments`:

```json
{
  "id": "unique_id",
  "language": "python",
  "title": "Problem Title",
  "description": "Problem description here...",
  "starter_code": "def solution():\n    pass",
  "entry_point": "solution",
  "public_tests": [
    {
      "input": [1, 2],
      "expected_output": 3,
      "description": "test description"
    }
  ],
  "hidden_tests": [
    {
      "input": [5, 5],
      "expected_output": 10
    }
  ],
  "limits": {
    "time_seconds": 5,
    "memory_mb": 128
  }
}
```

Then restart the API or run:
```bash
cd api
python database.py
```

## Security Features

### Code Isolation
All user code runs in ephemeral Docker containers with:
- No network access (`--network none`)
- Memory limits (`--memory 128m`)
- CPU limits (`--cpus 0.5`)
- Execution timeouts (5 seconds default)
- Read-only code mounts

### Hidden Test Protection
Hidden test cases are:
- Never sent to the frontend
- Only stored server-side in database
- Not included in API responses
- Results show pass/fail count only, no details

### Input Sanitization
- Code is never `eval()`'d on the host
- All execution happens in containers
- Temporary files are cleaned up
- No persistent storage in execution containers

## AI Feedback (Optional)

EdgeLab can provide code review using local AI models.

### Setup with Ollama

1. Install Ollama: https://ollama.ai
2. Pull Phi-3: `ollama pull phi3:mini`
3. Restart the API

The system will automatically detect Ollama and use it for feedback.

### How It Works

- Only public test info is sent to the AI (never hidden tests)
- Generates 2-3 sentence constructive feedback
- Falls back to simple feedback if AI unavailable
- 30 second timeout to avoid delays

### Model Choice

I chose Phi-3 Mini (3.8B) because:
- Small enough to run on laptops
- Strong code reasoning abilities
- Fast inference (<5 seconds)
- Runs locally (no API costs or data leakage)

Alternative models that work:
- `qwen2.5-coder:1.5b` (faster, less sophisticated)
- `deepseek-coder:1.3b` (good for code)

## Known Limitations

### 1. SQL Support
Currently uses SQLite in Alpine containers. Real production systems would use PostgreSQL or MySQL. Some SQL syntax may differ from assignment expectations.

### 2. Java Compilation
Java submissions compile every time. Could be optimized with caching.

### 3. Concurrency
Uses threading for background execution. Would need a proper job queue (Celery, RQ) for production scale.

### 4. Error Messages
Some compiler/runtime errors could be more user-friendly. Currently shows raw output.

### 5. Code Editor
Using a textarea. A real IDE-like editor (Monaco, CodeMirror) would be better.

### 6. No Authentication
Anyone can submit code. Production needs user accounts and auth.

## What I'd Improve Next

Given more time, I would:

1. **Better code editor**: Monaco Editor with syntax highlighting and autocomplete
2. **Test case management**: UI for creating assignments without editing JSON
3. **User accounts**: Login system with submission history
4. **Leaderboard**: Track fastest/cleanest solutions
5. **More languages**: Support for JavaScript, Rust, Go
6. **Job queue**: Replace threading with Celery/Redis
7. **Real database**: Switch to PostgreSQL for production
8. **Better SQL support**: Actual MySQL/PostgreSQL containers
9. **Code playback**: Show execution step-by-step
10. **Plagiarism detection**: Compare solutions for similarity

## Development

### Run Without Docker

API:
```bash
cd api
pip install -r requirements.txt
python database.py  # initialize DB
python app.py
```

UI:
```bash
cd ui
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Testing

Test the executor directly:
```bash
cd api
python executor.py
```

Test database:
```bash
cd api
python database.py
```

## Tech Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: Streamlit
- **Database**: SQLite
- **Execution**: Docker containers
- **AI**: Phi-3 via Ollama (optional)
- **Orchestration**: Docker Compose

## File Structure

```
edgelab/
├── api/
│   ├── app.py              # Flask API
│   ├── database.py         # Database operations
│   ├── executor.py         # Code execution engine
│   ├── ai_feedback.py      # AI integration
│   └── requirements.txt
├── ui/
│   ├── streamlit_app.py    # Streamlit interface
│   └── requirements.txt
├── assignments/
│   ├── python_two_sum.json
│   ├── sql_top_salaries.json
│   └── java_palindrome.json
├── database/
│   └── edgelab.db          # Created on first run
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.ui
└── README.md
```

## License

Built as a take-home assignment for LunarTech.

## Author

Submitted for LunarTech AI/Software Engineering position.
