import pytest
from core.agent.agent_core import InsuranceSchemaAgent
from core.database.metadata_extractor import DatabaseMetadataExtractor
from core.knowledge.vector_store import VectorStore
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

class TestLLMAgent:
    @pytest.fixture
    def setup(self):
        """Set up test components"""
        self.metadata_extractor = DatabaseMetadataExtractor()
        self.vector_store = VectorStore()
        self.agent = InsuranceSchemaAgent()
        
    def test_schema_queries(self, setup):
        """Test various schema-related queries"""
        # First, ensure we have data in the vector store
        tables_df = self.metadata_extractor.extract_tables()
        if tables_df.empty:
            pytest.skip("No tables found in database")
            
        # Store schema information in vector store
        for _, table in tables_df.iterrows():
            columns_df = self.metadata_extractor.extract_columns(table['table_name'])
            columns_list = columns_df.to_dict('records')
            
            self.vector_store.add_table(
                table_name=table['table_name'],
                description=table['description'],
                columns=columns_list,
                metadata={
                    'row_count': int(table['row_count']),
                    'created_at': str(table['created_at']),
                    'updated_at': str(table['updated_at'])
                }
            )
        
        # Test queries
        test_queries = [
            # "I am developing the email for welcome email for new members, you should focus on the tables related to the email, member",
            "what is the tables related to company and member?",
            # "Show me the structure of the accident table",
            # "What are the main tables for storing insurance claims?",
            # "How are policies and claims related in the database?",
            # "What tables store customer information?"
        ]
        
        for query in test_queries:
            console.print(Panel(f"[bold blue]Query:[/bold blue] {query}", title="Testing LLM Agent"))
            
            try:
                # Get response from agent
                response = self.agent.ask(query)
                
                # Basic validation
                assert response is not None, "Response should not be None"
                assert len(response) > 0, "Response should not be empty"
                
            except Exception as e:
                console.print(f"[bold red]Error processing query: {str(e)}[/bold red]")
                raise
    
    # def test_specific_table_queries(self, setup):
    #     """Test queries about specific tables"""
    #     # Get a sample table
    #     tables_df = self.metadata_extractor.extract_tables()
    #     if tables_df.empty:
    #         pytest.skip("No tables found in database")
            
    #     sample_table = tables_df.iloc[0]
        
    #     # Test specific queries about this table
    #     specific_queries = [
    #         f"What is the purpose of the {sample_table['table_name']} table?",
    #         f"Show me the columns in the {sample_table['table_name']} table",
    #         f"What are the relationships of the {sample_table['table_name']} table?",
    #         f"Explain the data types used in the {sample_table['table_name']} table"
    #     ]
        
    #     for query in specific_queries:
    #         console.print(Panel(f"[bold blue]Query:[/bold blue] {query}", title="Testing Specific Table Queries"))
            
    #         try:
    #             # Get response from agent
    #             response = self.agent.ask(query)
                
    #             # Print response in a nice format
    #             console.print(Panel(
    #                 Markdown(response),
    #                 title="LLM Response",
    #                 border_style="green"
    #             ))
                
    #             # Basic validation
    #             assert response is not None, "Response should not be None"
    #             assert len(response) > 0, "Response should not be empty"
    #             assert sample_table['table_name'].lower() in response.lower(), f"Response should mention {sample_table['table_name']}"
                
    #         except Exception as e:
    #             console.print(f"[bold red]Error processing query: {str(e)}[/bold red]")
    #             raise
    
    # def test_relationship_queries(self, setup):
    #     """Test queries about table relationships"""
    #     # Get foreign keys
    #     foreign_keys_df = self.metadata_extractor.extract_foreign_keys()
    #     if foreign_keys_df.empty:
    #         pytest.skip("No foreign keys found in database")
            
    #     # Test relationship queries
    #     relationship_queries = [
    #         "What are the main relationships between tables in this database?",
    #         "How are policies and claims connected?",
    #         "Show me the foreign key relationships in the database",
    #         "What tables reference the user table?"
    #     ]
        
    #     for query in relationship_queries:
    #         console.print(Panel(f"[bold blue]Query:[/bold blue] {query}", title="Testing Relationship Queries"))
            
    #         try:
    #             # Get response from agent
    #             response = self.agent.ask(query)
                
    #             # Print response in a nice format
    #             console.print(Panel(
    #                 Markdown(response),
    #                 title="LLM Response",
    #                 border_style="green"
    #             ))
                
    #             # Basic validation
    #             assert response is not None, "Response should not be None"
    #             assert len(response) > 0, "Response should not be empty"
                
    #         except Exception as e:
    #             console.print(f"[bold red]Error processing query: {str(e)}[/bold red]")
    #             raise 