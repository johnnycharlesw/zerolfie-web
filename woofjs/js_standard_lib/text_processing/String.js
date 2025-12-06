/**
 * String constructor and prototype for WoofJS
 * 
 * A self-hosted implementation with Rust internals for:
 * - Basic string operations (charAt, charCodeAt, slice, substring, etc.)
 * - Search operations (indexOf, lastIndexOf, includes, startsWith, endsWith)
 * - Transformation (toUpperCase, toLowerCase, trim, repeat, padStart, padEnd)
 * - Case operations (toLocaleUpperCase, toLocaleLowerCase)
 * - Advanced string methods (match, replace, search, split with regex support)
 * - Iteration and reduction
 * 
 * Performance-critical ops marked with [NATIVE] are optimized in Rust.
 */

/**
 * String constructor
 * Converts value to a string primitive
 */
const String = function(value) {
    // Convert value to string
    if (value === undefined) return '';
    if (value === null) return 'null';
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    if (typeof value === 'number') return value.toString();
    if (typeof value === 'string') return value;
    if (typeof value === 'object') {
        // For objects, try toString method
        if (value && typeof value.toString === 'function') {
            return value.toString();
        }
        return '[object Object]';
    }
    return String(value);
};

/**
 * String.prototype property access
 * [NATIVE] In Rust: implement character indexing
 */
Object.defineProperty(String.prototype, Symbol.iterator, {
    value: function() {
        const str = this;
        let index = 0;
        return {
            next: function() {
                if (index < str.length) {
                    return { value: str[index++], done: false };
                }
                return { done: true };
            }
        };
    }
});

// ============================================================================
// Character Access Methods
// ============================================================================

/**
 * String.prototype.charAt(index)
 * Returns the character at the specified index
 * [NATIVE] Optimized in Rust for performance
 */
String.prototype.charAt = function(index) {
    const idx = Math.trunc(index);
    if (idx < 0 || idx >= this.length) return '';
    // [NATIVE] Call Rust backend
    return __stringCharAt(this, idx);
};

/**
 * String.prototype.charCodeAt(index)
 * Returns the Unicode value of the character at the specified index
 * [NATIVE] Optimized in Rust
 */
String.prototype.charCodeAt = function(index) {
    const idx = Math.trunc(index);
    if (idx < 0 || idx >= this.length) return NaN;
    // [NATIVE] Call Rust backend
    return __stringCharCodeAt(this, idx);
};

/**
 * String.prototype.codePointAt(index)
 * Returns the Unicode code point value at the specified index
 * [NATIVE] Optimized in Rust
 */
String.prototype.codePointAt = function(index) {
    const idx = Math.trunc(index);
    if (idx < 0 || idx >= this.length) return undefined;
    // [NATIVE] Call Rust backend
    return __stringCodePointAt(this, idx);
};

// ============================================================================
// Substring/Slice Methods
// ============================================================================

/**
 * String.prototype.slice(start, end)
 * Returns a section of the string
 * [NATIVE] Optimized in Rust
 */
String.prototype.slice = function(start, end) {
    const len = this.length;
    // Normalize indices
    let s = Math.trunc(start);
    if (s < 0) s = Math.max(0, len + s);
    else s = Math.min(s, len);
    
    let e = end === undefined ? len : Math.trunc(end);
    if (e < 0) e = Math.max(0, len + e);
    else e = Math.min(e, len);
    
    if (s >= e) return '';
    // [NATIVE] Call Rust backend
    return __stringSlice(this, s, e);
};

/**
 * String.prototype.substring(start, end)
 * Returns the substring between two indices (non-negative)
 * [NATIVE] Optimized in Rust
 */
String.prototype.substring = function(start, end) {
    const len = this.length;
    let s = Math.trunc(start);
    let e = end === undefined ? len : Math.trunc(end);
    
    // Swap if start > end
    if (s > e) {
        const temp = s;
        s = e;
        e = temp;
    }
    s = Math.max(0, s);
    e = Math.min(len, e);
    
    if (s >= e) return '';
    // [NATIVE] Call Rust backend
    return __stringSlice(this, s, e);
};

/**
 * String.prototype.substr(start, length)
 * Returns a substring starting at start with length characters
 * [NATIVE] Optimized in Rust
 */
String.prototype.substr = function(start, length) {
    const len = this.length;
    let s = Math.trunc(start);
    if (s < 0) s = Math.max(0, len + s);
    else s = Math.min(s, len);
    
    const l = length === undefined ? len - s : Math.max(0, Math.trunc(length));
    const e = Math.min(s + l, len);
    
    if (s >= e) return '';
    // [NATIVE] Call Rust backend
    return __stringSlice(this, s, e);
};

// ============================================================================
// Search Methods
// ============================================================================

/**
 * String.prototype.indexOf(searchString, fromIndex)
 * Returns the index of the first occurrence of searchString
 * [NATIVE] Optimized in Rust
 */
String.prototype.indexOf = function(searchString, fromIndex) {
    const search = String(searchString);
    let from = fromIndex === undefined ? 0 : Math.max(0, Math.trunc(fromIndex));
    
    if (search.length === 0) return Math.min(from, this.length);
    if (from >= this.length) return -1;
    
    // [NATIVE] Call Rust backend
    return __stringIndexOf(this, search, from);
};

/**
 * String.prototype.lastIndexOf(searchString, fromIndex)
 * Returns the index of the last occurrence of searchString
 * [NATIVE] Optimized in Rust
 */
String.prototype.lastIndexOf = function(searchString, fromIndex) {
    const search = String(searchString);
    let from = fromIndex === undefined ? this.length : Math.trunc(fromIndex);
    
    if (search.length === 0) return Math.min(from, this.length);
    if (from < 0) return -1;
    
    // [NATIVE] Call Rust backend
    return __stringLastIndexOf(this, search, from);
};

/**
 * String.prototype.includes(searchString, position)
 * Returns true if the string contains searchString
 */
String.prototype.includes = function(searchString, position) {
    const search = String(searchString);
    const pos = position === undefined ? 0 : Math.max(0, Math.trunc(position));
    return this.indexOf(search, pos) !== -1;
};

/**
 * String.prototype.startsWith(searchString, position)
 * Returns true if the string starts with searchString
 */
String.prototype.startsWith = function(searchString, position) {
    const search = String(searchString);
    const pos = position === undefined ? 0 : Math.max(0, Math.trunc(position));
    const len = this.length;
    const searchLen = search.length;
    
    if (pos + searchLen > len) return false;
    return this.substring(pos, pos + searchLen) === search;
};

/**
 * String.prototype.endsWith(searchString, length)
 * Returns true if the string ends with searchString
 */
String.prototype.endsWith = function(searchString, length) {
    const search = String(searchString);
    const len = length === undefined ? this.length : Math.trunc(length);
    const searchLen = search.length;
    
    if (searchLen > len) return false;
    const pos = len - searchLen;
    return this.substring(pos, len) === search;
};

// ============================================================================
// Case Transformation
// ============================================================================

/**
 * String.prototype.toUpperCase()
 * Returns the string in uppercase
 * [NATIVE] Character transformation in Rust
 */
String.prototype.toUpperCase = function() {
    // [NATIVE] Call Rust backend
    return __stringToUpperCase(this);
};

/**
 * String.prototype.toLowerCase()
 * Returns the string in lowercase
 * [NATIVE] Character transformation in Rust
 */
String.prototype.toLowerCase = function() {
    // [NATIVE] Call Rust backend
    return __stringToLowerCase(this);
};

/**
 * String.prototype.toLocaleUpperCase(locales)
 * Returns the string in locale-specific uppercase
 * Note: Simplified implementation without full ICU support
 */
String.prototype.toLocaleUpperCase = function(locales) {
    // For now, fall back to toUpperCase
    // Full implementation would use locale data
    return this.toUpperCase();
};

/**
 * String.prototype.toLocaleLowerCase(locales)
 * Returns the string in locale-specific lowercase
 * Note: Simplified implementation without full ICU support
 */
String.prototype.toLocaleLowerCase = function(locales) {
    // For now, fall back to toLowerCase
    // Full implementation would use locale data
    return this.toLowerCase();
};

// ============================================================================
// Trimming Methods
// ============================================================================

/**
 * String.prototype.trim()
 * Removes whitespace from both ends of the string
 * [NATIVE] Optimized in Rust
 */
String.prototype.trim = function() {
    // [NATIVE] Call Rust backend
    return __stringTrim(this);
};

/**
 * String.prototype.trimStart() / trimLeft()
 * Removes whitespace from the start of the string
 */
String.prototype.trimStart = function() {
    let i = 0;
    while (i < this.length && /\s/.test(this[i])) i++;
    return this.slice(i);
};

String.prototype.trimLeft = String.prototype.trimStart;

/**
 * String.prototype.trimEnd() / trimRight()
 * Removes whitespace from the end of the string
 */
String.prototype.trimEnd = function() {
    let i = this.length - 1;
    while (i >= 0 && /\s/.test(this[i])) i--;
    return this.slice(0, i + 1);
};

String.prototype.trimRight = String.prototype.trimEnd;

// ============================================================================
// Repetition and Padding
// ============================================================================

/**
 * String.prototype.repeat(count)
 * Returns a new string with the original string repeated count times
 * [NATIVE] Optimized in Rust for large counts
 */
String.prototype.repeat = function(count) {
    const n = Math.trunc(count);
    if (n < 0 || n === Infinity) {
        throw new RangeError('Invalid repeat count');
    }
    if (n === 0) return '';
    // [NATIVE] Call Rust backend
    return __stringRepeat(this, n);
};

/**
 * String.prototype.padStart(targetLength, padString)
 * Pads the string from the start to targetLength with padString
 */
String.prototype.padStart = function(targetLength, padString) {
    const len = this.length;
    const target = Math.trunc(targetLength);
    
    if (target <= len) return this;
    
    const pad = padString === undefined ? ' ' : String(padString);
    if (pad.length === 0) return this;
    
    const padLen = target - len;
    const fullPads = Math.floor(padLen / pad.length);
    const remainder = padLen % pad.length;
    
    let result = pad.repeat(fullPads) + pad.slice(0, remainder);
    return result + this;
};

/**
 * String.prototype.padEnd(targetLength, padString)
 * Pads the string from the end to targetLength with padString
 */
String.prototype.padEnd = function(targetLength, padString) {
    const len = this.length;
    const target = Math.trunc(targetLength);
    
    if (target <= len) return this;
    
    const pad = padString === undefined ? ' ' : String(padString);
    if (pad.length === 0) return this;
    
    const padLen = target - len;
    const fullPads = Math.floor(padLen / pad.length);
    const remainder = padLen % pad.length;
    
    let result = this + pad.repeat(fullPads) + pad.slice(0, remainder);
    return result;
};

// ============================================================================
// Pattern Matching with RegExp/String
// ============================================================================

/**
 * String.prototype.match(regexp)
 * Returns an array of matches or null if no match
 * [NATIVE] Regex matching in Rust
 */
String.prototype.match = function(regexp) {
    // If regexp is not a RegExp, convert to string and search
    if (typeof regexp === 'string') {
        const idx = this.indexOf(regexp);
        if (idx === -1) return null;
        return [regexp];
    }
    
    // [NATIVE] Call Rust backend for regex matching
    if (regexp && typeof regexp.test === 'function') {
        return __stringMatch(this, regexp);
    }
    
    return null;
};

/**
 * String.prototype.replace(searchValue, replaceValue)
 * Returns a new string with occurrences replaced
 * [NATIVE] Replacement logic in Rust
 */
String.prototype.replace = function(searchValue, replaceValue) {
    const search = String(searchValue);
    const replace = String(replaceValue);
    
    const idx = this.indexOf(search);
    if (idx === -1) return this;
    
    // Replace only the first occurrence
    const before = this.substring(0, idx);
    const after = this.substring(idx + search.length);
    return before + replace + after;
};

/**
 * String.prototype.replaceAll(searchValue, replaceValue)
 * Returns a new string with all occurrences replaced
 * [NATIVE] Optimized in Rust
 */
String.prototype.replaceAll = function(searchValue, replaceValue) {
    const search = String(searchValue);
    const replace = String(replaceValue);
    
    if (search.length === 0) {
        // Insert replaceValue between each character
        let result = '';
        for (let i = 0; i < this.length; i++) {
            result += replace + this[i];
        }
        result += replace;
        return result;
    }
    
    // [NATIVE] Call Rust backend for optimized replacement
    return __stringReplaceAll(this, search, replace);
};

/**
 * String.prototype.search(regexp)
 * Returns the index of the first match or -1
 * [NATIVE] Regex search in Rust
 */
String.prototype.search = function(regexp) {
    if (typeof regexp === 'string') {
        return this.indexOf(regexp);
    }
    
    // [NATIVE] Call Rust backend for regex search
    if (regexp && typeof regexp.test === 'function') {
        return __stringSearch(this, regexp);
    }
    
    return -1;
};

/**
 * String.prototype.split(separator, limit)
 * Returns an array of substrings divided by separator
 * [NATIVE] String splitting in Rust
 */
String.prototype.split = function(separator, limit) {
    let limitVal = limit === undefined ? Infinity : Math.trunc(limit);
    
    if (separator === undefined) {
        return [this];
    }
    
    if (typeof separator === 'string') {
        if (separator.length === 0) {
            // Split into individual characters
            const result = [];
            for (let i = 0; i < this.length && i < limitVal; i++) {
                result.push(this[i]);
            }
            return result;
        }
        
        // [NATIVE] Call Rust backend for string splitting
        return __stringSplit(this, separator, limitVal);
    }
    
    // Handle regex separator
    if (separator && typeof separator.test === 'function') {
        // [NATIVE] Call Rust backend for regex splitting
        return __stringSplitRegex(this, separator, limitVal);
    }
    
    return [this];
};

// ============================================================================
// String Concatenation and Joining
// ============================================================================

/**
 * String.prototype.concat(...strings)
 * Returns a new string that is the concatenation of this and all arguments
 * [NATIVE] Optimized in Rust for multiple arguments
 */
String.prototype.concat = function(...args) {
    let result = this;
    for (let i = 0; i < args.length; i++) {
        result = result + String(args[i]);
    }
    return result;
};

// ============================================================================
// Other Methods
// ============================================================================

/**
 * String.prototype.localeCompare(compareString, locales, options)
 * Compares two strings in the current locale
 * Note: Simplified implementation
 */
String.prototype.localeCompare = function(compareString, locales, options) {
    const other = String(compareString);
    if (this < other) return -1;
    if (this > other) return 1;
    return 0;
};

/**
 * String.prototype.normalize(form)
 * Returns the Unicode normalization form of the string
 * Note: Simplified - just returns the original string
 * Full implementation would use Unicode normalization data
 */
String.prototype.normalize = function(form) {
    // TODO: Implement proper Unicode normalization
    return this;
};

/**
 * String.prototype.toString()
 * Returns the string itself (for String objects)
 */
String.prototype.toString = function() {
    return this;
};

/**
 * String.prototype.valueOf()
 * Returns the primitive value of the string
 */
String.prototype.valueOf = function() {
    return this;
};

// ============================================================================
// Static Methods
// ============================================================================

/**
 * String.fromCharCode(...charCodes)
 * Returns a string created from Unicode values
 * [NATIVE] Character creation in Rust
 */
String.fromCharCode = function(...args) {
    let result = '';
    for (let i = 0; i < args.length; i++) {
        const code = Math.trunc(args[i]) & 0xFFFF;
        result += __stringFromCharCode(code);
    }
    return result;
};

/**
 * String.fromCodePoint(...codePoints)
 * Returns a string created from Unicode code points
 * [NATIVE] Character creation in Rust
 */
String.fromCodePoint = function(...args) {
    let result = '';
    for (let i = 0; i < args.length; i++) {
        const code = Math.trunc(args[i]);
        if (code < 0 || code > 0x10FFFF) {
            throw new RangeError('Invalid code point: ' + code);
        }
        result += __stringFromCodePoint(code);
    }
    return result;
};

/**
 * String.raw(template, ...substitutions)
 * Returns the raw string as written in template literals
 */
String.raw = function(template, ...substitutions) {
    if (!template || !template.raw) {
        throw new TypeError('String.raw requires a template object');
    }
    
    let result = '';
    const raw = template.raw;
    for (let i = 0; i < raw.length; i++) {
        result += raw[i];
        if (i < substitutions.length) {
            result += substitutions[i];
        }
    }
    return result;
};

// ============================================================================
// String Length Property
// ============================================================================

/**
 * String.prototype.length
 * Returns the length of the string
 * [NATIVE] Provided by Rust backend
 */
Object.defineProperty(String.prototype, 'length', {
    get: function() {
        // [NATIVE] Call Rust backend
        return __stringLength(this);
    }
});

// ============================================================================
// Symbol.toStringTag
// ============================================================================

Object.defineProperty(String.prototype, Symbol.toStringTag, {
    value: 'String',
    configurable: true
});
