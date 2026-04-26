from google.adk.agents.llm_agent import Agent

data_aquisition_agent = Agent(
    model='gemini-flash-lite-latest',
    name='data_aquisition_agent',
    description = "An autonomous agent responsible for acquiring relevant datasets when the user has not provided data.",

    instruction = (
        "Identify appropriate datasets based on the user's task and autonomously fetch them from reliable sources "
        "such as Kaggle, the UCI Machine Learning Repository, public APIs, or via web scraping. "
        "Ensure the data is relevant, up-to-date, and usable. "
        "Download and store the dataset, validate its quality and freshness, "
        "and pass essential metadata (source, size, features, labels, timestamp, and usage constraints) "
        "to the next agent in the pipeline."
    ),

)
