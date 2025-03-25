/**
 * JavaScript heap manipulation module for generating heap spray and defragmentation code.
 */

class SprayConfig {
    /**
     * Configuration for heap spray operations.
     * @param {number} targetSize - Target size for spray objects
     * @param {number} count - Number of objects to spray
     * @param {string} objectType - Type of object ('array', 'object', 'string')
     * @param {string} [fillPattern] - Optional fill pattern
     * @param {number} [alignment=8] - Memory alignment
     */
    constructor(targetSize, count, objectType, fillPattern = null, alignment = 8) {
        this.targetSize = targetSize;
        this.count = count;
        this.objectType = objectType;
        this.fillPattern = fillPattern;
        this.alignment = alignment;
    }
}

class HeapManipulator {
    constructor() {
        this.sprayHistory = [];
    }

    /**
     * Generate JavaScript code for heap spraying
     * @param {SprayConfig} config - Spray configuration
     * @returns {string} Generated JavaScript code
     */
    generateSprayCode(config) {
        this.sprayHistory.push(config);

        switch (config.objectType) {
            case 'array':
                return this._generateArraySpray(config);
            case 'object':
                return this._generateObjectSpray(config);
            case 'string':
                return this._generateStringSpray(config);
            default:
                throw new Error(`Unsupported object type: ${config.objectType}`);
        }
    }

    /**
     * Generate code for array-based heap spray
     * @private
     */
    _generateArraySpray(config) {
        const fillValue = config.fillPattern || '0x41';
        return `
const spray = new Array(${config.count});
for (let i = 0; i < spray.length; i++) {
    spray[i] = new Array(${config.targetSize}).fill(Number(${fillValue}));
}`;
    }

    /**
     * Generate code for object-based heap spray
     * @private
     */
    _generateObjectSpray(config) {
        const properties = this._generateObjectProperties(config.targetSize);
        return `
const spray = new Array(${config.count});
for (let i = 0; i < spray.length; i++) {
    spray[i] = {
        ${properties.map(prop => `${prop}: Number(${config.fillPattern || '0x41'})`).join(',\n        ')}
    };
}`;
    }

    /**
     * Generate code for string-based heap spray
     * @private
     */
    _generateStringSpray(config) {
        const fillChar = config.fillPattern || 'A';
        return `
const spray = new Array(${config.count});
for (let i = 0; i < spray.length; i++) {
    spray[i] = '${fillChar}'.repeat(${config.targetSize});
}`;
    }

    /**
     * Generate code for heap defragmentation
     * @param {number} targetSize - Target size for dummy objects
     * @param {number} [count=100] - Number of dummy objects
     * @returns {string} Generated JavaScript code
     */
    generateDefragCode(targetSize, count = 100) {
        return `
const dummy = [];
for (let i = 0; i < ${count}; i++) {
    dummy.push(new Array(${targetSize}).fill(Number(0x42)));
}

// Force garbage collection
dummy.length = 0;
if (global.gc) global.gc();`;
    }

    /**
     * Generate object properties to achieve target size
     * @private
     */
    _generateObjectProperties(targetSize) {
        const properties = [];
        let currentSize = 0;

        while (currentSize < targetSize) {
            const propName = this._generateRandomString(8);
            properties.push(propName);
            currentSize += 8; // Approximate property size
        }

        return properties;
    }

    /**
     * Generate random string of specified length
     * @private
     */
    _generateRandomString(length) {
        const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
        return Array.from({ length }, () => chars[Math.floor(Math.random() * chars.length)]).join('');
    }

    /**
     * Generate code to prime freelist for specific slot size
     * @param {number} slotSize - Size of slots to prime
     * @param {number} count - Number of objects to create
     * @returns {string} Generated JavaScript code
     */
    generateFreelistPriming(slotSize, count) {
        return `
const prime = new Array(${count});
for (let i = 0; i < prime.length; i++) {
    prime[i] = new Array(${slotSize}).fill(Number(0x43));
}

// Free them to prime freelist
prime.length = 0;
if (global.gc) global.gc();`;
    }
}

// Export for use in other modules
export { HeapManipulator, SprayConfig }; 