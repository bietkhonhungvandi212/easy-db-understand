import os
import json
from typing import List, Dict, Any, Optional
from core.agent.llm_interface import LLMInterface, LLMResponse
from core.database.metadata_extractor import DatabaseMetadataExtractor
from core.knowledge.vector_store import VectorStore
from rich.console import Console
from settings_config import Settings
from core.utils.print_utils import print_dict_list_table

console = Console()

class AgentMemory:
    """Memory component for the agent to store conversation history"""
    
    def __init__(self, max_history: int = 10):
        self.conversation_history = []
        self.max_history = max_history
        self.context_cache = {}
        
    def add_interaction(self, query: str, response: LLMResponse):
        """Add a query-response pair to memory"""
        self.conversation_history.append({
            "query": query,
            "response": response
        })
        
        # Trim history if needed
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
            
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, LLMResponse]]:
        """Get conversation history, optionally limited to last N interactions"""
        if limit is None or limit >= len(self.conversation_history):
            return self.conversation_history
        return self.conversation_history[-limit:]
    
    def cache_context(self, query: str, context: Dict[str, Any]):
        """Cache context for a query"""
        self.context_cache[query] = context
        
    def get_cached_context(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached context for a query if available"""
        return self.context_cache.get(query)

class InsuranceSchemaAgent:
    """
    Advanced LLM agent for insurance database schema analysis
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        # db_config: Optional[Dict[str, Any]] = None,
        # llm_config: Optional[Dict[str, Any]] = None,
        # vector_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the agent with components and configuration"""
        self.settings = Settings()
        
        # Initialize components
        self.llm = LLMInterface()
        
        self.db = DatabaseMetadataExtractor()
        
        self.vector_store = VectorStore()
        
        # NOTE: Knowledge Graph is not used in this version
        # self.knowledge_graph = KnowledgeGraph()
        
        # Initialize memory
        self.memory = AgentMemory(max_history=10)
        
        # Define system prompts
        self.system_prompts = {
            "default": """You are an expert database analyst specializing in insurance database schemas. 
Your task is to analyze and explain database tables, columns, and relationships 
in a clear, concise manner. Focus on explaining how different database components 
relate to business functionality in the insurance domain.""",
            
            "schema_analysis": """You are an expert database schema analyst for insurance systems.
Analyze the provided database schema information and explain how it relates to 
the requested feature or functionality. Focus on identifying relevant tables, 
their relationships, and how they support business processes. Include specific
field names and data types where relevant. Your analysis should be comprehensive
yet easy to understand for both technical and business users."""
        }
        
    # def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
    #     """Load configuration from file or use defaults"""
    #     default_config = {
    #         "database": {
    #             "host": os.environ.get("MYSQL_HOST", "localhost"),
    #             "port": int(os.environ.get("MYSQL_PORT", "3306")),
    #             "user": os.environ.get("MYSQL_USER", "root"),
    #             "password": os.environ.get("MYSQL_PASSWORD", ""),
    #             "database": os.environ.get("MYSQL_DATABASE", "insurance_db")
    #         },
    #         "llm": {
    #             "base_url": os.environ.get("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
    #             "api_key": os.environ.get("LM_STUDIO_API_KEY", "lm-studio"),
    #             "model": os.environ.get("LM_STUDIO_MODEL", "DeepSeek-R1-Distill-Qwen-7B-Q4_K_M")
    #         },
    #         "vector": {
    #             "persist_directory": os.environ.get("CHROMA_PERSIST_DIRECTORY", "./data/embeddings"),
    #             "collection_name": os.environ.get("CHROMA_COLLECTION_NAME", "insurance_schema")
    #         },
    #         "max_history": 10,
    #         "cache_enabled": True,
    #         "cache_ttl": 3600,
    #         "max_tables_per_query": 50
    #     }
        
    #     if config_path and os.path.exists(config_path):
    #         with open(config_path, 'r') as f:
    #             file_config = json.load(f)
    #             # Merge configurations
    #             for key, value in file_config.items():
    #                 if key in default_config and isinstance(value, dict) and isinstance(default_config[key], dict):
    #                     default_config[key].update(value)
    #                 else:
    #                     default_config[key] = value
                        
    #     return default_config
    
    def _format_schema_context(self, tables_info: List[Dict[str, Any]], relationships: List[Dict[str, Any]], query: str, additional_notes: List[str] = None) -> str:
        """
        Format the schema context into a comprehensive, readable format.
        
        Args:
            tables_info: List of table information
            relationships: List of relationships
            query: The original query
            additional_notes: List of additional notes
            
        Returns:
            str: Formatted schema context
        """
        formatted_context = []
        
        # Add query section
        formatted_context.append("QUERY:")
        formatted_context.append(f"{query}\n")
        
        # Add schema overview
        formatted_context.append("SCHEMA OVERVIEW:")
        formatted_context.append("Here is a comprehensive summary of the database schema. Primary Keys are marked with (PK), and Foreign Keys/Indexes with (FK).\n")
        
        # Process each table with detailed formatting
        for i, table in enumerate(tables_info, 1):
            # Add table header with number
            formatted_context.append(f"{i}. {table['name']}: {table['description']}")
            
            # Process columns with detailed formatting
            for column in table['columns']:
                # Determine if column is PK or FK
                constraints = []
                
                # Add PK/FK markers
                if column.get('is_primary_key', False):
                    constraints.append("PK")
                if column.get('is_foreign_key', False):
                    constraints.append("FK")
                
                # Format constraints
                constraint_str = f" ({', '.join(constraints)})" if constraints else ""
                
                # Format column information with bullet point
                nullable_str = " (nullable)" if column.get('nullable', True) else " (not null)"
                
                # Special handling for ENUM types
                column_type = column['type']
                type_str = ""
                if 'enum' in column_type.lower():
                    type_str = f" ({column_type})"
                
                # Clean up description
                description = column['description'].strip()
                if 'Reference:' in description:
                    description = description.replace('Reference:', 'References:')
                if 'n' in description:
                    description = description.replace('n', ' ')
                
                formatted_context.append(f"   • {column['name']}{type_str}{constraint_str}{nullable_str}: {description}")
            
            formatted_context.append("")  # Add blank line between tables
        
        # Add relationships section with detailed formatting
        if relationships:
            formatted_context.append("RELATIONSHIPS:")
            # Group relationships by type
            outgoing_rels = [r for r in relationships if r['relationship_type'] == 'outgoing']
            incoming_rels = [r for r in relationships if r['relationship_type'] == 'incoming']
            
            if outgoing_rels:
                formatted_context.append("\nOutgoing Relationships:")
                for rel in outgoing_rels:
                    formatted_context.append(
                        f"   • {rel['source_table']}.{rel['source_column']} → {rel['target_table']}.{rel['target_column']}"
                    )
            
            if incoming_rels:
                formatted_context.append("\nIncoming Relationships:")
                for rel in incoming_rels:
                    formatted_context.append(
                        f"   • {rel['target_table']}.{rel['target_column']} ← {rel['source_table']}.{rel['source_column']}"
                    )
        
        # Add additional notes if any
        if additional_notes:
            formatted_context.append("\nADDITIONAL NOTES:")
            for note in additional_notes:
                formatted_context.append(f"   • {note}")
        
        # Add summary section
        formatted_context.append("\nSUMMARY:")
        formatted_context.append(f"   • Total Tables: {len(tables_info)}")
        formatted_context.append(f"   • Total Relationships: {len(relationships)}")
        total_columns = sum(len(table['columns']) for table in tables_info)
        formatted_context.append(f"   • Total Columns: {total_columns}")
        
        # Add a final overview paragraph
        formatted_context.append("\nOVERVIEW:")
        overview = "These tables collectively manage "
        table_purposes = []
        for table in tables_info:
            desc = table['description'].lower()
            if desc.startswith("this table stores"):
                desc = desc[16:]  # Remove "this table stores"
            table_purposes.append(desc)
        
        overview += ", ".join(table_purposes[:-1])
        if len(table_purposes) > 1:
            overview += f", and {table_purposes[-1]}"
        else:
            overview += table_purposes[0]
        
        formatted_context.append(overview)
        
        # Join all sections with newlines
        return "\n".join(formatted_context)

    def retrieve_context(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant context for a query"""

        max_tables_per_query = self.settings.agent.max_tables_per_query
        
        # Check cache if enabled
        if self.settings.agent.cache_enabled:
            cached_context = self.memory.get_cached_context(query)
            if cached_context:
                return cached_context
        
        # Extract keywords from query
        # For a simple implementation, we'll use the query directly
        
        # Search for relevant tables in vector store
        relevant_tables = self.vector_store.search(
            query=query,
            filter_metadata={"type": "table"},
            limit=max_tables_per_query
        )

        console.print("[bold green]🚀 Testing Table Search[/bold green]")
        print_dict_list_table(relevant_tables)

        
        # Get detailed schema information for relevant tables
        tables_info = []
        relationships = []
        
        for table_result in relevant_tables:
            table_name = table_result["metadata"]["table_name"]
            
            # Get columns for this table
            columns = self.db.extract_columns(table_name)
            
            # Filter out excluded fields
            if not columns.empty:
                columns = columns[~columns['column_name'].isin(self.settings.agent.excluded_fields)]
            
            # Get relationships for this table
            table_relationships = self.db.extract_foreign_keys(table_name)
            
            # Clean and format column information
            formatted_columns = []
            if not columns.empty:
                for _, col in columns.iterrows():
                    # Clean up text and format column info
                    column_info = {
                        "name": col['column_name'].strip(),
                        "type": str(col['data_type']).strip(),
                        "nullable": bool(col['is_nullable']),
                        "description": str(col.get('description', '')).strip().replace('\r\n', ' ').replace('\\', ''),
                        "is_primary_key": bool(col.get('is_primary_key', False)),
                        "is_foreign_key": bool(col.get('is_foreign_key', False))
                    }
                    formatted_columns.append(column_info)
            
            # Add to context with clean formatting
            tables_info.append({
                "name": table_name.strip(),
                "description": str(table_result["metadata"]["description"]).strip().replace('\r\n', ' ').replace('\\', ''),
                "columns": formatted_columns
            })
            
            # Add relationships with clean formatting
            if "outgoing" in table_relationships:
                for rel in table_relationships["outgoing"]:
                    relationships.append({
                        "source_table": rel["source_table"].strip(),
                        "source_column": rel["source_column"].strip(),
                        "target_table": rel["target_table"].strip(),
                        "target_column": rel["target_column"].strip(),
                        "relationship_type": "outgoing"
                    })
            
            if "incoming" in table_relationships:
                for rel in table_relationships["incoming"]:
                    relationships.append({
                        "source_table": rel["source_table"].strip(),
                        "source_column": rel["source_column"].strip(),
                        "target_table": rel["target_table"].strip(),
                        "target_column": rel["target_column"].strip(),
                        "relationship_type": "incoming"
                    })
        
        # Create context with clean formatting
        context = {
            "query": query.strip(),
            "tables": tables_info,
            "relationships": relationships,
            "additional_notes": []
        }

        # Format the schema context
        formatted_schema = self._format_schema_context(
            tables_info=tables_info,
            relationships=relationships,
            query=query,
            additional_notes=context["additional_notes"]
        )

        # Cache the context
        if self.settings.agent.cache_enabled:
            self.memory.cache_context(query, context)
            
        return formatted_schema
    
    def analyze_feature_schema(self, feature_keyword: str) -> Dict[str, Any]:
        """
        Analyze database schema related to a specific feature.
        This is a high-level method that uses both database metadata
        extraction and LLM analysis.
        """
        # Get schema information from database
        schema_info = self.db.analyze_feature_related_schema(feature_keyword)
        
        # Format as prompt for LLM
        schema_prompt = f"""
        I need to understand the database schema related to the '{feature_keyword}' feature.
        
        Here is the database information I've found:
        
        Related Tables ({len(schema_info['related_tables'])}):
        {json.dumps(schema_info['related_tables'], indent=2)}
        
        Relationships ({len(schema_info['relationships'])}):
        {json.dumps(schema_info['relationships'], indent=2)}
        
        Please analyze this schema and explain:
        1. How these tables relate to the '{feature_keyword}' feature
        2. The key relationships between these tables
        3. Important business considerations for implementing this feature
        4. Any data quality checks or validation rules that should be implemented
        5. Potential optimizations for performance and reliability
        
        Your analysis should be comprehensive yet easy to understand.
        """
        
        # Get LLM analysis
        analysis_response = self.llm.generate_response(
            prompt=schema_prompt,
            system_message=self.system_prompts["schema_analysis"]
        )
        
        # Combine database information with LLM analysis
        result = {
            "feature_keyword": feature_keyword,
            "tables": schema_info['related_tables'],
            "relationships": schema_info['relationships'],
            "analysis": analysis_response.content
        }
        
        return result
    
    def ask(self, query: str) -> str:
        """Process a natural language query about database schema"""
        
        # Retrieve relevant context
        context = self.retrieve_context(query)
        
        # # Format context for LLM prompt
        # context_str = json.dumps(context, indent=2)
        
        # Create prompt with context
        prompt = f"""
        You are an expert database analyst who explains complex database concepts
        User Query: {query}

        Database Context:
        {context}
        
        Analyze the provided database schema context and generate a detailed report answering the user's question. Structure your response exactly as follows:
        Please provide a detailed and helpful response to the user's query about the database schema.
        Focus on explaining relevant tables, columns, and relationships in a clear, informative manner.
        Include specific details about data types, keys, and business significance where appropriate.

        DETAILED RESPONSE INSTRUCTIONS:
        Analyze the provided schema context and generate a detailed report. Structure your response exactly as follows and adhere to all constraints:

        1.  Strictly exclude the following columns from your response: `deleted`, `remarks`, `created_by`, `created_on`, `updated_by`, `updated_on`.
        2.  Do not mention data types (e.g., INT, VARCHAR) in your descriptions.
        3.  Generate a numbered list of the most relevant tables. For each table, provide:
               The table name in bold.
               A concise, one-sentence description of its purpose in simple terms.
               A bulleted list of its key columns, explaining what each one stores.
        4.  After the numbered list, provide a concluding summary paragraph. This summary must explain how the main tables work together as a system to manage emails.

        Your entire response must be clear, concise, and easy for someone without a technical background to understand.
        """

        """Generate a response from the LLM"""
        console.print(f"[bold green]🚀 Prompt have created successfully:\n[/bold green] {prompt}")
        
        # Generate response
        response = self.llm.generate_response(
            prompt=prompt,
            system_message=self.system_prompts["default"]
        )
        
        # Save to memory
        self.memory.add_interaction(query, response.content)
        
        return response.content