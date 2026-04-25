from google.adk.agents.llm_agent import Agent
from ..tools import generate_final_report, get_overview_charts

reporting_agent = Agent(
    model='gemini-2.5-flash',
    name='reporting_agent',
    description = (
        "A presentation agent responsible for generating concrete visual dashboards "
        "and downloadable reports that summarize the entire analysis pipeline."
    ),

    instruction = (
        "Generate actual visual and report artifacts using the finalized analysis outputs. "
        "This agent must produce tangible files or renderable objects, not just summaries.\n\n"

        "Create visualizations including charts, plots, and tables using appropriate visualization tools "
        "(e.g., Matplotlib, Seaborn, Plotly, or equivalent). Visuals must directly reflect findings from EDA, "
        "statistical analysis, and modeling stages.\n\n"

        "Assemble these visuals into:\n"
        "- An interactive dashboard OR\n"
        "- A static report (PDF or HTML)\n\n"

        "The report MUST include:\n"
        "1. Title and problem statement\n"
        "2. Data overview and pipeline summary\n"
        "3. Key visualizations with explanations\n"
        "4. Insights and recommendations\n"
        "5. Limitations and next steps\n\n"

        "Ensure that:\n"
        "- Every visualization has a caption and explanation\n"
        "- All figures are readable and labeled\n"
        "- Outputs are saved to disk or returned as renderable objects\n\n"

        "Explicitly return:\n"
        "- File paths or URLs to generated reports\n"
        "- A list of generated charts\n"
        "- A short executive summary\n\n"

        "If visualization generation fails, log the error and generate a fallback "
        "static summary report instead."
    ),
    tools=[generate_final_report, get_overview_charts]
)
