import streamlit as st
import requests
import time
import json
import os

API_URL = os.getenv("API_URL", "http://localhost:5000")

st.set_page_config(
    page_title="EdgeLab",
    page_icon="🚀",
    layout="wide"
)

def check_api():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_assignments():
    """Fetch all assignments from API"""
    try:
        response = requests.get(f"{API_URL}/assignments")
        if response.status_code == 200:
            data = response.json()
            return data.get('assignments', [])
    except Exception as e:
        st.error(f"Failed to load assignments: {e}")
    return []

def get_assignment_details(assignment_id):
    """Get full details for an assignment"""
    try:
        response = requests.get(f"{API_URL}/assignments/{assignment_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get('assignment')
    except Exception as e:
        st.error(f"Failed to load assignment: {e}")
    return None

def submit_code(assignment_id, code):
    """Submit code to API"""
    try:
        response = requests.post(
            f"{API_URL}/submit",
            json={'assignment_id': assignment_id, 'code': code}
        )
        if response.status_code == 201:
            data = response.json()
            return data.get('submission_id')
    except Exception as e:
        st.error(f"Submission failed: {e}")
    return None

def get_results(submission_id):
    """Get results for a submission"""
    try:
        response = requests.get(f"{API_URL}/results/{submission_id}")
        if response.status_code == 200:
            data = response.json()
            return data.get('submission')
    except:
        pass
    return None

# main UI
st.title("🚀 EdgeLab")
st.markdown("*Practice coding problems with automated testing*")

# check API connection
if not check_api():
    st.error("⚠️ API server not running. Please start the API first.")
    st.code("cd api && python app.py", language="bash")
    st.stop()

# sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Browse Problems", "Submit Solution", "View Results"])

if page == "Browse Problems":
    st.header("Available Problems")
    
    assignments = get_assignments()
    
    if not assignments:
        st.warning("No assignments found. Make sure the database is initialized.")
    else:
        # filter by language
        languages = list(set(a['language'] for a in assignments))
        selected_lang = st.selectbox("Filter by language", ["All"] + languages)
        
        if selected_lang != "All":
            assignments = [a for a in assignments if a['language'] == selected_lang]
        
        # display assignments
        for assignment in assignments:
            with st.expander(f"**{assignment['title']}** ({assignment['language'].upper()})"):
                st.markdown(assignment['description'])
                
                if st.button(f"Start {assignment['id']}", key=assignment['id']):
                    st.session_state.selected_assignment = assignment['id']
                    st.session_state.page = "Submit Solution"
                    st.rerun()

elif page == "Submit Solution":
    st.header("Submit Your Solution")
    
    # assignment selection
    assignments = get_assignments()
    assignment_options = {f"{a['title']} ({a['language']})": a['id'] for a in assignments}
    
    selected = st.selectbox(
        "Choose a problem",
        options=list(assignment_options.keys())
    )
    
    if selected:
        assignment_id = assignment_options[selected]
        assignment = get_assignment_details(assignment_id)
        
        if assignment:
            # show problem details
            st.subheader(assignment['title'])
            st.markdown(assignment['description'])
            
            # show public test cases
            if assignment.get('public_tests'):
                with st.expander("📋 Public Test Cases"):
                    for i, test in enumerate(assignment['public_tests'], 1):
                        st.text(f"Test {i}: {test.get('description', '')}")
                        st.code(f"Input: {test['input']}\nExpected: {test['expected_output']}")
            
            # code editor
            st.subheader("Your Code")
            starter_code = assignment.get('starter_code', '# Write your code here')
            
            code = st.text_area(
                "Code Editor",
                value=starter_code,
                height=400,
                key="code_editor"
            )
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if st.button("▶️ Run Tests", type="primary"):
                    if code.strip() == starter_code.strip():
                        st.warning("Please write your solution first!")
                    else:
                        with st.spinner("Submitting and evaluating..."):
                            submission_id = submit_code(assignment_id, code)
                            
                            if submission_id:
                                st.session_state.last_submission = submission_id
                                
                                # wait for results (poll for up to 30 seconds)
                                for _ in range(30):
                                    time.sleep(1)
                                    results = get_results(submission_id)
                                    
                                    if results and results['status'] != 'pending':
                                        st.session_state.results = results
                                        st.rerun()
                                        break
                                
                                if not results or results['status'] == 'pending':
                                    st.info("Evaluation taking longer than expected. Check 'View Results' tab.")
            
            # show results if available
            if hasattr(st.session_state, 'results'):
                results = st.session_state.results
                
                st.divider()
                st.subheader("Results")
                
                if results['status'] == 'error':
                    st.error(f"Error: {results.get('results', {}).get('error', 'Unknown error')}")
                else:
                    test_results = results.get('results', {})
                    
                    # score display
                    score = test_results.get('score', 0)
                    if score == 100:
                        st.success(f"🎉 Perfect! Score: {score}%")
                    elif score >= 70:
                        st.info(f"✓ Good job! Score: {score}%")
                    else:
                        st.warning(f"Score: {score}%")
                    
                    # test breakdown
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Passed", test_results.get('passed_tests', 0))
                    col2.metric("Total", test_results.get('total_tests', 0))
                    col3.metric("Score", f"{score}%")
                    
                    # public test details
                    st.subheader("Test Details")
                    for test in test_results.get('test_results', []):
                        if test['is_public']:
                            status = "✅ Passed" if test['passed'] else "❌ Failed"
                            desc = test.get('description', f"Test {test['test_num']}")
                            with st.expander(f"{status} - {desc}", expanded=not test['passed']):
                                st.text(f"Expected: {test.get('expected')}")
                                st.text(f"Got: {test.get('actual')}")
                    
                    # hidden tests summary
                    hidden_count = test_results.get('hidden_tests', 0)
                    if hidden_count > 0:
                        hidden_passed = sum(
                            1 for t in test_results.get('test_results', [])
                            if not t['is_public'] and t['passed']
                        )
                        st.info(f"🔒 Hidden tests: {hidden_passed}/{hidden_count} passed")
                    
                    # AI feedback
                    if results.get('ai_feedback'):
                        st.subheader("💡 Feedback")
                        st.info(results['ai_feedback'])

elif page == "View Results":
    st.header("Recent Submissions")
    
    try:
        response = requests.get(f"{API_URL}/recent?limit=20")
        if response.status_code == 200:
            data = response.json()
            submissions = data.get('submissions', [])
            
            if not submissions:
                st.info("No submissions yet. Go solve some problems!")
            else:
                for sub in submissions:
                    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                    
                    with col1:
                        st.text(f"#{sub['id']}")
                    with col2:
                        st.text(sub['assignment_id'])
                    with col3:
                        status = sub['status']
                        if status == 'passed':
                            st.success(status)
                        elif status == 'failed':
                            st.error(status)
                        else:
                            st.warning(status)
                    with col4:
                        if st.button("View", key=f"view_{sub['id']}"):
                            result = get_results(sub['id'])
                            if result:
                                st.session_state.results = result
                                st.session_state.page = "Submit Solution"
                                st.rerun()
    except Exception as e:
        st.error(f"Failed to load submissions: {e}")

# footer
st.sidebar.markdown("---")
st.sidebar.markdown("**EdgeLab v0.1**")
st.sidebar.caption("Built for LunarTech")
