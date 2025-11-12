from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.tools import google_search

# =============================================================================
# Pattern 3: Parallel Agent - Multi-Topic Research
# Use case: When you have independent tasks that can run at the same time
# =============================================================================

# Research Agent 1: Tech & AI Trends (Can run in parallel to other researchers)
tech_researcher = Agent(
    name="TechResearcher",
    model="gemini-2.5-flash-lite",
    instruction="""Research the latest AI/ML trends. Include 3 key developments, 
    the main companies involved, and the potential impact.
    Keep the report very concise (100 words).
    """,
    tools=[google_search],
    output_key="tech_research"
)

# Research Agent 2: Health & Medical Breakthroughs (Can run in parallel to other researchers)
health_researcher = Agent(
    name="HealthResearcher",
    model="gemini-2.5-flash-lite",
    instruction="""Research recent medical breakthroughs. Include 3 significant advances,
    their practical applications, and estimated timelines. Keep the report concise (100 words).
    """,
    tools=[google_search],
    output_key="health_research"
)

# Research Agent 3: Finance & Fintech Trends (Can run in parallel to other researchers)
finance_researcher = Agent(
    name="FinanceResearcher",
    model="gemini-2.5-flash-lite",
    instruction="""Research current fintech trends. Include 3 key trends,
    their market implications, and the future outlook. Keep the report concise (100 words)
    """,
    tools=[google_search],
    output_key="finance_research"
)

# Aggregator Agent: Runs AFTER parallel runs of researchers complete
aggregator_agent = Agent(
    name="AggregatorAgent",
    model="gemini-2.5-flash-lite",
    instruction="""Combine these three research findings into a single executive summary:
    
    **Technology Trends:**
    {tech_research}
    
    **Health Breakthroughs:**
    {health_research}
    
    **Finance Innovations:**
    {finance_research}
    
    Your summary should highlight common themes, surprising connections, and 
    the most important key takeaways from all three reports. The final
    summary should be around 200 words.
    """,
    output_key="executive_summary"
)

# Parallel team: All 3 researchers run simultaneously
parallel_research_team = ParallelAgent(
    name="ParallelResearchTeam",
    sub_agents=[tech_researcher, health_researcher, finance_researcher]
)

# Root Agent: Run parallel team first, then aggregator
root_agent = SequentialAgent(
    name="ResearchSystem",
    sub_agents=[parallel_research_team, aggregator_agent]
)
