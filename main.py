"""
Main application with LangChain GitLab integration
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from src.graph.async_workflow import create_release_notes_graph
from src.graph.state import ReleaseNotesState


async def main():
    """Run the GitLab release notes generator with LangChain GitLab toolkit"""
    print("Starting GitLab Release Notes Generator...")
    
    # Load environment variables
    load_dotenv()
    print("Environment variables loaded")
    
    # Initialize LLM
    print("Initializing OpenAI LLM...")
    llm = ChatOpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        model="gpt-3.5-turbo",
        temperature=0.3
    )
    print("LLM initialized")
    
    try:
        # Create workflow with LangChain GitLab integration
        print("Creating release notes workflow...")
        app = await create_release_notes_graph(llm)
        
        # Generate release notes for last 30 days
        initial_state = ReleaseNotesState(
            project_id=os.getenv('PROJECT_ID'),
            from_date=datetime.now(timezone.utc) - timedelta(days=60),  # Last 60 days
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
        
        # Run the workflow
        print("🚀 Starting release notes generation...")
        final_state = await app.ainvoke(initial_state)
        
        # Save release notes
        if not final_state.get('error'):
            with open('RELEASE_NOTES.md', 'w') as f:
                f.write(final_state['release_notes_markdown'])
            print(f"\n✅ Release notes saved to RELEASE_NOTES.md")
        else:
            print(f"\n❌ Error: {final_state['error']}")
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        


if __name__ == "__main__":
    asyncio.run(main())