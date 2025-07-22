from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage

class WriterAgent:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.categorization_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a release notes expert. Categorize the following changes:
            - Features: New functionality
            - Fixes: Bug fixes
            - Breaking: Breaking changes
            - Performance: Performance improvements
            - Documentation: Doc updates
            - Other: Everything else"""),
            ("human", "Categorize this change: {change}")
        ])
        
    def categorize_changes(self, state: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Use LLM to categorize all changes"""
        categories = {
            'features': [],
            'fixes': [],
            'breaking': [],
            'performance': [],
            'documentation': [],
            'other': []
        }
        
        # Process merge requests
        for mr in state['merge_requests']:
            chain = self.categorization_prompt | self.llm
            result = chain.invoke({'change': f"{mr['title']} - {mr['description']}"})
            category = self._extract_category(result.content)
            categories[category].append(mr)
        
        return categories
    
    def generate_release_notes(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate formatted release notes"""
        categorized = self.categorize_changes(state)
        
        sections = {}
        markdown_parts = [f"# Release Notes - {state.get('to_tag', 'Latest')}\n"]
        
        # Features section
        if categorized['features']:
            sections['features'] = [f"- {mr['title']} (#{mr['iid']})" 
                                   for mr in categorized['features']]
            markdown_parts.append("\n## ✨ New Features")
            markdown_parts.extend(sections['features'])
        
        # Bug fixes
        if categorized['fixes']:
            sections['fixes'] = [f"- {mr['title']} (#{mr['iid']})" 
                               for mr in categorized['fixes']]
            markdown_parts.append("\n## 🐛 Bug Fixes")
            markdown_parts.extend(sections['fixes'])
        
        # Breaking changes
        if categorized['breaking']:
            sections['breaking'] = [f"- {mr['title']} (#{mr['iid']})" 
                                  for mr in categorized['breaking']]
            markdown_parts.append("\n## ⚠️ Breaking Changes")
            markdown_parts.extend(sections['breaking'])
        
        # Contributors
        if state['contributors']:
            markdown_parts.append(f"\n## 👥 Contributors")
            markdown_parts.append(f"Thanks to: {', '.join(sorted(state['contributors']))}")
        
        return {
            'categorized_changes': categorized,
            'release_notes_sections': sections,
            'release_notes_markdown': '\n'.join(markdown_parts)
        }
    
    def _extract_category(self, llm_response: str) -> str:
        """Extract category from LLM response"""
        response_lower = llm_response.lower()
        if 'feature' in response_lower:
            return 'features'
        elif 'fix' in response_lower or 'bug' in response_lower:
            return 'fixes'
        elif 'breaking' in response_lower:
            return 'breaking'
        elif 'performance' in response_lower:
            return 'performance'
        elif 'documentation' in response_lower:
            return 'documentation'
        return 'other'