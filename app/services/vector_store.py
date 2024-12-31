# services/vector_store.py
from llama_index.core import VectorStoreIndex

class VectorStoreService:
    def __init__(self, documents=None):
        """Initialize vector store service with optional documents."""
        self.documents = documents
        self.index = None
        if documents:
            self.build_index(documents)

    def build_index(self, documents):
        """Build a vector index from documents."""
        self.index = VectorStoreIndex.from_documents(documents)

    def as_query_engine(self):
        """Return the query engine if index exists."""
        if not self.index:
            raise ValueError("Index not built. Use 'build_index' to create an index first.")
        return self.index.as_query_engine()
