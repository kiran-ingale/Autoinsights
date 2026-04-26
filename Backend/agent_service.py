from __future__ import annotations

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from Backend/Agents/main/.env
env_path = Path(__file__).parent / "Agents" / "main" / ".env"
load_dotenv(dotenv_path=env_path)

from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from .data_analyzer import analyze_dataset, load_dataset


from .utils import (
    _profile_dataset, 
    _clean_dataset, 
    _answer_direct_question, 
    _build_narrative, 
    _build_overview_charts
)

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
        # Unique session for each dataset + user to avoid collision
        dataset_id = uploaded_file.split('.')[0]
        session_id = f"session_{dataset_id}" 
        user_id = "user_1"
        app_name = "AutoInsights"
        
        try:
            # Check if session exists
            await _session_service.get_session(user_id=user_id, session_id=session_id)
        except Exception:
            # If not, try creating it, but ignore if it was created in parallel
            try:
                await _session_service.create_session(user_id=user_id, session_id=session_id, app_name=app_name)
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"Session creation warning: {e}")
            
        runner = Runner(agent=root_agent, session_service=_session_service, app_name=app_name)

        # Context for the agent
        prompt_text = f"User Query: {query}\nDataset Filename: {uploaded_file}\nPlease execute the full data analysis pipeline."
        prompt_content = Content(role="user", parts=[{"text": prompt_text}])
        
        full_text = ""
        steps = ["Initializing Multi-Agent Pipeline"]
        agent_charts = []
        
        # Execute the agentic pipeline
        import asyncio
        
        async def execute_runner():
            nonlocal full_text, steps, agent_charts
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=prompt_content):
                # Process events
                event_name = type(event).__name__
                if event_name not in steps:
                    steps.append(event_name)
                
                # Capture text and charts from content parts
                if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        # Capture text
                        if hasattr(part, 'text') and part.text:
                            full_text += part.text
                        
                        # Capture charts from function results (tool outputs)
                        if hasattr(part, 'function_response') and part.function_response:
                            response_data = part.function_response.response
                            if response_data and isinstance(response_data, dict):
                                tool_charts = response_data.get("charts", [])
                                if tool_charts:
                                    agent_charts.extend(tool_charts)

        # Wait for completion
        await execute_runner()

        if not full_text:
             # If no text was emitted, try to get the last message from session history
             try:
                 session = await _session_service.get_session(user_id=user_id, session_id=session_id)
                 if session.history:
                     last_msg = session.history[-1]
                     if last_msg.role == "model":
                         for part in last_msg.parts:
                             if hasattr(part, 'text') and part.text:
                                 full_text += part.text
             except:
                 pass

        if not full_text:
             full_text = "Analysis complete. The agents have processed your request, but no textual summary was generated."

        # Generate overview charts and merge with agent-generated charts
        raw_df = load_dataset(uploaded_file)
        profile = _profile_dataset(raw_df)
        overview_charts = _build_overview_charts(raw_df, profile)
        
        # Merge charts: agent charts come first as they are more specific to the query
        merged_charts = _merge_charts(agent_charts, overview_charts)

        return {
            "text": full_text,
            "steps": steps,
            "charts": merged_charts
        }

    except Exception as e:
        import traceback
        error_msg = str(e)
        full_traceback = traceback.format_exc()
        
        # Log error to file for debugging
        try:
            with open("Backend/error.log", "a") as f:
                f.write(f"\n--- Error at {pd.Timestamp.now()} ---\n")
                f.write(f"Query: {query}\n")
                f.write(f"Error: {error_msg}\n")
                f.write(full_traceback)
                f.write("-" * 30 + "\n")
        except:
            pass

        print(f"Agent Execution Error: {error_msg}")
        # ... fallback logic remains ...
        raw_df = load_dataset(uploaded_file)
        profile = _profile_dataset(raw_df)
        cleaned_df, cleaning_notes = _clean_dataset(raw_df)
        direct_answer = _answer_direct_question(cleaned_df, query)
        analysis = analyze_dataset(cleaned_df, query)
        overview_charts = _build_overview_charts(cleaned_df, profile)
        charts = _merge_charts(analysis.get("charts", []), overview_charts)

        return {
            "text": f"*(Agent execution encountered an error: {error_msg}. Falling back to programmatic analysis)*\n\n" + 
                    _build_narrative(query, uploaded_file, profile, cleaning_notes, analysis, direct_answer),
            "steps": [
                f"Agentic pipeline error: {error_msg}",
                "Fell back to robust programmatic analysis routines"
            ],
            "charts": charts,
        }
