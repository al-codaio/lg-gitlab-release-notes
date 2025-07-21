# GitLab Release Notes Generator

A LangGraph-powered application that automatically generates comprehensive release notes by analyzing GitLab activity between releases using the LangChain GitLab toolkit.

## Features

- **LangChain GitLab Integration**: Uses LangChain's GitLab toolkit with direct python-gitlab API access
- **Automated Data Collection**: Fetches merge requests, issues, and commits from GitLab
- **Smart Categorization**: Uses LLM to categorize changes into features, bug fixes, breaking changes, etc.
- **Human-in-the-Loop**: Optional review step for generated release notes
- **Flexible Date Ranges**: Support for both tag-based and date-based analysis
- **Customizable Output**: Markdown-formatted release notes with emoji sections

## Architecture

The application uses a two-agent system with LangChain GitLab integration:

1. **Collector Agent**: Gathers data from GitLab via LangChain GitLab toolkit
2. **Writer Agent**: Analyzes and generates formatted release notes

## Setup

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- GitLab account with API access
- OpenAI API key

### Installation

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone <repository-url>
cd gitlab-release-notes
```

3. Create virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Environment Variables

- `GITLAB_URL`: Your GitLab instance URL (default: https://gitlab.com)
- `GITLAB_PRIVATE_TOKEN`: Your GitLab personal access token
- `PROJECT_ID`: The GitLab project ID to analyze
- `OPENAI_API_KEY`: Your OpenAI API key

## Usage

```bash
uv run python main.py
```

The application uses LangChain's GitLab toolkit for GitLab integration, providing:
- Direct access to python-gitlab API through LangChain wrapper
- Full GitLab API capabilities with proper filtering
- Robust error handling and pagination support

The application will:
1. Collect data from the last 30 days (configurable)
2. Categorize changes using AI
3. Generate formatted release notes
4. Optionally request human review
5. Save output to `RELEASE_NOTES.md`

## Project Structure

```
gitlab-release-notes/
├── src/
│   ├── agents/          # Collector and Writer agents
│   ├── graph/           # LangGraph async workflow and state
│   ├── tools/           # GitLab LangChain tools integration
│   └── config.py        # Configuration management
├── main.py              # Entry point
├── pyproject.toml       # Project configuration and dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Development

Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

Run tests:
```bash
pytest
```

Format code:
```bash
black src/
```

Lint code:
```bash
ruff check src/
```

Type checking:
```bash
mypy src/
```

## Customization

### Modify Date Range

Edit `main.py` to change the analysis period:
```python
initial_state = ReleaseNotesState(
    project_id=os.getenv('PROJECT_ID'),
    from_date=datetime.now() - timedelta(days=60),  # Last 60 days
    to_date=datetime.now(),
    ...
)
```

### Use Tag-Based Analysis

Specify tags instead of dates:
```python
initial_state = ReleaseNotesState(
    from_tag="v1.0.0",
    to_tag="v2.0.0",
    ...
)
```

### Disable Human Review

Remove the review node from the workflow in `src/graph/async_workflow.py`.

## Example Output

```markdown
# Release Notes - v2.1.0

## 🎉 New Features
- Add user authentication system (#123)
- Implement dark mode support (#145)

## 🐛 Bug Fixes
- Fix memory leak in data processor (#134)
- Resolve login timeout issues (#156)

## ⚠️ Breaking Changes
- API endpoint `/users` now requires authentication
- Removed deprecated `getUser()` method

## 👥 Contributors
Thanks to: @alice, @bob, @charlie
```

## License

MIT License