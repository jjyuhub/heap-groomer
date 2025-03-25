/**
 * Heap visualization module using D3.js
 */

import * as d3 from 'd3';

export class HeapVisualizer {
    constructor(containerId) {
        this.container = d3.select(`#${containerId}`);
        this.width = 800;
        this.height = 600;
        this.margin = { top: 20, right: 20, bottom: 30, left: 40 };
        
        this.svg = this.container
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height);
            
        this.setupScales();
        this.setupAxes();
    }

    /**
     * Update visualization with new heap state
     * @param {Object} heapState - Current heap state
     * @param {Map<number, Array>} heapState.freelists - Freelist state by bucket
     * @param {Array} heapState.allocations - Current allocations
     */
    updateVisualization(heapState) {
        this.clearVisualization();
        this.drawFreelists(heapState.freelists);
        this.drawAllocations(heapState.allocations);
    }

    /**
     * Draw timeline of heap state changes
     * @param {Array} timeline - Array of heap state snapshots
     */
    drawTimeline(timeline) {
        const timelineHeight = 100;
        const timelineY = this.height - timelineHeight - this.margin.bottom;
        
        const timelineSvg = this.svg
            .append('g')
            .attr('transform', `translate(0, ${timelineY})`);
            
        const xScale = d3.scaleTime()
            .domain(d3.extent(timeline, d => d.timestamp))
            .range([this.margin.left, this.width - this.margin.right]);
            
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(timeline, d => d.freeChunks)])
            .range([timelineHeight, 0]);
            
        // Draw timeline line
        const line = d3.line()
            .x(d => xScale(d.timestamp))
            .y(d => yScale(d.freeChunks));
            
        timelineSvg.append('path')
            .datum(timeline)
            .attr('fill', 'none')
            .attr('stroke', 'steelblue')
            .attr('stroke-width', 2)
            .attr('d', line);
    }

    /**
     * Draw diff visualization between two heap states
     * @param {Object} before - Previous heap state
     * @param {Object} after - Current heap state
     */
    drawDiff(before, after) {
        const diffGroup = this.svg.append('g')
            .attr('class', 'diff-visualization');
            
        // Draw added allocations in green
        this.drawAllocationDiffs(before.allocations, after.allocations, 'green', diffGroup);
        
        // Draw removed allocations in red
        this.drawAllocationDiffs(after.allocations, before.allocations, 'red', diffGroup);
    }

    // Private helper methods
    setupScales() {
        this.xScale = d3.scaleLinear()
            .range([this.margin.left, this.width - this.margin.right]);
            
        this.yScale = d3.scaleLinear()
            .range([this.height - this.margin.bottom, this.margin.top]);
    }

    setupAxes() {
        const xAxis = d3.axisBottom(this.xScale);
        const yAxis = d3.axisLeft(this.yScale);
        
        this.svg.append('g')
            .attr('transform', `translate(0, ${this.height - this.margin.bottom})`)
            .call(xAxis);
            
        this.svg.append('g')
            .attr('transform', `translate(${this.margin.left}, 0)`)
            .call(yAxis);
    }

    clearVisualization() {
        this.svg.selectAll('.heap-element').remove();
    }

    drawFreelists(freelists) {
        const freelistGroup = this.svg.append('g')
            .attr('class', 'freelists');
            
        let yOffset = this.margin.top;
        
        for (const [bucketSize, chunks] of freelelists) {
            const bucketGroup = freelistGroup.append('g')
                .attr('class', `bucket-${bucketSize}`);
                
            // Draw bucket header
            bucketGroup.append('text')
                .attr('x', this.margin.left)
                .attr('y', yOffset)
                .text(`Bucket ${bucketSize} bytes (${chunks.length} chunks)`);
                
            // Draw chunks
            chunks.forEach((chunk, index) => {
                bucketGroup.append('rect')
                    .attr('class', 'heap-element freelist-chunk')
                    .attr('x', this.margin.left + index * 30)
                    .attr('y', yOffset + 20)
                    .attr('width', 25)
                    .attr('height', 20)
                    .attr('fill', 'lightblue')
                    .attr('stroke', 'steelblue');
            });
            
            yOffset += 50;
        }
    }

    drawAllocations(allocations) {
        const allocationGroup = this.svg.append('g')
            .attr('class', 'allocations');
            
        allocations.forEach((alloc, index) => {
            allocationGroup.append('rect')
                .attr('class', 'heap-element allocation')
                .attr('x', this.margin.left + index * 30)
                .attr('y', this.height - this.margin.bottom - 30)
                .attr('width', 25)
                .attr('height', alloc.size / 10) // Scale height based on size
                .attr('fill', 'lightgreen')
                .attr('stroke', 'darkgreen');
        });
    }

    drawAllocationDiffs(before, after, color, group) {
        const added = after.filter(alloc => 
            !before.some(b => b.address === alloc.address)
        );
        
        added.forEach((alloc, index) => {
            group.append('rect')
                .attr('class', 'heap-element diff')
                .attr('x', this.margin.left + index * 30)
                .attr('y', this.height - this.margin.bottom - 60)
                .attr('width', 25)
                .attr('height', alloc.size / 10)
                .attr('fill', color)
                .attr('stroke', d3.color(color).darker());
        });
    }
} 