import asyncio
from agent import root_agent
from google.adk.runners import InMemoryRunner

async def main():
    # Create a runner with our agent
    runner = InMemoryRunner(agent=root_agent)
    print(f"🏃Created runner: {runner}\n")

    # Create a new session
    session_id = await runner.create_session()
    print(f"📝 Created session: {session_id}\n")

    #Ask the agent a question
    question = "What is Agent Development Kit from Google? What languages is the SDK available in?"
    print(f"🤖 User: {question}\n")
    print("🤔 Agent is thinking...\n")

    # Send message and process response
    async for event in runner.run_async(session_id, question):
        # Print agent responses
        if hasattr(event, 'content') and event.content:
            print(f"✅ Agent: {event.content}")

    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())