from __future__ import annotations

from datetime import date
from io import BytesIO
import re
from html import escape
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import streamlit as st


st.set_page_config(page_title="Cynbit AI Project Copilot", page_icon="🧭", layout="wide")

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


def assess(text: str, category: str, users: str, systems: str, constraints: str) -> dict:
    guide = OPPORTUNITY_GUIDES[category]
    words = {w.strip(".,!?;:").lower() for w in text.split()}
    signals = {
        "repetitive work": bool(words & {"manual", "repetitive", "copy", "duplicate", "routine", "re-enter"}),
        "high volume": bool(words & {"many", "volume", "daily", "thousands", "frequent", "scale"}),
        "slow turnaround": bool(words & {"slow", "delay", "wait", "backlog", "late", "time"}),
        "quality issues": bool(words & {"error", "errors", "inconsistent", "miss", "mistake", "quality"}),
        "information overload": bool(words & {"search", "find", "documents", "knowledge", "unstructured", "scattered"}),
    }
    score = 2 + sum(signals.values())
    readiness = "Needs discovery" if not text.strip() else "Promising pilot" if score >= 5 else "Needs validation"
    if not systems.strip() or not constraints.strip():
        readiness = "Needs discovery" if readiness != "Needs discovery" else readiness
    evidence = [name for name, found in signals.items() if found]
    if not evidence:
        evidence = ["No clear automation signal found in the description"]
    return {
        "category": category,
        "use_case": guide["use_case"],
        "readiness": readiness,
        "score": score,
        "signals": evidence,
        "approach": guide["approach"],
        "metrics": guide["metrics"],
        "risk": guide["risk"],
        "users": users.strip() or "To be confirmed during discovery",
        "systems": systems.strip() or "To be confirmed during discovery",
        "constraints": constraints.strip() or "To be confirmed during discovery",
        "description": text.strip() or "No problem description provided.",
    }


def make_report(client: str, result: dict) -> str:
    metrics = "\n".join(f"- {item}" for item in result["metrics"])
    signals = "\n".join(f"- {item}" for item in result["signals"])
    return f"""# Client Opportunity Brief {client or 'New client'}

**Prepared:** {date.today().isoformat()}  
**Status:** {result['readiness']}  
**Prototype score:** {result['score']}/7 (heuristic, not a validated prediction)

## Client problem
{result['description']}

## Recommended opportunity
**{result['use_case']}**

**Why it may fit:**
{signals}

## Proposed approach
{result['approach']}

## Discovery details
- Intended users: {result['users']}
- Current tools or data: {result['systems']}
- Constraints: {result['constraints']}

## Pilot success measures
{metrics}

## Main risk and safeguard
{result['risk']}

## Suggested next steps
1. Confirm the problem, current baseline, and who experiences it.
2. Check data access, quality, privacy, and integrations with the client.
3. Prototype one narrow workflow using sample or approved data.
4. Compare the pilot with the baseline and gather user feedback.
5. Expand only if the agreed measures improve without unacceptable risk.

## Limitations
This educational demo uses keyword signals and a fixed opportunity guide. It does not use a trained ML model, inspect client systems, or provide a validated business case. A Cynbit team member should verify the analysis with the client.
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


st.title("🧭 Cynbit AI Project Copilot")
st.caption("A discovery assistant that turns a client problem into a structured AI opportunity brief.")
st.info("Assessment prototype: recommendations use transparent keyword rules and a small opportunity guide. Treat outputs as discussion prompts, not client-approved advice.")

with st.sidebar:
    st.header("Client context")
    client = st.text_input("Client or project name", "Sample Retail Co.")
    category = st.selectbox("Problem area", list(OPPORTUNITY_GUIDES))
    users = st.text_input("Who has this problem?", "Support team")
    systems = st.text_input("Current tools or data", "Shared inbox and FAQ documents")
    constraints = st.text_input("Constraints to consider", "Human approval for customer-facing answers")

st.subheader("Describe the client requirement")
problem = st.text_area("What is difficult today, how often does it happen, and what outcome is desired?", height=150,
    placeholder="Example: Our support team receives many repetitive questions each day. Staff search several documents before replying, so response times are slow and answers can be inconsistent.")

if st.button("Analyze opportunity", type="primary"):
    st.session_state["analysis"] = assess(problem, category, users, systems, constraints)

if "analysis" not in st.session_state:
    if st.button("Load example"):
        st.session_state["analysis"] = assess(
            "Our support team receives many repetitive questions each day. Staff search several documents before replying, so response times are slow and answers can be inconsistent.",
            "Customer support", "Support team", "Shared inbox and FAQ documents", "Human approval for customer-facing answers")

if "analysis" in st.session_state:
    result = st.session_state["analysis"]
    st.divider()
    st.header("Opportunity brief")
    a, b, c = st.columns(3)
    a.metric("Recommended opportunity", result["use_case"])
    b.metric("Readiness", result["readiness"])
    c.metric("Prototype signal score", f"{result['score']}/7")
    st.caption("The score counts keyword signals in the description. It is not an ML confidence score or forecast.")
    st.markdown("**Signals found**")
    st.write(", ".join(result["signals"]))
    st.markdown("**Suggested approach**")
    st.write(result["approach"])
    left, right = st.columns(2)
    with left:
        st.markdown("**Pilot measures**")
        for metric in result["metrics"]:
            st.write(f"- {metric}")
    with right:
        st.markdown("**Risk and safeguard**")
        st.write(result["risk"])
    report = markdown_to_docx(make_report(client, result))
    st.download_button("Download client brief (Word)", report, file_name="cynbit_client_opportunity_brief.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    table = pd.DataFrame([{"client": client, "category": result["category"], "opportunity": result["use_case"], "readiness": result["readiness"], "signal_score": result["score"]}])
    st.download_button("Download summary (CSV)", table.to_csv(index=False), file_name="cynbit_opportunity_summary.csv", mime="text/csv")

with st.expander("How this prototype works"):
    st.write("The app checks the problem description for a handful of explicit workflow signals, then combines them with the selected problem area. There is no external API call, no model training, and no client information is sent elsewhere by this code.")
