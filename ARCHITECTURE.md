# EdgeLab System Architecture

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                            USER                                  │
│                    (Browser/Client)                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP Requests
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (Port 8501)                      │
│  ┌────────────┬──────────────┬────────────────┐                │
│  │  Browse    │   Submit     │     View       │                 │
│  │  Problems  │   Solution   │    Results     │                 │
│  └────────────┴──────────────┴────────────────┘                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ REST API Calls
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK API (Port 5000)                         │
│                                                                   │
│  Endpoints:                                                       │
│  - GET  /assignments        (list problems)                      │
│  - GET  /assignments/:id    (get problem details)                │
│  - POST /submit             (submit code)                        │
│  - GET  /results/:id        (get submission results)             │
│                                                                   │
└─────┬──────────────────────┬──────────────────────┬─────────────┘
      │                      │                      │
      │                      │                      │
      ▼                      ▼                      ▼
┌──────────────┐  ┌──────────────────┐  ┌─────────────────────┐
│   DATABASE   │  │   CODE EXECUTOR  │  │   AI FEEDBACK       │
│   (SQLite)   │  │                  │  │   (Phi-3/Ollama)    │
│              │  │  ┌────────────┐  │  │                     │
│ - assignments│  │  │  Docker    │  │  │  - Analyze code     │
│ - submissions│  │  │ Containers │  │  │  - Generate tips    │
│ - results    │  │  │            │  │  │  - Only public info │
│              │  │  │ Python:3.11│  │  │                     │
│              │  │  │ OpenJDK:11 │  │  │  (Optional)         │
│              │  │  │ Alpine+SQL │  │  │                     │
│              │  │  └────────────┘  │  │                     │
└──────────────┘  └──────────────────┘  └─────────────────────┘
```

## Execution Flow

1. User browses assignments via UI
2. UI requests assignment list from API
3. API queries database, strips hidden tests, returns public data
4. User writes code and clicks "Submit"
5. UI sends code to API /submit endpoint
6. API:
   - Saves submission to database (status: pending)
   - Spawns background thread for execution
   - Returns submission ID immediately
7. Background thread:
   - Retrieves full assignment (with hidden tests) from DB
   - Calls executor with code and tests
   - Executor spawns isolated Docker container
   - Runs code with timeouts and resource limits
   - Compares output to expected results
   - Returns test results
   - (Optional) Calls AI for feedback
   - Updates submission in DB with results
8. UI polls /results endpoint
9. API returns results (hiding hidden test details)
10. UI displays score, test breakdown, and feedback

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Network Isolation                                  │
│  - All containers run with --network none                    │
│  - No outbound connections possible                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: Resource Limits                                    │
│  - Memory cap: 128-256 MB                                    │
│  - CPU limit: 0.5 cores                                      │
│  - Execution timeout: 5 seconds                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: Filesystem Isolation                               │
│  - Code mounted read-only                                    │
│  - Temp files only                                           │
│  - No persistent storage                                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: Information Hiding                                 │
│  - Hidden tests never sent to frontend                       │
│  - API strips sensitive data before responses                │
│  - Results show pass/fail count only for hidden tests        │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow: Submission Lifecycle

```
[User Code] 
    │
    ▼
[API: Create Submission]
    │ (Save to DB with status='pending')
    ▼
[Background Thread Started]
    │
    ▼
[Executor: Get Full Assignment]
    │ (Including hidden tests)
    ▼
[For Each Test Case:]
    │
    ├─► [Spawn Docker Container]
    │       │
    │       ├─► [Copy code to container]
    │       ├─► [Set resource limits]
    │       ├─► [Execute with timeout]
    │       ├─► [Capture output]
    │       └─► [Destroy container]
    │
    └─► [Compare output vs expected]
            │
            ▼
        [Record pass/fail]

[All Tests Complete]
    │
    ▼
[Calculate Score]
    │
    ▼
[Optional: Get AI Feedback]
    │
    ▼
[Update DB: status='passed/failed', results, feedback]
    │
    ▼
[User polls /results]
    │
    ▼
[API: Return sanitized results]
    │ (No hidden test details)
    ▼
[UI: Display results]
```

## Component Responsibilities

### Streamlit UI
- Present problems in readable format
- Provide code editor interface
- Handle user interactions
- Poll for results
- Display test outcomes

### Flask API
- Route HTTP requests
- Validate inputs
- Coordinate components
- Manage async execution
- Enforce security policies

### Database Module
- Store persistent data
- Provide data access layer
- Handle migrations
- Load assignments from files

### Code Executor
- Spawn isolated environments
- Enforce resource limits
- Run code safely
- Compare outputs
- Handle errors gracefully

### AI Feedback
- Analyze code quality
- Generate constructive tips
- Operate on public data only
- Fallback to simple feedback

## Technology Choices

| Component  | Technology       | Why?                              |
|------------|------------------|-----------------------------------|
| Frontend   | Streamlit        | Fast to build, looks good         |
| API        | Flask            | Simple, Python-native             |
| Database   | SQLite           | No setup, sufficient for demo     |
| Containers | Docker           | Industry standard, secure         |
| AI         | Phi-3 + Ollama   | Local, free, good code reasoning  |
| Language   | Python 3.11      | Familiar, good libraries          |

## Deployment

```
$ docker compose up

Docker Compose orchestrates:
  - Builds API image (Flask + executor)
  - Builds UI image (Streamlit)
  - Creates network bridge
  - Mounts volumes (database, assignments)
  - Exposes ports (5000, 8501)
  - Starts services in dependency order
```

## File System Layout

```
/home/claude/edgelab/
│
├── api/                      # Backend service
│   ├── app.py               # Flask routes
│   ├── database.py          # DB operations
│   ├── executor.py          # Code runner
│   ├── ai_feedback.py       # AI integration
│   └── requirements.txt
│
├── ui/                       # Frontend service
│   ├── streamlit_app.py     # UI logic
│   └── requirements.txt
│
├── assignments/              # Problem definitions
│   ├── python_two_sum.json
│   ├── sql_top_salaries.json
│   └── java_palindrome.json
│
├── database/                 # Persistent storage
│   └── edgelab.db           # SQLite file
│
├── docker-compose.yml        # Orchestration
├── Dockerfile.api           # API image build
├── Dockerfile.ui            # UI image build
└── README.md                # Documentation
```
