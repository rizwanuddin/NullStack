import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'edgelab.db')
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize database tables"""
    conn = get_conn()
    c = conn.cursor()
    
    # assignments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id TEXT PRIMARY KEY,
            language TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            data TEXT NOT NULL
        )
    ''')
    
    # submissions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id TEXT NOT NULL,
            code TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            results TEXT,
            ai_feedback TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (assignment_id) REFERENCES assignments(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def load_assignments_from_files():
    """Load all assignment JSON files into the database"""
    assignments_dir = os.path.join(os.path.dirname(__file__), '..', 'assignments')
    
    if not os.path.exists(assignments_dir):
        print(f"Warning: assignments directory not found at {assignments_dir}")
        return
    
    conn = get_conn()
    c = conn.cursor()
    loaded = 0
    
    for filename in os.listdir(assignments_dir):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(assignments_dir, filename)
        try:
            with open(filepath, 'r') as f:
                assignment = json.load(f)
                
            c.execute('''
                INSERT OR REPLACE INTO assignments (id, language, title, description, data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                assignment['id'],
                assignment['language'],
                assignment['title'],
                assignment['description'],
                json.dumps(assignment)
            ))
            loaded += 1
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    
    conn.commit()
    conn.close()
    print(f"Loaded {loaded} assignments into database")

def get_all_assignments():
    """Get list of all assignments (without hidden tests)"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, language, title, description FROM assignments')
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'language': row[1],
            'title': row[2],
            'description': row[3]
        }
        for row in rows
    ]

def get_assignment(assignment_id):
    """Get full assignment data including tests"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT data FROM assignments WHERE id = ?', (assignment_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None

def get_assignment_public(assignment_id):
    """Get assignment WITHOUT hidden tests (for users)"""
    assignment = get_assignment(assignment_id)
    if not assignment:
        return None
    
    # remove hidden tests before sending to user
    public_assignment = assignment.copy()
    if 'hidden_tests' in public_assignment:
        del public_assignment['hidden_tests']
    
    return public_assignment

def create_submission(assignment_id, code):
    """Create a new submission record"""
    conn = get_conn()
    c = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    c.execute('''
        INSERT INTO submissions (assignment_id, code, status, created_at)
        VALUES (?, ?, ?, ?)
    ''', (assignment_id, code, 'pending', timestamp))
    
    submission_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return submission_id

def update_submission_results(submission_id, status, results, ai_feedback=None):
    """Update submission with test results"""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('''
        UPDATE submissions
        SET status = ?, results = ?, ai_feedback = ?
        WHERE id = ?
    ''', (status, json.dumps(results), ai_feedback, submission_id))
    
    conn.commit()
    conn.close()

def get_submission(submission_id):
    """Get submission by ID"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        'id': row[0],
        'assignment_id': row[1],
        'code': row[2],
        'status': row[3],
        'results': json.loads(row[4]) if row[4] else None,
        'ai_feedback': row[5],
        'created_at': row[6]
    }

def get_recent_submissions(limit=10):
    """Get most recent submissions"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT id, assignment_id, status, created_at 
        FROM submissions 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'assignment_id': row[1],
            'status': row[2],
            'created_at': row[3]
        }
        for row in rows
    ]

if __name__ == '__main__':
    # setup script
    init_db()
    load_assignments_from_files()
