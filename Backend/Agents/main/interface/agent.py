from google.adk.agents.llm_agent import Agent

interface_agent = Agent(
    model='gemini-flash-lite-latest',
    name='interface_agent',
    description = "An interface agent that interacts directly with the user to understand their problem and requirements.",

    instruction = (
        "Engage with the user to collect essential inputs such as the problem statement, domain, "
        "and any provided dataset. Identify constraints including time limits, accuracy requirements, "
        "explainability needs, and deployment preferences. "
        "Ask only minimal and necessary clarification questions when information is missing or ambiguous. "
        "Translate the user’s intent into a clear, structured representation that can be consumed by downstream agents, "
        "explicitly indicating whether the user has provided data or if data acquisition is required."
    ),

)
