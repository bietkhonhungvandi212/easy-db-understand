# Agent Component Documentation

## Overview
The agent component is responsible for interacting with the LLM to analyze and explain database schemas. It processes user queries, retrieves relevant schema information, and generates human-readable explanations.

## Key Components

### LLMInterface
- Handles communication with the LLM service
- Manages API calls and response formatting
- Implements error handling and retry logic

### AgentCore
- Main agent implementation for database analysis
- Processes user queries and retrieves context
- Formats schema information for LLM consumption
- Generates comprehensive schema explanations

## Key Features

### Schema Context Retrieval
- Extracts relevant tables and relationships
- Filters out unnecessary technical details
- Formats information for clear understanding

### Query Processing
- Analyzes user queries for intent
- Identifies relevant database components
- Generates appropriate context

### Response Generation
- Creates human-readable explanations
- Includes relevant examples
- Provides relationship context

## Usage Examples

### Basic Usage
```python
from core.agent.agent_core import AgentCore

# Initialize the agent
agent = AgentCore()

# Ask a simple question about the database
response = agent.ask("What tables are used for email functionality?")
```

### Advanced Usage
```python
from core.agent.agent_core import AgentCore
from settings_config import Settings

# Initialize with custom settings
settings = Settings(
    agent=AgentSettings(
        max_tables_per_query=10,
        cache_enabled=True
    )
)
agent = AgentCore(settings=settings)

# Ask complex questions
response = agent.ask("""
    Explain how the email system works, including:
    1. How are email templates stored?
    2. How are recipients managed?
    3. What tables track email delivery?
""")
```

## Configuration
The agent can be configured through settings:
- LLM model selection
- Response formatting options
- Context retrieval parameters
- Cache settings
- Error handling preferences 