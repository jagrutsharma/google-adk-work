from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import FunctionTool

# =============================================================================
# Pattern 4: Loop Agent - Iterative Story Refinement
# Use case: When you need iterative improvement through feedback cycles
# =============================================================================

# Step 1: Initial Writer - Creates the first draft (runs once)
initial_writer_agent = Agent(
    name="InitialWriterAgent",
    model="gemini-2.5-flash-lite",
    instruction="""Based on the user's prompt, write the first draft of a short story (around 100-150 words).
    Output only the story text, with no introduction or explanation.
    """,
    output_key="current_story"
)

# Step 2: Critic Agent - Review and provides feedback
critic_agent = Agent(
    name="CriticAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a constructive story critic. Review the story provided below.
    Story: {current_story}
    
    Evaluate the story's plot, characters, and pacing.
    - If the story is well-written and complete, you MUST respond with the exact phrase: "APPROVED"
    - Otherwise, provide 2-3 specific, actionable suggestions for improvement.
    """,
    output_key="critique"
)

# Exit function: Called when the story is approved
def exit_loop():
    """Call this function ONLY when the critique is 'APPROVED',
    indicating the story is finished"""
    return {
        "status": "approved",
        "message": "Story approved. Exiting refinement loop."
    }

# Step 3: Refiner Agent - Rewrites based on feedback OR exits if approved
# Note the use of FunctionTool - It wraps Python function so agents can call it
refiner_agent = Agent(
    name="RefinerAgent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a story refiner. You have a story draft and critique.
    
    Story Draft: {current_story}
    Critique: {critique}
    
    Your task is to analyze the critique.
    - IF the critique is EXACTLY "APPROVED", you MUST call the `exit_loop` function and nothing else.
    - OTHERWISE, rewrite the story draft to fully incorporate the feedback from the critique.
    """,
    tools=[FunctionTool(exit_loop)],
    output_key="current_story"
)

# Loop: Critic -> Refiner (repeats until approved or max iterations)
# Idea is that each loop iteration will improve the output
# This is a new type of agent: LoopAgent
story_refinement_loop = LoopAgent(
    name="StoryRefinementLoop",
    sub_agents=[critic_agent, refiner_agent],
    max_iterations=2    # Prevents infinite loops
)

# Root Agent: Initial Write -> Refinement Loop
root_agent = SequentialAgent(
    name="StoryPipeline",
    sub_agents=[initial_writer_agent, story_refinement_loop]
)