import faiss
import numpy as np
import json
import os
from typing import List, Dict, Optional, Tuple
from config import Config
import logging

logger = logging.getLogger(__name__)


class FAISSService:
    """Service for FAISS vector similarity search"""

    def __init__(self):
        self.dimension = Config.EMBEDDING_DIMENSION
        self.index_path = Config.FAISS_INDEX_PATH
        self.metadata_path = Config.FAISS_METADATA_PATH
        self.index = None
        self.metadata = []
        self.initialize_index()

    def initialize_index(self):
        """Initialize or load FAISS index"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # Load existing index
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                # Create new index
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = []
                logger.info("Created new FAISS index")
        except Exception as e:
            logger.error(f"Error initializing FAISS index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def add_vector(
        self,
        vector: List[float],
        user_id: int,
        message_id: int,
        text: str,
        intent: Optional[str] = None,
        domain: Optional[str] = None
    ) -> bool:
        """Add a vector to the index with metadata"""
        try:
            # Convert to numpy array and add to index
            vector_array = np.array([vector], dtype=np.float32)
            self.index.add(vector_array)

            # Store metadata
            metadata_entry = {
                "user_id": user_id,
                "message_id": message_id,
                "text": text,
                "intent": intent,
                "domain": domain,
                "index_position": len(self.metadata)
            }
            self.metadata.append(metadata_entry)

            # Save periodically (every 10 additions)
            if len(self.metadata) % 10 == 0:
                self.save_index()

            return True
        except Exception as e:
            logger.error(f"Error adding vector: {e}")
            return False

    def search_similar(
        self,
        query_vector: List[float],
        k: int = 5,
        user_id: Optional[int] = None
    ) -> List[Dict]:
        """Search for similar vectors"""
        try:
            if self.index.ntotal == 0:
                return []

            # Convert query to numpy array
            query_array = np.array([query_vector], dtype=np.float32)

            # Search
            distances, indices = self.index.search(query_array, min(k * 3, self.index.ntotal))

            # Filter results
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx == -1:  # No more results
                    break

                meta = self.metadata[idx]

                # Filter by user if specified
                if user_id and meta['user_id'] != user_id:
                    continue

                results.append({
                    "text": meta["text"],
                    "intent": meta["intent"],
                    "domain": meta["domain"],
                    "similarity_score": float(distance),
                    "message_id": meta["message_id"]
                })

                if len(results) >= k:
                    break

            return results
        except Exception as e:
            logger.error(f"Error searching similar vectors: {e}")
            return []

    def get_user_query_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's query history from FAISS metadata"""
        try:
            user_queries = [
                meta for meta in self.metadata
                if meta['user_id'] == user_id
            ]
            return user_queries[-limit:]
        except Exception as e:
            logger.error(f"Error getting user query history: {e}")
            return []

    def save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.info("FAISS index saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            return False

    def get_index_stats(self) -> Dict:
        """Get statistics about the index"""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "metadata_count": len(self.metadata)
        }

    def clear_user_vectors(self, user_id: int):
        """Clear all vectors for a specific user (requires rebuilding index)"""
        try:
            # Filter metadata
            filtered_metadata = [
                meta for meta in self.metadata
                if meta['user_id'] != user_id
            ]

            if len(filtered_metadata) == len(self.metadata):
                logger.info(f"No vectors found for user {user_id}")
                return True

            # Rebuild index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

            logger.info(f"Cleared vectors for user {user_id}")
            self.save_index()
            return True
        except Exception as e:
            logger.error(f"Error clearing user vectors: {e}")
            return False
