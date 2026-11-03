# GrowthSignal AI
### Customer Feedback → Intelligence → Growth Actions

GrowthSignal AI is an AI-powered customer intelligence prototype built for the AI Growth & Automation Associate assessment. It analyzes unstructured customer feedback, identifies recurring themes and growth opportunities, generates an evidence-based action plan, and suggests trigger-condition-action automations.

## Features
- CSV upload and validation with Pandas
- LLM-powered feedback-level sentiment, intent, urgency, topic, and pain-point classification
- Opportunity detection with evidence, priority, impact, and confidence
- Growth strategy with action plan and experiments
- Smart automation recommendations with human-review guidance
- Interactive Plotly dashboard
- JSON and CSV export
- Prompt documentation and iteration log

## Tech stack
Python · Streamlit · Groq API · Pandas · Plotly · Prompt Engineering

## Run locally (Windows)
1. Install Python 3.10+.
2. Extract this project folder and open it in VS Code.
3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   ```
6. Run:
   ```bash
   streamlit run app.py
   ```

## CSV input
Required text column: `feedback`, `review`, `comment`, `message`, or `text`.
Optional columns: `customer_id`, `date`, `source`, `product`.
A sample file is available at `data/sample_feedback.csv`.

## Deploy to Streamlit Community Cloud
1. Push the project to a GitHub repository.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Click **Create app**, select the repository, branch, and `app.py`.
4. In **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "your_actual_key"
   GROQ_MODEL = "openai/gpt-oss-120b"
   ```
5. Deploy. Never commit your `.env` or API key to GitHub.
6. Test with `data/sample_feedback.csv`.

## AI and privacy note
The application sends the selected feedback records and optional business context to Groq when the user runs analysis. Do not upload confidential, personally identifiable, or sensitive health information. Outputs are AI-generated hypotheses and should be reviewed before business decisions.

## Assessment deliverables
- Live application link
- GitHub repository
- `docs/prompt_engineering_log.md`
- Video demonstration (see `docs/video_script.md`)
