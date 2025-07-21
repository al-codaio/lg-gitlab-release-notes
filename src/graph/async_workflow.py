"""
Async LangGraph workflow with LangChain GitLab integration
"""

from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from typing import Dict, Any
from .state import ReleaseNotesState
from ..agents.collector import CollectorAgent
from ..agents.writer import WriterAgent
from ..tools.gitlab_langchain_tools import GitLabLangChainTools


async def create_release_notes_graph(llm: ChatOpenAI):
    """Create async LangGraph workflow with LangChain GitLab integration"""
    
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
        """Optional human review node"""
        print("\n--- GENERATED RELEASE NOTES ---")
        print(state['release_notes_markdown'])
        print("\n--- END ---")
        
        approve = input("\nApprove these release notes? (y/n): ")
        if approve.lower() != 'y':
            state['needs_human_review'] = True
        return state
    
    # Add nodes
    workflow.add_node("collect", collect_data)
    workflow.add_node("write", write_notes)
    workflow.add_node("review", human_review)
    
    # Define edges
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
    
    workflow.add_edge("review", END)
    
    # Set entry point
    workflow.add_edge(START, "collect")
    
    return workflow.compile()