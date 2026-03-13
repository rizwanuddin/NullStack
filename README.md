# NullStack ⚡

A lightweight, self-hosted platform for running and testing Python, SQL, and Java code — with sandboxed execution and optional AI-powered feedback.

---

## ✨ Features

- 🧪 **Automated testing** — public + hidden test cases with instant pass/fail results
- 🐳 **Sandboxed execution** — all code runs in isolated Docker containers (no network, memory-limited, time-limited)
- 🤖 **AI code review** — optional constructive feedback via Phi-3 Mini running locally through Ollama
- 📝 **Multi-language support** — Python, SQL, and Java out of the box
- 🔒 **Hidden test protection** — hidden test cases are never exposed to the frontend
- ⚡ **One-command setup** — `docker compose up` and you're running

---

## 🚀 Quick Start

```bash
docker compose up
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🏗️ Architecture

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
       └──────► Code Executor (isolated Docker containers)
                        │
                        └──► Phi-3 AI via Ollama (optional)
```

| Layer | Tech |
|---|---|
| Frontend | Streamlit |
| Backend | Flask (Python 3.11) |
| Database | SQLite |
| Execution | Docker containers |
| AI Feedback | Phi-3 Mini via Ollama (optional) |
| Orchestration | Docker Compose |

---

## 📁 Project Structure

```
nullstack/
├── api/
│   ├── app.py              # Flask REST API
│   ├── database.py         # DB operations
│   ├── executor.py         # Sandboxed code runner
│   ├── ai_feedback.py      # Ollama integration
│   └── requirements.txt
├── ui/
│   ├── streamlit_app.py    # Web interface
│   └── requirements.txt
├── assignments/
│   ├── python_two_sum.json
│   ├── sql_top_salaries.json
│   └── java_palindrome.json
├── database/
│   └── nullstack.db          # Auto-created on first run
├── docker-compose.yml
├── Dockerfile.api
└── Dockerfile.ui
```

---

## 🔐 Security

All user-submitted code runs in ephemeral Docker containers with:

- `--network none` — no internet access
- `--memory 128m` — memory cap
- `--cpus 0.5` — CPU cap
- 5-second execution timeout
- Read-only code mounts
- No `eval()` on the host — ever

Hidden test cases are stored server-side only and never sent to the frontend or AI model.

---

## 🤖 AI Feedback (Optional)

NullStack can generate 2–3 sentence code reviews using a local LLM — no API keys, no data leaving your machine.

**Setup:**

```bash
# Install Ollama: https://ollama.ai
ollama pull phi3:mini
# Then restart the API — it auto-detects Ollama
```

**Alternative models:**
- `qwen2.5-coder:1.5b` — faster, lighter
- `deepseek-coder:1.3b` — good code understanding

---

## ➕ Adding Your Own Problems

Create a JSON file in `/assignments/`:

```json
{
  "id": "unique_id",
  "language": "python",
  "title": "Problem Title",
  "description": "Problem description...",
  "starter_code": "def solution():\n    pass",
  "entry_point": "solution",
  "public_tests": [
    { "input": [1, 2], "expected_output": 3, "description": "basic case" }
  ],
  "hidden_tests": [
    { "input": [5, 5], "expected_output": 10 }
  ],
  "limits": {
    "time_seconds": 5,
    "memory_mb": 128
  }
}
```

Then run:
```bash
cd api && python database.py
```

---

## 🛠️ Run Without Docker

**API:**
```bash
cd api
pip install -r requirements.txt
python database.py   # initialize DB
python app.py
```

**UI:**
```bash
cd ui
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## 📋 Sample Problems Included

| Problem | Language | Description |
|---|---|---|
| Two Sum | Python | Find two numbers that add up to a target |
| Top Salaries | SQL | Query top 3 salaries per department |
| Valid Palindrome | Java | Check if a string is a palindrome |

---

## ⚠️ Known Limitations

- SQL uses SQLite (not MySQL/PostgreSQL) — some syntax may differ
- Java recompiles on every submission — no caching yet
- No user authentication — open access by design for now
- Basic textarea editor — no syntax highlighting

---

## 📄 License

MIT © [Syed Rizwan Uddin](https://github.com/syedrizwanuddin) — 2026
