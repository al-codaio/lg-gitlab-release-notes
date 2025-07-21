from typing import Dict, Any
from ..tools.gitlab_langchain_tools import GitLabLangChainTools

class CollectorAgent:
    def __init__(self, gitlab_tools: GitLabLangChainTools):
        self.tools = gitlab_tools
    
    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Collect all relevant data from GitLab using LangChain GitLab toolkit"""
        try:
            project_id = state['project_id']
            
            # Determine date range
            if state.get('from_tag') and state.get('to_tag'):
                # Get commits between tags
                commits = await self.tools.get_commits(
                    project_id,
                    state['from_tag'], 
                    state['to_tag']
                )
                # Extract date range from commits if needed
                from_date = state.get('from_date', commits[-1]['committed_date'] if commits else None)
                to_date = state.get('to_date', commits[0]['committed_date'] if commits else None)
            else:
                # Use provided dates
                from_date = state['from_date']
                to_date = state['to_date']
                commits = []
            
            # Collect data using LangChain GitLab tools
            merge_requests = await self.tools.get_merge_requests(project_id, from_date, to_date)
            issues = await self.tools.get_issues(project_id, from_date, to_date)
            
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