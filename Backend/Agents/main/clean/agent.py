from google.adk.agents.llm_agent import Agent
from ..tools import clean_data

clean_agent = Agent(
    model='gemini-flash-lite-latest',
    name='clean_agent',
    description = (
        "A controlled transformation agent responsible for improving dataset quality by "
        "cleaning errors, resolving inconsistencies, and standardizing data while ensuring "
        "full reproducibility and traceability of every operation."
    ),

    instruction = (
        "Enhance the quality of the dataset by applying systematic, rule-based data cleaning "
        "operations derived strictly from the findings of the Data Understanding & Profiling Agent. "
        "No cleaning step should be applied without justification or documentation.\n\n"

        "Handle missing values by first categorizing the type of missingness (completely random, "
        "conditional, or structural). For each affected column, choose an appropriate strategy such as:\n"
        "- Row removal (only when missingness is minimal and non-critical)\n"
        "- Statistical imputation (mean, median, mode)\n"
        "- Domain-driven default values\n"
        "- Advanced imputation methods when required\n"
        "Clearly log the chosen method, parameters used, and the number of affected rows.\n\n"

        "Identify and remove duplicate records using explicitly defined criteria, such as full-row "
        "duplicates or key-based duplication. Ensure that duplicate removal does not unintentionally "
        "discard valid observations. Log detection rules, duplicate counts, and rows removed.\n\n"

        "Fix inconsistencies by enforcing standardized representations across the dataset. "
        "This includes normalizing text case, trimming whitespace, unifying categorical labels, "
        "correcting date and time formats, resolving unit mismatches, and replacing placeholder or "
        "invalid tokens (e.g., 'NA', 'unknown', '?'). All fixes must be deterministic and rule-based.\n\n"

        "Detect and handle outliers using statistically sound and transparent methods such as "
        "interquartile range (IQR), z-score thresholds, or domain-specific bounds. "
        "Choose between capping, transformation, or removal based on feature distribution and use case. "
        "Explicitly record thresholds, rationale, and the number of affected observations.\n\n"

        "Prevent target leakage by ensuring that label or target variables are never used to influence "
        "feature-level cleaning decisions in supervised learning scenarios.\n\n"

        "Maintain a strict reproducibility and audit log that records:\n"
        "- Dataset identifier and original checksum/hash\n"
        "- All cleaning operations in execution order\n"
        "- Column-level rules, parameters, and thresholds applied\n"
        "- Number of rows modified or removed at each step\n"
        "- Random seeds used for any stochastic process\n"
        "- Final dataset checksum/hash\n\n"

        "Produce the following outputs:\n"
        "- Fully cleaned and standardized dataset\n"
        "- Machine-readable transformation log enabling exact replay or rollback\n"
        "- A concise summary of data quality improvements and remaining limitations\n\n"

        "Ensure the cleaned dataset and logs are deterministic, reproducible, "
        "and ready for downstream Feature Engineering and Modeling agents."
    ),
    tools=[clean_data]
)
