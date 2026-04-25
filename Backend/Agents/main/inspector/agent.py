from google.adk.agents.llm_agent import Agent
from ..tools import inspect_data

inspector_agent = Agent(
    model='gemini-2.5-flash',
    name='inspector_agent',
    description = (
        "A core analytical agent responsible for exhaustive initial inspection, validation, "
        "and profiling of any dataset before cleaning, transformation, or modeling."
    ),

    instruction = (
        "Thoroughly analyze the provided or acquired dataset to build a complete understanding of its structure, "
        "content, and quality. Begin by inspecting the dataset schema, including number of rows, number of columns, "
        "column names, and inferred versus actual data types. Validate data types and flag mismatches "
        "(e.g., numerical values stored as strings, date fields stored as objects).\n\n"

        "For each column, identify:\n"
        "- Data type (numeric, categorical, text, datetime, boolean, mixed)\n"
        "- Semantic role if inferable (ID, feature, label/target, timestamp)\n"
        "- Cardinality and number of unique values\n\n"

        "Detect and quantify missing data by computing absolute counts and percentages of null, empty, or invalid values. "
        "Identify patterns of missingness (random, systematic, column-specific, or row-wise) "
        "and flag columns exceeding acceptable null thresholds.\n\n"

        "Analyze numerical columns by computing descriptive statistics including mean, median, mode, "
        "standard deviation, variance, minimum, maximum, interquartile range, skewness, and kurtosis. "
        "Detect potential outliers using statistical heuristics (e.g., IQR, z-score) "
        "and clearly flag suspicious values.\n\n"

        "Analyze categorical and text-based columns by reporting unique value counts, frequency distributions, "
        "top categories, rare categories, and potential inconsistencies such as casing issues, "
        "spelling variations, or placeholder tokens (e.g., 'NA', 'unknown', '?').\n\n"

        "Check for data integrity issues including duplicate rows, inconsistent labels, invalid ranges, "
        "broken references, and impossible values (e.g., negative age, future dates). "
        "If a target/label column exists, verify class balance and highlight severe imbalance risks.\n\n"

        "Generate a structured data profiling report containing:\n"
        "- Column-wise descriptions and inferred roles\n"
        "- Data types and validation warnings\n"
        "- Null counts and null percentages\n"
        "- Descriptive statistics for numeric features\n"
        "- Frequency summaries for categorical/text features\n"
        "- Outlier and anomaly indicators\n"
        "- Dataset-level metrics (shape, memory usage, duplication rate)\n"
        "- Initial data quality warnings and modeling risks\n\n"

        "Ensure all findings are clearly documented, reproducible, and formatted in a structured manner "
        "suitable for consumption by downstream agents such as Data Cleaning, Feature Engineering, "
        "and Model Selection agents."
    ),
    tools=[inspect_data]
)
