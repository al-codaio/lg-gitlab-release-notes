from typing import Dict, Any
from datetime import datetime
from ..tools.gitlab_langchain_tools import GitLabLangChainTools

class CollectorAgent:
    def __init__(self, gitlab_tools: GitLabLangChainTools):
        self.tools = gitlab_tools
    
    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Collect all relevant data from GitLab using LangChain GitLab toolkit"""
        try:
            project_id = state.get('project_id')
            if not project_id:
                raise ValueError("project_id is required in state")
            
            # For now, only support date-based collection (tags can be added later)
            from_date = state.get('from_date')
            to_date = state.get('to_date')
            
            if not from_date or not to_date:
                raise ValueError("from_date and to_date are required")
            
            # Convert string dates to datetime if needed
            if isinstance(from_date, str):
                from_date = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            if isinstance(to_date, str):
                to_date = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            
            # Collect data using LangChain GitLab tools
            merge_requests = await self.tools.get_merge_requests(project_id, from_date, to_date)
            issues = await self.tools.get_issues(project_id, from_date, to_date)
            commits = await self.tools.get_commits(project_id, from_date, to_date)
            
            # Extract contributors
            contributors = set()
            for mr in merge_requests:
                if 'author' in mr:
                    contributors.add(mr['author'])
            for issue in issues:
                if issue.get('closed_by'):
                    contributors.add(issue['closed_by'])
            
            return {
                'merge_requests': merge_requests,
                'issues': issues,
                'commits': commits,
                'contributors': contributors
            }
            
        except Exception as e:
            return {'error': str(e)}