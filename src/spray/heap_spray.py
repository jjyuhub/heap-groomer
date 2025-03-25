from typing import List, Dict, Optional
from dataclasses import dataclass
import random
import string

@dataclass
class SprayConfig:
    """Configuration for heap spraying operations."""
    target_size: int
    num_objects: int
    object_type: str  # "array", "object", "string"
    fill_pattern: Optional[str] = None
    alignment: int = 8

class HeapSprayGenerator:
    """Generates JavaScript code for heap manipulation."""
    
    def __init__(self):
        self.spray_history: List[SprayConfig] = []
    
    def generate_array_spray(self, config: SprayConfig) -> str:
        """Generate JavaScript code to spray arrays of specific size."""
        if config.fill_pattern is None:
            fill_pattern = "0x41"  # Default fill pattern
        
        code = []
        code.append("// Array spray configuration")
        code.append(f"const targetSize = {config.target_size};")
        code.append(f"const numObjects = {config.num_objects};")
        code.append("const sprayArrays = [];")
        code.append("\n// Spray arrays")
        code.append("for (let i = 0; i < numObjects; i++) {")
        code.append("    const arr = new Array(targetSize);")
        code.append("    for (let j = 0; j < targetSize; j++) {")
        code.append(f"        arr[j] = {fill_pattern};")
        code.append("    }")
        code.append("    sprayArrays.push(arr);")
        code.append("}")
        code.append("\n// Prevent garbage collection")
        code.append("globalThis.sprayArrays = sprayArrays;")
        
        return "\n".join(code)
    
    def generate_object_spray(self, config: SprayConfig) -> str:
        """Generate JavaScript code to spray objects with specific properties."""
        if config.fill_pattern is None:
            fill_pattern = "0x41"
        
        code = []
        code.append("// Object spray configuration")
        code.append(f"const targetSize = {config.target_size};")
        code.append(f"const numObjects = {config.num_objects};")
        code.append("const sprayObjects = [];")
        code.append("\n// Spray objects")
        code.append("for (let i = 0; i < numObjects; i++) {")
        code.append("    const obj = {};")
        code.append("    for (let j = 0; j < targetSize; j++) {")
        code.append(f"        obj[`prop${j}`] = {fill_pattern};")
        code.append("    }")
        code.append("    sprayObjects.push(obj);")
        code.append("}")
        code.append("\n// Prevent garbage collection")
        code.append("globalThis.sprayObjects = sprayObjects;")
        
        return "\n".join(code)
    
    def generate_string_spray(self, config: SprayConfig) -> str:
        """Generate JavaScript code to spray strings of specific size."""
        if config.fill_pattern is None:
            fill_pattern = "A" * config.target_size
        
        code = []
        code.append("// String spray configuration")
        code.append(f"const targetSize = {config.target_size};")
        code.append(f"const numObjects = {config.num_objects};")
        code.append("const sprayStrings = [];")
        code.append("\n// Spray strings")
        code.append(f"const fillPattern = '{fill_pattern}';")
        code.append("for (let i = 0; i < numObjects; i++) {")
        code.append("    sprayStrings.push(fillPattern);")
        code.append("}")
        code.append("\n// Prevent garbage collection")
        code.append("globalThis.sprayStrings = sprayStrings;")
        
        return "\n".join(code)
    
    def generate_defrag_code(self, target_size: int, num_holes: int) -> str:
        """Generate JavaScript code to defragment the heap."""
        code = []
        code.append("// Heap defragmentation")
        code.append(f"const targetSize = {target_size};")
        code.append(f"const numHoles = {num_holes};")
        code.append("const defragObjects = [];")
        code.append("\n// Create holes")
        code.append("for (let i = 0; i < numHoles; i++) {")
        code.append("    const arr = new Array(targetSize);")
        code.append("    defragObjects.push(arr);")
        code.append("}")
        code.append("\n// Force garbage collection")
        code.append("globalThis.defragObjects = defragObjects;")
        code.append("if (global.gc) {")
        code.append("    global.gc();")
        code.append("}")
        
        return "\n".join(code)
    
    def generate_spray(self, config: SprayConfig) -> str:
        """Generate appropriate spray code based on configuration."""
        self.spray_history.append(config)
        
        if config.object_type == "array":
            return self.generate_array_spray(config)
        elif config.object_type == "object":
            return self.generate_object_spray(config)
        elif config.object_type == "string":
            return self.generate_string_spray(config)
        else:
            raise ValueError(f"Unsupported object type: {config.object_type}")
    
    def generate_complete_spray_sequence(self, 
                                       target_size: int,
                                       num_objects: int,
                                       object_type: str = "array",
                                       fill_pattern: Optional[str] = None) -> str:
        """Generate a complete spray sequence including setup and cleanup."""
        config = SprayConfig(
            target_size=target_size,
            num_objects=num_objects,
            object_type=object_type,
            fill_pattern=fill_pattern
        )
        
        code = []
        code.append("// Heap spray sequence")
        code.append("(function() {")
        code.append("    // Prevent garbage collection during spray")
        code.append("    const keepAlive = [];")
        code.append("\n    // Generate spray")
        code.append(self.generate_spray(config))
        code.append("\n    // Force garbage collection")
        code.append("    if (global.gc) {")
        code.append("        global.gc();")
        code.append("    }")
        code.append("})();")
        
        return "\n".join(code) 