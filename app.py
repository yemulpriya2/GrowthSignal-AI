import io
import json
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from src.data_processor import normalize_feedback, validate_feedback
from src.groq_client import GroqService
from src.analysis_pipeline import analyze_feedback, detect_opportunities, generate_strategy, generate_automations



load_dotenv()



st.set_page_config(page_title="GrowthSignal AI", page_icon="*", layout="wide")
st.markdown("""
<style>
.main .block-container {padding-top: 1.6rem; max-width: 1250px;}
div[data-testid="stMetric"] {background: rgba(100,116,139,.08); padding: 14px; border-radius: 12px;}
.small-note {color: #7c8798; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None




def get_service():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        try:
            key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        except Exception:
            key = ""
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
    try:
        model = str(st.secrets.get("GROQ_MODEL", model)).strip()
    except Exception:
        pass
    if not key:
        return None
    return GroqService(key, model)




with st.sidebar:
    st.title(" GrowthSignal AI")
    st.caption("Customer intelligence → growth actions")
    st.divider()
    st.markdown("### How it works")
    st.markdown("1. Upload feedback CSV\n2. Analyze customer voice\n3. Discover opportunities\n4. Generate strategy & workflows")
    st.divider()
    st.caption("Privacy: uploaded data is processed for this session and sent to your configured LLM provider when you run AI analysis. Do not upload sensitive personal or health information.")
    st.caption("Built as an AI Growth & Automation project.")

st.title("GrowthSignal AI")
st.subheader("Turn customer feedback into your next growth opportunity.")
st.write("Analyze customer comments, uncover patterns, and turn them into prioritized strategies and automation ideas.")

with st.expander(" CSV format & sample data", expanded=False):
    st.write("Upload a CSV with a column named `feedback`, `review`, `comment`, `message`, or `text`. Optional columns: `customer_id`, `date`, `source`, `product`.")
    sample = pd.DataFrame({
        "customer_id": ["C001","C002","C003","C004","C005","C006"],
        "date": ["2026-10-01","2026-10-02","2026-10-03","2026-10-04","2026-10-05","2026-10-06"],
        "source": ["Review","Email","Survey","Review","Support","Survey"],
        "product": ["CloudDesk"]*6,
        "feedback": [
            "The dashboard is useful but loading reports takes too long.",
            "I want a simple way to invite my whole team. The current process is confusing.",
            "Pricing is fair and support replied quickly. I would recommend it.",
            "We need an integration with Google Sheets to avoid manual exports.",
            "I am considering cancelling because onboarding took too much time.",
            "Can you add weekly email summaries? That would save me checking the dashboard."
        ]
    })
    st.download_button("Download sample CSV", sample.to_csv(index=False).encode("utf-8"), "sample_feedback.csv", "text/csv")

uploaded = st.file_uploader("Upload customer feedback (CSV)", type=["csv"])
if uploaded:
    try:
        raw_df = pd.read_csv(uploaded)
        cleaned_df, feedback_col = normalize_feedback(raw_df)
        errors = validate_feedback(cleaned_df)
        if errors:
            st.error(" | ".join(errors))
        else:
            st.success(f"Loaded {len(cleaned_df)} feedback records. Detected feedback column: `{feedback_col}`")
            st.dataframe(cleaned_df.head(12), use_container_width=True)
            max_records = st.slider("Maximum feedback records to send for AI analysis", 3, min(200, len(cleaned_df)), min(60, len(cleaned_df)), step=1)
            business_context = st.text_area(
                "Business context (optional)",
                placeholder="Example: B2B SaaS company offering a project management tool for small teams.",
                help="This context helps the AI make more relevant recommendations."
            )
            service = get_service()
            if not service:
                st.warning("Add GROQ_API_KEY in your .env file or Streamlit Cloud Secrets to enable AI analysis.")
            run = st.button(" Analyze feedback & discover opportunities", type="primary", disabled=not service)
            if run:
                feedback_records = cleaned_df.head(max_records).to_dict(orient="records")
                progress = st.progress(0, text="Preparing feedback...")
                try:
                    progress.progress(15, text="Analyzing feedback with the LLM...")
                    analyses = analyze_feedback(service, feedback_records, business_context)
                    progress.progress(50, text="Detecting patterns and opportunities...")
                    opportunities = detect_opportunities(service, analyses, business_context)
                    progress.progress(75, text="Generating growth strategy...")
                    strategy = generate_strategy(service, opportunities, business_context)
                    progress.progress(90, text="Building automation suggestions...")
                    automations = generate_automations(service, opportunities, business_context)
                    result = {
                        "analyzed_at": datetime.now().isoformat(timespec="seconds"),
                        "feedback_count": len(feedback_records),
                        "business_context": business_context,
                        "analyses": analyses,
                        "opportunities": opportunities,
                        "strategy": strategy,
                        "automations": automations
                    }
                    st.session_state.analysis_result = result
                    progress.progress(100, text="Analysis complete!")
                except Exception as e:
                    progress.empty()
                    st.error(f"AI analysis failed: {e}")
                    st.info("Check your Groq API key, model name, internet connection, and account rate limits.")
    except Exception as e:
        st.error(f"Could not read CSV: {e}")

result = st.session_state.analysis_result
if result:
    st.divider()
    st.header(" Intelligence dashboard")
    analyses = result.get("analyses", [])
    opps = result.get("opportunities", [])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Feedback analyzed", result.get("feedback_count", 0))
    sentiment_counts = pd.Series([x.get("sentiment","Unknown") for x in analyses]).value_counts()
    positive = int(sentiment_counts.get("Positive", 0))
    negative = int(sentiment_counts.get("Negative", 0))
    col2.metric("Positive signals", positive)
    col3.metric("Negative signals", negative)
    col4.metric("Opportunities found", len(opps))

    left, right = st.columns(2)
    with left:
        if sentiment_counts.size:
            fig = px.pie(names=sentiment_counts.index, values=sentiment_counts.values, title="Feedback sentiment distribution", hole=.45)
            st.plotly_chart(fig, use_container_width=True)
    with right:
        painpoints = pd.Series([x.get("pain_point","Not specified") for x in analyses]).value_counts().head(8)
        if painpoints.size:
            fig2 = px.bar(x=painpoints.values, y=painpoints.index, orientation="h", title="Most frequent pain points", labels={"x":"Mentions","y":"Pain point"})
            fig2.update_layout(yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader(" Feedback-level analysis")
    analysis_df = pd.DataFrame(analyses)
    if not analysis_df.empty:
        st.dataframe(analysis_df, use_container_width=True)

    st.subheader(" Opportunity radar")
    if opps:
        for i, item in enumerate(opps, start=1):
            with st.expander(f"{i}. {item.get('title','Opportunity')} · {item.get('priority','Medium')} priority", expanded=(i==1)):
                st.write(item.get("description",""))
                st.markdown(f"**Evidence:** {item.get('evidence','Not provided')}")
                st.markdown(f"**Recommended action:** {item.get('recommended_action','')}")
                st.markdown(f"**Impact:** {item.get('potential_impact','')}")
                st.markdown(f"**Confidence:** {item.get('confidence','Not specified')}")
    else:
        st.info("The model did not return opportunities in the expected format. See raw response below.")

    st.subheader(" Growth strategy")
    if isinstance(result.get("strategy"), dict):
        strategy = result["strategy"]
        st.markdown(f"**North-star recommendation:** {strategy.get('north_star','')}")
        st.markdown("### Prioritized action plan")
        for action in strategy.get("action_plan", []):
            st.markdown(f"- **{action.get('timeframe','Next')}: {action.get('action','')}** — {action.get('reason','')}")
        st.markdown("### Experiments")
        for experiment in strategy.get("experiments", []):
            st.markdown(f"- **{experiment.get('hypothesis','')}** | Metric: {experiment.get('success_metric','')} | {experiment.get('effort','')}")
        st.markdown(f"**Risks / assumptions:** {strategy.get('risks_assumptions','')}")
    else:
        st.write(result.get("strategy"))

    st.subheader(" Smart automation ideas")
    for auto in result.get("automations", []):
        with st.expander(auto.get("name","Suggested workflow")):
            st.markdown(f"**Trigger:** {auto.get('trigger','')}")
            st.markdown(f"**Condition:** {auto.get('condition','')}")
            st.markdown(f"**Action:** {auto.get('action','')}")
            st.markdown(f"**Human review:** {auto.get('human_review', 'Not specified')}")

    st.subheader(" Export")
    export_bundle = {
        "analyzed_at": result["analyzed_at"],
        "feedback_count": result["feedback_count"],
        "analyses": result["analyses"],
        "opportunities": result["opportunities"],
        "strategy": result["strategy"],
        "automations": result["automations"]
    }
    st.download_button("Download full analysis (JSON)", json.dumps(export_bundle, indent=2, ensure_ascii=False), "growthsignal_report.json", "application/json")
    if analyses:
        st.download_button("Download feedback analysis (CSV)", pd.DataFrame(analyses).to_csv(index=False).encode("utf-8"), "feedback_analysis.csv", "text/csv")

st.divider()
st.caption("GrowthSignal AI · AI-assisted decision support. Recommendations are hypotheses; validate them with customers and business data before acting.")




st.markdown("""
<style>

/* Main application background */
.stApp {
    background-color: #F5EBDD;
    color: #1C1C1C;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #E8D8C3;
}

/* Main headings */
h1, h2, h3 {
    color: #800020 !important;
    font-weight: 700;
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: #800020;
}

/* Buttons */
.stButton > button {
    background-color: #800020;
    color: #FFFFFF;
    border: 1px solid #800020;
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 600;
}

/* Button hover effect */
.stButton > button:hover {
    background-color: #600018;
    color: #FFFFFF;
    border: 1px solid #600018;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea {
    background-color: #FFF9F0;
    color: #1C1C1C;
    border: 1px solid #800020;
    border-radius: 6px;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #E8D8C3;
    border: 1px dashed #800020;
    border-radius: 10px;
}

/* Information boxes */
.stAlert {
    background-color: #E8D8C3;
    color: #1C1C1C;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #E8D8C3;
    padding: 15px;
    border-radius: 10px;
}

/* Expander */
[data-testid="stExpander"] {
    background-color: #E8D8C3;
    border: 1px solid #800020;
    border-radius: 8px;
}

/* Links */
a {
    color: #800020 !important;
}

/* Horizontal divider */
hr {
    border-color: #800020;
}

<CodeBlock language="css" editable>
/* Download buttons */
.stDownloadButton > button {
    background-color: #800020 !important;
    color: #FFFFFF !important;
    border: 1px solid #800020 !important;
    border-radius: 8px !important;
    box-shadow: 0 3px 8px rgba(128, 0, 32, 0.25);
}


/* Download button hover */
.stDownloadButton > button:hover {
background-color: #600018 !important;
color: #FFFFFF !important;
border-color: #600018 !important;
box-shadow: 0 4px 12px rgba(128, 0, 32, 0.35);
}

/* File uploader browse button */
[data-testid="stFileUploader"] button {
background-color: #800020 !important;
color: #FFFFFF !important;
border: 1px solid #800020 !important;
border-radius: 6px !important;
}

/* File uploader hover */
[data-testid="stFileUploader"] button:hover {
background-color: #600018 !important;
color: #FFFFFF !important;
}

/* Uploaded file container */
[data-testid="stFileUploaderFile"] {
background-color: #E8D8C3 !important;
border: 1px solid #800020 !important;
border-radius: 8px !important;
}

/* Uploaded file name */
[data-testid="stFileUploaderFile"] * {
color: #800020 !important;
}

/* Success message - replace green with burgundy */
[data-testid="stAlert"][data-baseweb="notification"] {
background-color: #F0DFE4 !important;
border-left: 5px solid #800020 !important;
color: #1C1C1C !important;
}

/* Success message text and icon */
[data-testid="stAlert"][data-baseweb="notification"] * {
color: #800020 !important;
}

/* Export section shadow */
.stDownloadButton {
filter: drop-shadow(0 2px 5px rgba(128, 0, 32, 0.18));
}

/* Focus border for interactive elements */
.stTextInput input:focus,
.stTextArea textarea:focus {
border-color: #800020 !important;
box-shadow: 0 0 0 2px rgba(128, 0, 32, 0.15) !important;
}

/* Checkbox and radio selection */
.stCheckbox label,
.stRadio label {
accent-color: #800020 !important;
}

/* Progress bar */
.stProgress > div > div > div {
background-color: #800020 !important;
}

/* Selected tab underline */
.stTabs [data-baseweb="tab-highlight"] {
background-color: #800020 !important;
}

/* Selectbox focus */
[data-baseweb="select"] {
border-color: #800020 !important;
}

/* Slider accent */
.stSlider [data-baseweb="slider"] div {
background-color: #800020;
}
</CodeBlock>


/* Sidebar small text - pure black */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] small {
    color: #000000 !important;
}

/* Sidebar main title - Burgundy */
[data-testid="stSidebar"] h1 {
    color: #800020 !important;
    font-weight: 800 !important;
}

/* Sidebar "How it works" heading - Black */
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] h4 {
    color: #000000 !important;
}

/* Last line: GrowthSignal AI - Burgundy */
[data-testid="stSidebar"] div:last-child p:last-child {
    color: #800020 !important;
    font-weight: 600 !important;
}

</style>
""", unsafe_allow_html=True)
