from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json
from pydantic import BaseModel

class AllocationEvent(BaseModel):
    """Represents a single allocation or deallocation event."""
    timestamp: float
    event_type: str  # "alloc" or "free"
    size: int
    address: Optional[int] = None
    bucket_index: Optional[int] = None
    object_type: Optional[str] = None

class BucketInfo(BaseModel):
    """Information about a specific size bucket in PartitionAlloc."""
    size: int
    alignment: int
    slot_size: int
    num_slots: int
    free_slots: List[int]
    used_slots: List[int]

class PartitionAllocAnalyzer:
    """Analyzes PartitionAlloc behavior and structure."""
    
    def __init__(self):
        self.events: List[AllocationEvent] = []
        self.buckets: Dict[int, BucketInfo] = {}
        self.slot_sizes: Dict[int, int] = {}
        self.alignment_rules: Dict[int, int] = {}
        
    def add_event(self, event: AllocationEvent) -> None:
        """Add an allocation or deallocation event to the analysis."""
        self.events.append(event)
        self._update_bucket_info(event)
    
    def _update_bucket_info(self, event: AllocationEvent) -> None:
        """Update bucket information based on an event."""
        if event.bucket_index is None:
            return
            
        if event.bucket_index not in self.buckets:
            self.buckets[event.bucket_index] = BucketInfo(
                size=event.size,
                alignment=self._infer_alignment(event.size),
                slot_size=self._infer_slot_size(event.size),
                num_slots=0,
                free_slots=[],
                used_slots=[]
            )
        
        bucket = self.buckets[event.bucket_index]
        if event.event_type == "alloc":
            if event.address not in bucket.used_slots:
                bucket.used_slots.append(event.address)
                if event.address in bucket.free_slots:
                    bucket.free_slots.remove(event.address)
        else:  # free
            if event.address in bucket.used_slots:
                bucket.used_slots.remove(event.address)
                bucket.free_slots.append(event.address)
    
    def _infer_alignment(self, size: int) -> int:
        """Infer alignment requirements for a given size."""
        # Common alignment rules in PartitionAlloc
        if size <= 8:
            return 8
        elif size <= 16:
            return 16
        elif size <= 32:
            return 32
        else:
            return 64
    
    def _infer_slot_size(self, size: int) -> int:
        """Infer the actual slot size for a given allocation size."""
        alignment = self._infer_alignment(size)
        return (size + alignment - 1) & ~(alignment - 1)
    
    def analyze_reuse_patterns(self) -> Dict[int, List[Tuple[int, int]]]:
        """Analyze memory reuse patterns across allocations."""
        reuse_patterns: Dict[int, List[Tuple[int, int]]] = {}
        
        for i, event in enumerate(self.events):
            if event.event_type == "free":
                # Look for subsequent allocations that reuse this address
                for j in range(i + 1, len(self.events)):
                    if self.events[j].event_type == "alloc":
                        if self.events[j].address == event.address:
                            if event.size not in reuse_patterns:
                                reuse_patterns[event.size] = []
                            reuse_patterns[event.size].append((i, j))
                            break
        
        return reuse_patterns
    
    def get_bucket_boundaries(self) -> List[Tuple[int, int]]:
        """Get the size boundaries for each bucket."""
        boundaries = []
        sorted_buckets = sorted(self.buckets.items())
        
        for i in range(len(sorted_buckets) - 1):
            current_bucket = sorted_buckets[i][1]
            next_bucket = sorted_buckets[i + 1][1]
            boundaries.append((current_bucket.size, next_bucket.size))
        
        return boundaries
    
    def export_analysis(self, filename: str) -> None:
        """Export the analysis results to a JSON file."""
        analysis_data = {
            "buckets": {str(k): v.dict() for k, v in self.buckets.items()},
            "events": [e.dict() for e in self.events],
            "reuse_patterns": self.analyze_reuse_patterns(),
            "boundaries": self.get_bucket_boundaries()
        }
        
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=2)
    
    def load_analysis(self, filename: str) -> None:
        """Load analysis results from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
            
        self.buckets = {
            int(k): BucketInfo(**v) for k, v in data["buckets"].items()
        }
        self.events = [AllocationEvent(**e) for e in data["events"]] 