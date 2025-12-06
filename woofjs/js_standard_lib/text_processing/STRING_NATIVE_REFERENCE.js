/**
 * WoofJS String Native Functions Reference
 * 
 * This document lists all native functions that String.js calls into Rust.
 * Each function is marked with [NATIVE] and should be implemented in the Rust runtime.
 * 
 * Implementation Strategy:
 * - Add these functions to the global context in runtime.rs
 * - They should be wrappers around Rust string operations
 * - They must handle edge cases and Unicode properly
 */

// ============================================================================
// CHARACTER ACCESS - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringCharAt(str: String, index: i32) -> String
 * Returns the character at the given index
 * - Returns empty string if index is out of bounds
 * - Required for: String.prototype.charAt
 */
function __stringCharAt(str, index) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringCharAt not implemented');
}

/**
 * __stringCharCodeAt(str: String, index: i32) -> Number
 * Returns the Unicode code unit at the given index
 * - Returns NaN if index is out of bounds
 * - Required for: String.prototype.charCodeAt
 */
function __stringCharCodeAt(str, index) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringCharCodeAt not implemented');
}

/**
 * __stringCodePointAt(str: String, index: i32) -> Number | undefined
 * Returns the Unicode code point at the given index
 * - Returns undefined if index is out of bounds
 * - Handles surrogate pairs correctly
 * - Required for: String.prototype.codePointAt
 */
function __stringCodePointAt(str, index) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringCodePointAt not implemented');
}

// ============================================================================
// SLICING - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringSlice(str: String, start: i32, end: i32) -> String
 * Returns substring from start (inclusive) to end (exclusive)
 * - Assumes start and end are already normalized (non-negative, within bounds)
 * - Required for: String.prototype.slice, substring, substr
 */
function __stringSlice(str, start, end) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringSlice not implemented');
}

// ============================================================================
// SEARCHING - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringIndexOf(str: String, searchStr: String, fromIndex: i32) -> i32
 * Returns the index of the first occurrence of searchStr
 * - Returns -1 if not found
 * - Starts searching from fromIndex
 * - Required for: String.prototype.indexOf
 */
function __stringIndexOf(str, searchStr, fromIndex) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringIndexOf not implemented');
}

/**
 * __stringLastIndexOf(str: String, searchStr: String, fromIndex: i32) -> i32
 * Returns the index of the last occurrence of searchStr
 * - Returns -1 if not found
 * - Searches backwards from fromIndex
 * - Required for: String.prototype.lastIndexOf
 */
function __stringLastIndexOf(str, searchStr, fromIndex) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringLastIndexOf not implemented');
}

// ============================================================================
// CASE TRANSFORMATION - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringToUpperCase(str: String) -> String
 * Returns the string in uppercase
 * - Must handle Unicode case mappings correctly
 * - Required for: String.prototype.toUpperCase
 */
function __stringToUpperCase(str) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringToUpperCase not implemented');
}

/**
 * __stringToLowerCase(str: String) -> String
 * Returns the string in lowercase
 * - Must handle Unicode case mappings correctly
 * - Required for: String.prototype.toLowerCase
 */
function __stringToLowerCase(str) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringToLowerCase not implemented');
}

// ============================================================================
// TRIMMING - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringTrim(str: String) -> String
 * Removes whitespace from both ends of the string
 * - Whitespace includes space, tab, newline, carriage return, form feed, vertical tab
 * - Required for: String.prototype.trim
 */
function __stringTrim(str) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringTrim not implemented');
}

// ============================================================================
// REPETITION - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringRepeat(str: String, count: i32) -> String
 * Returns a string with str repeated count times
 * - Assumes count is already validated (>= 0 and not Infinity)
 * - Should be optimized for large counts
 * - Required for: String.prototype.repeat
 */
function __stringRepeat(str, count) {
    // [NATIVE] Rust implementation needed (can be optimized with exponential growth)
    throw new Error('__stringRepeat not implemented');
}

// ============================================================================
// PATTERN MATCHING - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringMatch(str: String, regexp: RegExp) -> Array | null
 * Returns an array of matches or null
 * - If regexp has global flag, returns all matches
 * - Otherwise returns array with match and capture groups
 * - Required for: String.prototype.match
 */
function __stringMatch(str, regexp) {
    // [NATIVE] Rust implementation needed (uses JsRegExp)
    throw new Error('__stringMatch not implemented');
}

/**
 * __stringSearch(str: String, regexp: RegExp) -> i32
 * Returns the index of the first match or -1
 * - Does not use the global flag (always finds first match)
 * - Required for: String.prototype.search
 */
function __stringSearch(str, regexp) {
    // [NATIVE] Rust implementation needed (uses JsRegExp)
    throw new Error('__stringSearch not implemented');
}

/**
 * __stringReplaceAll(str: String, searchStr: String, replaceStr: String) -> String
 * Returns a string with all occurrences of searchStr replaced with replaceStr
 * - Assumes searchStr is not empty
 * - Should be optimized for performance
 * - Required for: String.prototype.replaceAll
 */
function __stringReplaceAll(str, searchStr, replaceStr) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringReplaceAll not implemented');
}

/**
 * __stringSplit(str: String, separator: String, limit: Number) -> Array
 * Returns an array of strings split by separator
 * - Handles edge cases like empty separator
 * - Respects limit on array length
 * - Required for: String.prototype.split (string version)
 */
function __stringSplit(str, separator, limit) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringSplit not implemented');
}

/**
 * __stringSplitRegex(str: String, regexp: RegExp, limit: Number) -> Array
 * Returns an array of strings split by a regular expression
 * - Handles capture groups in the result array
 * - Respects limit on array length
 * - Required for: String.prototype.split (regex version)
 */
function __stringSplitRegex(str, regexp, limit) {
    // [NATIVE] Rust implementation needed (uses JsRegExp)
    throw new Error('__stringSplitRegex not implemented');
}

// ============================================================================
// CHARACTER CREATION - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringFromCharCode(charCode: i32) -> String
 * Returns a single character from a Unicode code unit
 * - charCode is a 16-bit value
 * - Required for: String.fromCharCode
 */
function __stringFromCharCode(charCode) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringFromCharCode not implemented');
}

/**
 * __stringFromCodePoint(codePoint: i32) -> String
 * Returns a character from a Unicode code point
 * - Properly handles code points outside BMP (creates surrogate pairs if needed)
 * - Assumes codePoint is already validated (0 <= codePoint <= 0x10FFFF)
 * - Required for: String.fromCodePoint
 */
function __stringFromCodePoint(codePoint) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringFromCodePoint not implemented');
}

// ============================================================================
// PROPERTIES - NATIVE FUNCTIONS
// ============================================================================

/**
 * __stringLength(str: String) -> i32
 * Returns the length of the string in UTF-16 code units
 * - Note: length is the number of UTF-16 code units, not code points
 * - Required for: String.prototype.length property
 */
function __stringLength(str) {
    // [NATIVE] Rust implementation needed
    throw new Error('__stringLength not implemented');
}

// ============================================================================
// IMPLEMENTATION NOTES FOR RUST BACKEND
// ============================================================================

/**
 * When implementing these functions in Rust, consider:
 * 
 * 1. STRING REPRESENTATION
 *    - Use Rust's String type (UTF-8) internally
 *    - Convert to UTF-16 for length/index calculations when needed
 *    - Handle surrogate pairs for code points outside BMP
 * 
 * 2. UNICODE HANDLING
 *    - Correctly handle combining characters
 *    - Handle case mapping for non-ASCII characters
 *    - Properly split/join surrogate pairs for code points
 * 
 * 3. PERFORMANCE
 *    - Use efficient algorithms for searching (Boyer-Moore, KMP, etc.)
 *    - Cache regex compilations when possible
 *    - Optimize string repetition with exponential growth
 * 
 * 4. ERROR HANDLING
 *    - Return sensible defaults (empty string, -1, NaN) for edge cases
 *    - Throw RangeError for invalid code points
 *    - Throw TypeError for invalid arguments
 * 
 * 5. INTEGRATION WITH PyO3
 *    - These functions should be exposed to the Python runtime
 *    - They need to bridge between Python strings and Rust String operations
 *    - Consider thread safety if called from multiple threads
 */
