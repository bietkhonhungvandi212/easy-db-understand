# Knowledge Component Documentation

## Overview
The knowledge component manages the vector store and knowledge base for efficient schema information retrieval. It implements semantic search capabilities and maintains the database schema knowledge base.

## Key Components

### VectorStore
- Implements vector-based schema search
- Manages schema embeddings
- Provides semantic search capabilities

### KnowledgeBase
- Maintains schema information
- Updates and refreshes knowledge
- Manages metadata storage

## Key Features

### Vector Search
- Semantic schema search
- Similarity matching
- Context-aware retrieval

### Knowledge Management
- Schema information storage
- Metadata management
- Knowledge base updates

## Usage Examples

### Basic Vector Search
```python
from core.knowledge.vector_store import VectorStore

# Initialize vector store
vector_store = VectorStore()

# Simple search for email-related tables
results = vector_store.search(
    query="email system tables",
    filter_metadata={"type": "table"},
    limit=5
)

# Process results
for result in results:
    print(f"Found table: {result['metadata']['table_name']}")
    print(f"Relevance score: {result['score']}")
```

### Advanced Search with Filters
```python
from core.knowledge.vector_store import VectorStore
from settings_config import Settings

# Initialize with custom settings
settings = Settings(
    knowledge=KnowledgeSettings(
        similarity_threshold=0.7,
        max_results=10
    )
)
vector_store = VectorStore(settings=settings)

# Complex search with multiple filters
results = vector_store.search(
    query="Find tables related to email templates and recipients",
    filter_metadata={
        "type": "table",
        "category": "email"
    },
    limit=10
)

# Process and analyze results
for result in results:
    metadata = result['metadata']
    print(f"""
    Table: {metadata['table_name']}
    Description: {metadata['description']}
    Relevance: {result['score']:.2f}
    """)
```

### Knowledge Base Management
```python
from core.knowledge.vector_store import VectorStore
from core.exceptions import VectorStoreError

vector_store = VectorStore()

try:
    # Update knowledge base with new schema information
    vector_store.update_knowledge_base(
        tables_info=[
            {
                "table_name": "email_setting",
                "description": "Email settings configuration",
                "columns": [...]
            }
        ]
    )
    
    # Verify update
    results = vector_store.search("email settings")
    print(f"Found {len(results)} relevant items")
    
except VectorStoreError as e:
    print(f"Error updating knowledge base: {e}")
    # Handle error appropriately
```

## Configuration
Knowledge base settings include:
- Vector store parameters
- Search configuration
- Knowledge base update frequency
- Caching options
- Similarity thresholds
- Error handling policies 