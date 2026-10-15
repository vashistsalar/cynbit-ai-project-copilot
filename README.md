# Cynbit AI Project Copilot

A beginner-friendly Streamlit prototype for analyzing client requirements and preparing a structured AI opportunity brief. The chosen opportunity is **client requirement analysis and AI opportunity discovery**, which aligns with Cynbit's public positioning in AI automation, custom software, and a discovery-led project lifecycle.

## What the demo does

- Captures a client problem, affected users, current tools, and constraints.
- Uses transparent keyword signals plus a small opportunity guide to suggest a pilot.
- Shows possible success measures, a risk, and a safeguard.
- Downloads a client brief as Markdown (`.md`) and a one-row summary in CSV.

This is a rule-based educational prototype, not a trained ML system. Its signal score is not a confidence estimate or business forecast. A human should validate recommendations with the client.

## Run it in VS Code (Windows)

1. Install Python 3.10 or later and VS Code. In VS Code, install the Microsoft Python extension.
2. Open this project folder in VS Code (`File` → `Open Folder`).
3. Open **Terminal** → **New Terminal**.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt in VS Code and run `.venv\Scripts\activate.bat`.

5. Install the app dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

7. Streamlit opens a browser page, usually at `http://localhost:8501`. Click **Load example**, review the brief and downloads, then try a new client requirement.

## Suggested demo scenario

> Our support team receives many repetitive questions each day. Staff search several documents before replying, so response times are slow and answers can be inconsistent.

Select **Customer support**. Explain that the pilot would retrieve from approved FAQs, draft responses, and hand uncertain questions to a human.

## How to present the assessment

1. **Opportunity:** speed up Cynbit's client discovery by structuring incoming requirements and identifying a small AI pilot.
2. **Prototype:** demonstrate the form and generated opportunity brief.
3. **Approach:** begin with interviews and a baseline; build a narrow, human-reviewed pilot; evaluate against agreed measures.
4. **Responsible use:** verify recommendations, use approved data, and retain a human decision-maker.
5. **Next iteration:** collect labeled examples with consent, evaluate extraction and recommendation quality, then consider an approved LLM or classifier only if it improves measurable outcomes.

## GitHub submission checklist

1. Create a GitHub repository named `cynbit-ai-project-copilot`.
2. In VS Code, open Source Control, initialize the repository, review the files, and commit with a message such as `Build Cynbit AI Project Copilot prototype`.
3. Add the GitHub repository as a remote and publish/push the branch using VS Code's **Publish to GitHub** flow.
4. Confirm the repository has `app.py`, `requirements.txt`, `README.md`, and `.gitignore`, and that no credentials or private client data are included.
5. Submit the repository link and the downloaded brief according to the assessment instructions before **October 17, 2026**.

## References

- Cynbit Technologies, public website: <https://www.cynbit.in/> (reviewed October 15, 2026). The site describes AI automation, custom software, SaaS products, and discovery/audit as part of its project lifecycle. This project concept is an assessment proposal, not a claim that Cynbit currently has this internal workflow or its performance data.
