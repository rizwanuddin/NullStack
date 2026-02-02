from flask import Flask, request, jsonify
from flask_cors import CORS
import database as db
import executor
import ai_feedback
import threading

app = Flask(__name__)
CORS(app)  # allow requests from streamlit

# initialize database on startup
db.init_db()
db.load_assignments_from_files()

@app.route('/')
def home():
    """API health check"""
    return jsonify({
        'status': 'running',
        'message': 'EdgeLab API v0.1',
        'endpoints': {
            'GET /assignments': 'List all assignments',
            'GET /assignments/<id>': 'Get assignment details',
            'POST /submit': 'Submit code for evaluation',
            'GET /results/<id>': 'Get submission results'
        }
    })

@app.route('/assignments', methods=['GET'])
def list_assignments():
    """Get all available assignments"""
    try:
        assignments = db.get_all_assignments()
        return jsonify({
            'success': True,
            'count': len(assignments),
            'assignments': assignments
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/assignments/<assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """Get specific assignment (without hidden tests)"""
    try:
        assignment = db.get_assignment_public(assignment_id)
        
        if not assignment:
            return jsonify({
                'success': False,
                'error': 'Assignment not found'
            }), 404
        
        return jsonify({
            'success': True,
            'assignment': assignment
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/submit', methods=['POST'])
def submit_code():
    """Submit code for evaluation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        assignment_id = data.get('assignment_id')
        code = data.get('code')
        
        if not assignment_id or not code:
            return jsonify({
                'success': False,
                'error': 'Missing assignment_id or code'
            }), 400
        
        # check assignment exists
        assignment = db.get_assignment(assignment_id)
        if not assignment:
            return jsonify({
                'success': False,
                'error': 'Invalid assignment_id'
            }), 404
        
        # create submission record
        submission_id = db.create_submission(assignment_id, code)
        
        # run evaluation in background thread
        def run_eval():
            try:
                results = executor.evaluate_submission(assignment, code)
                
                # try to get AI feedback
                feedback = ai_feedback.get_ai_feedback(code, assignment, results)
                if not feedback:
                    feedback = ai_feedback.get_simple_feedback(results)
                
                # update submission with results
                db.update_submission_results(
                    submission_id,
                    results['status'],
                    results,
                    feedback
                )
            except Exception as e:
                print(f"Evaluation error: {e}")
                db.update_submission_results(
                    submission_id,
                    'error',
                    {'error': str(e)},
                    None
                )
        
        thread = threading.Thread(target=run_eval)
        thread.start()
        
        return jsonify({
            'success': True,
            'submission_id': submission_id,
            'message': 'Code submitted successfully. Evaluation in progress...'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/results/<int:submission_id>', methods=['GET'])
def get_results(submission_id):
    """Get submission results"""
    try:
        submission = db.get_submission(submission_id)
        
        if not submission:
            return jsonify({
                'success': False,
                'error': 'Submission not found'
            }), 404
        
        return jsonify({
            'success': True,
            'submission': submission
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/recent', methods=['GET'])
def recent_submissions():
    """Get recent submissions for debugging"""
    try:
        limit = request.args.get('limit', 10, type=int)
        submissions = db.get_recent_submissions(limit)
        
        return jsonify({
            'success': True,
            'submissions': submissions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting EdgeLab API...")
    print("Database initialized")
    app.run(host='0.0.0.0', port=5000, debug=True)
