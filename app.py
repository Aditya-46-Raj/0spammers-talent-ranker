"""
Streamlit Sandbox for the Redrob Candidate Ranker.
Accepts a small candidate sample (≤100) and produces a ranked CSV.
"""

import streamlit as st
import pandas as pd
import json
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pipeline.orchestrator import run_pipeline
from src.pipeline.reasoning import generate_reasoning
from src.config import JD_QUERY

st.set_page_config(page_title="Redrob Candidate Ranker", layout="wide")
st.title("🧠 Redrob Candidate Ranker — Sandbox")
st.caption("Team: 0spammers | Intelligent Candidate Discovery & Ranking Challenge")

st.markdown("""
Upload a candidate JSON or JSONL file (≤100 candidates).
The system will run the full ranking pipeline and produce a ranked CSV.
""")

uploaded_file = st.file_uploader("Upload candidates (JSON / JSONL)", type=["json", "jsonl"])

if uploaded_file is not None:
    with st.spinner("Loading and parsing candidates..."):
        content = uploaded_file.read().decode("utf-8")
        candidates = []
        try:
            data = json.loads(content)
            if isinstance(data, list):
                candidates = data
            else:
                candidates = [data]
        except json.JSONDecodeError:
            for line in content.splitlines():
                line = line.strip()
                if line:
                    candidates.append(json.loads(line))

    st.success(f"Loaded {len(candidates)} candidates.")

    if st.button("🚀 Run Ranking Pipeline"):
        start = time.time()
        with st.spinner("Running multi-stage pipeline (BM25 → Semantic → Feature Scoring)..."):
            top_results = run_pipeline(candidates, JD_QUERY)

        elapsed = time.time() - start
        st.success(f"Pipeline completed in {elapsed:.2f} seconds.")

        # Build results table
        rows = []
        for item in top_results:
            cand = item["candidate"]
            reasoning = generate_reasoning(item)
            rows.append({
                "candidate_id": cand.get("candidate_id", "UNKNOWN"),
                "rank": item["rank"],
                "score": item["score"],
                "reasoning": reasoning,
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        # Download button
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="team_0spammers.csv",
            mime="text/csv",
        )
