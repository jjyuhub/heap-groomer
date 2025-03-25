"""
Main entry point for the heap grooming toolkit.
"""

import argparse
import json
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from allocator.analyzer import AllocatorAnalyzer
from js.heap_manipulator import HeapManipulator, SprayConfig
from analysis.freelist_analyzer import FreelistAnalyzer, ObjectMetadata, ObjectClass
from strategy.generator import StrategyGenerator, GroomingStrategy
from visualization.heap_viewer import HeapViewer, HeapSnapshot
from bug_mode.analyzer import BugAnalyzer, BugConfig, BugType, TargetObject

class HeapGroomer:
    """Main class for the heap grooming toolkit."""
    
    def __init__(self):
        self.console = Console()
        self.allocator_analyzer = AllocatorAnalyzer()
        self.heap_manipulator = HeapManipulator()
        self.freelist_analyzer = FreelistAnalyzer()
        self.strategy_generator = StrategyGenerator()
        self.heap_viewer = HeapViewer()
        self.bug_analyzer = BugAnalyzer()
        
    def analyze_allocator(self, events_file: Optional[str] = None) -> None:
        """Analyze allocator behavior."""
        self.console.print(Panel("Starting Allocator Analysis", title="Phase 1"))
        
        if events_file:
            # Load events from file
            with open(events_file, 'r') as f:
                events = json.load(f)
                for event in events:
                    self.allocator_analyzer.record_allocation(event)
        else:
            # Interactive mode
            while True:
                size = Prompt.ask("Enter allocation size (or 'q' to quit)")
                if size.lower() == 'q':
                    break
                    
                try:
                    size = int(size)
                    address = int(Prompt.ask("Enter allocation address"))
                    obj_type = Prompt.ask("Enter object type")
                    
                    self.allocator_analyzer.record_allocation({
                        "size": size,
                        "address": address,
                        "timestamp": 0,  # Would need real timestamps
                        "object_type": obj_type
                    })
                except ValueError:
                    self.console.print("[red]Invalid input[/red]")
                    
        # Show analysis results
        self.console.print("\n[bold]Allocator Analysis Results:[/bold]")
        self.console.print(self.allocator_analyzer.get_slot_statistics())
        
    def generate_spray(self, size: int, count: int, obj_type: str) -> None:
        """Generate heap spray code."""
        self.console.print(Panel("Generating Heap Spray", title="Phase 2"))
        
        config = SprayConfig(
            target_size=size,
            count=count,
            object_type=obj_type
        )
        
        code = self.heap_manipulator.generate_spray_code(config)
        self.console.print(Panel(code, title="Generated JavaScript Code"))
        
    def analyze_freelist(self, target_size: int) -> None:
        """Analyze freelist behavior."""
        self.console.print(Panel("Analyzing Freelist", title="Phase 3"))
        
        # Register some common objects
        self._register_common_objects()
        
        # Analyze potential targets
        candidates = self.freelist_analyzer.get_spray_candidates(target_size)
        
        self.console.print("\n[bold]Potential Target Objects:[/bold]")
        for candidate in candidates:
            self.console.print(f"- {candidate.name} (size: {candidate.size})")
            
    def generate_strategy(self, target_size: int, target_type: str) -> None:
        """Generate grooming strategy."""
        self.console.print(Panel("Generating Grooming Strategy", title="Phase 4"))
        
        strategy = self.strategy_generator.generate_strategy(
            target_size, target_type)
            
        self.console.print("\n[bold]Generated Strategy:[/bold]")
        self.console.print(strategy.description)
        
    def visualize_heap(self) -> None:
        """Visualize heap state."""
        self.console.print(Panel("Visualizing Heap State", title="Phase 5"))
        
        # Generate some sample snapshots
        self._generate_sample_snapshots()
        
        # Show visualization
        self.heap_viewer.plot_timeline()
        self.heap_viewer.print_current_state()
        
    def analyze_bug(self, bug_type: str, size: int, offset: int) -> None:
        """Analyze bug scenario."""
        self.console.print(Panel("Analyzing Bug Scenario", title="Phase 6"))
        
        config = BugConfig(
            type=BugType(bug_type),
            size=size,
            offset=offset,
            overwrite_size=size,
            target_object="",
            constraints={}
        )
        
        analysis = self.bug_analyzer.analyze_bug(config)
        
        self.console.print("\n[bold]Analysis Results:[/bold]")
        self.console.print(f"Overall Score: {analysis['exploitability']['overall_score']}")
        self.console.print("\nFactors:")
        for factor in analysis['exploitability']['factors']:
            self.console.print(f"- {factor}")
            
    def _register_common_objects(self) -> None:
        """Register common target objects."""
        common_objects = [
            ObjectMetadata(
                name="ArrayBuffer",
                size=0x20,
                alignment=8,
                class_type=ObjectClass.DANGEROUS,
                dangerous_fields=["data", "length"],
                vtable_offset=0x8
            ),
            ObjectMetadata(
                name="JSFunction",
                size=0x30,
                alignment=8,
                class_type=ObjectClass.DANGEROUS,
                dangerous_fields=["code", "scope"],
                vtable_offset=0x0
            ),
            ObjectMetadata(
                name="TypedArray",
                size=0x40,
                alignment=8,
                class_type=ObjectClass.DANGEROUS,
                dangerous_fields=["buffer", "length"],
                vtable_offset=0x8
            )
        ]
        
        for obj in common_objects:
            self.freelist_analyzer.register_object_type(obj)
            
    def _generate_sample_snapshots(self) -> None:
        """Generate sample heap snapshots for visualization."""
        snapshots = [
            HeapSnapshot(
                timestamp=0,
                bucket_states={
                    0x20: {"free": 10, "occupied": 5},
                    0x30: {"free": 8, "occupied": 3},
                    0x40: {"free": 6, "occupied": 4}
                },
                total_allocated=1000,
                total_free=2000
            ),
            HeapSnapshot(
                timestamp=1,
                bucket_states={
                    0x20: {"free": 8, "occupied": 7},
                    0x30: {"free": 6, "occupied": 5},
                    0x40: {"free": 4, "occupied": 6}
                },
                total_allocated=1500,
                total_free=1500
            )
        ]
        
        for snapshot in snapshots:
            self.heap_viewer.add_snapshot(snapshot)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Heap Grooming Toolkit")
    parser.add_argument("--analyze", action="store_true", help="Analyze allocator behavior")
    parser.add_argument("--spray", action="store_true", help="Generate heap spray")
    parser.add_argument("--freelist", action="store_true", help="Analyze freelist")
    parser.add_argument("--strategy", action="store_true", help="Generate grooming strategy")
    parser.add_argument("--visualize", action="store_true", help="Visualize heap state")
    parser.add_argument("--bug", action="store_true", help="Analyze bug scenario")
    
    args = parser.parse_args()
    
    groomer = HeapGroomer()
    
    if args.analyze:
        groomer.analyze_allocator()
    elif args.spray:
        size = int(input("Enter spray size: "))
        count = int(input("Enter spray count: "))
        obj_type = input("Enter object type: ")
        groomer.generate_spray(size, count, obj_type)
    elif args.freelist:
        size = int(input("Enter target size: "))
        groomer.analyze_freelist(size)
    elif args.strategy:
        size = int(input("Enter target size: "))
        obj_type = input("Enter target type: ")
        groomer.generate_strategy(size, obj_type)
    elif args.visualize:
        groomer.visualize_heap()
    elif args.bug:
        bug_type = input("Enter bug type (overflow/uaf/double_free): ")
        size = int(input("Enter size: "))
        offset = int(input("Enter offset: "))
        groomer.analyze_bug(bug_type, size, offset)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 