/**
 * parseFloat() - Parse a string and return a floating point number
 * 
 * According to MDN: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/parseFloat
 * 
 * - Converts the argument to a string first
 * - Parses the string from left to right
 * - Stops at the first character that cannot be converted to a number
 * - Returns NaN if the first character cannot be converted
 * - Ignores leading whitespace
 */
function parseFloat(string) {
    // Convert to string
    const str = String(string);
    
    // Trim leading whitespace
    const trimmed = str.trimStart();
    
    // Empty string returns NaN
    if (trimmed.length === 0) {
        return NaN;
    }
    
    // Try to use host implementation if available
    if (typeof __WoofJS__ !== 'undefined' && __WoofJS__.getFloatFromString) {
        return __WoofJS__.getFloatFromString(trimmed);
    }
    
    // Fallback implementation
    // Match: optional sign, digits, optional decimal point, optional digits, optional exponent
    const floatRegex = /^[+\-]?(\d+\.?\d*|\.\d+)([eE][+\-]?\d+)?/;
    const match = trimmed.match(floatRegex);
    
    if (match) {
        const num = Number(match[0]);
        return isNaN(num) ? NaN : num;
    }
    
    // If first character is not a valid start, return NaN
    return NaN;
}