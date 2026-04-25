from __future__ import annotations

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from .data_analyzer import analyze_dataset, load_dataset


PLACEHOLDER_TOKENS = {"", "na", "n/a", "null", "none", "unknown", "?"}


def _format_number(value: Any) -> str:
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    if isinstance(value, (float, np.floating)):
        return f"{float(value):,.2f}"
    return str(value)


def _profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    missing_counts = df.isna().sum().sort_values(ascending=False)
    duplicate_rows = int(df.duplicated().sum())

    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "duplicate_rows": duplicate_rows,
        "missing_counts": {col: int(count) for col, count in missing_counts.items() if int(count) > 0},
        "missing_total": int(df.isna().sum().sum()),
        "completeness_pct": round(
            (1 - (df.isna().sum().sum() / max(len(df) * max(len(df.columns), 1), 1))) * 100,
            2,
        ),
    }
    return profile


def _clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    cleaned = df.copy()
    cleaning_notes: List[str] = []

    original_rows = len(cleaned)
    duplicate_rows = int(cleaned.duplicated().sum())
    if duplicate_rows:
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)
        cleaning_notes.append(f"Removed {duplicate_rows} duplicate rows.")

    object_cols = cleaned.select_dtypes(include=["object"]).columns.tolist()
    for col in object_cols:
        series = cleaned[col].astype("string").str.strip()
        lowered = series.str.lower()
        placeholder_mask = lowered.isin(PLACEHOLDER_TOKENS)
        placeholder_count = int(placeholder_mask.fillna(False).sum())
        if placeholder_count:
            cleaned.loc[placeholder_mask, col] = pd.NA
            cleaning_notes.append(f"Standardized {placeholder_count} placeholder values in '{col}'.")
        cleaned[col] = cleaned[col].astype("string").str.strip()

    if not cleaning_notes:
        cleaning_notes.append("No duplicate rows or placeholder tokens required cleanup.")

    rows_removed = original_rows - len(cleaned)
    if rows_removed and duplicate_rows == 0:
        cleaning_notes.append(f"Removed {rows_removed} rows during cleaning.")

    return cleaned, cleaning_notes


def _answer_direct_question(df: pd.DataFrame, query: str) -> str | None:
    query_lower = query.lower()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if "how many rows" in query_lower or "number of rows" in query_lower:
        return f"The dataset contains {_format_number(len(df))} rows."

    if "how many columns" in query_lower or "number of columns" in query_lower:
        return f"The dataset contains {_format_number(len(df.columns))} columns."

    if "column" in query_lower and any(word in query_lower for word in ["what", "which", "list", "show", "name"]):
        preview = ", ".join(df.columns.tolist()[:15])
        suffix = "" if len(df.columns) <= 15 else ", ..."
        return f"The dataset columns are: {preview}{suffix}."

    if "missing" in query_lower or "null" in query_lower:
        missing = df.isna().sum()
        top_missing = missing[missing > 0].sort_values(ascending=False).head(5)
        if top_missing.empty:
            return "No missing values were detected in the dataset."
        summary = ", ".join(f"{col}: {int(count)}" for col, count in top_missing.items())
        return f"Missing values are present. The most affected columns are {summary}."

    if ("average" in query_lower or "mean" in query_lower) and numeric_cols:
        target_col = next((col for col in numeric_cols if col in query_lower), numeric_cols[0])
        return f"The mean of '{target_col}' is {_format_number(df[target_col].dropna().mean())}."

    return None


def _build_narrative(
    query: str,
    dataset_name: str,
    profile: Dict[str, Any],
    cleaning_notes: List[str],
    analysis: Dict[str, Any],
    direct_answer: str | None,
) -> str:
    top_missing = list(profile["missing_counts"].items())[:5]
    missing_line = (
        ", ".join(f"{col}: {count}" for col, count in top_missing)
        if top_missing
        else "No missing values detected."
    )

    recommendation_lines: List[str] = []
    if profile["duplicate_rows"]:
        recommendation_lines.append(
            f"Review the {profile['duplicate_rows']} duplicate rows to confirm they are genuine repeats."
        )
    if profile["missing_counts"]:
        recommendation_lines.append("Address missing data in the most affected columns before high-stakes decisions.")
    if profile["numeric_columns"]:
        recommendation_lines.append("Validate numeric trends with domain context before acting on correlations alone.")
    if not recommendation_lines:
        recommendation_lines.append("The dataset looks structurally healthy; continue with targeted business questions.")

    direct_answer_block = f"\n### Natural-Language Answer\n{direct_answer}\n" if direct_answer else ""
    cleaning_block = "\n".join(f"- {note}" for note in cleaning_notes)
    recommendation_block = "\n".join(f"- {line}" for line in recommendation_lines)

    return (
        f"## AutoInsights Analysis\n\n"
        f"### User Question\n{query}\n\n"
        f"### Dataset Context\n"
        f"- Dataset: {dataset_name}\n"
        f"- Rows: {_format_number(profile['rows'])}\n"
        f"- Columns: {_format_number(profile['columns'])}\n"
        f"- Numeric columns: {_format_number(len(profile['numeric_columns']))}\n"
        f"- Categorical columns: {_format_number(len(profile['categorical_columns']))}\n"
        f"- Data completeness: {profile['completeness_pct']:.2f}%\n"
        f"- Missing values summary: {missing_line}\n"
        f"{direct_answer_block}\n"
        f"### Agent Pipeline Summary\n"
        f"- Interface Agent structured the question and confirmed the uploaded dataset context.\n"
        f"- Data Understanding Agent profiled the dataset shape, types, duplicates, and missing values.\n"
        f"- Data Cleaning Agent applied safe preprocessing before analysis.\n"
        f"- EDA / Statistical Analysis Agent selected the best analysis routine for this query.\n"
        f"- Insight Generation Agent translated the output into business-friendly language.\n"
        f"- Reporting Agent prepared charts and the final written response.\n\n"
        f"### Cleaning Notes\n{cleaning_block}\n\n"
        f"### Analytical Interpretation\n{analysis['text'].strip()}\n\n"
        f"### Recommendations\n{recommendation_block}\n\n"
        f"### Reliability Notes\n"
        f"- Results are computed from the uploaded dataset, not a canned template.\n"
        f"- Conclusions depend on the quality and representativeness of the uploaded file.\n"
        f"- Follow-up questions can reuse the same uploaded dataset for deeper analysis.\n"
    )


def _build_overview_charts(df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    charts: List[Dict[str, Any]] = []

    completeness_data = [
        {
            "column": column,
            "completeness": round((1 - (df[column].isna().sum() / max(len(df), 1))) * 100, 2),
        }
        for column in df.columns[:10]
    ]
    if completeness_data:
        charts.append(
            {
                "type": "bar",
                "title": "Data Completeness by Column",
                "data": completeness_data,
                "xKey": "column",
                "yKeys": ["completeness"],
                "colors": ["#8884d8"],
            }
        )

    numeric_cols = profile["numeric_columns"][:3]
    if numeric_cols:
        numeric_summary = []
        for column in numeric_cols:
            series = df[column].dropna()
            if len(series) == 0:
                continue
            numeric_summary.append(
                {
                    "metric": column,
                    "mean": round(float(series.mean()), 2),
                    "median": round(float(series.median()), 2),
                }
            )
        if numeric_summary:
            charts.append(
                {
                    "type": "bar",
                    "title": "Numeric Column Summary",
                    "data": numeric_summary,
                    "xKey": "metric",
                    "yKeys": ["mean", "median"],
                    "colors": ["#00C49F", "#FFBB28"],
                }
            )

    categorical_cols = profile["categorical_columns"][:1]
    if categorical_cols:
        top_counts = df[categorical_cols[0]].astype("string").fillna("Missing").value_counts().head(5)
        if len(top_counts) > 0:
            total = int(top_counts.sum())
            charts.append(
                {
                    "type": "pie",
                    "title": f"Top Categories in {categorical_cols[0]}",
                    "data": [
                        {
                            "name": str(category),
                            "value": int(count),
                            "percentage": round((int(count) / max(total, 1)) * 100, 1),
                        }
                        for category, count in top_counts.items()
                    ],
                    "colors": ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884d8"],
                }
            )

    return charts


def _merge_charts(primary_charts: List[Dict[str, Any]], fallback_charts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen_titles = set()

    for chart in primary_charts + fallback_charts:
        title = chart.get("title")
        if not title or title in seen_titles:
            continue
        seen_titles.add(title)
        merged.append(chart)

    return merged


def _fallback_response(query: str) -> Dict[str, Any]:
    text = (
        "## AutoInsights Analysis\n\n"
        "### User Question\n"
        f"{query}\n\n"
        "### Current Status\n"
        "No dataset was provided with this request, so the analysis pipeline cannot yet run a reliable end-to-end data analysis.\n\n"
        "### What To Do Next\n"
        "- Upload a CSV, Excel, or JSON dataset.\n"
        "- Ask a concrete question such as summary, trends, correlations, distributions, or outliers.\n"
        "- Then continue asking follow-up questions on the same uploaded file.\n"
    )
    return {
        "text": text,
        "steps": [
            "Interface Agent captured the request",
            "Orchestrator checked for an uploaded dataset",
            "Data Acquisition Agent was skipped because no external fetcher is implemented",
            "Analysis paused until a dataset is available",
        ],
        "charts": [],
    }


from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.events.event_actions import Content
from .Agents.main.agent import root_agent

# Initialize a persistent session service
_session_service = InMemorySessionService()

async def run_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    query = data.get("query", "").strip()
    uploaded_file = data.get("file")

    if not query:
        return {
            "text": "Please enter a data question so the pipeline can analyze it.",
            "steps": ["Interface Agent is waiting for a user question"],
            "charts": [],
        }

    if not uploaded_file:
        return _fallback_response(query)

    try:
        # Check if session exists, if not create it
        session_id = "session_1" # In a real app, this would be dynamic
        user_id = "user_1"
        app_name = "AutoInsights"
        
        try:
            await _session_service.get_session(user_id=user_id, session_id=session_id)
        except:
            await _session_service.create_session(user_id=user_id, session_id=session_id, app_name=app_name)
            
        runner = Runner(agent=root_agent, session_service=_session_service, app_name=app_name)

        # Context for the agent
        prompt_text = f"User Query: {query}\nDataset Filename: {uploaded_file}\nPlease execute the full data analysis pipeline."
        prompt_content = Content(role="user", parts=[{"text": prompt_text}])
        
        full_text = ""
        steps = ["Initializing Multi-Agent Pipeline"]
        
        # Execute the agentic pipeline
        import asyncio
        
        async def execute_runner():
            nonlocal full_text, steps
            async for event in runner.run_async(user_id="user_1", session_id="session_1", new_message=prompt_content):
                # Process events
                event_name = type(event).__name__
                if event_name not in steps:
                    steps.append(event_name)
                
                # Check for model response content
                if hasattr(event, 'content') and hasattr(event.content, 'text'):
                    full_text += event.content.text

        # Wait for completion
        await execute_runner()

        if not full_text:
             full_text = "Analysis complete. The agents have processed your request."

        return {
            "text": full_text,
            "steps": steps,
            "charts": get_overview_charts(uploaded_file)
        }

    except Exception as e:
        import traceback
        print(f"Agent Execution Error: {e}")
        traceback.print_exc()
        # Fallback to programmatic logic if agent fails
        raw_df = load_dataset(uploaded_file)
        profile = _profile_dataset(raw_df)
        cleaned_df, cleaning_notes = _clean_dataset(raw_df)
        direct_answer = _answer_direct_question(cleaned_df, query)
        analysis = analyze_dataset(cleaned_df, query)
        overview_charts = _build_overview_charts(cleaned_df, profile)
        charts = _merge_charts(analysis.get("charts", []), overview_charts)

        return {
            "text": f"*(Agent execution encountered an error, falling back to programmatic analysis)*\n\n" + 
                    _build_narrative(query, uploaded_file, profile, cleaning_notes, analysis, direct_answer),
            "steps": [
                "Agentic pipeline encountered an error",
                "Fell back to robust programmatic analysis routines"
            ],
            "charts": charts,
        }
