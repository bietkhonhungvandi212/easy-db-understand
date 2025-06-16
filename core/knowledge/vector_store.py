import os
import json
from typing import List, Dict, Any, Optional, Union
import numpy as np
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from chromadb import Client, Settings as ChromaSettings
from settings_config import Settings as AppSettings

class VectorStore:
    """
    ChromaDB-based vector store for schema metadata storage and retrieval
    """
    
    def __init__(self):
        """Initialize the vector store with configuration"""
        settings = AppSettings()
        self.persist_directory = settings.vector_store.persist_directory
        self.collection_name = settings.vector_store.collection_name
        self.embedding_model = settings.vector_store.embedding_model
        
        # Initialize the embedding model
        self.model = SentenceTransformer(self.embedding_model)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text string"""
        return self.model.encode(text).tolist()
    
    def add_table(
        self,
        table_name: str,
        description: str,
        columns: List[Dict[str, Any]],
        metadata: Dict[str, Any] = {}
    ) -> str:
        """
        Add a table schema to the vector store
        Returns the document ID
        """
        # Create a rich text representation of the table
        table_text = f"Table: {table_name}\nDescription: {description}\n\nColumns:\n"
        for col in columns:
            col_desc = col.get("description", "")
            table_text += f"- {col['column_name']} ({col['data_type']}): {col_desc}\n"
            
        # Create a unique ID for the document
        doc_id = f"table_{table_name}"
        
        # Prepare metadata
        doc_metadata = {
            "type": "table",
            "table_name": table_name,
            "description": description,
            **metadata
        }
        
        # Add to collection
        self.collection.add(
            documents=[table_text],
            metadatas=[doc_metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def add_column(
        self,
        table_name: str,
        column_name: str,
        data_type: str,
        description: str,
        metadata: Dict[str, Any] = {}
    ) -> str:
        """
        Add a column schema to the vector store
        Returns the document ID
        """
        # Create a rich text representation of the column
        column_text = (
            f"Column: {column_name}\n"
            f"Table: {table_name}\n"
            f"Type: {data_type}\n"
            f"Description: {description}"
        )
            
        # Create a unique ID for the document
        doc_id = f"column_{table_name}_{column_name}"
        
        # Prepare metadata
        doc_metadata = {
            "type": "column",
            "table_name": table_name,
            "column_name": column_name,
            "data_type": data_type,
            "description": description,
            **metadata
        }
        
        # Add to collection
        self.collection.add(
            documents=[column_text],
            metadatas=[doc_metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    def add_relationship(
        self,
        source_table: str,
        source_column: str,
        target_table: str,
        target_column: str,
        relationship_type: str,
        description: str,
        metadata: Dict[str, Any] = {}
    ) -> str:
        """
        Add a relationship to the vector store
        Returns the document ID
        """
        # Create a rich text representation of the relationship
        relationship_text = (
            f"Relationship: {source_table}.{source_column} -> {target_table}.{target_column}\n"
            f"Type: {relationship_type}\n"
            f"Description: {description}"
        )
            
        # Create a unique ID for the document
        doc_id = f"relationship_{source_table}_{source_column}_{target_table}_{target_column}"
        
        # Prepare metadata
        doc_metadata = {
            "type": "relationship",
            "source_table": source_table,
            "source_column": source_column,
            "target_table": target_table,
            "target_column": target_column,
            "relationship_type": relationship_type,
            "description": description,
            **metadata
        }
        
        # Add to collection
        self.collection.add(
            documents=[relationship_text],
            metadatas=[doc_metadata],
            ids=[doc_id]
        )
        
        return doc_id
        
    def search(
        self,
        query: str,
        filter_metadata: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search the vector store for relevant schema elements
        Returns a list of results with documents and metadata
        """
        # Generate embedding for the query
        query_embedding = self.get_embedding(query)
        
        # Search the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            where=filter_metadata,
            n_results=limit
        )
        
        # Format the results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })
            
        return formatted_results
    
    def get_by_table_name(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all documents related to a specific table"""
        results = self.collection.get(
            where={"table_name": table_name}
        )
        
        # Format the results
        formatted_results = []
        for i in range(len(results["ids"])):
            formatted_results.append({
                "id": results["ids"][i],
                "document": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
            
        return formatted_results
    
    def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get a specific document by ID"""
        result = self.collection.get(
            ids=[doc_id]
        )
        
        if len(result["ids"]) == 0:
            return None
            
        return {
            "id": result["ids"][0],
            "document": result["documents"][0],
            "metadata": result["metadatas"][0]
        }