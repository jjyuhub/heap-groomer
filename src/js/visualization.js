/**
 * Heap visualization module using D3.js
 */

import * as d3 from 'd3';

class HeapSnapshot {
    /**
     * Represents a snapshot of the heap state
     * @param {number} timestamp - Timestamp of the snapshot
     * @param {Object} bucketStates - State of each bucket
     * @param {number} totalAllocated - Total allocated memory
     * @param {number} totalFree - Total free memory
     */
    constructor(timestamp, bucketStates, totalAllocated, totalFree) {
        this.timestamp = timestamp;
        this.bucketStates = bucketStates;
        this.totalAllocated = totalAllocated;
        this.totalFree = totalFree;
    }
}

class HeapVisualizer {
    constructor(containerId) {
        this.container = d3.select(containerId);
        this.snapshots = [];
        this.margin = { top: 20, right: 30, bottom: 30, left: 40 };
        this.width = 800 - this.margin.left - this.margin.right;
        this.height = 400 - this.margin.top - this.margin.bottom;
    }

    /**
     * Add a new heap snapshot
     * @param {HeapSnapshot} snapshot - Snapshot to add
     */
    addSnapshot(snapshot) {
        this.snapshots.push(snapshot);
        this.updateVisualization();
    }

    /**
     * Update the visualization with current snapshots
     */
    updateVisualization() {
        if (this.snapshots.length === 0) return;

        // Clear previous visualization
        this.container.selectAll("*").remove();

        // Create SVG
        const svg = this.container.append("svg")
            .attr("width", this.width + this.margin.left + this.margin.right)
            .attr("height", this.height + this.margin.top + this.margin.bottom)
            .append("g")
            .attr("transform", `translate(${this.margin.left},${this.margin.top})`);

        // Prepare data
        const timestamps = this.snapshots.map(s => s.timestamp);
        const buckets = Object.keys(this.snapshots[0].bucketStates);

        // Create scales
        const x = d3.scaleLinear()
            .domain([0, d3.max(timestamps)])
            .range([0, this.width]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(this.snapshots, s => 
                Math.max(...Object.values(s.bucketStates).map(state => 
                    state.free + state.occupied
                ))
            )])
            .range([this.height, 0]);

        const color = d3.scaleOrdinal(d3.schemeCategory10);

        // Create axes
        svg.append("g")
            .attr("transform", `translate(0,${this.height})`)
            .call(d3.axisBottom(x))
            .append("text")
            .attr("fill", "#000")
            .attr("x", this.width / 2)
            .attr("y", 30)
            .text("Time");

        svg.append("g")
            .call(d3.axisLeft(y))
            .append("text")
            .attr("fill", "#000")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Chunks");

        // Create lines for each bucket
        buckets.forEach((bucket, i) => {
            const line = d3.line()
                .x(d => x(d.timestamp))
                .y(d => y(d.bucketStates[bucket].free + d.bucketStates[bucket].occupied));

            svg.append("path")
                .datum(this.snapshots)
                .attr("fill", "none")
                .attr("stroke", color(i))
                .attr("stroke-width", 1.5)
                .attr("d", line)
                .append("title")
                .text(`Bucket ${bucket}`);
        });

        // Add legend
        const legend = svg.append("g")
            .attr("font-family", "sans-serif")
            .attr("font-size", 10)
            .attr("text-anchor", "start")
            .selectAll("g")
            .data(buckets)
            .enter().append("g")
            .attr("transform", (d, i) => `translate(0,${i * 20})`);

        legend.append("rect")
            .attr("x", this.width - 19)
            .attr("width", 19)
            .attr("height", 19)
            .attr("fill", (d, i) => color(i));

        legend.append("text")
            .attr("x", this.width - 24)
            .attr("y", 9.5)
            .attr("dy", "0.32em")
            .text(d => `Bucket ${d}`);
    }

    /**
     * Show differences between two snapshots
     * @param {number} snapshot1 - Index of first snapshot
     * @param {number} snapshot2 - Index of second snapshot
     */
    showDiff(snapshot1, snapshot2) {
        if (!(0 <= snapshot1 < this.snapshots.length && 
              0 <= snapshot2 < this.snapshots.length)) {
            return;
        }

        const s1 = this.snapshots[snapshot1];
        const s2 = this.snapshots[snapshot2];

        // Create diff table
        const table = document.createElement('table');
        table.className = 'diff-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Bucket</th>
                    <th>Free Δ</th>
                    <th>Occupied Δ</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        `;

        const tbody = table.querySelector('tbody');
        const buckets = new Set([
            ...Object.keys(s1.bucketStates),
            ...Object.keys(s2.bucketStates)
        ]);

        buckets.forEach(bucket => {
            const state1 = s1.bucketStates[bucket] || { free: 0, occupied: 0 };
            const state2 = s2.bucketStates[bucket] || { free: 0, occupied: 0 };

            const freeDiff = state2.free - state1.free;
            const occupiedDiff = state2.occupied - state1.occupied;

            if (freeDiff !== 0 || occupiedDiff !== 0) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${bucket}</td>
                    <td>${freeDiff}</td>
                    <td>${occupiedDiff}</td>
                `;
                tbody.appendChild(row);
            }
        });

        // Add table to container
        this.container.selectAll('.diff-table').remove();
        this.container.node().appendChild(table);
    }
}

// Export for use in other modules
export { HeapVisualizer, HeapSnapshot }; 