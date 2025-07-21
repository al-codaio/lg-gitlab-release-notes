from typing import TypedDict, List, Dict, Set, Optional
from datetime import datetime

class ReleaseNotesState(TypedDict):
    # Configuration
    project_id: str
    from_tag: Optional[str]
    to_tag: Optional[str]
    from_date: Optional[datetime]
    to_date: Optional[datetime]
    
    # Raw data from GitLab
    merge_requests: List[Dict]
    issues: List[Dict]
    commits: List[Dict]
    
    # Processed data
    categorized_changes: Dict[str, List[Dict]]
    contributors: Set[str]
    statistics: Dict[str, int]
    
    # Output
    release_notes_markdown: str
    release_notes_sections: Dict[str, List[str]]
    
    # Control flow
    needs_human_review: bool
    error: Optional[str]