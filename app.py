from __future__ import annotations

from datetime import date
from io import BytesIO
import re
from html import escape
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import streamlit as st
from classifier import cross_validate_categories, predict_category, train_category_classifier


st.set_page_config(page_title="Cynbit AI Project Copilot", page_icon=":material/explore:", layout="wide")

st.session_state.setdefault("theme_mode", "Dark")
if not st.session_state.get("_local_planner_v2_initialized", False):
    for old_key in (
        "ai_provider", "_auto_provider_default_migrated", "analysis",
        "analysis_requested", "analysis_error", "submitted_provider",
        "generation_warning", "gemini_error_details",
    ):
        st.session_state.pop(old_key, None)
    st.session_state["_local_planner_v2_initialized"] = True

st.html("""
<style>
.stApp {
  background:
    radial-gradient(ellipse at 75% 0%, rgba(139, 124, 255, .19), transparent 40%),
    radial-gradient(ellipse at 5% 45%, rgba(72, 113, 214, .15), transparent 38%),
    #0a0f1f;
}
.stApp::before {
  content: "";
  position: fixed;
  inset: -20%;
  z-index: 0;
  pointer-events: none;
  opacity: .13;
  background:
    radial-gradient(ellipse at 24% 28%, rgba(167, 139, 250, .16), transparent 34%),
    radial-gradient(ellipse at 78% 70%, rgba(103, 232, 249, .10), transparent 38%);
  filter: blur(42px);
}
.stApp > header { background: transparent; }
.stMainBlockContainer {
  position: relative;
  z-index: 1;
  max-width: 1120px;
  padding: 2.25rem 2rem 4rem;
}
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(19, 27, 48, .98), rgba(10, 15, 31, .98));
  border-right: 0;
}
section[data-testid="stSidebar"] > div { padding: 1.4rem 1.1rem 2rem; }
section[data-testid="stSidebar"] h2 {
  margin: .25rem 0 .2rem;
  font-size: 1.1rem;
  letter-spacing: -.025em;
}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  margin-bottom: .8rem;
  line-height: 1.45;
}
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
  font-size: .82rem;
  font-weight: 600;
}
section[data-testid="stSidebar"] [data-testid="stRadioGroup"] {
  display: flex;
  flex-wrap: nowrap;
  width: 100%;
  gap: .3rem;
  padding: .28rem;
  border: 0;
  border-radius: 11px;
  background: rgba(10, 15, 31, .52);
}
section[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div { flex: 1 1 0; min-width: 0; }
section[data-testid="stSidebar"] [data-testid="stRadioOption"] {
  justify-content: center;
  white-space: nowrap;
  padding: .38rem .45rem;
  border-radius: 8px;
  transition: background .18s ease, color .18s ease;
}
section[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child { display: none; }
section[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioOption"] {
  background: rgba(167, 139, 250, .16);
}
section[data-testid="stSidebar"] [data-testid="stRadioGroup"] [data-testid="stMarkdownContainer"] p {
  margin: 0;
  font-size: .82rem;
  font-weight: 600;
}
.stMarkdown, [data-testid="stCaptionContainer"] { color: #b7c2d8; }
h1, h2, h3 { letter-spacing: -.035em; }
.stMainBlockContainer [data-testid="stMarkdownContainer"] p { line-height: 1.65; }
.stMainBlockContainer [data-testid="stMarkdownContainer"] li { margin-bottom: .38rem; line-height: 1.55; }
button:focus-visible, summary:focus-visible {
  outline: 2px solid #67e8f9 !important;
  outline-offset: 3px;
}
.challenge-title {
  margin: 0;
  text-align: center;
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: -.035em;
  text-shadow: 0 0 24px rgba(167, 139, 250, .12);
}
div[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid rgba(151, 163, 199, .12);
  border-radius: 18px;
  background: rgba(18, 26, 47, .48);
  box-shadow: 0 14px 38px rgba(3, 8, 20, .12);
}
div[data-testid="stMetric"] {
  min-height: 118px;
  padding: 1rem 1.1rem;
  border: 1px solid rgba(151, 163, 199, .12);
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(27, 37, 65, .92), rgba(17, 26, 46, .88));
  transition: border-color .18s ease, transform .18s ease, background .18s ease;
}
div[data-testid="stMetric"]:hover {
  transform: translateY(-1px);
  border-color: rgba(167, 139, 250, .32);
}
div[data-testid="stMetricLabel"] { color: #b7c2d8; }
div[data-testid="stMetricValue"] { color: #f0efff; }
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border: 1px solid rgba(151, 163, 199, .22);
  border-radius: 12px;
  background-color: rgba(10, 16, 34, .82);
  transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, .13);
}
div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button {
  min-height: 2.8rem;
  border-radius: 12px;
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease, background .16s ease;
}
div[data-testid="stButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover {
  transform: translateY(-1px);
  box-shadow: 0 5px 15px rgba(139, 124, 255, .12);
  border-color: rgba(167, 139, 250, .46);
}
div[data-testid="stButton"] button[kind="primary"] {
  color: #ffffff;
  background: linear-gradient(135deg, #7969e8, #6257ca);
  border: 1px solid rgba(186, 174, 255, .22);
  box-shadow: 0 5px 16px rgba(91, 79, 183, .18);
}
[data-testid="stExpander"] details {
  border: 1px solid rgba(151, 163, 199, .14);
  border-radius: 14px;
  background: rgba(18, 26, 47, .44);
}
[data-testid="stAlert"] { border-radius: 14px; }
.copilot-hero {
  position: relative;
  display: flex;
  min-height: 116px;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;
  margin: 0 0 .3rem;
  padding: .7rem 1.25rem;
  border: 0;
  border-radius: 0;
  background: radial-gradient(ellipse at 78% 48%, rgba(139, 124, 255, .16), transparent 38%);
  box-shadow: none;
}
.hero-copy { position: relative; z-index: 2; max-width: 100%; }
.hero-eyebrow {
  display: flex;
  align-items: center;
  gap: .6rem;
  margin: 0 0 .8rem;
  color: #aab7d1;
  font: 600 .7rem/1.4 "Segoe UI", sans-serif;
  letter-spacing: .16em;
}
.hero-signal {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #a78bfa;
  box-shadow: 0 0 8px rgba(167, 139, 250, .55);
}
.hero-title {
  margin: 0;
  color: #f1f2ff;
  font: 700 clamp(1.8rem, 4vw, 2.4rem)/1.08 "Segoe UI", sans-serif;
  letter-spacing: -.065em;
}
.hero-title span {
  white-space: nowrap;
  color: #a78bfa;
  text-shadow: 0 0 24px rgba(167, 139, 250, .16);
}
.hero-description {
  max-width: 570px;
  margin: .8rem 0 0;
  color: #b7c2d8;
  font: 400 1rem/1.7 "Segoe UI", sans-serif;
}
.hero-orbit {
  position: absolute;
  right: 0;
  display: grid;
  width: 150px;
  height: 150px;
  flex: 0 0 150px;
  place-items: center;
  margin-right: 0;
  opacity: .24;
  border: 0;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 124, 255, .18), transparent 68%);
  box-shadow: 0 0 52px rgba(139, 124, 255, .10);
}
.hero-orbit::before, .hero-orbit::after {
  position: absolute;
  inset: 12px;
  border: 0;
  border-radius: 50%;
  content: "";
}
.hero-orbit::after {
  inset: 31px -7px;
  border-color: rgba(103, 232, 249, .28);
  transform: rotate(-35deg);
}
.hero-core {
  width: 58px;
  height: 58px;
  border: 0;
  border-radius: 50%;
  background: radial-gradient(circle at 38% 34%, #f2eaff, #a78bfa 30%, #6366f1 66%, #172554);
  box-shadow: 0 0 22px rgba(167, 139, 250, .38), 0 0 48px rgba(103, 232, 249, .12);
}
@media (max-width: 700px) {
  .stMainBlockContainer { padding: 1rem .85rem 2.5rem; }
  .copilot-hero { min-height: 100px; padding: .65rem .4rem; }
  .hero-title { font-size: clamp(1.75rem, 8vw, 2.25rem); }
  .hero-orbit { right: -70px; width: 130px; height: 130px; opacity: .16; }
  .challenge-title { font-size: 1.5rem; }
  div[data-testid="stTextArea"] textarea { min-height: 9rem; }
}
</style>
""")

if st.session_state["theme_mode"] == "Light":
    st.html("""
    <style>
    .stApp {
      background:
        radial-gradient(ellipse at 75% 0%, rgba(139, 124, 255, .14), transparent 40%),
        radial-gradient(ellipse at 5% 45%, rgba(103, 150, 230, .10), transparent 38%),
        #f6f6fc;
      color: #24253b;
    }
    .stApp::before {
      opacity: .24;
    }
    section[data-testid="stSidebar"] {
      background: linear-gradient(180deg, rgba(255, 255, 255, .98), rgba(242, 242, 251, .98));
      border-right: 0;
    }
    section[data-testid="stSidebar"] *,
    .stMainBlockContainer [data-testid="stCaptionContainer"] *,
    .stMainBlockContainer [data-testid="stMarkdownContainer"] *,
    .stMainBlockContainer [data-testid="stWidgetLabel"] *,
    .stMainBlockContainer h1,
    .stMainBlockContainer h2,
    .stMainBlockContainer h3,
    .stMainBlockContainer label {
      color: #30314a !important;
      opacity: 1 !important;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] p,
    [data-testid="stHeadingWithActionElements"] h1,
    [data-testid="stHeadingWithActionElements"] h2,
    [data-testid="stHeadingWithActionElements"] h3,
    [data-testid="stWidgetLabel"] * { color: #42435d !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
      border: 1px solid rgba(100, 93, 153, .12);
      background: rgba(255, 255, 255, .76);
      box-shadow: 0 12px 32px rgba(55, 48, 100, .06);
    }
    div[data-testid="stMetric"] {
      border: 1px solid #e7e4f1;
      background: linear-gradient(145deg, #ffffff, #f0effa);
    }
    div[data-testid="stMetric"]:hover { border-color: #c9c0f1; }
    div[data-testid="stMetricLabel"] { color: #65667c; }
    div[data-testid="stMetricValue"] { color: #27283e; }
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
      color: #27283e !important;
      border-color: #e1def0 !important;
      background-color: #ffffff !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] * {
      color: #27283e !important;
    }
    div[data-testid="stSelectbox"] div[role="group"] {
      border: 0 !important;
      border-radius: 11px;
      background: #ffffff !important;
    }
    div[data-testid="stSelectbox"] input[role="combobox"] {
      color: #27283e !important;
      background: transparent !important;
    }
    div[data-testid="stSelectbox"] button {
      color: #65667c !important;
      background: transparent !important;
    }
    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder { color: #778895; }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
      border-color: #7867e8;
      box-shadow: 0 0 0 3px rgba(120, 103, 232, .15);
    }
    section[data-testid="stSidebar"] [data-testid="stRadioGroup"] {
      border: 1px solid #e1def0;
      background: #eeedf7;
    }
    section[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioOption"] {
      background: #ffffff;
      box-shadow: 0 1px 5px rgba(55, 48, 100, .12);
    }
    .hero-title { color: #27283e; }
    .hero-title span { color: #6957d9; text-shadow: 0 0 28px rgba(105, 87, 217, .16); }
    .hero-description { color: #65667c; }
    button:focus-visible, summary:focus-visible { outline-color: #6957d9 !important; }
    .hero-orbit { opacity: .28; }
    div[data-testid="stButton"] button:not([kind="primary"]),
    div[data-testid="stDownloadButton"] button {
      color: #30314a;
      border-color: #d9d6e9;
      background: rgba(255, 255, 255, .9);
    }
    div[data-testid="stButton"] button:not([kind="primary"]):hover,
    div[data-testid="stDownloadButton"] button:hover {
      background: #f4f1ff;
      border-color: #bdb2ec;
    }
    div[data-testid="stButton"] button[kind="primary"] {
      color: #ffffff;
      background: linear-gradient(135deg, #7969e8, #6257ca);
      border-color: #7868d9;
    }
    [data-testid="stExpander"] details {
      border-color: rgba(100, 93, 153, .16);
      border-radius: 14px;
      background: rgba(255, 255, 255, .56);
    }
    [data-testid="stAlert"] { border-radius: 14px; }
    header[data-testid="stHeader"] { background: rgba(246, 246, 252, .9); }
    </style>
    """)

OPPORTUNITY_GUIDES = {
    "Customer support": {
        "use_case": "AI support assistant with human handoff",
        "approach": "Index approved FAQs and support documents, retrieve relevant passages, draft an answer, and route low-confidence or sensitive cases to a person.",
        "metrics": ["First response time", "Resolution time", "Escalation rate", "Answer helpfulness"],
        "risk": "Outdated or incomplete source material can produce misleading answers. Restrict answers to approved sources and show citations.",
    },
    "Sales and lead management": {
        "use_case": "Lead qualification and follow-up copilot",
        "approach": "Extract needs and intent from enquiry text, score leads with transparent rules, suggest follow-up questions, and let a salesperson approve messages.",
        "metrics": ["Time to qualify", "Lead-to-meeting rate", "Follow-up completion", "Salesperson acceptance"],
        "risk": "A score can encode bias or overstate intent. Keep criteria visible and leave decisions with the sales team.",
    },
    "Document processing": {
        "use_case": "Document intake and extraction assistant",
        "approach": "Classify incoming documents, extract key fields, validate them against business rules, and send uncertain cases to a reviewer.",
        "metrics": ["Processing time per document", "Field extraction accuracy", "Manual correction rate", "Backlog size"],
        "risk": "OCR and extraction errors can affect downstream decisions. Track confidence and require review for important fields.",
    },
    "Internal workflow": {
        "use_case": "Workflow triage and next-step assistant",
        "approach": "Summarize requests, classify them by team and urgency, propose the next action, and require staff approval before routing or changing records.",
        "metrics": ["Time to triage", "Misrouting rate", "Work completed per week", "Staff satisfaction"],
        "risk": "Incorrect routing can delay work. Keep an audit trail and make reassignment easy.",
    },
    "Product or service idea": {
        "use_case": "AI-enabled product discovery prototype",
        "approach": "Test a narrow customer-facing workflow with synthetic or consented data, measure usage and task completion, and expand only after user review.",
        "metrics": ["Task completion rate", "Repeat usage", "User satisfaction", "Support requests"],
        "risk": "A technically impressive feature may not solve a real customer problem. Validate demand with interviews and a small pilot.",
    },
}

# Each matched pattern counts as one rule for the app's qualitative match label.
# The label is a rule-match count, not a probability or calibrated confidence.
CATEGORY_KEYWORD_RULES = {
    "Customer support": [
        r"\bcustomer support\b", r"\bsupport team\b", r"\bcustomer service\b",
        r"\bhelp desk\b", r"\bservice desk\b", r"\bsupport tickets?\b",
        r"\bFAQs?\b", r"\bhelp center\b", r"\bhelp articles?\b",
        r"\b(?:booking|itinerary|appointment|clinic hours|repair questions?|return rules?|visitor services)\b",
        r"\bvisitors?\b",
    ],
    "Sales and lead management": [
        r"\bsales\b", r"\bleads?\b", r"\bprospects?\b", r"\benquir(?:y|ies)\b",
        r"\bfollow[- ]?ups?\b", r"\bquotes?\b", r"\bmembership\b",
        r"\bCRM\b", r"\bpipeline\b", r"\baccount managers?\b",
        r"\b(?:sales representatives?|business development|reps)\b",
    ],
    "Document processing": [
        r"\binvoices?\b", r"\bPDFs?\b", r"\bforms?\b", r"\bdocuments?\b",
        r"\bOCR\b", r"\bdata entry\b", r"\bextract(?:ion|ing)?\b",
        r"\bscanned\b", r"\battachments?\b", r"\btranscription errors?\b",
        r"\bclaim forms?\b", r"\binspection sheets?\b",
    ],
    "Internal workflow": [
        r"\binternal workflow\b", r"\bapproval\b", r"\btask routing\b", r"\bworkflow\b",
        r"\bwork orders?\b", r"\brequests?\b", r"\bschedules?\b", r"\btriage\b",
        r"\bmaintenance\b", r"\b(?:assign|assigned|assignment|route|routed|routing)\b",
        r"\bbug reports?\b", r"\bpolicy questions?\b", r"\boperations\b",
        r"\bdiscovery (?:call )?notes?\b", r"\brequirements briefs?\b",
    ],
    "Product or service idea": [
        r"\bnew product\b", r"\bproduct idea\b", r"\bproduct feature\b", r"\bproduct concept\b",
        r"\bprototype\b", r"\bspending patterns\b", r"\bspeaking practice\b",
        r"\bplant[- ]care\b", r"\bcare instructions?\b", r"\bguided product\b",
        r"\bwant to (?:explore|test|prototype|build)\b", r"\bfeature that\b",
    ],
}


def count_category_keyword_matches(text: str, category: str | None) -> int:
    """Count distinct keyword rules matched for one selected category."""
    if not category:
        return 0
    return sum(bool(re.search(rule, text, re.IGNORECASE)) for rule in CATEGORY_KEYWORD_RULES.get(category, []))


def classify_category_by_rules(text: str) -> str | None:
    """Return the category with the most matching rules, or None if there is no match."""
    scores = {category: count_category_keyword_matches(text, category) for category in CATEGORY_KEYWORD_RULES}
    category = max(scores, key=scores.get)
    return category if scores[category] else None


def is_specific_tool_source(source: str) -> bool:
    """Only treat named applications or concrete system types as a test source."""
    specific_sources = (
        r"\bCRM\b", r"\bshared inbox\b", r"\bJira(?: Service Management)?\b",
        r"\bGoogle Sheets\b", r"\bMicrosoft Excel\b", r"\bExcel\b",
        r"\bSalesforce\b", r"\bHubSpot\b", r"\bFreshdesk\b", r"\bZendesk\b",
        r"\bServiceNow\b", r"\bOutlook\b", r"\bGmail\b", r"\bSharePoint\b",
        r"\bConfluence\b", r"\bQuickBooks\b", r"\bXero\b", r"\bSAP\b",
        r"\bOracle\b", r"\bDynamics 365\b",
    )
    return any(re.search(rule, source, re.IGNORECASE) for rule in specific_sources)

# Synthetic scenarios for the explicit Load example action (not used as initial values).
# Tuple fields: client, category, users, tools/data, constraints, problem statement.
EXAMPLE_CASES = [
    ("Assessment demo (hypothetical)", "Internal workflow", "Discovery consultants (hypothetical)", "Synthetic discovery notes and public website information", "Use synthetic or public information; a consultant approves recommendations", "Assessment scenario (hypothetical): A software consultancy spends time turning discovery-call notes and public client information into a first-pass requirements brief. Important details such as affected users, current tools, and constraints can be missed. How could a local copilot make the review more consistent while keeping a consultant in control?"),
    ("Harbor Travel (Sample)", "Customer support", "Customer service agents", "Email inbox and booking records", "Do not change or cancel bookings automatically", "Agents spend a long time finding booking details across emails and records. Customers wait for simple itinerary answers."),
    ("BrightPath Learning (Sample)", "Customer support", "Students and support staff", "Help center articles", "Answers must use approved school policies", "Students frequently ask the same questions about course access. Staff manually search help articles and replies are delayed during busy periods."),
    ("Northstar Utilities (Sample)", "Customer support", "Service desk agents", "Ticketing system and service guides", "Escalate safety issues to a human immediately", "The service desk receives a high volume of similar outage questions. Agents repeatedly look up service guides and response times increase during incidents."),
    ("Willow Health Desk (Sample)", "Customer support", "Clinic reception team", "Appointment FAQ documents", "No diagnosis; staff review all health-related replies", "Reception staff repeatedly answer appointment and clinic-hours questions by searching several FAQ documents, creating delays on busy days."),
    ("Cedar Home Services (Sample)", "Customer support", "Customer service team", "Shared inbox and repair guides", "Technician approval for repair instructions", "Customers send frequent repair questions with photos. Staff manually locate the right guide, and inconsistent answers lead to repeat calls."),
    ("Pinecone Market (Sample)", "Customer support", "Support agents", "Returns policy and order database", "Refund decisions stay with a person", "Agents spend too much time checking return rules and order details. The backlog grows after promotions and customers wait for updates."),
    ("Metro Arts Center (Sample)", "Customer support", "Visitor services staff", "Event pages and venue FAQ", "Only publish current event information", "Visitors ask repeated questions about event times and accessibility. Staff search different pages and sometimes miss recent schedule changes."),
    ("Sample Solar Sales", "Sales and lead management", "Sales representatives", "CRM and enquiry emails", "Salespeople approve outreach before it is sent", "Reps manually read many incoming enquiries to identify serious leads. Follow-ups are delayed and the CRM is updated inconsistently."),
    ("Summit Software (Sample)", "Sales and lead management", "Business development team", "HubSpot and call notes", "Lead scores must be explainable", "The team spends hours summarizing call notes and deciding which prospects need follow-up. Important leads sometimes wait too long."),
    ("Bluebird Realty (Sample)", "Sales and lead management", "Property sales agents", "CRM and property enquiry forms", "Do not infer sensitive personal traits", "Agents receive many property enquiries and manually sort them by stated budget, location, and timing, slowing their response to buyers."),
    ("Fieldstone Events (Sample)", "Sales and lead management", "Event sales staff", "Web forms and spreadsheet", "Staff review every proposed quote", "Staff copy event requirements from web forms into spreadsheets and draft quotes by hand. Busy weeks create errors and missed follow-ups."),
    ("Sample Freight Partners", "Sales and lead management", "Account managers", "CRM and customer emails", "Only use information provided by the customer", "Account managers manually search old emails to understand a prospect's shipping needs. Preparing a useful first response takes too long."),
    ("Greenway Fitness (Sample)", "Sales and lead management", "Membership sales team", "Website enquiry forms and CRM", "No automated promises about membership terms", "The team receives daily membership enquiries and manually records preferences before calling people back. Some follow-ups are forgotten."),
    ("Sample Ledger Works", "Document processing", "Accounts payable clerks", "Email attachments and accounting system", "Human review before payment", "Clerks key invoice details from many PDFs into the accounting system. Duplicate entries and data-entry errors create rework."),
    ("Orchard Logistics (Sample)", "Document processing", "Shipping coordinators", "Scanned bills of lading and spreadsheet", "Verify shipment details before dispatch", "Coordinators manually copy shipment numbers and addresses from scanned documents. Backlogs delay dispatch and errors require corrections."),
    ("Sample Talent Desk", "Document processing", "Recruiting coordinators", "Applicant PDFs and hiring tracker", "Do not rank candidates; recruiters review summaries", "Recruiters spend time extracting basic work history and contact details from many resumes into a tracker."),
    ("Maple Grove Insurance (Sample)", "Document processing", "Claims intake team", "Claim forms and document folders", "Adjusters decide coverage and claim outcomes", "The intake team receives claims with multiple attachments and manually checks whether required forms are present, slowing the queue."),
    ("Sample Community Grants", "Document processing", "Grant administrators", "Application PDFs and shared drive", "Eligibility decisions remain with the review panel", "Administrators manually locate budgets and project dates in many grant applications, making preparation for review slow."),
    ("Stonebridge Manufacturing (Sample)", "Document processing", "Quality technicians", "Inspection sheets and production database", "Technicians verify measurements and exceptions", "Technicians re-enter inspection measurements from paper forms. Frequent transcription errors make trend reporting unreliable."),
    ("Sample Campus Records", "Document processing", "Records office staff", "Student forms and records database", "Protect student data; review every record change", "Staff process many enrollment forms by hand and search for missing fields, creating a slow backlog at the start of term."),
    ("Sample People Operations", "Internal workflow", "HR operations team", "Shared inbox and HR portal", "HR staff approve sensitive requests", "The HR inbox receives repetitive policy and leave questions. Staff manually route messages and response delays frustrate employees."),
    ("Lakeside Facilities (Sample)", "Internal workflow", "Facilities coordinators", "Work-order system and email", "Urgent safety issues go directly to staff", "Coordinators manually read many maintenance requests and assign them to teams. Misrouted work orders delay repairs."),
    ("Sample Procurement Office", "Internal workflow", "Procurement staff", "Purchase request forms and ERP", "Purchases require existing approval", "Purchase requests arrive in different formats. Staff repeatedly copy details and chase missing information, increasing approval time."),
    ("Canyon Legal Support (Sample)", "Internal workflow", "Office administrators", "Shared mailbox and matter tracker", "No legal advice; administrators verify routing", "Administrators manually classify office requests and update a matter tracker. The queue grows when requests arrive in batches."),
    ("Sample IT Service Desk", "Internal workflow", "IT support staff", "Jira Service Management and knowledge base", "Access changes require technician approval", "IT staff repeatedly summarize tickets and search knowledge articles before assigning them. Common issues wait behind a growing backlog."),
    ("Riverbend Nonprofit (Sample)", "Internal workflow", "Program coordinators", "Email, spreadsheets, and calendar", "Coordinators approve schedule changes", "Coordinators manually combine updates from emails and spreadsheets to prepare weekly schedules. Duplicate work and late changes are common."),
    ("Sample Quality Assurance Team", "Internal workflow", "QA analysts", "Bug tracker and release notes", "QA leads confirm severity and release readiness", "Analysts triage a high volume of bug reports by hand, looking for duplicates and missing reproduction steps before assigning work."),
    ("Sample Community Bank", "Product or service idea", "Small-business customers", "Synthetic transaction data for prototype", "No financial decisions or account actions", "We want to explore a tool that helps small-business customers find spending patterns in their transactions and prepare questions for an advisor."),
    ("Evergreen Garden Supply (Sample)", "Product or service idea", "Home gardeners", "Public plant-care guides", "Label general information and uncertainty", "Customers struggle to find care instructions for their plants. We want to test a product feature that answers questions using approved gardening guides."),
    ("Sample Language Coach", "Product or service idea", "Adult language learners", "Synthetic lesson content", "Learners control feedback and data retention", "Learners want more speaking practice between classes. We want to prototype a conversational practice feature and measure whether they return to it."),
    ("Trailhead Outfitters (Sample)", "Product or service idea", "Outdoor shoppers", "Product catalog and published fit guides", "Do not guarantee safety or fit", "Shoppers find it hard to compare gear for different trips. We want to explore a guided product discovery feature using catalog details."),
    ("Sample City Services", "Product or service idea", "Residents", "Published city service pages", "Use only public guidance; urgent issues go to staff", "Residents have trouble finding the right city service page. We want to test a plain-language guide to published information."),
    ("Meadow Health Education (Sample)", "Product or service idea", "Patients learning about appointments", "Clinician-approved educational content", "No diagnosis or treatment recommendations", "Patients often arrive unsure what appointment instructions mean. We want to test a simple explanation tool based on clinician-approved materials."),
]


@st.cache_resource(show_spinner=False)
def get_category_classifier():
    """Cache the trained demonstration classifier and its reproducible CV results."""
    model = train_category_classifier(EXAMPLE_CASES)
    metrics = cross_validate_categories(EXAMPLE_CASES, classify_category_by_rules)
    print(
        "Category cross-validation accuracy — "
        f"rules: {metrics['rule_accuracy']:.1%}; ML: {metrics['ml_accuracy']:.1%}"
    )
    return model, metrics


def extract_client_context(text: str) -> dict:
    """Extract only details directly stated in the client's problem description."""
    context = {"client": "", "category": None, "users": "", "systems": "", "constraints": ""}

    client_match = re.search(
        r"(?i:\b(?:client|company|organization|organisation|project)(?:\s+name)?\s*[:=]\s*)([^,.;!?\n]+)"
        r"|(?i:\b(?:client|company|organization|organisation|project)\s+(?:called|named)\s+)([^,.;!?\n]+)"
        r"|(?i:\b(?:client|company|organization|organisation|project)\s+is\s+)([A-Z][\w&'.-]*(?:\s+[A-Z][\w&'.-]*){0,3})",
        text,
    )
    if client_match:
        client_name = next(group for group in client_match.groups() if group)
        client_name = re.split(
            r"\s+(?:and|but|because|who|which|is|has|needs?|wants?|currently|offers|provides|serves)\b",
            client_name,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]
        context["client"] = client_name.strip(" .,:;-\t")

    user_match = re.search(
        r"\b(?:our|the|for|used by)\s+((?:customer\s+)?(?:support|sales|service|operations|finance|marketing|engineering|development|HR|IT|customer success)\s+(?:team|staff|agents|representatives|reps))\b",
        text,
        re.IGNORECASE,
    )
    if user_match:
        context["users"] = user_match.group(1).strip()
    else:
        user_match = re.search(r"\b(?:our|the|for|used by)\s+(customers|clients|employees|agents|students|patients|users)\b", text, re.IGNORECASE)
        if user_match:
            context["users"] = user_match.group(1).strip()

    context["category"] = classify_category_by_rules(text)

    source_match = re.search(
        r"\b(?:current(?:ly)?\s+(?:tools?|systems?|data sources?)|tools?|systems?|data sources?)\s*[:=-]\s*([^.;!?\n]+)",
        text,
        re.IGNORECASE,
    )
    source_text = source_match.group(1) if source_match else ""
    source_is_explicit = bool(re.search(
        r"\b(?:currently use|using|via|through|search(?:es|ed|ing)?\s+(?:(?:in|through)\s+)?(?:the|these|several|multiple|our|their)?\s*(?:documents?|FAQs?|spreadsheets?|records?)|stored in|in\s+(?:a|the|our|their)\s+(?:shared inbox|CRM|spreadsheet|database|FAQ))\b",
        text,
        re.IGNORECASE,
    ))
    if not source_text and source_is_explicit:
        known_sources = [
            "Google Sheets", "shared inbox", "Microsoft Excel", "Salesforce", "HubSpot", "Freshdesk",
            "Zendesk", "ServiceNow", "Outlook", "Gmail", "Jira", "Excel", "CRM", "spreadsheet",
            "spreadsheets", "FAQ documents", "FAQ", "documents", "database", "email",
        ]
        mentioned = [name for name in known_sources if re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE)]
        source_text = ", ".join(dict.fromkeys(mentioned))
    context["systems"] = source_text.strip(" .,:;-\t")

    constraint_match = re.search(
        r"\b(?:must not|cannot|can't|should not|do not|don't|requires? human (?:review|approval)|human approval|required human review|only approved|must remain|must be reviewed|must have)\b[^.!?;\n]*",
        text,
        re.IGNORECASE,
    )
    if constraint_match:
        context["constraints"] = constraint_match.group(0).strip(" .,:;-\t")
    return context


def generate_local_solution_approach(text: str, context: dict) -> str | None:
    """Build a tailored solution plan from local rules and the supplied context."""
    category = context.get("category") or classify_category_by_rules(text)
    guide = OPPORTUNITY_GUIDES.get(category)
    statement = re.sub(r"\s+", " ", text).strip()
    lower_text = statement.lower()

    signals = []
    signal_rules = [
        (r"\b(manual(?:ly)?|repetitive|repeated|again and again|copy(?:ing)?|re-enter)\b", "repeated manual work"),
        (r"\b(delay(?:ed|s)?|slow|wait(?:ing)?|backlog|takes? too long|late)\b", "delays or a growing backlog"),
        (r"\b(errors?|mistakes?|inconsistent|duplicates?|miss(?:ed|ing)|incorrect)\b", "errors or missed work"),
        (r"\b(search|find|look(?:ing)? up|hunt(?:ing)?)\b", "time spent finding information"),
        (r"\b(overwhelmed|high volume|too many|large number|busy periods?)\b", "high or uneven workload"),
    ]
    for pattern, signal in signal_rules:
        if re.search(pattern, lower_text):
            signals.append(signal)

    if not category and not signals:
        return None

    if not guide:
        category = classify_category_by_rules(lower_text)
        guide = OPPORTUNITY_GUIDES.get(category)

    category_match_count = count_category_keyword_matches(statement, category)
    if category_match_count >= 3:
        match_strength = "High"
    elif category_match_count == 2:
        match_strength = "Medium"
    else:
        match_strength = "Low"

    if guide:
        recommendation = guide["approach"]
        metrics = guide["metrics"]
        category_line = f"This looks most like **{category}** based on the words in your description."
    else:
        recommendation = (
            "Map the current task, find the slowest or most error-prone step, and test a small digital assistant or automation there. "
            "Keep a person responsible for decisions until the pilot proves reliable."
        )
        metrics = ["Time per task", "Errors or rework", "Backlog", "User feedback"]
        category_line = "I could not confidently match this to one of the built-in workflow types, so the plan starts with discovery."

    if signals:
        found_signals = signals[:3]
        if len(found_signals) == 1:
            joined_signals = found_signals[0]
        elif len(found_signals) == 2:
            joined_signals = " and ".join(found_signals)
        else:
            joined_signals = ", ".join(found_signals[:-1]) + ", and " + found_signals[-1]
        friction_line = "The friction signals I found are " + joined_signals + "."
    else:
        friction_line = "The exact source of the difficulty is not yet clear from the description."

    users = context.get("users") or "the people who handle this task"
    if category == "Customer support":
        first_step = "List the most common question types and gather the approved answers used today."
    elif category == "Sales and lead management":
        first_step = "Map how an enquiry moves from arrival to first response, and identify which details staff need to decide the next action."
    elif category == "Document processing":
        first_step = "Choose one frequent document type and list the fields and validation rules staff use when processing it."
    elif category == "Internal workflow":
        first_step = "Map how a request arrives, gets assigned, and is completed; note where it waits or gets sent to the wrong person."
    elif category == "Product or service idea":
        first_step = "Choose one user task to improve and confirm it through a few short conversations before building."
    else:
        first_step = "Write down the current steps and identify the one step that causes the most delay, repetition, or rework."

    source = context.get("systems")
    if source and is_specific_tool_source(source):
        source_step = f"Use **{source}** as the first test source, and verify a small sample with the people who know it."
    else:
        source_step = "Identify which documents, systems, or records contain the information needed; this was not specified."

    constraint = context.get("constraints")
    if constraint:
        safety_step = f"Build in the stated safeguard: **{constraint}**. Keep a person able to review and correct the result."
    else:
        safety_step = "Keep a person reviewing important outputs. Do not automate payments, access changes, customer promises, or other irreversible decisions in the first pilot."

    pilot_group = context.get("users") or "a small group of intended users"
    if not re.match(r"^(?:the|a|an|our|my|your|their|his|her|this|these|those)\b", pilot_group, re.IGNORECASE):
        pilot_group = "the " + pilot_group
    steps = [
        first_step,
        source_step,
        f"Prototype this direction: {recommendation}",
        safety_step,
        f"Try it with {pilot_group} on a small sample. Compare the measures below with today's process, collect feedback, and expand only if the results improve.",
    ]

    questions = []
    if not context.get("users"):
        questions.append("Who will use this first or be affected by it?")
    if not context.get("systems"):
        questions.append("Which tools, documents, or data are currently involved?")
    if not context.get("constraints") and len(questions) < 2:
        questions.append("What must stay under human review or never be automated?")

    opportunity = guide["use_case"] if guide else "A focused workflow improvement opportunity"
    data_note = (
        f"Start with a small, approved sample from **{source}**; confirm access, quality, ownership, and retention before use."
        if source and is_specific_tool_source(source)
        else "The data source was not specified. Confirm which approved records or documents can be used before selecting any data."
    )
    risk_note = guide["risk"] if guide else "The workflow and risks need discovery before choosing an automation method."

    answer_parts = [
        "**What I understood**\n" + category_line + " " + friction_line,
        f"**Match strength:** {match_strength} ({category_match_count} category keyword rule{'s' if category_match_count != 1 else ''} matched).",
        "**Suggested use case**\n" + opportunity + ". Treat this as a hypothesis to validate with the affected users, not a confirmed client requirement.",
        "**Recommended direction**\n" + recommendation,
        "**How the proposed workflow could work**\n"
        "1. A staff member provides a request or selects an approved source.\n"
        "2. The system identifies relevant details and drafts a suggested next step.\n"
        "3. It shows the source or reason behind the suggestion and flags missing information.\n"
        "4. A person checks, edits, and approves the result before it affects a customer or business record.",
        "**Practical pilot plan**\n" + "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1)),
        "**Data and safeguards**\n" + data_note + " " + safety_step + " Follow the client's privacy, access, and retention rules; do not use personal or confidential data without approval.",
        "**Main risk to manage**\n" + risk_note + " Check for incorrect or incomplete suggestions, and keep an easy human correction and escalation path.",
        "**What to measure**\nChoose two or three: " + ", ".join(metrics[:4]) + ".",
        "Set a baseline before the pilot and agree target improvements with the process owner; this prototype does not invent performance targets.",
    ]
    if questions:
        answer_parts.append("**Details to confirm**\n" + "\n".join(f"- {question}" for question in questions))
    answer_parts.append(
        "**Prototype scope**\nThe solution plan uses local keyword rules and built-in guides. A separate small classifier compares category predictions; it does not write the plan. The app does not connect to client systems or validate the proposal with real users."
    )
    return "\n\n".join(answer_parts)


def generate_assessment_addendum(text: str, context: dict) -> str:
    """Create practical MVP, acceptance, data, and evaluation guidance without inventing facts."""
    users = context.get("users") or "an affected user (not specified)"
    source = context.get("systems") or "Not specified"
    constraints = context.get("constraints") or "Not specified"
    category = context.get("category") or extract_client_context(text).get("category")
    guide = OPPORTUNITY_GUIDES.get(category or "")
    metrics = guide["metrics"][:3] if guide else ["Time per task", "Errors or rework", "User feedback"]

    questions = []
    if not context.get("users"):
        questions.append("Who performs this workflow, and who is affected by its outcome?")
    if not context.get("systems"):
        questions.append("Which approved documents, tools, or data sources are involved?")
    if not context.get("constraints"):
        questions.append("What privacy, security, approval, or automation limits must the solution follow?")
    questions.append("What baseline and target should the process owner use to decide whether a pilot succeeds?")

    return f"""## Suggested MVP features
1. Accept a problem statement and optional client context.
2. Extract only details explicitly stated and flag missing information.
3. Produce an editable first-pass opportunity brief with follow-up questions.
4. Keep a person responsible for reviewing recommendations and consequential actions.
5. Export the reviewed brief for discussion.

These are proposed MVP requirements; the current prototype demonstrates local extraction, rule-based categorization, report generation, and export.

## Example user story and acceptance checks
**User story:** As {users}, I want a first-pass brief from discovery notes so I can review the problem and next steps more consistently.

**Acceptance checks:**
- The brief reflects the problem statement and does not add unstated client facts.
- Missing users, systems, or constraints are labeled “Not specified” or asked as questions.
- A user can edit the context before generating the brief.
- The output identifies its local, rules-based nature and leaves important decisions to a human.

## Data checklist
- Problem statement: provided by the user.
- Intended users: {users}.
- Current tools or data: {source}.
- Constraints: {constraints}.
- Confirm before a real pilot: data owner, approved sample, access permissions, sensitive fields, retention period, and consent or other required approval.

## Suggested test scenarios
These are checks to run; they are not claimed test results.
1. **Complete statement:** include a workflow, affected users, and a named source; confirm the report uses those details accurately.
2. **Missing context:** omit users and systems; confirm the app leaves them unspecified and asks follow-up questions.
3. **Explicit safeguard:** state that a person must approve an action; confirm the safeguard appears in the proposed workflow.
4. **Unclear or out-of-scope statement:** confirm the app expresses uncertainty and recommends discovery rather than claiming a confident classification.

## Pilot measurement plan
First record the current baseline. Then select two or three measures with the process owner, for example: {", ".join(metrics)}. Define the measurement window and target with the owner; this prototype does not invent impact figures.

## Suggested implementation roadmap
1. **Discover:** confirm the process, affected users, data owner, and constraints.
2. **Prepare:** agree on approved examples, baseline measures, and acceptance checks.
3. **Pilot:** review outputs with a small user group and log corrections or unsafe suggestions.
4. **Decide:** refine, stop, or expand based on measured results and human feedback.

## Assumptions and questions to resolve
No client workflow, system access, data permission, or performance target is assumed beyond what was entered. Confirm:
""" + "\n".join(f"- {question}" for question in questions)


def prepare_chat_prompt() -> None:
    """Capture the draft and extract its context before rendering the reply."""
    text = st.session_state.get("chat_prompt", "").strip()
    if not text:
        return

    st.session_state.pop("example_status", None)
    st.session_state.pop("analysis_error", None)
    st.session_state.pop("analysis_unrecognized", None)
    st.session_state["problem"] = text
    if text != st.session_state.get("last_analysis_input"):
        extracted = extract_client_context(text)
        for key in ("client", "category", "users", "systems", "constraints"):
            st.session_state[key] = extracted[key]

    st.session_state["submitted_context"] = {
        key: st.session_state.get(key, "")
        for key in ("client", "category", "users", "systems", "constraints")
    }
    st.session_state["last_analysis_input"] = text
    st.session_state["analysis_stale"] = False
    st.session_state["pending_chat_prompt"] = text


def refresh_analysis_from_context() -> None:
    if "analysis" in st.session_state:
        st.session_state["analysis_stale"] = True


def load_example() -> None:
    example_index = (st.session_state.get("example_index", -1) + 1) % len(EXAMPLE_CASES)
    sample = dict(zip(("client", "category", "users", "systems", "constraints", "problem"), EXAMPLE_CASES[example_index]))
    st.session_state["example_index"] = example_index
    st.session_state["example_status"] = f"Example {example_index + 1} of {len(EXAMPLE_CASES)} loaded · review it in the message box, then press Send."
    for key, value in sample.items():
        if key != "problem":
            st.session_state[key] = value
    st.session_state["chat_prompt"] = sample["problem"]
    st.session_state["last_analysis_input"] = sample["problem"]
    st.session_state["submitted_context"] = {
        key: sample[key] for key in ("client", "category", "users", "systems", "constraints")
    }
    st.session_state["analysis_stale"] = "analysis" in st.session_state
    st.session_state.pop("analysis_error", None)
    st.session_state.pop("analysis_unrecognized", None)


def render_chat_assistant(message: dict, message_index: int, show_details: bool) -> None:
    """Render one assistant turn and keep secondary assessment material tucked away."""
    if message.get("error"):
        st.warning(message["content"])
        return

    st.markdown(message["content"])
    if not show_details or "result" not in message:
        return

    result = message["result"]
    metrics = message["classifier_metrics"]
    st.caption("This plan is generated locally from rules and built-in guides. Review it before using it with a client.")
    with st.expander("Category comparison, validation and downloads"):
        category_model, _ = get_category_classifier()
        rule_category = classify_category_by_rules(result["description"])
        ml_category, ml_probability = predict_category(category_model, result["description"])
        rule_column, ml_column = st.columns(2, gap="medium")
        with rule_column:
            st.metric("Rule-based category", rule_category or "No category match")
        with ml_column:
            st.metric("ML-predicted category", ml_category)
            st.caption(f"Estimated class probability: {ml_probability:.1%}")
        st.caption("Match strength counts category keyword rules. It is not a probability. The classifier is trained on 34 synthetic examples and is a demonstration, not production-ready.")
        st.caption(f"Measured 5-fold accuracy on those examples: keyword rules {metrics['rule_accuracy']:.1%}; ML classifier {metrics['ml_accuracy']:.1%}.")

        validation_tab, technical_tab = st.tabs(["MVP & validation", "Technical approach"])
        with validation_tab:
            with st.container(border=True):
                st.markdown(result.get("assessment_addendum", "No validation details are available."))
        technical_report_text = make_technical_report(result, metrics)
        with technical_tab:
            st.markdown("**Prototype flow** · local planning rules, a synthetic-trained category comparison, and human review")
            flow_steps = [
                ("1 · Input", "Problem statement and optional context"),
                ("2 · Classify", "Rules and a small ML model side by side"),
                ("3 · Draft", "Built-in guide creates a suggested brief"),
                ("4 · Review", "Person checks and edits recommendations"),
                ("5 · Export", "Word reports and CSV summary"),
            ]
            flow_columns = st.columns(len(flow_steps), gap="small")
            for flow_column, (flow_title, flow_copy) in zip(flow_columns, flow_steps):
                with flow_column:
                    with st.container(border=True):
                        st.markdown(f"**{flow_title}**")
                        st.caption(flow_copy)
            with st.container(border=True):
                st.markdown(technical_report_text)

        report = markdown_to_docx(make_report(result, metrics))
        technical_report = markdown_to_docx(technical_report_text)
        table = pd.DataFrame([{
            "client": result["context"].get("client", ""),
            "problem_statement": result["description"],
            "solution_approach": result["solution_approach"],
            "generated_with": "Built-in local rule-based planner with separate synthetic-trained ML category comparison; no API",
        }])
        report_col, technical_col, summary_col = st.columns(3, gap="medium")
        with report_col:
            st.download_button("Opportunity report (Word)", report, file_name="cynbit_ai_opportunity_report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", icon=":material/description:", width="stretch", key=f"opportunity_report_{message_index}")
        with technical_col:
            st.download_button("Technical approach (Word)", technical_report, file_name="cynbit_ai_technical_approach.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", icon=":material/build:", width="stretch", key=f"technical_report_{message_index}")
        with summary_col:
            st.download_button("Summary data (CSV)", table.to_csv(index=False), file_name="cynbit_ai_opportunity_summary.csv", mime="text/csv", icon=":material/download:", width="stretch", key=f"summary_csv_{message_index}")


def make_report(result: dict, classifier_metrics: dict[str, float]) -> str:
    """Build a detailed, assessment-ready opportunity report for the Word export."""
    context = result["context"]
    client = context.get("client", "") or "Not specified"
    category = context.get("category") or "Not specified"
    guide = OPPORTUNITY_GUIDES.get(category)
    use_case = guide["use_case"] if guide else "Focused workflow improvement with human review"
    recommendation = guide["approach"] if guide else (
        "Map the workflow, identify its slowest or most error-prone step, and test a narrow digital assistant or automation there."
    )
    main_risk = guide["risk"] if guide else (
        "The workflow and its risks need discovery before choosing an automation method."
    )
    metrics = guide["metrics"][:4] if guide else ["Time per task", "Errors or rework", "Backlog", "User feedback"]
    context_lines = "\n".join(
        f"- **{label}:** {context.get(key) or 'Not specified'}"
        for label, key in (
            ("Problem area", "category"),
            ("Intended users", "users"),
            ("Current tools or data", "systems"),
            ("Constraints", "constraints"),
        )
    )
    questions = []
    if not context.get("users"):
        questions.append("Who performs this workflow, and who is affected by its outcome?")
    if not context.get("systems"):
        questions.append("Which approved documents, tools, or data sources are involved?")
    if not context.get("constraints"):
        questions.append("What privacy, security, approval, or automation limits must the pilot follow?")
    questions.append("What baseline and target should the process owner use to decide whether the pilot succeeds?")
    question_lines = "\n".join(f"- {question}" for question in questions)
    example_count = len(EXAMPLE_CASES)

    return f"""# Cynbit AI Opportunity Report

**Client or project:** {client}
**Prepared:** {date.today().isoformat()}
**Assessment:** AI/ML opportunity identification and prototype

## Executive summary
This report evaluates a client discovery and requirements copilot as an opportunity to explore. It would help a consultant turn discovery notes into a structured first-pass brief, while leaving review and decisions with a person. The opportunity is a hypothesis based on the supplied problem statement and Cynbit's publicly described discovery, AI automation, and custom software positioning. It is not evidence that Cynbit has confirmed this internal need.

The current prototype demonstrates a local, rule-based planning workflow and a separate category-classification comparison. It does not connect to company systems or use a generative AI service. A small pilot should first validate the workflow, source data, safeguards, and success measures with the people who would use it.

## Problem statement and context
**Problem statement supplied:**
{result['description']}

**Context provided:**
{context_lines}

Missing details remain marked as not specified. The report does not infer a client identity, system, constraint, or business result that was not supplied.

## Opportunity selection
**Selected use case:** {use_case}

The selected opportunity is a discovery copilot that organizes stated needs, affected users, current tools, constraints, and open questions into a consultant-reviewed brief. It is a practical first candidate for this assessment because the output can be checked by a person and demonstrated without connecting to client data.

**Other opportunity hypotheses to validate:**
- A knowledge assistant that retrieves approved answers for repeated support questions and routes uncertain cases to staff.
- A document-intake assistant that extracts and validates fields from forms or invoices before a reviewer approves them.
- An internal request-triage assistant that summarizes requests and suggests a team or next action for staff review.

These are candidate ideas, not claims about Cynbit's current operations. Compare them with stakeholder interviews before selecting any for a real deployment. No financial benefit or opportunity ranking is assumed here.

**Public references for the opportunity hypothesis:** Cynbit website (https://www.cynbit.in/) and services page (https://www.cynbit.in/services). Verify current service details and validate this proposal with Cynbit stakeholders before submission or implementation.

[[PAGE_BREAK]]

## Proposed solution approach
{recommendation}

The app's current plan also identifies friction signals, suggests a human-reviewed pilot, lists possible measures, highlights a guide-specific risk, and raises questions for missing context. These outputs are starting points for discovery, not confirmed requirements.

## How a pilot could work
1. **Map the workflow:** observe how a discovery note is currently reviewed and turned into a requirements summary. Record handoffs, delays, repeated work, and corrections.
2. **Agree on inputs:** select a small, approved or synthetic sample. Confirm who owns it and what sensitive fields must be excluded.
3. **Draft a brief:** use the copilot to structure the problem, stated context, candidate use case, safeguards, and unanswered questions.
4. **Review with a person:** have a consultant verify every extracted detail and recommendation before sharing or acting on the brief.
5. **Compare and decide:** review feedback and agreed measures against the baseline. Refine, stop, or expand only after the process owner approves the evidence.

## Minimum viable pilot and validation
Start with a narrow workflow and a small reviewer group. The first version should accept a problem statement, extract only explicitly stated details, mark missing information, produce an editable brief, and export it for discussion. Keep client decisions and consequential actions under human control.

**Suggested measures:** choose two or three with the process owner from {", ".join(metrics)}. Record the existing baseline first, define how each measure will be collected, and agree a target before the pilot. This report does not claim time savings, accuracy improvement, or financial return.

**Checks before expanding:** verify that the brief does not add unstated facts; check category and context extraction; confirm reviewers can correct the result; and record omissions, unsupported suggestions, and user feedback. The built-in examples are synthetic test scenarios, not client evidence.

## Risks, safeguards, and open questions
**Main risk to manage:** {main_risk}

Also confirm that approved data is used, access is limited to the intended reviewers, retention rules are understood, and uncertain or sensitive cases are escalated. Keep a clear correction path and do not automate irreversible decisions in the first pilot.

**Questions to resolve with stakeholders:**
{question_lines}

## Prototype evidence and limitations
The solution approach is generated by local keyword rules and fixed opportunity guides. A separate TF-IDF + Logistic Regression model predicts a category; it does not generate the plan. Stratified five-fold cross-validation on {example_count} synthetic examples measured **{classifier_metrics['rule_accuracy']:.1%}** accuracy for the keyword rules and **{classifier_metrics['ml_accuracy']:.1%}** for the ML classifier. This small synthetic set is a demonstration, not production evidence, and the ML classifier should not be treated as production-ready.

The prototype has no client-system integration, generative AI service, or validated client-specific impact estimate. The recommended next step is stakeholder discovery and a controlled pilot proposal, not a production rollout.
"""


def make_technical_report(result: dict, classifier_metrics: dict[str, float]) -> str:
    context = result["context"]
    category = context.get("category") or "Not specified"
    return f"""# Cynbit AI Technical Approach Report

**Prepared:** {date.today().isoformat()}
**Prototype:** Cynbit AI Project Copilot
**Implementation status:** Local assessment prototype; no external AI service or client system connection

## 1. Scope and objective
Demonstrate how a client discovery note could be converted into a structured first-pass opportunity brief. The consultant remains responsible for validating details and approving recommendations.

## 2. Current prototype architecture
**Flow:** Problem statement + optional context → local detail extraction → rule and ML category comparison → built-in opportunity guide → rule-based draft brief → user review and Word/CSV export.

1. Streamlit collects the problem statement and optional context fields.
2. Local regular-expression rules extract only details explicitly present in the statement.
3. Keyword rules classify the likely workflow and identify friction signals. A separate TF-IDF + Logistic Regression classifier predicts a category for side-by-side comparison.
4. A built-in guide provides a matching starting direction, measures, risks, and follow-up questions.
5. The app renders the report and exports Word and CSV files.

The solution plan remains a deterministic rules-based baseline. The comparison classifier is trained locally on only 34 synthetic examples and is a demonstration, not production-ready. The app has no generative language model, needs no API key, and does not send the statement to a provider.

## 3. Inputs and data pipeline
- Problem statement: {result['description']}
- Problem area: {category}
- Intended users: {context.get('users') or 'Not specified'}
- Current tools or data: {context.get('systems') or 'Not specified'}
- Constraints: {context.get('constraints') or 'Not specified'}

The current prototype uses the user-entered text and optional context only. Production data sources, retention rules, access permissions, and data quality are not specified and must be agreed before any integration.

## 4. Model and prompt approach
The solution plan uses transparent keyword rules and fixed guides. The category comparison uses TF-IDF features with Logistic Regression, trained on the 34 synthetic examples. The held-out 5-fold cross-validation accuracy measured on those examples was {classifier_metrics['ml_accuracy']:.1%} for the ML classifier; the rule baseline scored {classifier_metrics['rule_accuracy']:.1%}. These small synthetic-data results are demonstration measurements, not evidence of production performance. There is no generative model or prompt.

## 5. Output contract and human review
The app returns a problem interpretation, opportunity hypothesis, proposed workflow, practical pilot steps, data safeguards, risks, measures, and unanswered questions. Missing details are labeled as not specified or presented as questions. A human should review the output before it is used for a client decision.

## 6. Evaluation plan
On the 34 synthetic examples, 5-fold cross-validation measured {classifier_metrics['rule_accuracy']:.1%} accuracy for keyword rules and {classifier_metrics['ml_accuracy']:.1%} for TF-IDF + Logistic Regression. This small demonstration set is not representative of production. Review category classification and extracted details on a larger, approved set before drawing conclusions. In a pilot, track two or three agreed operational measures, such as time per brief, correction rate, and consultant acceptance. Set target thresholds with the process owner; this report does not invent targets.

## 7. Risks and controls
- Incorrect classification: show the detected category and allow the user to correct context.
- Missing or unsupported details: label gaps and ask questions rather than guessing.
- Sensitive information: use synthetic or approved data for the prototype; define access and retention before production use.
- Over-reliance on recommendations: require consultant review and keep final decisions with a person.
- Template limitations: expand and evaluate the local rules against representative examples before relying on them.

## 8. Execution plan
1. Confirm the use case, users, current workflow, and constraints through discovery.
2. Agree on approved sample data, privacy controls, baseline measures, and acceptance criteria.
3. Test the current local prototype with representative synthetic or approved examples and record errors.
4. Refine extraction rules and report templates; have consultants review every output.
5. Collect a larger, representative, approved dataset and compare the rules and ML classifier before deciding whether the ML component is useful beyond this demonstration.

## 9. Known limitations
The prototype does not connect to source systems, retrieve or cite documents, call a generative AI service, learn from feedback, or provide validated client-specific performance estimates. Its category guides and rules are hand-authored. The comparison classifier is trained on only 34 synthetic examples and must not be treated as production-ready.
"""


def markdown_to_docx(markdown: str) -> bytes:
    """Turn the app's simple Markdown report into a formatted Word document."""
    output = BytesIO()
    paragraphs = []

    def paragraph(text: str, style: str = "Normal") -> str:
        runs = []
        for chunk in re.split(r"(\*\*.*?\*\*)", text):
            if not chunk:
                continue
            bold = chunk.startswith("**") and chunk.endswith("**")
            content = chunk[2:-2] if bold else chunk
            run_properties = "<w:rPr><w:b/></w:rPr>" if bold else ""
            runs.append(f'<w:r>{run_properties}<w:t xml:space="preserve">{escape(content)}</w:t></w:r>')
        return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{"".join(runs)}</w:p>'

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line == "[[PAGE_BREAK]]":
            paragraphs.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        elif line.startswith("# "):
            paragraphs.append(paragraph(line[2:].strip().rstrip(":"), "Title"))
        elif line.startswith("## "):
            heading = re.sub(r"^\d+\.\s*", "", line[3:]).strip().rstrip(":")
            paragraphs.append(paragraph(heading, "Heading1"))
        elif line.startswith("- "):
            paragraphs.append(paragraph("•  " + line[2:]))
        elif re.match(r"^\d+\.\s", line):
            number, content = line.split(".", 1)
            paragraphs.append(paragraph(f"{number}.  {content.strip()}"))
        else:
            paragraphs.append(paragraph(line))

    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{"".join(paragraphs)}
<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1150" w:bottom="1000" w:left="1150" w:header="500" w:footer="500" w:gutter="0"/></w:sectPr></w:body></w:document>'''
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="21"/><w:color w:val="28303A"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="100" w:line="260" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:rPr><w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/><w:b/><w:sz w:val="48"/><w:color w:val="1B3E61"/></w:rPr><w:pPr><w:spacing w:after="180"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="9"/><w:qFormat/><w:rPr><w:rFonts w:ascii="Aptos Display" w:hAnsi="Aptos Display"/><w:b/><w:sz w:val="30"/><w:color w:val="1B3E61"/></w:rPr><w:pPr><w:keepNext/><w:spacing w:before="180" w:after="80"/></w:pPr></w:style>
</w:styles>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
    package_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
    document_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''

    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", package_rels)
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/_rels/document.xml.rels", document_rels)
        archive.writestr("word/styles.xml", styles_xml)
    return output.getvalue()


for key, initial in {
    "client": "",
    "category": None,
    "users": "",
    "systems": "",
    "constraints": "",
    "problem": "",
}.items():
    st.session_state.setdefault(key, initial)

st.html("""
<section class="copilot-hero" aria-label="Cynbit AI Project Copilot">
  <div class="hero-copy">
    <h1 class="hero-title">Cynbit AI<br><span>Project Copilot</span></h1>
  </div>
  <div class="hero-orbit" aria-hidden="true"><div class="hero-core"></div></div>
</section>
""")
st.caption("Client discovery and AI opportunity analysis · assessment prototype")
st.html('<p class="hero-description">Turn a client\'s challenge into a structured first-pass opportunity brief for a human consultant to review.</p>')

with st.expander("Why this opportunity?", icon=":material/lightbulb:"):
    st.write("**Selected opportunity hypothesis:** a client discovery copilot that organizes problem statements and discovery notes into a first-pass brief: problem area, affected users, current tools, constraints, a possible solution approach, and questions to confirm.")
    st.write("This is a proposal based on Cynbit's public positioning, not a claim about its internal workflow. Cynbit describes a **Discovery & Audit** stage and AI automation/custom software services on its [website](https://www.cynbit.in/) and [services page](https://www.cynbit.in/services).")

with st.sidebar:
    st.header("Client context", icon=":material/folder_shared:")
    st.caption("The rules-based planner runs locally. No API key or internet connection is needed.")
    client = st.text_input("Client or project name", key="client", on_change=refresh_analysis_from_context)
    category = st.selectbox("Problem area", list(OPPORTUNITY_GUIDES), index=None, placeholder="Select if specified", key="category", on_change=refresh_analysis_from_context)
    users = st.text_input("Who has this problem?", key="users", on_change=refresh_analysis_from_context)
    systems = st.text_input("Current tools or data", key="systems", on_change=refresh_analysis_from_context)
    constraints = st.text_input("Constraints to consider", key="constraints", on_change=refresh_analysis_from_context)
    st.caption("Appearance")
    st.radio("Theme", ["Dark", "Light"], horizontal=True, key="theme_mode", label_visibility="collapsed")

st.session_state.setdefault("chat_messages", [])
st.session_state.setdefault("chat_turn_counter", 0)
st.caption("Describe a client challenge. The local planner will reply with a first-pass solution approach.")

with st.expander("How this prototype works", icon=":material/info:"):
    st.write("**Prototype pipeline:** problem statement and optional context → extraction of explicitly stated details → local rules and a small ML classifier compare workflow categories → a built-in opportunity guide drafts the approach, measures, and missing-detail questions → consultant review and Word/CSV export.")
    st.write("The solution plan remains deterministic and rules-based. The separate TF-IDF + Logistic Regression category classifier is trained on only 34 synthetic examples and is a demonstration, not production-ready. It uses no API and makes no external requests.")

if "example_status" in st.session_state:
    st.caption(st.session_state["example_status"])
st.caption("Private by design: your problem statement stays in this app and is not sent to an AI service.")

if st.session_state.get("analysis_stale"):
    st.info("Client context changed. Your next message will use the updated details.")

if not st.session_state["chat_messages"]:
    with st.chat_message("assistant"):
        st.markdown("Tell me about a client challenge and I’ll suggest a practical starting approach. Include who is affected, what is difficult today, and any tools or constraints you know.")

for message_index, message in enumerate(st.session_state["chat_messages"]):
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            render_chat_assistant(
                message,
                message.get("turn_id", message_index),
                show_details=message_index == len(st.session_state["chat_messages"]) - 1,
            )

with st.bottom:
    input_column, example_column = st.columns([5.2, 1.35], vertical_alignment="bottom")
    with input_column:
        with st.form("chat_composer", clear_on_submit=True, border=False):
            text_column, send_column = st.columns([5.5, 1], vertical_alignment="bottom")
            with text_column:
                st.text_area(
                    "Message",
                    key="chat_prompt",
                    placeholder="Describe the client's challenge...",
                    height=74,
                    label_visibility="collapsed",
                )
            with send_column:
                st.form_submit_button(
                    "Send",
                    icon=":material/arrow_upward:",
                    type="primary",
                    on_click=prepare_chat_prompt,
                    use_container_width=True,
                )
    with example_column:
        st.button(
            "Load example",
            icon=":material/quick_reference:",
            on_click=load_example,
            use_container_width=True,
        )
submitted_prompt = st.session_state.pop("pending_chat_prompt", None)

if submitted_prompt:
    text = submitted_prompt.strip()
    if text:
        st.session_state["chat_turn_counter"] += 1
        turn_id = st.session_state["chat_turn_counter"]
        user_message = {"role": "user", "content": text}
        st.session_state["chat_messages"].append(user_message)
        with st.chat_message("user"):
            st.markdown(text)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Putting together a practical approach..."):
                    context = st.session_state.get("submitted_context", {})
                    answer = generate_local_solution_approach(text, context)
                    if answer is not None:
                        result = {
                            "description": text,
                            "solution_approach": answer,
                            "assessment_addendum": generate_assessment_addendum(text, context),
                            "context": context,
                        }
                        _, classifier_metrics = get_category_classifier()
                if answer is None:
                    assistant_message = {
                        "role": "assistant",
                        "content": "I couldn't recognize this problem type. Try adding who is affected, what is slow or difficult, and which tools are used.",
                        "error": True,
                        "turn_id": turn_id,
                    }
                    st.session_state.pop("analysis", None)
                    st.warning(assistant_message["content"])
                else:
                    assistant_message = {
                        "role": "assistant",
                        "content": answer,
                        "result": result,
                        "classifier_metrics": classifier_metrics,
                        "turn_id": turn_id,
                    }
                    st.session_state["analysis"] = result
                    st.session_state["analysis_stale"] = False
                    render_chat_assistant(assistant_message, turn_id, show_details=True)
            except Exception as exc:
                assistant_message = {
                    "role": "assistant",
                    "content": f"I couldn't generate the solution approach: {exc}",
                    "error": True,
                    "turn_id": turn_id,
                }
                st.error(assistant_message["content"])

        st.session_state["chat_messages"].append(assistant_message)
