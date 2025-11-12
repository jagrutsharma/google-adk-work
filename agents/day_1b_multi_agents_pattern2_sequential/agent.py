from google.adk.agents import Agent, SequentialAgent

# =============================================================================
# Pattern 2: Sequential Agent - Blog Post Creation Pipeline
# Use case: When you need tasks to run in a specific, guaranteed order
# =============================================================================

# Step 1: Outline Agent - Creates the blog structure
outline_agent = Agent(
    name="OutlineAgent",
    model="gemini-2.5-flash-lite",
    instruction="""Create a blog outline for the given topic with:
    1. A catchy headline
    2. An introduction hook
    3. 3-5 main sections with 2-3 bullet points for each
    4. A concluding thought
    """,
    output_key="blog_outline"
)

# Step 2: Writer Agent - Writes the full blog post
writer_agent = Agent(
    name="WriterAgent",
    model="gemini-2.5-flash-lite",
    instruction="""Following this outline strictly: {blog_outline}
    Write a brief, 200 to 300-word blog post with an engaging and informative tone.""",
    output_key="blog_draft"
)

# Step 3: Editor Agent - Polishes the draft
editor_agent = Agent(
    name="EditorAgent",
    model="gemini-2.5-flash-lite",
    instruction="""Edit this draft: {blog_draft}
    Your task is to polish the text by fixing any grammatical errors, 
    improving the flow and sentence structure, and enhancing overall clarity.
    Your secondary goal is to also provide an analysis of what you fixed. Provide
    those statistics in below format at the end of your polished text:
    a. Total grammar errors fixed: <count>
    b. Total sentence errors fixed: <count>
    c. Total spellings fixed: <count>""",
    output_key=""
)

# Root Agent: Sequential pipeline that runs agents in order
# The order of execution is as specified below
# Note that there is no LLM decision in the order of how sub-agents are run
# The order is deterministic as laid out here
root_agent = SequentialAgent(
    name="BlogPipeline",
    sub_agents=[outline_agent, writer_agent, editor_agent]
)