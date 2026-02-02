# Quick Start Guide

Get EdgeLab running in under 5 minutes.

## Prerequisites

- Docker Desktop installed and running
- 4GB free RAM
- 2GB free disk space

## Setup

### 1. Extract the project

```bash
cd edgelab
```

### 2. Verify everything is ready

```bash
python3 test_setup.py
```

This checks:
- Docker is installed
- All files are present
- Assignment files are valid

### 3. Start the system

```bash
docker compose up
```

First run will take 2-3 minutes to:
- Build Docker images
- Pull base images (Python, Java, Alpine)
- Initialize database
- Start services

### 4. Open the UI

Once you see:
```
ui-1   | You can now view your Streamlit app in your browser.
api-1  | * Running on http://0.0.0.0:5000
```

Open: http://localhost:8501

## Testing It Out

### Try the Python problem:

1. Click "Browse Problems"
2. Select "Two Sum"
3. Write this solution:

```python
def solution(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
```

4. Click "▶️ Run Tests"
5. Wait 3-5 seconds
6. See results!

### Try the SQL problem:

```sql
SELECT department_id, salary
FROM employees e1
WHERE (
    SELECT COUNT(DISTINCT salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
    AND e2.salary >= e1.salary
) <= 3
ORDER BY department_id, salary DESC
```

### Try the Java problem:

```java
public class Solution {
    public static boolean isPalindrome(String s) {
        s = s.replaceAll("[^a-zA-Z0-9]", "").toLowerCase();
        int left = 0, right = s.length() - 1;
        while (left < right) {
            if (s.charAt(left) != s.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }
}
```

## Stopping the System

Press `Ctrl+C` in the terminal, then:

```bash
docker compose down
```

## Troubleshooting

### "Port 5000 already in use"

Another service is using port 5000. Either:
- Stop that service, or
- Change the port in docker-compose.yml

### "Cannot connect to Docker daemon"

Docker Desktop isn't running. Start it and try again.

### "UI shows API not running"

The API takes ~10 seconds to start. Wait a bit, then refresh.

### Tests are very slow

First run downloads Docker images. Subsequent runs are much faster.

### Want to reset everything?

```bash
docker compose down -v
rm database/edgelab.db
docker compose up
```

## Optional: AI Feedback

To enable AI-powered code feedback:

1. Install Ollama: https://ollama.ai
2. Pull Phi-3:
   ```bash
   ollama pull phi3:mini
   ```
3. Restart EdgeLab

The system will automatically detect Ollama and use it.

## Next Steps

- Read README.md for full documentation
- Check ARCHITECTURE.md to understand the design
- Look at assignment JSON files to see the format
- Try creating your own assignment!

## Getting Help

If something doesn't work:

1. Check `docker compose logs` for errors
2. Run `python3 test_setup.py` to verify setup
3. Make sure Docker has enough resources (Settings → Resources)

## Tips

- Use Chrome or Firefox (best Streamlit support)
- Keep terminal open to see logs
- First execution per language is slower (image pull)
- Hidden tests never show details - that's intentional!
