"""
Heap visualization module for displaying allocator state and timeline tracking.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static
from rich.console import Console
from rich.table import Table

@dataclass
class HeapSnapshot:
    """Represents a snapshot of the heap state."""
    timestamp: float
    bucket_states: Dict[int, Dict]  # bucket_index -> {free: int, occupied: int}
    total_allocated: int
    total_free: int

class HeapViewer:
    """Main class for visualizing heap state."""
    
    def __init__(self):
        self.snapshots: List[HeapSnapshot] = []
        self.console = Console()
        
    def add_snapshot(self, snapshot: HeapSnapshot) -> None:
        """Add a new heap snapshot."""
        self.snapshots.append(snapshot)
        
    def plot_timeline(self, save_path: Optional[str] = None) -> None:
        """Plot heap state evolution over time."""
        if not self.snapshots:
            return
            
        # Prepare data
        timestamps = [s.timestamp for s in self.snapshots]
        buckets = sorted(list(self.snapshots[0].bucket_states.keys()))
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot per-bucket state
        for bucket in buckets:
            free = [s.bucket_states[bucket]["free"] for s in self.snapshots]
            occupied = [s.bucket_states[bucket]["occupied"] for s in self.snapshots]
            
            ax1.plot(timestamps, free, label=f"Bucket {bucket} (Free)")
            ax1.plot(timestamps, occupied, '--', label=f"Bucket {bucket} (Occupied)")
            
        ax1.set_title("Per-Bucket State Evolution")
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Chunks")
        ax1.legend()
        ax1.grid(True)
        
        # Plot total state
        total_allocated = [s.total_allocated for s in self.snapshots]
        total_free = [s.total_free for s in self.snapshots]
        
        ax2.plot(timestamps, total_allocated, label="Total Allocated")
        ax2.plot(timestamps, total_free, label="Total Free")
        
        ax2.set_title("Total Heap State")
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Bytes")
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()
            
    def print_current_state(self) -> None:
        """Print current heap state in a formatted table."""
        if not self.snapshots:
            return
            
        current = self.snapshots[-1]
        
        # Create table
        table = Table(title="Current Heap State")
        table.add_column("Bucket")
        table.add_column("Free Chunks")
        table.add_column("Occupied Chunks")
        table.add_column("Total Size")
        
        for bucket, state in current.bucket_states.items():
            total_size = (state["free"] + state["occupied"]) * bucket
            table.add_row(
                str(bucket),
                str(state["free"]),
                str(state["occupied"]),
                f"{total_size:,} bytes"
            )
            
        # Add totals row
        table.add_row(
            "TOTAL",
            str(current.total_free),
            str(current.total_allocated),
            f"{current.total_free + current.total_allocated:,} bytes"
        )
        
        self.console.print(table)
        
    def show_diff(self, snapshot1: int, snapshot2: int) -> None:
        """Show differences between two snapshots."""
        if not (0 <= snapshot1 < len(self.snapshots) and 
                0 <= snapshot2 < len(self.snapshots)):
            return
            
        s1 = self.snapshots[snapshot1]
        s2 = self.snapshots[snapshot2]
        
        table = Table(title=f"Heap State Diff (Snapshot {snapshot1} -> {snapshot2})")
        table.add_column("Bucket")
        table.add_column("Free Δ")
        table.add_column("Occupied Δ")
        
        for bucket in sorted(set(s1.bucket_states.keys()) | set(s2.bucket_states.keys())):
            state1 = s1.bucket_states.get(bucket, {"free": 0, "occupied": 0})
            state2 = s2.bucket_states.get(bucket, {"free": 0, "occupied": 0})
            
            free_diff = state2["free"] - state1["free"]
            occupied_diff = state2["occupied"] - state1["occupied"]
            
            if free_diff != 0 or occupied_diff != 0:
                table.add_row(
                    str(bucket),
                    str(free_diff),
                    str(occupied_diff)
                )
                
        self.console.print(table)

class HeapViewerApp(App):
    """Textual application for interactive heap visualization."""
    
    def __init__(self, viewer: HeapViewer):
        super().__init__()
        self.viewer = viewer
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            Static(self._generate_state_table()),
            id="state"
        )
        yield Footer()
        
    def _generate_state_table(self) -> str:
        """Generate the current state table."""
        if not self.viewer.snapshots:
            return "No snapshots available"
            
        current = self.viewer.snapshots[-1]
        table = Table(title="Current Heap State")
        
        table.add_column("Bucket")
        table.add_column("Free")
        table.add_column("Occupied")
        
        for bucket, state in current.bucket_states.items():
            table.add_row(
                str(bucket),
                str(state["free"]),
                str(state["occupied"])
            )
            
        return str(table) 