"""
Grooming strategy generator module for creating allocation patterns and sequences.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import random

class TriggerType(Enum):
    """Types of trigger conditions for grooming strategies."""
    IMMEDIATE = "immediate"
    GC_TRIGGER = "gc_trigger"
    TIMEOUT = "timeout"
    CUSTOM = "custom"

@dataclass
class AllocationStep:
    """Represents a single step in an allocation sequence."""
    size: int
    count: int
    object_type: str
    fill_pattern: Optional[str] = None
    delay_ms: int = 0

@dataclass
class DeallocationStep:
    """Represents a single step in a deallocation sequence."""
    object_type: str
    count: int
    delay_ms: int = 0

@dataclass
class TriggerCondition:
    """Represents a trigger condition for the grooming strategy."""
    type: TriggerType
    value: Optional[int] = None  # For timeout in ms
    custom_code: Optional[str] = None

class GroomingStrategy:
    """Represents a complete grooming strategy."""
    def __init__(self):
        self.allocation_steps: List[AllocationStep] = []
        self.deallocation_steps: List[DeallocationStep] = []
        self.trigger: Optional[TriggerCondition] = None
        self.description: str = ""
        
class StrategyGenerator:
    """Generates grooming strategies for specific target objects."""
    
    def __init__(self):
        self.known_patterns: Dict[str, List[GroomingStrategy]] = {}
        
    def generate_strategy(self, target_size: int, 
                         target_type: str,
                         overwrite_size: Optional[int] = None) -> GroomingStrategy:
        """Generate a grooming strategy for a target object."""
        strategy = GroomingStrategy()
        
        # Generate allocation steps
        strategy.allocation_steps = self._generate_allocation_steps(
            target_size, target_type, overwrite_size)
            
        # Generate deallocation steps
        strategy.deallocation_steps = self._generate_deallocation_steps(
            target_size, target_type)
            
        # Generate trigger condition
        strategy.trigger = self._generate_trigger_condition(target_type)
        
        # Generate description
        strategy.description = self._generate_description(strategy)
        
        return strategy
        
    def _generate_allocation_steps(self, target_size: int,
                                 target_type: str,
                                 overwrite_size: Optional[int]) -> List[AllocationStep]:
        """Generate allocation steps for the strategy."""
        steps = []
        
        # Initial spray to fill holes
        steps.append(AllocationStep(
            size=target_size,
            count=random.randint(50, 100),
            object_type="array",
            fill_pattern="0x41"
        ))
        
        # If we need to overwrite more than target_size
        if overwrite_size and overwrite_size > target_size:
            # Add filler objects
            remaining_size = overwrite_size - target_size
            steps.append(AllocationStep(
                size=remaining_size,
                count=random.randint(20, 40),
                object_type="array",
                fill_pattern="0x42"
            ))
            
        # Target object allocation
        steps.append(AllocationStep(
            size=target_size,
            count=1,
            object_type=target_type,
            fill_pattern="0x43"
        ))
        
        return steps
        
    def _generate_deallocation_steps(self, target_size: int,
                                   target_type: str) -> List[DeallocationStep]:
        """Generate deallocation steps for the strategy."""
        steps = []
        
        # Deallocate filler objects
        steps.append(DeallocationStep(
            object_type="array",
            count=random.randint(20, 40),
            delay_ms=random.randint(100, 500)
        ))
        
        # Deallocate target object
        steps.append(DeallocationStep(
            object_type=target_type,
            count=1,
            delay_ms=random.randint(100, 500)
        ))
        
        return steps
        
    def _generate_trigger_condition(self, target_type: str) -> TriggerCondition:
        """Generate trigger condition for the strategy."""
        # For objects that need GC to be triggered
        if target_type in ["ArrayBuffer", "TypedArray"]:
            return TriggerCondition(
                type=TriggerType.GC_TRIGGER,
                value=random.randint(1000, 3000)
            )
            
        # For objects that need immediate triggering
        if target_type in ["JSFunction", "JSObject"]:
            return TriggerCondition(
                type=TriggerType.IMMEDIATE
            )
            
        # Default to timeout-based triggering
        return TriggerCondition(
            type=TriggerType.TIMEOUT,
            value=random.randint(500, 2000)
        )
        
    def _generate_description(self, strategy: GroomingStrategy) -> str:
        """Generate human-readable description of the strategy."""
        desc = []
        
        # Describe allocation steps
        desc.append("Allocation Steps:")
        for step in strategy.allocation_steps:
            desc.append(f"- Allocate {step.count} {step.object_type}(s) of size {step.size}")
            
        # Describe deallocation steps
        desc.append("\nDeallocation Steps:")
        for step in strategy.deallocation_steps:
            desc.append(f"- Deallocate {step.count} {step.object_type}(s)")
            
        # Describe trigger
        desc.append("\nTrigger:")
        if strategy.trigger.type == TriggerType.IMMEDIATE:
            desc.append("- Immediate trigger")
        elif strategy.trigger.type == TriggerType.GC_TRIGGER:
            desc.append(f"- GC trigger after {strategy.trigger.value}ms")
        elif strategy.trigger.type == TriggerType.TIMEOUT:
            desc.append(f"- Timeout trigger after {strategy.trigger.value}ms")
            
        return "\n".join(desc)
        
    def register_pattern(self, name: str, strategy: GroomingStrategy) -> None:
        """Register a known grooming pattern."""
        if name not in self.known_patterns:
            self.known_patterns[name] = []
        self.known_patterns[name].append(strategy)
        
    def get_patterns_for_size(self, size: int) -> List[GroomingStrategy]:
        """Get known grooming patterns for a specific size."""
        patterns = []
        for strategies in self.known_patterns.values():
            for strategy in strategies:
                if any(step.size == size for step in strategy.allocation_steps):
                    patterns.append(strategy)
        return patterns 