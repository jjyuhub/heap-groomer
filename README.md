# Heap Groomer Toolkit

A comprehensive toolkit for analyzing and automating heap grooming strategies for modern browser allocators like Chrome's PartitionAlloc.

## Features

### 1. Allocator Behavior Reverse Engineering
- Infer slot sizes, alignment, freelist structure, and bucket boundaries
- Detect reuse patterns from allocations and deallocations
- Fingerprint PartitionAlloc's behavior across Chrome versions

### 2. JavaScript Heap Spray + Defrag Utilities
- Generate optimized JS code for heap spraying
- Create defragmentation sequences
- Prime freelists with specific object shapes

### 3. Freelist Control Analysis
- Analyze potential target objects after simulated bugs
- Classify allocations into "spray candidates," "harmless," or "dangerous"
- Build allocation → overwrite → hijackable field graphs

### 4. Grooming Strategy Generator
- Auto-generate allocation patterns
- Create deallocation sequences
- Define trigger conditions

### 5. Heap Visualization / Timeline Tracker
- Visualize allocator state evolution
- Track per-bucket freelist changes
- Log snapshots with diff view

### 6. Target Bug Mode
- Define simulated bugs (overflow, UAF, etc.)
- Recommend candidate objects
- Generate grooming sequences
- Suggest fake object layouts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/heap_groomer.git
cd heap_groomer
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

The toolkit provides several command-line options:

```bash
python src/main.py [options]

Options:
  --analyze     Analyze allocator behavior
  --spray       Generate heap spray
  --freelist    Analyze freelist
  --strategy    Generate grooming strategy
  --visualize   Visualize heap state
  --bug         Analyze bug scenario
```

### Example Usage

1. Analyze allocator behavior:
```bash
python src/main.py --analyze
```

2. Generate heap spray:
```bash
python src/main.py --spray
# Enter size, count, and object type when prompted
```

3. Analyze freelist:
```bash
python src/main.py --freelist
# Enter target size when prompted
```

4. Generate grooming strategy:
```bash
python src/main.py --strategy
# Enter target size and type when prompted
```

5. Visualize heap state:
```bash
python src/main.py --visualize
```

6. Analyze bug scenario:
```bash
python src/main.py --bug
# Enter bug type, size, and offset when prompted
```

## Project Structure

```
heap_groomer/
├── src/
│   ├── allocator/
│   │   └── analyzer.py
│   ├── js/
│   │   └── heap_manipulator.py
│   ├── analysis/
│   │   └── freelist_analyzer.py
│   ├── strategy/
│   │   └── generator.py
│   ├── visualization/
│   │   └── heap_viewer.py
│   ├── bug_mode/
│   │   └── analyzer.py
│   └── main.py
├── tests/
├── requirements.txt
└── README.md
```

## Dependencies

- Python 3.10+
- matplotlib
- numpy
- playwright
- textual
- pydantic
- rich
- networkx
- pytest
- black
- mypy
- pytest-cov

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This toolkit is for educational and research purposes only. Do not use it for malicious purposes or against systems you don't own or have permission to test. 