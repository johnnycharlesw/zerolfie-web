/**
 * parseInt() - Parse a string and return an integer
 * 
 * According to MDN: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/parseInt
 * 
 * - Converts the argument to a string first
 * - Parses the string from left to right
 * - Stops at the first character that cannot be converted to a number
 * - Returns NaN if the first character cannot be converted
 * - Ignores leading whitespace
 * - Radix: 2-36, or 0 (auto-detect from prefix: 0x=16, 0o=8, 0b=2, else 10)
 */
function parseInt(string, radix) {
    // Convert to string
    const str = String(string);
    
    // Trim leading whitespace
    const trimmed = str.trimStart();
    
    // Empty string returns NaN
    if (trimmed.length === 0) {
        return NaN;
    }
    
    // Handle radix
    let actualRadix = radix;
    
    // If radix is undefined, 0, or not provided, auto-detect
    if (actualRadix === undefined || actualRadix === 0) {
        // Check for hex prefix (0x or 0X)
        if (trimmed.length >= 2 && trimmed[0] === '0' && (trimmed[1] === 'x' || trimmed[1] === 'X')) {
            actualRadix = 16;
        }
        // Check for octal prefix (0o or 0O) - ES6+
        else if (trimmed.length >= 2 && trimmed[0] === '0' && (trimmed[1] === 'o' || trimmed[1] === 'O')) {
            actualRadix = 8;
        }
        // Check for binary prefix (0b or 0B) - ES6+
        else if (trimmed.length >= 2 && trimmed[0] === '0' && (trimmed[1] === 'b' || trimmed[1] === 'B')) {
            actualRadix = 2;
        }
        // Legacy octal (leading 0) - only in non-strict mode, but we'll default to 10 for safety
        else if (trimmed[0] === '0' && trimmed.length > 1) {
            actualRadix = 10; // Modern behavior: treat as decimal
        }
        else {
            actualRadix = 10;
        }
    }
    
    // Validate radix (must be 2-36)
    if (actualRadix < 2 || actualRadix > 36) {
        return NaN;
    }
    
    // Try to use host implementation if available
    if (typeof __WoofJS__ !== 'undefined' && __WoofJS__.getIntFromString) {
        return __WoofJS__.getIntFromString(trimmed, actualRadix);
    }
    
    // Fallback implementation
    // Skip prefix if present
    let startIndex = 0;
    if (actualRadix === 16 && trimmed.length >= 2 && trimmed[0] === '0' && (trimmed[1] === 'x' || trimmed[1] === 'X')) {
        startIndex = 2;
    } else if (actualRadix === 8 && trimmed.length >= 2 && trimmed[0] === '0' && (trimmed[1] === 'o' || trimmed[1] === 'O')) {
        startIndex = 2;
    } else if (actualRadix === 2 && trimmed.length >= 2 && trimmed[0] === '0' && (trimmed[1] === 'b' || trimmed[1] === 'B')) {
        startIndex = 2;
    }
    
    // Build valid digit set for radix
    const digits = '0123456789abcdefghijklmnopqrstuvwxyz'.substring(0, actualRadix);
    const digitsUpper = digits.toUpperCase();
    
    // Parse digits
    let result = 0;
    let foundDigit = false;
    
    for (let i = startIndex; i < trimmed.length; i++) {
        const char = trimmed[i];
        const digitIndex = digits.indexOf(char) !== -1 ? digits.indexOf(char) : digitsUpper.indexOf(char);
        
        if (digitIndex === -1) {
            // Invalid character - stop parsing
            break;
        }
        
        foundDigit = true;
        result = result * actualRadix + digitIndex;
    }
    
    // If no valid digits found, return NaN
    if (!foundDigit) {
        return NaN;
    }
    
    // Handle sign
    if (startIndex === 0 && trimmed[0] === '-') {
        return -result;
    }
    if (startIndex === 0 && trimmed[0] === '+') {
        return result;
    }
    
    return result;
}