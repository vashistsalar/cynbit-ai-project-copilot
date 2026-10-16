from __future__ import annotations

from datetime import date
from io import BytesIO
import re
from html import escape
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import streamlit as st


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
@keyframes ambient-drift {
  0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
  50% { transform: translate3d(2%, -1%, 0) scale(1.04); }
}
@keyframes orbit {
  to { transform: rotate(360deg); }
}
@keyframes breathe {
  0%, 100% { transform: scale(.96); opacity: .75; }
  50% { transform: scale(1.04); opacity: 1; }
}
@keyframes rise-in {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

.stApp {
  background:
    radial-gradient(ellipse at 75% 0%, rgba(26, 121, 132, .16), transparent 38%),
    radial-gradient(ellipse at 5% 45%, rgba(42, 73, 129, .12), transparent 35%),
    #071019;
}
.stApp::before {
  content: "";
  position: fixed;
  inset: -20%;
  z-index: 0;
  pointer-events: none;
  opacity: .2;
  background:
    radial-gradient(ellipse at 24% 28%, rgba(61, 222, 196, .13), transparent 33%),
    radial-gradient(ellipse at 78% 70%, rgba(69, 112, 221, .12), transparent 36%);
  filter: blur(34px);
  animation: ambient-drift 18s ease-in-out infinite;
}
.stApp > header { background: transparent; }
.stMainBlockContainer {
  position: relative;
  z-index: 1;
  max-width: 1180px;
  padding-top: 3rem;
  padding-bottom: 4rem;
}
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(12, 28, 40, .98), rgba(8, 18, 28, .98));
  border-right: 0;
}
section[data-testid="stSidebar"] > div { padding-top: 1.35rem; }
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
  background: rgba(7, 17, 26, .34);
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
  background: rgba(75, 205, 180, .12);
}
section[data-testid="stSidebar"] [data-testid="stRadioGroup"] [data-testid="stMarkdownContainer"] p {
  margin: 0;
  font-size: .82rem;
  font-weight: 600;
}
.stMarkdown, [data-testid="stCaptionContainer"] { color: #a8bac6; }
h1, h2, h3 { letter-spacing: -.035em; }
.challenge-title {
  margin: 0;
  text-align: center;
  font-size: 1.75rem;
  font-weight: 600;
  letter-spacing: -.035em;
  text-shadow: 0 0 34px rgba(112, 240, 208, .2);
}
div[data-testid="stVerticalBlockBorderWrapper"] {
  border: 0;
  border-radius: 18px;
  background: radial-gradient(ellipse at 50% 0%, rgba(23, 83, 91, .2), transparent 72%);
  box-shadow: none;
  animation: rise-in .55s ease-out both;
}
div[data-testid="stMetric"] {
  min-height: 118px;
  padding: 1rem 1.1rem;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(145deg, rgba(19, 42, 54, .88), rgba(11, 26, 38, .82));
  transition: border-color .2s ease, transform .2s ease;
}
div[data-testid="stMetric"]:hover {
  transform: translateY(-3px);
  box-shadow: 0 0 34px rgba(112, 240, 208, .12);
}
div[data-testid="stMetricLabel"] { color: #a8bac6; }
div[data-testid="stMetricValue"] { color: #e9f5f5; }
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-color: transparent;
  border-radius: 11px;
  background-color: rgba(7, 17, 26, .72);
  transition: border-color .2s ease, box-shadow .2s ease;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: #70f0d0;
  box-shadow: 0 0 0 3px rgba(112, 240, 208, .12);
}
div[data-testid="stButton"] button,
div[data-testid="stDownloadButton"] button {
  border-radius: 11px;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
div[data-testid="stButton"] button:hover,
div[data-testid="stDownloadButton"] button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(55, 208, 183, .16);
  border-color: rgba(112, 240, 208, .55);
}
div[data-testid="stButton"] button[kind="primary"] {
  box-shadow: 0 0 24px rgba(55, 208, 183, .16);
}
.copilot-hero {
  position: relative;
  display: flex;
  min-height: 124px;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;
  margin: 0 0 .65rem;
  padding: .75rem 1.5rem;
  border: 0;
  border-radius: 0;
  background: radial-gradient(ellipse at 78% 48%, rgba(30, 130, 137, .13), transparent 34%);
  box-shadow: none;
  animation: rise-in .7s ease-out both;
}
.hero-copy { position: relative; z-index: 2; max-width: 100%; }
.hero-eyebrow {
  display: flex;
  align-items: center;
  gap: .6rem;
  margin: 0 0 1rem;
  color: #8ca8b2;
  font: 600 .7rem/1.4 "Segoe UI", sans-serif;
  letter-spacing: .16em;
}
.hero-signal {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #70f0d0;
  box-shadow: 0 0 12px #70f0d0;
  animation: breathe 2.4s ease-in-out infinite;
}
.hero-title {
  margin: 0;
  color: #edf7f7;
  font: 700 clamp(1.8rem, 4vw, 2.4rem)/1.08 "Segoe UI", sans-serif;
  letter-spacing: -.065em;
}
.hero-title span {
  white-space: nowrap;
  color: #70f0d0;
  text-shadow: 0 0 32px rgba(112, 240, 208, .2);
}
.hero-description {
  max-width: 570px;
  margin: 1rem 0 0;
  color: #a8bac6;
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
  opacity: .4;
  border: 0;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(65, 184, 166, .12), transparent 68%);
  box-shadow: 0 0 80px rgba(59, 191, 181, .09);
}
.hero-orbit::before, .hero-orbit::after {
  position: absolute;
  inset: 12px;
  border: 0;
  border-radius: 50%;
  content: "";
  animation: orbit 18s linear infinite;
}
.hero-orbit::after {
  inset: 31px -7px;
  border-color: rgba(112, 170, 240, .24);
  transform: rotate(-35deg);
  animation-duration: 24s;
  animation-direction: reverse;
}
.hero-core {
  width: 58px;
  height: 58px;
  border: 0;
  border-radius: 50%;
  background: radial-gradient(circle at 38% 34%, #b5fff0, #45d4b7 24%, #117a84 62%, #102c40);
  box-shadow: 0 0 28px rgba(74, 230, 201, .62), 0 0 76px rgba(74, 230, 201, .24);
  animation: breathe 4s ease-in-out infinite;
}
@media (max-width: 700px) {
  .stMainBlockContainer { padding: .6rem 1rem 3rem; }
  .copilot-hero { min-height: 130px; padding: .75rem 1.1rem; }
  .hero-orbit { position: absolute; right: -62px; width: 140px; height: 140px; opacity: .38; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    scroll-behavior: auto !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
  }
}
</style>
""")

if st.session_state["theme_mode"] == "Light":
    st.html("""
    <style>
    .stApp {
      background:
        radial-gradient(ellipse at 75% 0%, rgba(50, 167, 163, .12), transparent 38%),
        radial-gradient(ellipse at 5% 45%, rgba(86, 133, 201, .10), transparent 35%),
        #f3f7fa;
      color: #20313f;
    }
    .stApp::before {
      opacity: .24;
    }
    section[data-testid="stSidebar"] {
      background: linear-gradient(180deg, rgba(250, 253, 255, .98), rgba(238, 245, 249, .98));
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
      color: #263b49 !important;
      opacity: 1 !important;
    }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] p,
    [data-testid="stHeadingWithActionElements"] h1,
    [data-testid="stHeadingWithActionElements"] h2,
    [data-testid="stHeadingWithActionElements"] h3,
    [data-testid="stWidgetLabel"] * { color: #344b5b !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
      border: 0;
      background: radial-gradient(ellipse at 50% 0%, rgba(183, 231, 231, .28), transparent 72%);
      box-shadow: none;
    }
    div[data-testid="stMetric"] {
      border: 0;
      background: linear-gradient(145deg, #ffffff, #eef5f8);
    }
    div[data-testid="stMetricLabel"] { color: #526575; }
    div[data-testid="stMetricValue"] { color: #20313f; }
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
      color: #20313f !important;
      border-color: transparent !important;
      background-color: #ffffff !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] * {
      color: #20313f !important;
    }
    div[data-testid="stSelectbox"] div[role="group"] {
      border: 0 !important;
      border-radius: 11px;
      background: #ffffff !important;
    }
    div[data-testid="stSelectbox"] input[role="combobox"] {
      color: #20313f !important;
      background: transparent !important;
    }
    div[data-testid="stSelectbox"] button {
      color: #526575 !important;
      background: transparent !important;
    }
    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder { color: #778895; }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
      border-color: #168f83;
      box-shadow: 0 0 0 3px rgba(22, 143, 131, .13);
    }
    section[data-testid="stSidebar"] [data-testid="stRadioGroup"] {
      border-color: #d5e0e7;
      background: #eaf1f5;
    }
    section[data-testid="stSidebar"] [data-testid="stRadioGroup"] > div[data-selected="true"] [data-testid="stRadioOption"] {
      background: #ffffff;
      box-shadow: 0 1px 4px rgba(29, 54, 72, .12);
    }
    .hero-title { color: #20313f; }
    .hero-title span { color: #087e78; text-shadow: 0 0 28px rgba(8, 126, 120, .13); }
    .hero-orbit { opacity: .28; }
    div[data-testid="stButton"] button:not([kind="primary"]),
    div[data-testid="stDownloadButton"] button {
      color: #20313f;
      border-color: #c8d6df;
      background: rgba(255, 255, 255, .82);
    }
    div[data-testid="stButton"] button[kind="primary"] {
      color: #ffffff;
      background: #0f766e;
    }
    header[data-testid="stHeader"] { background: rgba(243, 247, 250, .88); }
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

# Synthetic scenarios for the explicit Load example action (not used as initial values).
# Tuple fields: client, category, users, tools/data, constraints, problem statement.
EXAMPLE_CASES = [
    ("Sample Retail Co.", "Customer support", "Support team", "Shared inbox and FAQ documents", "Human approval for customer-facing answers", "Our support team receives many repetitive questions each day. Staff search several documents before replying, so response times are slow and answers can be inconsistent."),
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

    category_rules = [
        ("Customer support", r"\b(customer support|support team|support ticket|customer service|help desk|FAQ|customer questions)\b"),
        ("Sales and lead management", r"\b(sales|lead|prospect|sales pipeline|CRM pipeline)\b"),
        ("Document processing", r"\b(invoice|document processing|data entry|OCR|form extraction|extract(?:ing)? data from documents)\b"),
        ("Internal workflow", r"\b(internal workflow|approval workflow|task routing|workflow|work order)\b"),
        ("Product or service idea", r"\b(new product|product idea|product feature|product concept)\b"),
    ]
    for label, pattern in category_rules:
        if re.search(pattern, text, re.IGNORECASE):
            context["category"] = label
            break

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


def generate_local_solution_approach(text: str, context: dict) -> str:
    """Build a tailored solution plan from local rules and the supplied context."""
    category = context.get("category") or extract_client_context(text)["category"]
    guide = OPPORTUNITY_GUIDES.get(category)
    statement = re.sub(r"\s+", " ", text).strip()
    lower_text = statement.lower()

    signals = []
    signal_rules = [
        (r"\b(manual(?:ly)?|repetitive|repeated|again and again|copy(?:ing)?|re-enter)\b", "repeated manual work"),
        (r"\b(delay(?:ed|s)?|slow|wait(?:ing)?|backlog|takes? too long|late)\b", "delays or a growing backlog"),
        (r"\b(error|mistake|inconsistent|duplicate|miss(?:ed|ing)|incorrect)\b", "errors, inconsistency, or missed work"),
        (r"\b(search|find|look(?:ing)? up|hunt(?:ing)?)\b", "time spent finding information"),
        (r"\b(overwhelmed|high volume|too many|large number|busy periods?)\b", "high or uneven workload"),
    ]
    for pattern, signal in signal_rules:
        if re.search(pattern, lower_text):
            signals.append(signal)

    if not guide:
        # Fall back to a broad local classification when the user leaves the
        # category field blank. These rules use only terms in the statement.
        fallback_rules = [
            ("Customer support", r"\b(customer|support|ticket|FAQ|help desk|questions?)\b"),
            ("Sales and lead management", r"\b(sales|lead|prospect|enquir(?:y|ies)|follow-up)\b"),
            ("Document processing", r"\b(invoice|PDF|form|document|spreadsheet|data entry|extract)\b"),
            ("Internal workflow", r"\b(workflow|approval|routing|request|work order|schedule|triage)\b"),
            ("Product or service idea", r"\b(product|feature|prototype|customers want|we want to build)\b"),
        ]
        category = next((name for name, pattern in fallback_rules if re.search(pattern, lower_text)), None)
        guide = OPPORTUNITY_GUIDES.get(category)

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
        friction_line = "The friction signals I found are " + ", ".join(signals[:3]) + "."
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
    if source:
        source_step = f"Use **{source}** as the first test source, and verify a small sample with the people who know it."
    else:
        source_step = "Identify which documents, systems, or records contain the information needed; this was not specified."

    constraint = context.get("constraints")
    if constraint:
        safety_step = f"Build in the stated safeguard: **{constraint}**. Keep a person able to review and correct the result."
    else:
        safety_step = "Keep a person reviewing important outputs. Do not automate payments, access changes, customer promises, or other irreversible decisions in the first pilot."

    pilot_group = context.get("users") or "a small group of intended users"
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

    answer_parts = [
        "**What I understood**\n" + category_line + " " + friction_line,
        "**Recommended direction**\n" + recommendation,
        "**A practical plan**\n" + "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1)),
        "**What to measure**\nChoose two or three: " + ", ".join(metrics[:4]) + ".",
    ]
    if questions:
        answer_parts.append("**Details to confirm**\n" + "\n".join(f"- {question}" for question in questions))
    return "\n\n".join(answer_parts)


def analyze_requirements() -> None:
    st.session_state.pop("example_status", None)
    st.session_state.pop("analysis_error", None)
    text = st.session_state.get("problem", "").strip()
    st.session_state.pop("analysis", None)
    if not text:
        st.session_state["analysis_error"] = "Enter a problem statement first."
        st.session_state["analysis_requested"] = False
        return

    previous_problem = st.session_state.get("last_analysis_input")
    if text != previous_problem:
        extracted = extract_client_context(text)
        for key in ("client", "category", "users", "systems", "constraints"):
            st.session_state[key] = extracted[key]

    context = {key: st.session_state.get(key, "") for key in ("client", "category", "users", "systems", "constraints")}
    st.session_state["submitted_context"] = context
    st.session_state["last_analysis_input"] = text
    st.session_state["analysis_stale"] = False
    st.session_state["analysis_requested"] = True


def refresh_analysis_from_context() -> None:
    if "analysis" in st.session_state:
        st.session_state["analysis_stale"] = True


def load_example() -> None:
    example_index = (st.session_state.get("example_index", -1) + 1) % len(EXAMPLE_CASES)
    sample = dict(zip(("client", "category", "users", "systems", "constraints", "problem"), EXAMPLE_CASES[example_index]))
    st.session_state["example_index"] = example_index
    st.session_state["example_status"] = f"Loaded example {example_index + 1} of {len(EXAMPLE_CASES)} · {sample['client']}"
    for key, value in sample.items():
        st.session_state[key] = value
    st.session_state["last_analysis_input"] = sample["problem"]
    st.session_state["analysis_requested"] = False
    st.session_state["analysis_stale"] = False
    st.session_state.pop("analysis", None)
    st.session_state.pop("analysis_error", None)


def make_report(client: str, result: dict) -> str:
    generated_with = "Built-in local planner (rule-based; no API)"
    return f"""# Solution Approach

**Client or project:** {client or 'Not specified'}
**Prepared:** {date.today().isoformat()}
**Generated with:** {generated_with}

## Problem statement
{result['description']}

## Solution plan
{result['solution_approach']}

## Context provided
- Problem area: {result['context'].get('category') or 'Not specified'}
- Intended users: {result['context'].get('users') or 'Not specified'}
- Current tools or data: {result['context'].get('systems') or 'Not specified'}
- Constraints: {result['context'].get('constraints') or 'Not specified'}

Confirm the approach with the people who do the work before building a solution.
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
        if line.startswith("# "):
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
st.caption("Enter a client challenge to get a clear, practical solution plan.")

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

with st.container():
    st.html('<h3 class="challenge-title">Define the challenge</h3>')
    st.caption("Describe the current workflow, where it gets stuck, and what a better outcome looks like.")
    problem = st.text_area("What is difficult today, how often does it happen, and what outcome is desired?", height=150,
        placeholder="For example: Our support team spends too much time searching documents to answer repeated questions...", key="problem", on_change=refresh_analysis_from_context)

analyze_button, example_button = st.columns([3, 2], gap="medium")
with analyze_button:
    st.button("Generate solution approach", type="primary", icon=":material/auto_awesome:", on_click=analyze_requirements, width="stretch")
with example_button:
    st.button("Load example", icon=":material/quick_reference:", on_click=load_example, width="stretch")
if "example_status" in st.session_state:
    st.caption(st.session_state["example_status"])
else:
    st.caption(f"Load example cycles through {len(EXAMPLE_CASES)} synthetic scenarios.")
st.caption("Private by design: your problem statement stays in this app and is not sent to an AI service.")

if st.session_state.pop("analysis_requested", False):
    try:
        with st.spinner("Building a tailored local solution plan..."):
            text = st.session_state.get("problem", "").strip()
            context = st.session_state.get("submitted_context", {})
            answer = generate_local_solution_approach(text, context)
        st.session_state["analysis"] = {
            "description": text,
            "solution_approach": answer,
            "context": context,
        }
        st.session_state["analysis_stale"] = False
    except Exception as exc:
        st.session_state["analysis_error"] = f"The local planner could not build an approach: {exc}"

if st.session_state.get("analysis_error"):
    st.error(f"Could not generate the solution approach: {st.session_state['analysis_error']}")
if st.session_state.get("analysis_stale"):
    st.info("Your problem statement or context changed. Generate the solution approach again to update it.")

if "analysis" in st.session_state:
    result = st.session_state["analysis"]
    if "solution_approach" not in result:
        st.session_state.pop("analysis", None)
    else:
        st.header("Solution approach", icon=":material/insights:")
        st.info("Built locally from the problem details and planning rules. No information is sent to an AI service.")
        with st.container(border=True):
            st.markdown(result["solution_approach"])
        st.subheader("Export your approach")
        report_col, summary_col = st.columns(2)
        report = markdown_to_docx(make_report(client, result))
        table = pd.DataFrame([{
            "client": client,
            "problem_statement": result["description"],
            "solution_approach": result["solution_approach"],
            "generated_with": "Built-in local planner (rule-based; no API)",
        }])
        with report_col:
            st.download_button("Download solution plan (Word)", report, file_name="cynbit_solution_approach.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", icon=":material/description:", width="stretch")
        with summary_col:
            st.download_button("Download solution plan (CSV)", table.to_csv(index=False), file_name="cynbit_solution_approach.csv", mime="text/csv", icon=":material/download:", width="stretch")

with st.expander("How this prototype works", icon=":material/info:"):
    st.write("The planner runs entirely inside this app. It uses local keyword patterns to identify a likely workflow type and pain points, combines those with your optional context, then builds a plan, measures, and follow-up questions from built-in guides. It does not call an external language model, so its answers are predictable and private but less open-ended than a generative AI service.")
