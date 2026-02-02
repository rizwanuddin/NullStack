# EdgeLab Demo Video Transcript (5 minutes)

## Introduction (30 seconds)

Hey there! I'm [Your Name], and I built EdgeLab as part of the LunarTech take-home assignment. 

EdgeLab is basically a coding practice platform - kind of like a mini LeetCode - where you can solve Python, SQL, and Java problems and get instant feedback on your solutions.

Let me walk you through how it works and some of the key decisions I made while building it.

## Quick Demo (1 minute)

[Screen: Show browser with Streamlit UI]

So here's the interface. It's built with Streamlit because I wanted something that looks professional but doesn't take forever to build. 

On the left, we've got three problems - Two Sum in Python, a SQL query for finding top salaries, and a Java palindrome checker.

[Click on Two Sum]

Let me pick Two Sum here. You can see the problem description, the test cases that are visible to the user, and a code editor.

[Type a simple solution]

I'll write a quick solution using a hash map approach...

[Click Run Tests]

And when I submit, it runs the code in an isolated Docker container, tests it against both public and hidden test cases, and gives me results.

[Show results appearing]

Cool - all tests passed. You can see it shows the score, which public tests passed, and a summary of the hidden tests. The actual hidden test details never get exposed to the user.

## Architecture Overview (1.5 minutes)

[Screen: Show diagram or code structure]

The system has four main parts:

First, there's the Streamlit UI you just saw. Pretty straightforward - it talks to the API and displays results.

Second is the Flask API. This handles all the business logic - receiving submissions, coordinating test execution, storing results. I kept it simple with RESTful endpoints.

Third is the database layer - just SQLite for now. It stores the assignment definitions, all the submissions, and results. In production, you'd want PostgreSQL, but SQLite works great for a prototype.

And fourth is the executor - this is probably the most interesting part. When you submit code, it spins up a fresh Docker container for your specific language, runs your code with time and memory limits, and compares the output to expected results.

## Security Decisions (1 minute)

One thing I want to highlight is security, since that was explicitly called out in the requirements.

Every submission runs in a completely isolated Docker container. These containers have no network access - I use the `--network none` flag. They also have strict CPU and memory limits, and execution timeouts.

The code never runs on the host machine. Everything happens in ephemeral containers that get destroyed immediately after execution.

For hidden tests - they only live in the database. When someone requests an assignment through the API, I strip out the hidden tests before sending the response. The frontend never sees them. And in the results, you only see whether hidden tests passed or failed, not what the actual test cases were.

[Show code snippet if possible]

Here's the part that strips hidden tests from API responses - it's a simple delete operation before returning the JSON.

## AI Component (45 seconds)

[Screen: Show AI feedback section]

I also added an optional AI component using Phi-3 Mini through Ollama. 

The idea is that after tests run, the AI looks at your code and the public test results and gives you a couple sentences of constructive feedback - like what you did well and where you could improve.

I went with Phi-3 because it's small enough to run on a laptop, it's actually pretty good at code reasoning, and it runs completely locally. No API costs, no data leaving the system.

The important part is that only public information goes to the AI - never the hidden tests or any confidential logic.

## Trade-offs and Next Steps (1 minute)

[Screen: Back to face or code]

If I had more time, here's what I'd improve:

The code editor is just a textarea right now. I'd swap that for Monaco Editor - the same one VS Code uses - with syntax highlighting and autocomplete.

SQL support is using SQLite in Alpine containers, which works but isn't quite the same as real MySQL or Postgres. For production, I'd spin up actual database containers.

There's no authentication - anyone can submit anything. Obviously you'd need user accounts for real use.

And the concurrency model uses Python threading. That's fine for a demo, but a real system needs a proper job queue like Celery with Redis.

Also, the Java execution compiles everything fresh each time. You could definitely optimize that with some caching.

## Wrap-up (15 seconds)

Overall though, it's a working end-to-end system. You can run it with one command - `docker compose up` - and start solving problems immediately.

Thanks for watching! Looking forward to discussing this further.

---

## Delivery Tips for Recording:

1. **Pace**: Speak naturally, not too fast. Pause briefly between sections.

2. **Tone**: Conversational and confident, not rehearsed or stiff. You're explaining your work to a colleague, not giving a formal presentation.

3. **Screen sharing**: 
   - Start with your face
   - Switch to screen for demo and architecture
   - Show code for security section
   - End with face

4. **Enthusiasm**: Show you care about the work, but don't oversell. Let the project speak for itself.

5. **Authenticity**: If you make a small mistake or stumble, that's fine - just keep going. Don't restart. It shows you're human.

6. **Technical depth**: Don't read code line by line. Explain the "why" not the "what".

7. **Eye contact**: Look at the camera when showing your face, not at yourself on screen.

8. **Background**: Clean, professional, good lighting.

9. **Length**: Aim for 4:30-5:00. Don't go over 5:30.

10. **Ending**: Don't trail off. Have a clear closing statement.
