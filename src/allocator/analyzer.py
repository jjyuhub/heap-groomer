"""
Core allocator analysis module for detecting slot sizes, alignment, and allocation patterns.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import numpy as np
from pydantic import BaseModel

@dataclass
class AllocationEvent:
    """Represents a single allocation event with metadata."""
    size: int
    address: int
    timestamp: float
    object_type: str
    bucket_index: Optional[int] = None

class SlotAnalysis(BaseModel):
    """Represents analysis of a specific slot size bucket."""
    size: int
    alignment: int
    count: int
    free_chunks: List[int]
    occupied_chunks: List[int]
    reuse_patterns: Dict[str, float]  # pattern -> frequency

class AllocatorAnalyzer:
    """Main class for analyzing allocator behavior."""
    
    def __init__(self):
        self.allocation_history: List[AllocationEvent] = []
        self.slot_analysis: Dict[int, SlotAnalysis] = {}
        self.bucket_boundaries: Dict[int, tuple] = {}  # bucket_index -> (min_size, max_size)
        
    def record_allocation(self, event: AllocationEvent) -> None:
        """Record a new allocation event and update analysis."""
        self.allocation_history.append(event)
        self._update_slot_analysis(event)
        
    def _update_slot_analysis(self, event: AllocationEvent) -> None:
        """Update slot analysis based on new allocation event."""
        if event.size not in self.slot_analysis:
            self.slot_analysis[event.size] = SlotAnalysis(
                size=event.size,
                alignment=self._detect_alignment(event.size),
                count=0,
                free_chunks=[],
                occupied_chunks=[],
                reuse_patterns={}
            )
        
        analysis = self.slot_analysis[event.size]
        analysis.count += 1
        analysis.occupied_chunks.append(event.address)
        
    def _detect_alignment(self, size: int) -> int:
        """Detect the alignment requirements for a given size."""
        # Common alignments: 8, 16, 32, 64
        for alignment in [8, 16, 32, 64]:
            if size % alignment == 0:
                return alignment
        return 8  # Default alignment
        
    def infer_bucket_boundaries(self) -> Dict[int, tuple]:
        """Infer bucket boundaries based on allocation patterns."""
        sizes = sorted([event.size for event in self.allocation_history])
        if not sizes:
            return {}
            
        # Use statistical analysis to find natural clusters
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=min(10, len(sizes)))
        clusters = kmeans.fit_predict(np.array(sizes).reshape(-1, 1))
        
        # Map clusters to bucket boundaries
        for i in range(len(kmeans.cluster_centers_)):
            cluster_sizes = [s for s, c in zip(sizes, clusters) if c == i]
            self.bucket_boundaries[i] = (min(cluster_sizes), max(cluster_sizes))
            
        return self.bucket_boundaries
        
    def detect_reuse_patterns(self) -> Dict[int, Dict[str, float]]:
        """Detect memory reuse patterns for each slot size."""
        patterns = {}
        
        for size, analysis in self.slot_analysis.items():
            # Analyze temporal patterns in allocation/deallocation
            addresses = [event.address for event in self.allocation_history 
                        if event.size == size]
            
            if len(addresses) < 2:
                continue
                
            # Look for address reuse
            reuse_count = len(addresses) - len(set(addresses))
            reuse_frequency = reuse_count / len(addresses)
            
            patterns[size] = {
                "reuse_frequency": reuse_frequency,
                "unique_addresses": len(set(addresses)),
                "total_allocations": len(addresses)
            }
            
        return patterns
        
    def get_slot_statistics(self) -> Dict[int, Dict]:
        """Get statistical analysis of each slot size."""
        stats = {}
        
        for size, analysis in self.slot_analysis.items():
            stats[size] = {
                "count": analysis.count,
                "alignment": analysis.alignment,
                "free_chunks": len(analysis.free_chunks),
                "occupied_chunks": len(analysis.occupied_chunks),
                "reuse_patterns": analysis.reuse_patterns
            }
            
        return stats 