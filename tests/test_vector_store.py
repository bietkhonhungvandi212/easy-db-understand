import pytest
import pandas as pd
from core.database.metadata_extractor import DatabaseMetadataExtractor
from core.knowledge.vector_store import VectorStore
from rich.console import Console

console = Console()

class TestVectorStore:
    @pytest.fixture
    def setup(self):
        """Set up test components"""
        self.metadata_extractor = DatabaseMetadataExtractor()
        self.vector_store = VectorStore()
        
    def test_store_and_retrieve_table(self, setup):
        """Test storing and retrieving table information"""
        # Extract a sample table
        tables_df = self.metadata_extractor.extract_tables()
        if tables_df.empty:
            pytest.skip("No tables found in database")
            
        # Get first table and its columns
        table = tables_df.iloc[0]
        columns_df = self.metadata_extractor.extract_columns(table['table_name'])
        columns_list = columns_df.to_dict('records')
        
        # Store table in vector store
        doc_id = self.vector_store.add_table(
            table_name=table['table_name'],
            description=table['description'],
            columns=columns_list,
            metadata={
                'row_count': int(table['row_count']),
                'created_at': str(table['created_at']),
                'updated_at': str(table['updated_at'])
            }
        )
        
        # Retrieve and verify
        stored_doc = self.vector_store.get_by_id(doc_id)
        assert stored_doc is not None, "Failed to retrieve stored table"
        assert stored_doc['metadata']['table_name'] == table['table_name']
        assert stored_doc['metadata']['type'] == 'table'
        
    def test_store_and_retrieve_column(self, setup):
        """Test storing and retrieving column information"""
        # Extract a sample column
        columns_df = self.metadata_extractor.extract_columns()
        if columns_df.empty:
            pytest.skip("No columns found in database")
            
        column = columns_df.iloc[0]
        
        # Store column in vector store
        doc_id = self.vector_store.add_column(
            table_name=column['table_name'],
            column_name=column['column_name'],
            data_type=column['data_type'],
            description=column['description'],
            metadata={
                'is_nullable': str(column['is_nullable']),
                'key_type': str(column['key_type'])
            }
        )
        
        # Retrieve and verify
        stored_doc = self.vector_store.get_by_id(doc_id)
        assert stored_doc is not None, "Failed to retrieve stored column"
        assert stored_doc['metadata']['table_name'] == column['table_name']
        assert stored_doc['metadata']['column_name'] == column['column_name']
        assert stored_doc['metadata']['type'] == 'column'
        
    def test_store_and_retrieve_relationship(self, setup):
        """Test storing and retrieving relationship information"""
        # Extract foreign keys
        foreign_keys_df = self.metadata_extractor.extract_foreign_keys()
        if foreign_keys_df.empty:
            pytest.skip("No foreign keys found in database")
            
        fk = foreign_keys_df.iloc[0]
        
        # Store relationship in vector store
        doc_id = self.vector_store.add_relationship(
            source_table=fk['table_name'],
            source_column=fk['column_name'],
            target_table=fk['referenced_table'],
            target_column=fk['referenced_column'],
            relationship_type='foreign_key',
            description=f"Foreign key relationship from {fk['table_name']}.{fk['column_name']} to {fk['referenced_table']}.{fk['referenced_column']}",
            metadata={
                'update_rule': str(fk['update_rule']),
                'delete_rule': str(fk['delete_rule'])
            }
        )
        
        # Retrieve and verify
        stored_doc = self.vector_store.get_by_id(doc_id)
        assert stored_doc is not None, "Failed to retrieve stored relationship"
        assert stored_doc['metadata']['type'] == 'relationship'
        assert stored_doc['metadata']['source_table'] == fk['table_name']
        assert stored_doc['metadata']['target_table'] == fk['referenced_table']
        
    def test_search_functionality(self, setup):
        """Test semantic search functionality"""
        # First, ensure we have some data
        tables_df = self.metadata_extractor.extract_tables()
        if tables_df.empty:
            pytest.skip("No tables found in database")
            
        # Store a sample table
        table = tables_df.iloc[0]
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
        
        # Test semantic search
        search_query = f"Find information about {table['table_name']}"
        results = self.vector_store.search(query=search_query)
        
        assert len(results) > 0, "Search returned no results"
        assert any(r['metadata']['table_name'] == table['table_name'] for r in results), "Search did not find the stored table"
        
    def test_get_by_table_name(self, setup):
        """Test retrieving all documents for a specific table"""
        # First, ensure we have some data
        tables_df = self.metadata_extractor.extract_tables()
        if tables_df.empty:
            pytest.skip("No tables found in database")
            
        # Store a sample table and its columns
        table = tables_df.iloc[0]
        columns_df = self.metadata_extractor.extract_columns(table['table_name'])
        
        # Store table
        self.vector_store.add_table(
            table_name=table['table_name'],
            description=table['description'],
            columns=columns_df.to_dict('records'),
            metadata={
                'row_count': int(table['row_count']),
                'created_at': str(table['created_at']),
                'updated_at': str(table['updated_at'])
            }
        )
        
        # Store each column
        for _, column in columns_df.iterrows():
            self.vector_store.add_column(
                table_name=column['table_name'],
                column_name=column['column_name'],
                data_type=column['data_type'],
                description=column['description'],
                metadata={
                    'is_nullable': str(column['is_nullable']),
                    'key_type': str(column['key_type'])
                }
            )
        
        # Retrieve all documents for the table
        table_docs = self.vector_store.get_by_table_name(table['table_name'])
        
        assert len(table_docs) > 0, "No documents found for table"
        assert all(doc['metadata']['table_name'] == table['table_name'] for doc in table_docs), "Retrieved documents contain incorrect table"
        
    def test_embedding_generation(self, setup):
        """Test embedding generation functionality"""
        test_text = "This is a test document for embedding generation"
        embedding = self.vector_store.get_embedding(test_text)
        
        assert isinstance(embedding, list), "Embedding should be a list"
        assert len(embedding) > 0, "Embedding should not be empty"
        assert all(isinstance(x, float) for x in embedding), "Embedding should contain floats"