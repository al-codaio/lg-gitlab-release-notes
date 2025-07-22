import asyncio
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.graph.async_workflow import create_release_notes_graph
from src.graph.state import ReleaseNotesState

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    model="gpt-3.5-turbo",
    temperature=0.3
)

# Create the app for LangGraph Studio with interrupt (no checkpointer)
app = asyncio.run(create_release_notes_graph(llm, use_interrupt=True))

async def run_release_notes_generation():
    print("Starting GitLab Release Notes Generator...")
    
    # Create CLI version without interrupt
    cli_app = await create_release_notes_graph(llm, use_interrupt=False)
    
    try:
        initial_state = ReleaseNotesState(
            project_id=os.getenv('PROJECT_ID'),
            from_date=datetime.now(timezone.utc) - timedelta(days=14),
            to_date=datetime.now(timezone.utc),
            merge_requests=[],
            issues=[],
            commits=[],
            contributors=set(),
            categorized_changes={},
            statistics={},
            release_notes_markdown="",
            release_notes_sections={},
            needs_human_review=False,
            error=None
        )
        
        print("🚀 Starting release notes generation...")
        final_state = await cli_app.ainvoke(initial_state)
        
        if final_state.get('error'):
            print(f"\n❌ Error: {final_state['error']}")
        elif final_state.get('rejected'):
            print("\n❌ Release notes were rejected")
        elif final_state.get('saved'):
            print("\n✅ Workflow completed successfully")
        else:
            print("\n⚠️ Workflow completed but release notes were not saved")
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_release_notes_generation())