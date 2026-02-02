import subprocess
import json

def get_ai_feedback(code, assignment, test_results):
    """
    Generate code feedback using local Phi-3 model via ollama
    Only sends public info - never leaks hidden test details
    """
    try:
        # check if ollama is available
        check = subprocess.run(['which', 'ollama'], capture_output=True)
        if check.returncode != 0:
            return None  # ollama not installed, skip AI feedback
        
        # prepare context (safe info only)
        public_tests_info = []
        for result in test_results.get('test_results', []):
            if result['is_public']:
                public_tests_info.append({
                    'passed': result['passed'],
                    'description': result.get('description', ''),
                    'expected': result.get('expected'),
                    'actual': result.get('actual')
                })
        
        prompt = f"""You are a coding mentor reviewing a student's solution.

Assignment: {assignment['title']}
Language: {assignment['language']}

Student's code:
```{assignment['language']}
{code}
```

Test results:
- Passed: {test_results['passed_tests']}/{test_results['total_tests']} tests
- Score: {test_results['score']}%

Public test details:
{json.dumps(public_tests_info, indent=2)}

Provide brief, constructive feedback (2-3 sentences). Focus on:
1. What they did well
2. One specific improvement if tests failed
3. Code quality or efficiency tip

Keep it encouraging and practical. Don't mention hidden tests."""

        # call ollama (with short timeout to not delay results)
        result = subprocess.run(
            ['ollama', 'run', 'phi3:mini', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            feedback = result.stdout.strip()
            # clean up any model artifacts
            if feedback and len(feedback) > 10:
                return feedback
        
        return None
        
    except subprocess.TimeoutExpired:
        return None  # AI took too long, skip it
    except Exception as e:
        print(f"AI feedback error: {e}")
        return None

# fallback simple feedback if AI not available
def get_simple_feedback(test_results):
    """Basic feedback when AI is unavailable"""
    score = test_results['score']
    passed = test_results['passed_tests']
    total = test_results['total_tests']
    
    if score == 100:
        return "Great job! All tests passed. Your solution is correct."
    elif score >= 70:
        return f"Good effort! You passed {passed}/{total} tests. Review the failed test cases to see where your logic needs adjustment."
    elif score >= 40:
        return f"You're on the right track. {passed}/{total} tests passed. Double-check your edge cases and logic flow."
    else:
        return f"Keep working on it. Only {passed}/{total} tests passed. Review the problem requirements and test your code with the public examples first."

if __name__ == '__main__':
    # test if ollama is available
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("Ollama available")
            print(result.stdout.decode())
        else:
            print("Ollama not found")
    except:
        print("Ollama not installed")
