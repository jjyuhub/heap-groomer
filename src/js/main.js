/**
 * Main entry point for the heap grooming toolkit
 */

import { HeapManipulator, SprayConfig } from './heap_manipulator.js';
import { HeapVisualizer, HeapSnapshot } from './visualization.js';

class HeapGroomer {
    constructor() {
        this.heapManipulator = new HeapManipulator();
        this.visualizer = new HeapVisualizer('#visualization');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Spray configuration form
        document.getElementById('spray-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSpraySubmit(e);
        });

        // Defragmentation form
        document.getElementById('defrag-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleDefragSubmit(e);
        });

        // Freelist priming form
        document.getElementById('freelist-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleFreelistSubmit(e);
        });
    }

    handleSpraySubmit(event) {
        const formData = new FormData(event.target);
        const config = new SprayConfig(
            parseInt(formData.get('targetSize')),
            parseInt(formData.get('count')),
            formData.get('objectType'),
            formData.get('fillPattern'),
            parseInt(formData.get('alignment'))
        );

        const code = this.heapManipulator.generateSprayCode(config);
        this.displayGeneratedCode(code);
        this.updateVisualization();
    }

    handleDefragSubmit(event) {
        const formData = new FormData(event.target);
        const targetSize = parseInt(formData.get('targetSize'));
        const count = parseInt(formData.get('count'));

        const code = this.heapManipulator.generateDefragCode(targetSize, count);
        this.displayGeneratedCode(code);
        this.updateVisualization();
    }

    handleFreelistSubmit(event) {
        const formData = new FormData(event.target);
        const slotSize = parseInt(formData.get('slotSize'));
        const count = parseInt(formData.get('count'));

        const code = this.heapManipulator.generateFreelistPriming(slotSize, count);
        this.displayGeneratedCode(code);
        this.updateVisualization();
    }

    displayGeneratedCode(code) {
        const codeElement = document.getElementById('generated-code');
        codeElement.textContent = code;
    }

    updateVisualization() {
        // Create a sample snapshot for visualization
        const snapshot = new HeapSnapshot(
            Date.now(),
            {
                '0x20': { free: 10, occupied: 5 },
                '0x30': { free: 8, occupied: 3 },
                '0x40': { free: 6, occupied: 4 }
            },
            1000,
            2000
        );

        this.visualizer.addSnapshot(snapshot);
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HeapGroomer();
}); 