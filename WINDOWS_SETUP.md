# Windows Setup Instructions

Since you're on Windows and Docker is giving path errors, here's the **easier way** to run EdgeLab:

## Quick Setup (No Docker Compose Needed)

### Step 1: Install Python packages

```bash
pip install flask flask-cors streamlit requests
```

### Step 2: Run the startup script

```bash
run_windows.bat
```

This will:
- Initialize the database
- Start the API in one window
- Start the UI in another window

### Step 3: Open your browser

Go to: http://localhost:8501

## Manual Start (if batch file doesn't work)

### Terminal 1 - API:
```bash
cd api
python database.py
python app.py
```

### Terminal 2 - UI:
```bash
cd ui
streamlit run streamlit_app.py
```

## Important Note About Code Execution

The code executor uses Docker to run submitted code safely. On Windows, you need:

1. **Docker Desktop must be running**
2. **WSL 2 backend enabled** (Docker Desktop → Settings → General → Use WSL 2)

If Docker isn't working, the code execution will fail but you can still:
- See the UI
- Test the API
- View the architecture

## Alternative: Use WSL 2

If Docker keeps having issues, run everything in WSL:

```bash
# In WSL terminal
cd /mnt/c/Users/Rizwan/Documents/EdgeLab/edgelab
docker compose up
```

## Troubleshooting

**"Module not found" errors:**
```bash
pip install -r api/requirements.txt
pip install -r ui/requirements.txt
```

**Port 5000 in use:**
- Close other applications using port 5000
- Or change the port in `api/app.py`: `app.run(host='0.0.0.0', port=5001)`

**Streamlit not found:**
```bash
pip install streamlit
```

## Testing Without Docker

If you can't get Docker working, you can still demonstrate the project by:

1. Showing the code and architecture
2. Explaining the security design
3. Walking through how it *would* work with Docker
4. Demonstrating the UI and API structure

The important part is understanding the system design, which you clearly do since the test passed!
