/**
 * RegExp constructor and prototype for WoofJS
 * 
 * WoofJS RegExp is a simplified implementation that supports:
 * - Flags: g (global), i (case-insensitive), m (multiline), s (dotAll)
 * - Methods: test(str), exec(str)
 * - String methods with regex: match(regex), replace(regex, replacement), search(regex), split(regex)
 */

// RegExp constructor
const RegExp = function(pattern, flags) {
    if (!(this instanceof RegExp)) {
        return new RegExp(pattern, flags);
    }
    // Pattern and flags are set in the Rust runtime
    this.source = pattern || '';
    this.flags = flags || '';
    this.global = (flags || '').includes('g');
    this.ignoreCase = (flags || '').includes('i');
    this.multiline = (flags || '').includes('m');
    this.dotAll = (flags || '').includes('s');
    this.lastIndex = 0;
};

/**
 * RegExp.prototype.test(str)
 * Returns true if the pattern matches the string, false otherwise.
 */
RegExp.prototype.test = function(str) {
    // Implemented in Rust runtime
    throw new Error('RegExp.prototype.test not yet implemented in WoofJS');
};

/**
 * RegExp.prototype.exec(str)
 * Returns an array of matched groups or null if no match.
 */
RegExp.prototype.exec = function(str) {
    // Implemented in Rust runtime
    throw new Error('RegExp.prototype.exec not yet implemented in WoofJS');
};

/**
 * String.prototype.match(regexp)
 * Returns an array of matches or null.
 */
String.prototype.match = function(regexp) {
    // Implemented in Rust runtime
    throw new Error('String.prototype.match not yet implemented in WoofJS');
};

/**
 * String.prototype.replace(regexp, replacement)
 * Returns a new string with matches replaced.
 */
String.prototype.replace = function(regexp, replacement) {
    // Implemented in Rust runtime
    throw new Error('String.prototype.replace not yet implemented in WoofJS');
};

/**
 * String.prototype.search(regexp)
 * Returns the index of the first match or -1.
 */
String.prototype.search = function(regexp) {
    // Implemented in Rust runtime
    throw new Error('String.prototype.search not yet implemented in WoofJS');
};

/**
 * String.prototype.split(regexp, limit)
 * Returns an array of strings split by the pattern.
 */
String.prototype.split = function(regexp, limit) {
    // Implemented in Rust runtime
    throw new Error('String.prototype.split not yet implemented in WoofJS');
};
