from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
import os
from langchain_openai import ChatOpenAI
from typing import Dict, Any
from .state import ReleaseNotesState
from ..agents.collector import CollectorAgent
from ..agents.writer import WriterAgent
from ..tools.gitlab_langchain_tools import GitLabLangChainTools


async def create_release_notes_graph(llm: ChatOpenAI, use_interrupt: bool = True):
    """Create async LangGraph workflow with LangChain GitLab integration
    
    Args:
        llm: The language model to use
        use_interrupt: Whether to use interrupt for human review (for LangGraph Studio)
    """
    
    try:
        # Initialize LangChain GitLab tools
        gitlab_tools = GitLabLangChainTools()
        
        # Initialize agents with GitLab tools
        collector = CollectorAgent(gitlab_tools)
        writer = WriterAgent(llm)
        
        # Create graph
        workflow = StateGraph(ReleaseNotesState)
    except Exception as e:
        print(f"Error initializing workflow components: {e}")
        raise
    
    # Define async nodes
    async def collect_data(state: ReleaseNotesState) -> ReleaseNotesState:
        """Async collector agent node"""
        try:
            result = await collector.run_async(state)
            return {**state, **result}
        except Exception as e:
            print(f"Error in collect_data node: {e}")
            return {**state, 'error': str(e)}
    
    def write_notes(state: ReleaseNotesState) -> ReleaseNotesState:
        """Writer agent node"""
        result = writer.generate_release_notes(state)
        return {**state, **result}
    
    def human_review(state: ReleaseNotesState) -> ReleaseNotesState:
        """Human review node - displays release notes for approval"""
        release_notes = state.get('release_notes_markdown', 'No release notes generated')
        
        print("\n=== RELEASE NOTES FOR REVIEW ===")
        print(release_notes)
        print("\n=== END OF RELEASE NOTES ===")
        
        if use_interrupt:
            # LangGraph Studio mode - just display for review
            print("\nPlease review the release notes above.")
            print("To approve: Continue the workflow in LangGraph Studio")
            print("To reject: Stop the workflow")
        else:
            # CLI mode - interactive prompt
            print("\nPlease review the release notes above.")
            approve = input("Approve these release notes? (y/n): ")
            if approve.lower() != 'y':
                state['needs_human_review'] = True
                state['rejected'] = True
                print("Release notes rejected. Workflow will end.")
        
        return state
    
    def save_release_notes(state: ReleaseNotesState) -> ReleaseNotesState:
        """Save the approved release notes to file"""
        try:
            with open('RELEASE_NOTES.md', 'w') as f:
                f.write(state.get('release_notes_markdown', ''))
            print("✅ Release notes saved to RELEASE_NOTES.md")
            state['saved'] = True
        except Exception as e:
            print(f"❌ Error saving release notes: {e}")
            state['error'] = str(e)
        return state
    
    # Add nodes
    workflow.add_node("collect", collect_data)
    workflow.add_node("write", write_notes)
    workflow.add_node("review", human_review)
    workflow.add_node("save", save_release_notes)
    
    # Define edges
    workflow.add_edge(START, "collect")
    workflow.add_edge("collect", "write")
    
    # Conditional edge for human review
    def should_review(state: ReleaseNotesState) -> str:
        if state.get('error'):
            return END
        return "review"
    
    workflow.add_conditional_edges(
        "write",
        should_review,
        {
            "review": "review",
            END: END
        }
    )
    
    # After review, conditionally save or end
    def after_review(state: ReleaseNotesState) -> str:
        if state.get('rejected'):
            return END
        return "save"
    
    workflow.add_conditional_edges(
        "review",
        after_review,
        {
            "save": "save",
            END: END
        }
    )
    
    workflow.add_edge("save", END)
    
    
    # Compile based on mode
    if use_interrupt:
        return workflow.compile(interrupt_before=["review"])
    else:
        return workflow.compile()