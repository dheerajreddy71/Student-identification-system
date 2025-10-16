"""
FAISS vector database for efficient similarity search
"""
import faiss
import numpy as np
import json
import os
from typing import List, Tuple, Optional, Dict
import pickle
from pathlib import Path


class FAISSVectorDB:
    """FAISS-based vector database for face embeddings"""
    
    def __init__(self, embedding_dim: int = 128, 
                 index_path: Optional[str] = None,
                 metadata_path: Optional[str] = None,
                 metric: str = 'cosine'):
        """
        Initialize FAISS index
        
        Args:
            embedding_dim: Dimension of embeddings (128 for SimpleFaceRecognizer)
            index_path: Path to save/load FAISS index
            metadata_path: Path to save/load metadata
            metric: 'cosine' or 'l2'
        """
        self.embedding_dim = embedding_dim
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.metric = metric
        
        # Initialize index
        if index_path and os.path.exists(index_path):
            # Load existing index
            self.index = faiss.read_index(index_path)
            print(f"✓ Loaded FAISS index from {index_path} ({self.index.ntotal} vectors)")
        else:
            # Create new index
            if metric == 'cosine':
                # Inner product for cosine similarity (embeddings must be normalized)
                self.index = faiss.IndexFlatIP(embedding_dim)
            else:  # l2
                self.index = faiss.IndexFlatL2(embedding_dim)
            print(f"✓ Created new FAISS index ({metric} metric)")
        
        # Load or initialize metadata
        self.metadata = {}
        if metadata_path and os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            print(f"✓ Loaded metadata ({len(self.metadata)} entries)")
    
    def add_embedding(self, embedding: np.ndarray, student_id: str, 
                     metadata: Optional[Dict] = None) -> int:
        """
        Add embedding to index
        
        Args:
            embedding: Embedding vector (128-D)
            student_id: Unique student identifier
            metadata: Additional metadata to store
            
        Returns:
            Index position
        """
        # Ensure embedding is 2D
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        # Normalize for cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(embedding)
        
        # Get current index position
        idx = self.index.ntotal
        
        # Add to FAISS index
        self.index.add(embedding.astype(np.float32))
        
        # Store metadata
        self.metadata[str(idx)] = {
            'student_id': student_id,
            'metadata': metadata or {}
        }
        
        return idx
    
    def add_embeddings_batch(self, embeddings: np.ndarray, 
                           student_ids: List[str],
                           metadatas: Optional[List[Dict]] = None) -> List[int]:
        """
        Add multiple embeddings at once
        
        Args:
            embeddings: Array of embeddings (N, 512)
            student_ids: List of student IDs
            metadatas: List of metadata dicts
            
        Returns:
            List of index positions
        """
        if len(embeddings) != len(student_ids):
            raise ValueError("Number of embeddings must match number of student IDs")
        
        # Normalize for cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(embeddings)
        
        # Get starting index
        start_idx = self.index.ntotal
        
        # Add to FAISS index
        self.index.add(embeddings.astype(np.float32))
        
        # Store metadata
        indices = []
        for i, student_id in enumerate(student_ids):
            idx = start_idx + i
            indices.append(idx)
            self.metadata[str(idx)] = {
                'student_id': student_id,
                'metadata': metadatas[i] if metadatas else {}
            }
        
        return indices
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for similar embeddings
        
        Args:
            query_embedding: Query embedding vector (512-D)
            k: Number of nearest neighbors to return
            
        Returns:
            (distances/similarities, indices)
        """
        # Ensure embedding is 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize for cosine similarity
        if self.metric == 'cosine':
            faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        return distances[0], indices[0]
    
    def search_with_threshold(self, query_embedding: np.ndarray, 
                             threshold: float = 0.45,
                             k: int = 5) -> List[Dict]:
        """
        Search with similarity threshold
        
        Args:
            query_embedding: Query embedding
            threshold: Minimum similarity score
            k: Max number of results
            
        Returns:
            List of matches with metadata
        """
        distances, indices = self.search(query_embedding, k)
        
        matches = []
        print(f"\n🔍 FAISS Search Results (threshold={threshold:.3f}):")
        print("-" * 70)
        
        for dist, idx in zip(distances, indices):
            # For cosine similarity (inner product), higher is better
            # For L2 distance, lower is better
            if self.metric == 'cosine':
                similarity = float(dist)
            else:  # l2
                # Convert L2 distance to similarity score
                similarity = 1.0 / (1.0 + float(dist))
            
            # Get student info for logging
            student_info = self.metadata.get(str(idx), {})
            student_id = student_info.get('student_id', 'Unknown')
            student_name = student_info.get('metadata', {}).get('name', 'Unknown')
            
            passed = "✓ MATCH" if similarity >= threshold else "✗ Below threshold"
            print(f"  [{passed}] Similarity: {similarity:.4f} | Student: {student_id} ({student_name})")
            
            # Check threshold
            if similarity >= threshold and str(idx) in self.metadata:
                match_data = self.metadata[str(idx)].copy()
                match_data['similarity'] = similarity
                match_data['faiss_index'] = int(idx)
                matches.append(match_data)
        
        print("-" * 70)
        print(f"✓ Found {len(matches)} matches above threshold\n")
        
        return matches
    
    def get_best_match(self, query_embedding: np.ndarray, 
                      threshold: float = 0.45) -> Optional[Dict]:
        """
        Get best matching student
        
        Args:
            query_embedding: Query embedding
            threshold: Minimum similarity threshold
            
        Returns:
            Best match dict or None
        """
        matches = self.search_with_threshold(query_embedding, threshold, k=1)
        return matches[0] if matches else None
    
    def remove_embedding(self, idx: int):
        """
        Remove embedding (by rebuilding index without it)
        Note: FAISS IndexFlat doesn't support remove, so we rebuild
        
        Args:
            idx: Index to remove
        """
        # Get all embeddings except the one to remove
        all_embeddings = []
        new_metadata = {}
        new_idx = 0
        
        for i in range(self.index.ntotal):
            if i != idx:
                # Get embedding
                emb = self.index.reconstruct(i)
                all_embeddings.append(emb)
                
                # Update metadata
                if str(i) in self.metadata:
                    new_metadata[str(new_idx)] = self.metadata[str(i)]
                    new_idx += 1
        
        # Rebuild index
        if all_embeddings:
            embeddings_array = np.vstack(all_embeddings)
            
            # Create new index
            if self.metric == 'cosine':
                self.index = faiss.IndexFlatIP(self.embedding_dim)
            else:
                self.index = faiss.IndexFlatL2(self.embedding_dim)
            
            # Add embeddings
            self.index.add(embeddings_array)
            self.metadata = new_metadata
    
    def update_embedding(self, idx: int, new_embedding: np.ndarray):
        """
        Update embedding at index
        
        Args:
            idx: Index to update
            new_embedding: New embedding vector
        """
        # Store metadata
        old_metadata = self.metadata.get(str(idx), {})
        
        # Remove old and add new
        self.remove_embedding(idx)
        
        # Add at same position (will be at end now)
        if old_metadata:
            self.add_embedding(new_embedding, 
                             old_metadata['student_id'],
                             old_metadata.get('metadata'))
    
    def save(self, index_path: Optional[str] = None, 
            metadata_path: Optional[str] = None):
        """
        Save index and metadata to disk
        
        Args:
            index_path: Path to save FAISS index
            metadata_path: Path to save metadata
        """
        index_path = index_path or self.index_path
        metadata_path = metadata_path or self.metadata_path
        
        if not index_path or not metadata_path:
            raise ValueError("Must provide paths to save index and metadata")
        
        # Create directories if needed
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"✓ Saved FAISS index to {index_path}")
        print(f"✓ Saved metadata to {metadata_path}")
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        return {
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.embedding_dim,
            'metric': self.metric,
            'metadata_entries': len(self.metadata)
        }
    
    def __len__(self):
        """Return number of vectors in index"""
        return self.index.ntotal
