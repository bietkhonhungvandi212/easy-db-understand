# Database Component Documentation

## Overview
The database component handles all database interactions, including connection management, metadata extraction, and schema analysis. It provides a unified interface for accessing database information.

## Key Components

### DatabaseConnection
- Manages database connections
- Implements connection pooling
- Handles connection errors and retries

### MetadataExtractor
- Extracts table and column information
- Identifies relationships and constraints
- Generates schema metadata

## Key Features

### Schema Extraction
- Table structure analysis
- Column metadata retrieval
- Relationship mapping
- Constraint identification

### Query Execution
- Safe query execution
- Result formatting
- Error handling

## Usage Examples

### Basic Schema Extraction
```python
from core.database.metadata_extractor import DatabaseMetadataExtractor

# Initialize the extractor
extractor = DatabaseMetadataExtractor()

# Get all tables
tables = extractor.extract_tables()
print(f"Found {len(tables)} tables")

# Get columns for a specific table
columns = extractor.extract_columns("email_setting")
for column in columns:
    print(f"Column: {column['column_name']}, Type: {column['data_type']}")
```

### Advanced Schema Analysis
```python
from core.database.metadata_extractor import DatabaseMetadataExtractor
from settings_config import Settings

# Initialize with custom settings
settings = Settings(
    database=DatabaseSettings(
        connection_timeout=30,
        max_retries=3
    )
)
extractor = DatabaseMetadataExtractor(settings=settings)

# Get foreign key relationships
relationships = extractor.extract_foreign_keys("email_setting")
for rel in relationships.get("outgoing", []):
    print(f"Foreign key: {rel['source_column']} -> {rel['target_table']}.{rel['target_column']}")

# Find tables by keyword
tables = extractor.find_tables_by_keyword("email")
for table in tables:
    print(f"Found table: {table['table_name']}")
```
## Configuration
Database settings include:
- Connection parameters
- Query timeouts
- Metadata extraction options
- Caching preferences
- Retry policies
- Error handling strategies 