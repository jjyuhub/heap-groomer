"""
Freelist analysis module for analyzing potential target objects and their relationships.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum
import networkx as nx

class ObjectClass(Enum):
    """Classification of potential target objects."""
    SPRAY_CANDIDATE = "spray_candidate"
    HARMLESS = "harmless"
    DANGEROUS = "dangerous"
    UNKNOWN = "unknown"

@dataclass
class ObjectMetadata:
    """Metadata about a potential target object."""
    name: str
    size: int
    alignment: int
    class_type: ObjectClass
    dangerous_fields: List[str]
    vtable_offset: Optional[int] = None
    metadata_size: int = 0

class FreelistAnalyzer:
    """Analyzes freelist behavior and potential target objects."""
    
    def __init__(self):
        self.object_metadata: Dict[str, ObjectMetadata] = {}
        self.overwrite_graph = nx.DiGraph()
        self.known_vtables: Set[int] = set()
        
    def register_object_type(self, metadata: ObjectMetadata) -> None:
        """Register a new object type with its metadata."""
        self.object_metadata[metadata.name] = metadata
        
    def analyze_overwrite_chain(self, target_size: int, 
                              overwrite_size: int) -> List[List[str]]:
        """Analyze potential overwrite chains for a given target size."""
        chains = []
        
        # Find all objects that could fit in the target size
        candidates = [obj for obj in self.object_metadata.values() 
                     if obj.size <= target_size]
        
        for candidate in candidates:
            # Build potential overwrite chains
            chain = self._build_overwrite_chain(candidate, overwrite_size)
            if chain:
                chains.append(chain)
                
        return chains
        
    def _build_overwrite_chain(self, target: ObjectMetadata, 
                             overwrite_size: int) -> Optional[List[str]]:
        """Build a potential overwrite chain for a target object."""
        if target.class_type == ObjectClass.HARMLESS:
            return None
            
        chain = [target.name]
        current_size = target.size
        
        while current_size < overwrite_size:
            # Find next object that could be overwritten
            next_target = self._find_next_target(current_size, overwrite_size)
            if not next_target:
                break
                
            chain.append(next_target.name)
            current_size += next_target.size
            
        return chain if current_size >= overwrite_size else None
        
    def _find_next_target(self, current_size: int, 
                         target_size: int) -> Optional[ObjectMetadata]:
        """Find the next potential target object in the chain."""
        for obj in self.object_metadata.values():
            if (obj.class_type != ObjectClass.HARMLESS and 
                current_size + obj.size <= target_size):
                return obj
        return None
        
    def classify_object(self, obj_type: str, size: int, 
                       has_vtable: bool = False) -> ObjectClass:
        """Classify an object based on its properties."""
        if has_vtable:
            return ObjectClass.DANGEROUS
            
        # Common dangerous object sizes
        dangerous_sizes = {0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80}
        if size in dangerous_sizes:
            return ObjectClass.DANGEROUS
            
        # Objects that are typically safe to overwrite
        harmless_sizes = {0x10, 0x18, 0x28, 0x38}
        if size in harmless_sizes:
            return ObjectClass.HARMLESS
            
        return ObjectClass.SPRAY_CANDIDATE
        
    def analyze_fake_object_layout(self, target: ObjectMetadata) -> Dict:
        """Generate a fake object layout for a target object."""
        layout = {
            "size": target.size,
            "vtable_offset": target.vtable_offset or 0,
            "fields": []
        }
        
        # Add dangerous fields
        for field in target.dangerous_fields:
            layout["fields"].append({
                "name": field,
                "offset": 0,  # Would need to be calculated based on actual layout
                "type": "pointer"
            })
            
        return layout
        
    def register_vtable(self, address: int) -> None:
        """Register a known vtable address."""
        self.known_vtables.add(address)
        
    def is_known_vtable(self, address: int) -> bool:
        """Check if an address is a known vtable."""
        return address in self.known_vtables
        
    def get_spray_candidates(self, target_size: int) -> List[ObjectMetadata]:
        """Get list of objects suitable for spraying at target size."""
        return [obj for obj in self.object_metadata.values() 
                if obj.size == target_size and 
                obj.class_type == ObjectClass.SPRAY_CANDIDATE] 