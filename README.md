# Cynbit AI Project Copilot

A Streamlit assessment prototype for a proposed **client discovery and requirements analysis copilot**. It turns a client problem statement into a structured first-pass opportunity brief using a transparent local rules-based planner.

## What it does

- Extracts details explicitly stated in the problem, such as workflow area, affected users, current tools, and constraints.
- Uses local keyword patterns to identify pain points like repetitive work, delays, errors, and information-search effort.
- Builds an opportunity analysis with a solution workflow, pilot plan, data safeguards, risks, success measures, and follow-up questions.
- Shows a separate technical approach covering the current architecture, data pipeline, model/prompt status, evaluation plan, and execution steps.
- Adds a suggested MVP, user story with acceptance checks, data checklist, test scenarios, pilot measurement plan, roadmap, and open questions.
- Visualizes the prototype's input-to-report flow while distinguishing implemented behavior from proposed future work.
- Demonstrates the proposed client-discovery workflow with a clearly labeled hypothetical scenario.
- Runs locally without sending information to an AI service or requiring an API key.
- Includes 34 synthetic examples, loaded only when the user clicks **Load example**.
- Downloads separate opportunity and technical approach reports as Word documents, plus a CSV summary.

## Local operation and limits

The opportunity is a proposal based on Cynbit's public positioning around its **Discovery & Audit** stage and AI automation/custom software services; it is not a claim about Cynbit's internal workflows. See [Cynbit's website](https://www.cynbit.in/) and [services page](https://www.cynbit.in/services).

The planner makes no API calls and needs no API key or internet connection to generate an approach. It is a transparent rule-based baseline, not a trained ML model or large language model. It is less open-ended than a generative AI assistant, but uses the statement and optional context to tailor its built-in plan. It leaves missing client details unspecified and suggests questions to clarify them.

## Run in VS Code on Windows

1. Install Python 3.10 or later and the Microsoft Python extension for VS Code.
2. Open this project folder in VS Code.
3. In **Terminal** → **New Terminal**, create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`.

4. Install the app dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

6. Open the local address shown in the terminal, usually `http://localhost:8501`. Enter a problem statement or click **Load example**, then choose **Generate opportunity brief**.

## Assessment demo

The first **Load example** is an explicitly hypothetical discovery scenario; it does not imply that Cynbit has reported this as an internal problem. Try this sample problem:

> Our support team receives many repetitive questions each day. Staff search several documents before replying, so response times are slow and answers can be inconsistent.

The generated opportunity report should identify the likely workflow and friction signals, leave missing details open, and propose a human-reviewed pilot. The MVP & validation tab adds test scenarios and checks to run; the technical tab documents what the current prototype actually implements.

## GitHub submission checklist

1. Create or open the `cynbit-ai-project-copilot` GitHub repository.
2. In VS Code Source Control, review and commit the project changes.
3. Push the branch and verify that `app.py`, `requirements.txt`, `README.md`, and `.gitignore` are present.
4. Submit the repository link and a generated Word report according to the assessment instructions before **October 17, 2026**.
