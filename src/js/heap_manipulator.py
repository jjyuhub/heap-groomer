"""
JavaScript heap manipulation module for generating heap spray and defragmentation code.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import random
import string

@dataclass
class SprayConfig:
    """Configuration for heap spray operations."""
    target_size: int
    count: int
    object_type: str  # 'array', 'object', 'string'
    fill_pattern: Optional[str] = None
    alignment: int = 8

class HeapManipulator:
    """Generates JavaScript code for heap manipulation."""
    
    def __init__(self):
        self.spray_history: List[SprayConfig] = []
        
    def generate_spray_code(self, config: SprayConfig) -> str:
        """Generate JavaScript code for heap spraying."""
        self.spray_history.append(config)
        
        if config.object_type == 'array':
            return self._generate_array_spray(config)
        elif config.object_type == 'object':
            return self._generate_object_spray(config)
        elif config.object_type == 'string':
            return self._generate_string_spray(config)
        else:
            raise ValueError(f"Unsupported object type: {config.object_type}")
            
    def _generate_array_spray(self, config: SprayConfig) -> str:
        """Generate code for array-based heap spray."""
        fill_value = config.fill_pattern or '0x41'
        code = []
        
        # Create array with specific size
        code.append(f"const spray = new Array({config.count});")
        code.append("for (let i = 0; i < spray.length; i++) {")
        code.append(f"    spray[i] = new Array({config.target_size}).fill(Number({fill_value}));")
        code.append("}")
        
        return "\n".join(code)
        
    def _generate_object_spray(self, config: SprayConfig) -> str:
        """Generate code for object-based heap spray."""
        code = []
        code.append(f"const spray = new Array({config.count});")
        
        # Generate object with specific shape
        properties = self._generate_object_properties(config.target_size)
        code.append("for (let i = 0; i < spray.length; i++) {")
        code.append("    spray[i] = {")
        for prop in properties:
            code.append(f"        {prop}: Number({config.fill_pattern or '0x41'}),")
        code.append("    };")
        code.append("}")
        
        return "\n".join(code)
        
    def _generate_string_spray(self, config: SprayConfig) -> str:
        """Generate code for string-based heap spray."""
        fill_char = config.fill_pattern or 'A'
        code = []
        
        code.append(f"const spray = new Array({config.count});")
        code.append("for (let i = 0; i < spray.length; i++) {")
        code.append(f"    spray[i] = '{fill_char}'.repeat({config.target_size});")
        code.append("}")
        
        return "\n".join(code)
        
    def generate_defrag_code(self, target_size: int, count: int = 100) -> str:
        """Generate code for heap defragmentation."""
        code = []
        
        # Create dummy objects to force GC
        code.append("const dummy = [];")
        code.append(f"for (let i = 0; i < {count}; i++) {{")
        code.append(f"    dummy.push(new Array({target_size}).fill(Number(0x42)));")
        code.append("}")
        
        # Force garbage collection
        code.append("dummy.length = 0;")
        code.append("if (global.gc) global.gc();")
        
        return "\n".join(code)
        
    def _generate_object_properties(self, target_size: int) -> List[str]:
        """Generate object properties to achieve target size."""
        properties = []
        current_size = 0
        
        while current_size < target_size:
            prop_name = ''.join(random.choices(string.ascii_letters, k=8))
            properties.append(prop_name)
            current_size += 8  # Approximate property size
            
        return properties
        
    def generate_freelist_priming(self, slot_size: int, count: int) -> str:
        """Generate code to prime freelist for specific slot size."""
        code = []
        
        # Create objects of specific size
        code.append(f"const prime = new Array({count});")
        code.append("for (let i = 0; i < prime.length; i++) {")
        code.append(f"    prime[i] = new Array({slot_size}).fill(Number(0x43));")
        code.append("}")
        
        # Free them to prime freelist
        code.append("prime.length = 0;")
        code.append("if (global.gc) global.gc();")
        
        return "\n".join(code) 