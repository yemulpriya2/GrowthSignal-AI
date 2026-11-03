import pandas as pd

CANDIDATE_COLUMNS = ["feedback", "review", "comment", "message", "text", "customer_feedback", "customer_review"]

def normalize_feedback(df: pd.DataFrame):
    """Normalize columns, locate feedback text, and remove empty/duplicate rows."""
    if df is None or df.empty:
        raise ValueError("The uploaded CSV is empty.")
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    feedback_col = next((c for c in CANDIDATE_COLUMNS if c in df.columns), None)
    if feedback_col is None:
        text_candidates = [c for c in df.columns if df[c].dtype == "object"]
        if len(text_candidates) == 1:
            feedback_col = text_candidates[0]
        else:
            raise ValueError("Could not identify feedback column. Rename the text column to feedback, review, comment, message, or text.")
    df = df.rename(columns={feedback_col: "feedback"})
    df["feedback"] = df["feedback"].astype(str).str.strip()
    df = df[df["feedback"].ne("") & df["feedback"].str.lower().ne("nan")]
    df = df.drop_duplicates(subset=["feedback"]).reset_index(drop=True)
    if df.empty:
        raise ValueError("No non-empty feedback rows were found.")
    return df, "feedback"






def validate_feedback(df: pd.DataFrame):
    issues = []
    if "feedback" not in df.columns:
        issues.append("Required feedback column is missing.")
    else:
        if df["feedback"].isna().any():
            issues.append("Some feedback rows are blank.")
        if (df["feedback"].str.len() > 5000).any():
            issues.append("Some feedback entries exceed 5,000 characters. Please shorten them.")
    if len(df) < 3:
        issues.append("Please upload at least 3 feedback records for useful pattern detection.")
    return issues
