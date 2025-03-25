"""
Target bug mode module for analyzing potential target objects and generating grooming sequences.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set
from enum import Enum
import random

class BugType(Enum):
    """Types of heap-related bugs."""
    OVERFLOW = "overflow"
    UAF = "use_after_free"
    DOUBLE_FREE = "double_free"
    HEAP_SPRAY = "heap_spray"

@dataclass
class BugConfig:
    """Configuration for a specific bug scenario."""
    type: BugType
    size: int
    offset: int
    overwrite_size: int
    target_object: str
    constraints: Dict[str, any]

@dataclass
class TargetObject:
    """Represents a potential target object for exploitation."""
    name: str
    size: int
    alignment: int
    dangerous_fields: List[str]
    vtable_offset: Optional[int]
    metadata_size: int
    exploitability_score: float

class BugAnalyzer:
    """Analyzes potential target objects and generates grooming sequences."""
    
    def __init__(self):
        self.known_objects: Dict[str, TargetObject] = {}
        self.bug_history: List[BugConfig] = []
        
    def register_object(self, obj: TargetObject) -> None:
        """Register a new target object type."""
        self.known_objects[obj.name] = obj
        
    def analyze_bug(self, config: BugConfig) -> Dict:
        """Analyze a bug scenario and generate recommendations."""
        self.bug_history.append(config)
        
        # Find potential target objects
        candidates = self._find_target_candidates(config)
        
        # Generate grooming sequences
        sequences = self._generate_grooming_sequences(config, candidates)
        
        # Analyze exploitability
        exploitability = self._analyze_exploitability(config, candidates)
        
        return {
            "candidates": candidates,
            "sequences": sequences,
            "exploitability": exploitability
        }
        
    def _find_target_candidates(self, config: BugConfig) -> List[TargetObject]:
        """Find potential target objects for the bug scenario."""
        candidates = []
        
        for obj in self.known_objects.values():
            # Check size constraints
            if obj.size > config.overwrite_size:
                continue
                
            # Check alignment
            if (config.offset + obj.size) % obj.alignment != 0:
                continue
                
            # Check if object has dangerous fields
            if not obj.dangerous_fields:
                continue
                
            # Calculate exploitability score
            score = self._calculate_exploitability_score(obj, config)
            if score > 0.5:  # Only include promising candidates
                candidates.append(obj)
                
        return sorted(candidates, key=lambda x: x.exploitability_score, reverse=True)
        
    def _calculate_exploitability_score(self, obj: TargetObject, 
                                     config: BugConfig) -> float:
        """Calculate exploitability score for a target object."""
        score = 0.0
        
        # Size match (0.3)
        if obj.size == config.overwrite_size:
            score += 0.3
        elif obj.size < config.overwrite_size:
            score += 0.2
            
        # Dangerous fields (0.3)
        score += min(0.3, len(obj.dangerous_fields) * 0.1)
        
        # Vtable presence (0.2)
        if obj.vtable_offset is not None:
            score += 0.2
            
        # Metadata size (0.2)
        if obj.metadata_size <= config.offset:
            score += 0.2
            
        return score
        
    def _generate_grooming_sequences(self, config: BugConfig,
                                   candidates: List[TargetObject]) -> List[Dict]:
        """Generate grooming sequences for target objects."""
        sequences = []
        
        for candidate in candidates:
            sequence = {
                "target": candidate.name,
                "steps": []
            }
            
            # Add allocation steps
            if config.type == BugType.UAF:
                sequence["steps"].extend(self._generate_uaf_sequence(
                    candidate, config))
            elif config.type == BugType.OVERFLOW:
                sequence["steps"].extend(self._generate_overflow_sequence(
                    candidate, config))
            elif config.type == BugType.DOUBLE_FREE:
                sequence["steps"].extend(self._generate_double_free_sequence(
                    candidate, config))
                    
            sequences.append(sequence)
            
        return sequences
        
    def _generate_uaf_sequence(self, target: TargetObject,
                             config: BugConfig) -> List[Dict]:
        """Generate grooming sequence for use-after-free."""
        steps = []
        
        # Allocate target object
        steps.append({
            "type": "allocate",
            "object": target.name,
            "count": 1,
            "size": target.size
        })
        
        # Allocate filler objects
        steps.append({
            "type": "allocate",
            "object": "array",
            "count": random.randint(10, 20),
            "size": target.size
        })
        
        # Free target object
        steps.append({
            "type": "free",
            "object": target.name,
            "count": 1
        })
        
        # Allocate attacker-controlled object
        steps.append({
            "type": "allocate",
            "object": "array",
            "count": 1,
            "size": target.size
        })
        
        return steps
        
    def _generate_overflow_sequence(self, target: TargetObject,
                                  config: BugConfig) -> List[Dict]:
        """Generate grooming sequence for overflow."""
        steps = []
        
        # Allocate target object
        steps.append({
            "type": "allocate",
            "object": target.name,
            "count": 1,
            "size": target.size
        })
        
        # Allocate victim object
        steps.append({
            "type": "allocate",
            "object": "array",
            "count": 1,
            "size": config.overwrite_size
        })
        
        return steps
        
    def _generate_double_free_sequence(self, target: TargetObject,
                                     config: BugConfig) -> List[Dict]:
        """Generate grooming sequence for double free."""
        steps = []
        
        # Allocate target object
        steps.append({
            "type": "allocate",
            "object": target.name,
            "count": 1,
            "size": target.size
        })
        
        # Free target object
        steps.append({
            "type": "free",
            "object": target.name,
            "count": 1
        })
        
        # Allocate filler
        steps.append({
            "type": "allocate",
            "object": "array",
            "count": 1,
            "size": target.size
        })
        
        # Free target object again
        steps.append({
            "type": "free",
            "object": target.name,
            "count": 1
        })
        
        return steps
        
    def _analyze_exploitability(self, config: BugConfig,
                              candidates: List[TargetObject]) -> Dict:
        """Analyze exploitability of the bug scenario."""
        analysis = {
            "overall_score": 0.0,
            "factors": [],
            "recommendations": []
        }
        
        if not candidates:
            analysis["overall_score"] = 0.0
            analysis["factors"].append("No suitable target objects found")
            return analysis
            
        # Calculate overall score
        best_candidate = candidates[0]
        analysis["overall_score"] = best_candidate.exploitability_score
        
        # Analyze factors
        if best_candidate.vtable_offset is not None:
            analysis["factors"].append("Vtable manipulation possible")
            
        if len(best_candidate.dangerous_fields) > 0:
            analysis["factors"].append(
                f"Found {len(best_candidate.dangerous_fields)} dangerous fields")
            
        # Generate recommendations
        if config.type == BugType.UAF:
            analysis["recommendations"].append(
                "Consider using heap spraying to increase reliability")
        elif config.type == BugType.OVERFLOW:
            analysis["recommendations"].append(
                "Ensure proper alignment of target objects")
            
        return analysis 