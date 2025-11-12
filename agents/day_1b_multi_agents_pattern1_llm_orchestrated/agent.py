from google.adk.agents import Agent
from google.adk.tools import AgentTool, google_search

# ================================================================================
# Pattern 1: LLM Orchestrated Multi-Agent system
# Use case: When you need dynamic decision-making about which agents to call
# ================================================================================

# Research Agent: Uses Google Search to find information
research_agent = Agent(
    name="ResearchAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a specialized research agent. 
    Your only job is to use the google_search tool to find 
    2-3 pieces of relevant information on the given topic 
    and present the findings with citations.""",
    tools=[google_search],
    output_key="research_findings",
)

# Summarizer Agent: Create concise summaries
summarizer_agent = Agent(
    name="SummarizerAgent",
    model="gemini-2.5-flash-lite",
    instruction="""Read the provided research findings: {research_findings}
    Create a concise summary as a bulleted list with 3-5 key points.""",
    output_key="final_summary"
)

# Root Coordinator: Orchestrates the workflow
# Note that LLM will decide what tool to call
# The order is decided by LLM based upon the prompt
# But the order of execution of research_agent and summarizer_agent is NOT deterministic
root_agent = Agent(
    name="ResearchCoordinator",
    model="gemini-2.5-flash-lite",
    instruction="""You are a research coordinator. Your goal is to answer 
    the user's query by orchestrating a workflow.
    1. First, you MUST call the ResearchAgent tool to find relevant information on the topic provided by the user.
    2. Next, after receiving the research findings, you MUST call the SummarizerAgent tool to create a concise summary.
    3. Finally, present the final summary clearly to the user as your response.""",
    tools=[
        AgentTool(research_agent),
        AgentTool(summarizer_agent)
    ]
)