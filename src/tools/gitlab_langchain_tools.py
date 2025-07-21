"""
GitLab tools using LangChain GitLab toolkit with proper python-gitlab API access

This implementation shows how to properly use the LangChain GitLabAPIWrapper
to access the underlying python-gitlab API for operations that aren't directly
exposed through the LangChain tools.
"""

import os
from typing import List, Dict, Set, Optional
from datetime import datetime
from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
from langchain_community.utilities.gitlab import GitLabAPIWrapper
import gitlab.exceptions

class GitLabLangChainTools:
    """GitLab tools using LangChain toolkit with direct python-gitlab access"""
    
    def __init__(self):
        # Initialize GitLab API wrapper
        print(f"Initializing GitLab connection...")
        print(f"GitLab URL: {os.getenv('GITLAB_URL', 'https://gitlab.com')}")
        print(f"Project ID: {os.getenv('PROJECT_ID')}")
        
        try:
            self.gitlab_wrapper = GitLabAPIWrapper(
                gitlab_base_url=os.getenv('GITLAB_URL', 'https://gitlab.com'),
                gitlab_personal_access_token=os.getenv('GITLAB_PRIVATE_TOKEN'),
                gitlab_repository=os.getenv('PROJECT_ID')  # Can be project ID or path
            )
            print("GitLab wrapper initialized successfully")
        except Exception as e:
            print(f"Error initializing GitLab wrapper: {e}")
            raise
        
        # After initialization, we have access to:
        # - self.gitlab_wrapper.gitlab: The python-gitlab Gitlab instance
        # - self.gitlab_wrapper.gitlab_repo_instance: The python-gitlab Project instance
        
        # Create toolkit for LangChain tools
        print("Creating GitLab toolkit...")
        try:
            self.toolkit = GitLabToolkit.from_gitlab_api_wrapper(self.gitlab_wrapper)
            self.tools = self.toolkit.get_tools()
            
            # Log available tools
            tool_names = [tool.name for tool in self.tools]
            print(f"Available LangChain GitLab tools: {', '.join(tool_names)}")
        except Exception as e:
            print(f"Error creating toolkit: {e}")
            # Continue anyway, we mainly use direct API access
            self.tools = []
        
        # Get direct access to project
        try:
            self.project = self.gitlab_wrapper.gitlab_repo_instance
            print(f"Connected to GitLab project: {self.project.path_with_namespace}")
        except Exception as e:
            print(f"Error accessing project: {e}")
            raise
    
    async def get_merge_requests(self, project_id: str, since: datetime, until: datetime) -> List[Dict]:
        """Get merged MRs using python-gitlab API directly"""
        try:
            # Use python-gitlab API directly
            merge_requests = self.project.mergerequests.list(
                state='merged',
                updated_after=since.isoformat(),
                updated_before=until.isoformat(),
                order_by='updated_at',
                sort='desc',
                all=True  # Get all pages
            )
            
            mrs_data = []
            for mr in merge_requests:
                try:
                    # Get full MR data
                    mr_full = self.project.mergerequests.get(mr.iid)
                    
                    # Check if actually merged in our date range
                    if mr_full.merged_at:
                        merged_date = datetime.fromisoformat(mr_full.merged_at.replace('Z', '+00:00'))
                        if since <= merged_date <= until:
                            mrs_data.append({
                                'iid': mr_full.iid,
                                'title': mr_full.title,
                                'description': mr_full.description or '',
                                'author': mr_full.author.get('username', 'Unknown'),
                                'merged_at': mr_full.merged_at,
                                'merged_by': mr_full.merged_by.get('username', 'Unknown') if mr_full.merged_by else None,
                                'web_url': mr_full.web_url,
                                'labels': mr_full.labels,
                                'milestone': mr_full.milestone.get('title') if mr_full.milestone else None,
                                'source_branch': mr_full.source_branch,
                                'target_branch': mr_full.target_branch
                            })
                except Exception as e:
                    print(f"Error processing MR {mr.iid}: {e}")
                    continue
            
            print(f"Found {len(mrs_data)} merged MRs between {since.date()} and {until.date()}")
            return mrs_data
            
        except Exception as e:
            print(f"Error fetching merge requests: {e}")
            return []
    
    async def get_issues(self, project_id: str, since: datetime, until: datetime) -> List[Dict]:
        """Get closed issues using python-gitlab API directly"""
        try:
            # Get closed issues
            issues = self.project.issues.list(
                state='closed',
                updated_after=since.isoformat(),
                updated_before=until.isoformat(),
                order_by='updated_at',
                sort='desc',
                all=True
            )
            
            issues_data = []
            for issue in issues:
                try:
                    # Get full issue data
                    issue_full = self.project.issues.get(issue.iid)
                    
                    # Check if closed in our date range
                    if issue_full.closed_at:
                        closed_date = datetime.fromisoformat(issue_full.closed_at.replace('Z', '+00:00'))
                        if since <= closed_date <= until:
                            issues_data.append({
                                'iid': issue_full.iid,
                                'title': issue_full.title,
                                'description': issue_full.description or '',
                                'author': issue_full.author.get('username', 'Unknown'),
                                'closed_at': issue_full.closed_at,
                                'closed_by': issue_full.closed_by.get('username', 'Unknown') if hasattr(issue_full, 'closed_by') and issue_full.closed_by else None,
                                'web_url': issue_full.web_url,
                                'labels': issue_full.labels,
                                'milestone': issue_full.milestone.get('title') if issue_full.milestone else None,
                                'assignees': [a.get('username', 'Unknown') for a in (issue_full.assignees or [])]
                            })
                except Exception as e:
                    print(f"Error processing issue {issue.iid}: {e}")
                    continue
            
            print(f"Found {len(issues_data)} closed issues between {since.date()} and {until.date()}")
            return issues_data
            
        except Exception as e:
            print(f"Error fetching issues: {e}")
            return []
    
    async def get_commits(self, project_id: str, since: datetime, until: datetime, ref_name: str = None) -> List[Dict]:
        """Get commits using python-gitlab API directly"""
        try:
            # Use default branch if not specified
            if not ref_name:
                ref_name = self.project.default_branch
            
            # Get commits
            commits = self.project.commits.list(
                ref_name=ref_name,
                since=since.isoformat(),
                until=until.isoformat(),
                all=True
            )
            
            commits_data = []
            for commit in commits:
                commits_data.append({
                    'id': commit.id,
                    'short_id': commit.short_id,
                    'title': commit.title,
                    'message': commit.message,
                    'author_name': commit.author_name,
                    'author_email': commit.author_email,
                    'authored_date': commit.authored_date,
                    'committed_date': commit.committed_date,
                    'web_url': commit.web_url,
                    'parent_ids': commit.parent_ids
                })
            
            print(f"Found {len(commits_data)} commits between {since.date()} and {until.date()}")
            return commits_data
            
        except Exception as e:
            print(f"Error fetching commits: {e}")
            return []
    
    def get_gitlab_api(self):
        """Get the underlying GitLab API wrapper for direct access if needed"""
        return self.gitlab_wrapper
    
    def get_project(self):
        """Get the python-gitlab project instance for direct access"""
        return self.project
    
    async def get_contributors(self, since: datetime, until: datetime) -> Set[str]:
        """Get unique contributors in the date range"""
        contributors = set()
        
        # Get from MRs
        mrs = await self.get_merge_requests(self.project.id, since, until)
        for mr in mrs:
            contributors.add(mr['author'])
            if mr.get('merged_by'):
                contributors.add(mr['merged_by'])
        
        # Get from commits
        commits = await self.get_commits(self.project.id, since, until)
        for commit in commits:
            contributors.add(commit['author_name'])
        
        # Get from issues
        issues = await self.get_issues(self.project.id, since, until)
        for issue in issues:
            contributors.add(issue['author'])
            contributors.update(issue.get('assignees', []))
        
        return contributors
    
    async def get_milestones(self, since: datetime, until: datetime) -> List[Dict]:
        """Get milestones in date range"""
        try:
            milestones = self.project.milestones.list(
                state='all',
                updated_after=since.isoformat(),
                updated_before=until.isoformat(),
                all=True
            )
            
            milestones_data = []
            for milestone in milestones:
                milestones_data.append({
                    'id': milestone.id,
                    'iid': milestone.iid,
                    'title': milestone.title,
                    'description': milestone.description,
                    'state': milestone.state,
                    'created_at': milestone.created_at,
                    'updated_at': milestone.updated_at,
                    'due_date': milestone.due_date,
                    'web_url': milestone.web_url
                })
            
            return milestones_data
            
        except Exception as e:
            print(f"Error fetching milestones: {e}")
            return []