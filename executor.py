import subprocess
import json
import tempfile
import os
import time

def run_python_code(code, test_input, timeout=5):
    """
    Run Python code in isolated Docker container using stdin
    """
    try:
        # Create a wrapper script that includes the code
        full_script = f"""
{code}

import json
args = {repr(test_input)}
result = solution(*args)
print(json.dumps(result))
"""
        
        # Run docker with code passed via stdin
        cmd = [
            'docker', 'run', '--rm', '-i',
            '--network', 'none',
            '--memory', '128m',
            '--cpus', '0.5',
            'python:3.11-slim',
            'python', '-c', full_script
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 2
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            try:
                import json
                return json.loads(output)
            except:
                return eval(output)
        else:
            error_msg = result.stderr.strip()
            if 'timeout' in error_msg.lower():
                return {'error': 'Time limit exceeded'}
            error_lines = [line for line in error_msg.split('\n') if line.strip() and 'Error' in line]
            return {'error': error_lines[0][:200] if error_lines else error_msg[:200]}
            
    except subprocess.TimeoutExpired:
        return {'error': 'Execution timeout'}
    except Exception as e:
        return {'error': f'Runtime error: {str(e)}'}

def run_sql_query(query, setup_sql, timeout=5):
    """
    Run SQL query in SQLite without file mounting
    """
    try:
        # Combine setup and query
        full_sql = f"{setup_sql}\n{query};"
        
        # Run sqlite directly with SQL passed as command
        cmd = [
            'docker', 'run', '--rm', '-i',
            '--network', 'none',
            '--memory', '128m',
            'alpine:latest',
            'sh', '-c',
            f'apk add --no-cache sqlite > /dev/null 2>&1 && echo {repr(full_sql)} | sqlite3 -batch -separator "|" :memory:'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 3
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return {'error': result.stderr.strip()[:200]}
            
    except subprocess.TimeoutExpired:
        return {'error': 'Query timeout'}
    except Exception as e:
        return {'error': f'SQL error: {str(e)}'}

def run_java_code(code, test_input, timeout=5):
    """
    Compile and run Java code without file mounting
    """
    try:
        # Create main wrapper
        test_harness = f"""
{code}

public class Main {{
    public static void main(String[] args) {{
        String input = "{test_input[0] if test_input else ""}";
        boolean result = Solution.isPalindrome(input);
        System.out.println(result);
    }}
}}
"""
        
        # Escape quotes for shell
        escaped_code = test_harness.replace('"', '\\"').replace('$', '\\$')
        
        # Run compilation and execution in one go
        cmd = [
            'docker', 'run', '--rm', '-i',
            '--network', 'none',
            '--memory', '256m',
            'openjdk:11-slim',
            'sh', '-c',
            f'echo "{escaped_code}" > Main.java && javac Main.java && timeout {timeout} java Main'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 3
        )
        
        if result.returncode == 0:
            output = result.stdout.strip().lower()
            return output == 'true'
        else:
            error = result.stderr.strip()
            if 'error' in error.lower():
                lines = error.split('\n')
                for line in lines:
                    if 'error' in line.lower():
                        return {'error': line[:150]}
            return {'error': error[:200]}
            
    except subprocess.TimeoutExpired:
        return {'error': 'Execution timeout'}
    except Exception as e:
        return {'error': f'Java error: {str(e)}'}

def evaluate_submission(assignment, code):
    """
    Run all test cases for a submission
    Returns results with pass/fail for each test
    """
    language = assignment['language']
    public_tests = assignment.get('public_tests', [])
    hidden_tests = assignment.get('hidden_tests', [])
    
    all_tests = public_tests + hidden_tests
    results = []
    
    for idx, test in enumerate(all_tests):
        is_public = idx < len(public_tests)
        
        # run the code
        if language == 'python':
            actual_output = run_python_code(code, test['input'])
        elif language == 'sql':
            setup = test.get('setup_sql', assignment.get('setup_sql', ''))
            actual_output = run_sql_query(code, setup)
        elif language == 'java':
            actual_output = run_java_code(code, test['input'])
        else:
            actual_output = {'error': 'Unsupported language'}
        
        # check if it passed
        expected = test['expected_output']
        
        if isinstance(actual_output, dict) and 'error' in actual_output:
            passed = False
        else:
            passed = (actual_output == expected)
        
        # build result object
        test_result = {
            'test_num': idx + 1,
            'passed': passed,
            'is_public': is_public
        }
        
        # only include details for public tests
        if is_public:
            test_result['description'] = test.get('description', f'Test {idx + 1}')
            test_result['expected'] = expected
            test_result['actual'] = actual_output
        
        results.append(test_result)
    
    # calculate stats
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    score = round((passed / total * 100), 1) if total > 0 else 0
    
    return {
        'total_tests': total,
        'passed_tests': passed,
        'public_tests': len(public_tests),
        'hidden_tests': len(hidden_tests),
        'test_results': results,
        'score': score,
        'status': 'passed' if passed == total else 'failed'
    }

# quick test if run directly
if __name__ == '__main__':
    test_code = '''
def solution(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
'''
    test_input = [[2, 7, 11, 15], 9]
    result = run_python_code(test_code, test_input)
    print(f"Test result: {result}")