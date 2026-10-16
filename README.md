# Cynbit AI Project Copilot

A Streamlit prototype for turning a client problem statement into a clear first-pass AI opportunity brief. It is designed to support a consultant's discovery process; a person should review the suggestions before using them.

**Live demo:** [Open the app](https://cynbit-ai-project-copilot-tvxzgavx5r4qc5grnknpsp.streamlit.app/)

## What the app does

1. Enter a problem statement and, if known, client context. The fields start blank; **Load example** adds sample data only when clicked.
2. The app extracts details stated by the user and leaves missing details unspecified. It does not invent client information.
3. Local keyword rules and a small ML classifier compare the likely problem category. The rules and built-in guides create a practical approach, pilot steps, risks, safeguards, success measures, and questions to ask.
4. Review and edit the context, then download an Opportunity Report (Word), Technical Approach Report (Word), or a CSV summary.

The app runs locally without an API key and does not send the problem statement to an AI service. Its solution plan is rule-based; the ML model predicts a category only and does not write the plan.

## Model demonstration

The classifier uses TF-IDF and Logistic Regression and is trained on 34 synthetic examples. In five-fold cross-validation on those examples, keyword rules scored **91.2% (31/34)** and the ML classifier scored **50.0% (17/34)**. These small synthetic-data results are for demonstration only; they do not predict real-world performance. The app's match-strength label counts keyword matches; it is not a probability.

## Run the app on Windows

Install Python 3.10 or later and open this folder in VS Code. In **Terminal → New Terminal**, run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local address shown in the terminal, usually `http://localhost:8501`. If PowerShell blocks environment activation, use Command Prompt and run `.venv\Scripts\activate.bat` instead.

## Try a sample problem

> Our support team receives many repetitive questions each day. Staff search several documents before replying, so response times are slow and answers can be inconsistent.

Click **Generate opportunity brief** to see the analysis. Click **Load example** to cycle through the app's 34 clearly labeled synthetic scenarios.

## Project files

- `app.py` — Streamlit interface, local planner, and report downloads.
- `classifier.py` — TF-IDF and Logistic Regression category classifier and evaluation.
- `requirements.txt` — Python packages needed to run the app.
- `ASSESSMENT_REPORT.docx` — assessment report included with the project.

## Assessment notes

The proposed opportunity is to help structure client requirements and identify a suitable AI pilot during discovery. This is a proposal based on Cynbit's publicly described services; it is not a claim about Cynbit's internal processes. The prototype uses synthetic examples and has not been validated with real client data or users. Before any real pilot, agree on data access, privacy safeguards, review responsibilities, and success measures with the client.

For submission, include the live app link, this GitHub repository, and the generated Word reports requested by the assessment.
