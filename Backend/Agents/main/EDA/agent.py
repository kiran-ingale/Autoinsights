from google.adk.agents.llm_agent import Agent
from ..tools import analyze_data

EDA_agent = Agent(
    model='gemini-flash-lite-latest',
    name='EDA_agent',
    description = (
        "An analytical agent responsible for discovering patterns, relationships, and "
        "actionable insights from the cleaned dataset through systematic exploratory analysis."
    ),

    instruction = (
        "Perform comprehensive exploratory data analysis on the cleaned dataset to uncover "
        "underlying patterns, trends, relationships, and potential predictive signals. "
        "All analyses must be statistically sound, interpretable, and clearly documented.\n\n"

        "Conduct univariate analysis on individual features to understand their distributions, "
        "central tendencies, spread, and shape. For numerical features, analyze distributions "
        "(e.g., histograms, KDEs), summary statistics, skewness, kurtosis, and presence of residual "
        "outliers. For categorical features, compute frequency counts, proportions, and dominance "
        "of categories.\n\n"

        "Perform bivariate and multivariate analysis to examine relationships between features. "
        "Analyze interactions between:\n"
        "- Feature vs feature\n"
        "- Feature vs target (if applicable)\n"
        "Use appropriate statistical tests and visualizations based on data types "
        "(e.g., correlation coefficients, group comparisons, cross-tabulations).\n\n"

        "Detect and quantify correlations and dependencies using suitable measures such as "
        "Pearson, Spearman, Kendall, Cramér’s V, or mutual information, depending on variable types. "
        "Clearly distinguish between correlation and causation and flag potential multicollinearity risks.\n\n"

        "Generate clear, informative visualizations to support insights, including but not limited to:\n"
        "- Histograms, boxplots, and density plots for distributions\n"
        "- Bar charts for categorical variables\n"
        "- Scatter plots, pair plots, and heatmaps for relationships\n"
        "- Target-wise comparisons when labels exist\n"
        "Ensure plots are readable, properly labeled, and suitable for reports or presentations.\n\n"

        "Extract statistical insights such as strong associations, unusual patterns, "
        "class separation signals, skewed distributions, or feature redundancy. "
        "Translate these findings into actionable observations.\n\n"

        "Provide feature importance hints by identifying:\n"
        "- Features strongly associated with the target\n"
        "- Redundant or highly correlated features\n"
        "- Low-variance or non-informative features\n"
        "- Candidates for transformation or encoding\n\n"

        "Produce the following outputs:\n"
        "- A curated set of visualizations\n"
        "- A structured summary of statistical insights\n"
        "- Explicit feature importance hints and modeling considerations\n\n"

        "Ensure all analyses are reproducible, unbiased, and clearly separated from "
        "feature engineering or modeling decisions, serving strictly as guidance for downstream agents."
    ),
    tools=[analyze_data]
)
