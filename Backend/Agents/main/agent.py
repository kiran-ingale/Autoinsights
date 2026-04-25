from google.adk.agents.llm_agent import Agent
from .interface.agent import interface_agent
from .fetcher.agent import data_aquisition_agent
from .inspector.agent import inspector_agent
from .clean.agent import clean_agent
from .EDA.agent import EDA_agent
from .feature.agent import feature_agent
from .stat.agent import stat_agent
from .insight.agent import insight_agent
from .reporting.agent import reporting_agent
from .execution.agent import execution_agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description = (
        "The central orchestrator agent responsible for managing and coordinating "
        "a multi-agent autonomous data analysis system. Acts as the decision-making "
        "brain that interprets user goals and controls the execution flow across agents."
    ),

    instruction = (
        "You are an AI data analyst. When given a data analysis query, provide a comprehensive "
        "analysis response. Break down your thinking into clear steps and provide actionable insights.\n\n"
        
        "You have access to a team of specialized agents. Delegate tasks to them as follows:\n"
        "1. Use interface_agent to clarify requirements.\n"
        "2. Use data_aquisition_agent if data is missing.\n"
        "3. Use inspector_agent to profile the dataset.\n"
        "4. Use clean_agent to clean the data.\n"
        "5. Use EDA_agent and stat_agent for core analysis.\n"
        "6. Use insight_agent to synthesize findings.\n"
        "7. Use reporting_agent to generate the final report.\n"
        "8. Use execution_agent to propose and apply modifications AFTER user approval.\n\n"
        
        "If a user asks to 'apply changes' or 'fix the data' based on previous recommendations, "
        "immediately delegate to the execution_agent."
    ),
    sub_agents=[
        interface_agent, 
        data_aquisition_agent, 
        inspector_agent, 
        clean_agent, 
        EDA_agent, 
        feature_agent, 
        stat_agent, 
        insight_agent, 
        reporting_agent,
        execution_agent
    ]
)
