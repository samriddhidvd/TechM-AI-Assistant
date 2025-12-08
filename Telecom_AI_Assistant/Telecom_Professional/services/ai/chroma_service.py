"""
ChromaDB Service
Handles vector storage and retrieval for document search
"""

import chromadb
import os
from typing import List, Dict, Any
from config.settings import Config

class ChromaService:
    """Service for managing ChromaDB operations"""
    
    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection("drive_docs")
    
    def upsert_document(self, name: str, url: str, text: str) -> bool:
        """
        Store document in ChromaDB
        
        Args:
            name: Document name
            url: Document URL (used as unique ID)
            text: Extracted text content
            
        Returns:
            bool: Success status
        """
        try:
            # Use URL as the unique document ID
            self.collection.upsert(
                documents=[text],
                metadatas=[{"name": name, "url": url}],
                ids=[url]
            )
            return True
        except Exception as e:
            print(f"Error upserting document to ChromaDB: {e}")
            return False
    
    def get_relevant_context(self, question: str, n_results: int = 5) -> str:
        """
        Query ChromaDB for relevant context based on user question
        
        Args:
            question: User's question
            n_results: Number of relevant documents to retrieve
            
        Returns:
            str: Relevant context from documents
        """
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results
            )
            
            if results['documents'] and results['documents'][0]:
                context = "\n\n".join(results['documents'][0])
                return context
            else:
                return "No relevant documents found."
                
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return "Error retrieving relevant context."
    
    def delete_document(self, url: str) -> bool:
        """
        Delete document from ChromaDB
        
        Args:
            url: Document URL (unique ID)
            
        Returns:
            bool: Success status
        """
        try:
            self.collection.delete(ids=[url])
            return True
        except Exception as e:
            print(f"Error deleting document from ChromaDB: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get ChromaDB collection statistics
        
        Returns:
            Dict containing collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": "drive_docs"
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"error": str(e)} 