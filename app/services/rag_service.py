# services/rag_service.py
from llama_index.core import VectorStoreIndex

class RAGService:
    def __init__(self, documents):
        """Initialize RAGService with documents, build an index, and set up a query engine."""
        self.documents = documents
        self.index = VectorStoreIndex.from_documents(documents)
        self.query_engine = self.index.as_query_engine()  # Initialize query engine

    def search(self, query: str):
        """Searches the query engine for the query and returns the most relevant response."""
        response = self.query_engine.query(query)
        return response
