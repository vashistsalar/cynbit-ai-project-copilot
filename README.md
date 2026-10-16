# Cynbit AI Project Copilot

A beginner-friendly Streamlit app that turns a client problem statement into a practical solution plan using a local rules-based planner.

## What it does

- Extracts details explicitly stated in the problem, such as workflow area, affected users, current tools, and constraints.
- Uses local keyword patterns to identify pain points like repetitive work, delays, errors, and information-search effort.
- Builds a tailored recommendation, implementation steps, possible success measures, and follow-up questions from built-in guides.
- Runs locally without sending information to an AI service or requiring an API key.
- Includes 34 synthetic examples, loaded only when the user clicks **Load example**.
- Downloads the plan as a Word document or CSV.

## Local operation and limits

The planner makes no API calls and needs no API key or internet connection to generate an approach. It is a transparent rule-based planner, not a large language model. It is less open-ended than a generative AI assistant, but uses the statement and optional context to tailor its built-in plan. It leaves missing client details unspecified and suggests questions to clarify them.

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

6. Open the local address shown in the terminal, usually `http://localhost:8501`. Enter a problem statement or click **Load example**, then choose **Generate solution approach**.

## Assessment demo

Try this sample problem:

> Our support team receives many repetitive questions each day. Staff search several documents before replying, so response times are slow and answers can be inconsistent.

The generated plan should identify customer support, repeated manual work, delays, and information-search effort; propose a small FAQ-based support assistant with human review; suggest measures; and ask about any missing users or data sources.

## GitHub submission checklist

1. Create or open the `cynbit-ai-project-copilot` GitHub repository.
2. In VS Code Source Control, review and commit the project changes.
3. Push the branch and verify that `app.py`, `requirements.txt`, `README.md`, and `.gitignore` are present.
4. Submit the repository link and a generated Word report according to the assessment instructions before **October 17, 2026**.
