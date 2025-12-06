// QUICK REFERENCE: WoofJS String Native Functions
// 
// All 20+ native functions that String.js calls into Rust
// Copy-paste this as a starting template for string_builtins.rs
//

use std::collections::HashMap;

pub struct StringBuiltins;

impl StringBuiltins {
    /// Get character at index (UTF-16 aware)
    pub fn char_at(s: &str, index: usize) -> String {
        s.chars().nth(index)
            .map(|c| c.to_string())
            .unwrap_or_default()
    }

    /// Get character code (Unicode value) at index
    pub fn char_code_at(s: &str, index: usize) -> f64 {
        s.chars().nth(index)
            .map(|c| c as u32 as f64)
            .unwrap_or(f64::NAN)
    }

    /// Get code point at index
    pub fn code_point_at(s: &str, index: usize) -> Option<u32> {
        s.chars().nth(index).map(|c| c as u32)
    }

    /// Slice string from start to end
    pub fn slice(s: &str, start: usize, end: usize) -> String {
        s.chars()
            .skip(start)
            .take(end - start)
            .collect()
    }

    /// Find first occurrence of substring
    pub fn index_of(haystack: &str, needle: &str, from_index: usize) -> i32 {
        if from_index >= haystack.len() {
            return -1;
        }
        haystack[from_index..]
            .find(needle)
            .map(|pos| (from_index + pos) as i32)
            .unwrap_or(-1)
    }

    /// Find last occurrence of substring
    pub fn last_index_of(haystack: &str, needle: &str, from_index: usize) -> i32 {
        haystack[..=from_index.min(haystack.len() - 1)]
            .rfind(needle)
            .map(|pos| pos as i32)
            .unwrap_or(-1)
    }

    /// Convert to uppercase
    pub fn to_upper_case(s: &str) -> String {
        s.to_uppercase()
    }

    /// Convert to lowercase
    pub fn to_lower_case(s: &str) -> String {
        s.to_lowercase()
    }

    /// Trim whitespace from both ends
    pub fn trim(s: &str) -> String {
        s.trim().to_string()
    }

    /// Repeat string n times
    pub fn repeat(s: &str, count: usize) -> String {
        s.repeat(count)
    }

    /// Split string by separator
    pub fn split(s: &str, separator: &str, limit: usize) -> Vec<String> {
        if separator.is_empty() {
            // Split into individual characters
            s.chars()
                .take(limit)
                .map(|c| c.to_string())
                .collect()
        } else {
            s.split(separator)
                .take(limit)
                .map(|part| part.to_string())
                .collect()
        }
    }

    /// Replace all occurrences
    pub fn replace_all(s: &str, search: &str, replace: &str) -> String {
        s.replace(search, replace)
    }

    /// Create character from UTF-16 code unit
    pub fn from_char_code(code: u16) -> String {
        (code as u32 as char).to_string()
    }

    /// Create character from code point (0-0x10FFFF)
    pub fn from_code_point(code: u32) -> Result<String, String> {
        char::from_u32(code)
            .map(|c| c.to_string())
            .ok_or_else(|| "Invalid code point".to_string())
    }

    /// Get length in UTF-16 code units
    pub fn length(s: &str) -> usize {
        let mut len = 0;
        for ch in s.chars() {
            // Characters beyond BMP need 2 UTF-16 code units (surrogate pair)
            len += if ch as u32 > 0xFFFF { 2 } else { 1 };
        }
        len
    }

    /// Regex-aware match (requires JsRegExp)
    pub fn match_regex(s: &str, pattern: &str, flags: &str) -> Option<Vec<String>> {
        // TODO: Implement with regex crate
        // This is called via __stringMatch in String.js
        None
    }

    /// Regex-aware search (requires JsRegExp)
    pub fn search_regex(s: &str, pattern: &str, flags: &str) -> i32 {
        // TODO: Implement with regex crate
        // This is called via __stringSearch in String.js
        -1
    }

    /// Regex-aware split (requires JsRegExp)
    pub fn split_regex(s: &str, pattern: &str, flags: &str, limit: usize) -> Vec<String> {
        // TODO: Implement with regex crate
        // This is called via __stringSplitRegex in String.js
        vec![s.to_string()]
    }
}

// ============================================================================
// EXAMPLE: How to register these in runtime.rs
// ============================================================================

/*
In runtime.rs, add to the init function:

pub fn init_global_context(context: &mut JsContext) {
    // String methods
    let builtins = StringBuiltins;
    
    // Character access
    context.register_builtin("__stringCharAt", |args| {
        if args.len() < 2 {
            return JsValue::Undefined;
        }
        let s = args[0].to_string();
        let index = args[1].to_number() as usize;
        JsValue::String(StringBuiltins::char_at(&s, index))
    });
    
    context.register_builtin("__stringCharCodeAt", |args| {
        if args.len() < 2 {
            return JsValue::Number(f64::NAN);
        }
        let s = args[0].to_string();
        let index = args[1].to_number() as usize;
        JsValue::Number(StringBuiltins::char_code_at(&s, index))
    });
    
    // ... register all other methods similarly
}
*/

// ============================================================================
// TESTING HELPERS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_char_at() {
        assert_eq!(StringBuiltins::char_at("hello", 0), "h");
        assert_eq!(StringBuiltins::char_at("hello", 4), "o");
        assert_eq!(StringBuiltins::char_at("hello", 10), "");
    }

    #[test]
    fn test_index_of() {
        assert_eq!(StringBuiltins::index_of("hello", "l", 0), 2);
        assert_eq!(StringBuiltins::index_of("hello", "l", 3), 3);
        assert_eq!(StringBuiltins::index_of("hello", "x", 0), -1);
    }

    #[test]
    fn test_slice() {
        assert_eq!(StringBuiltins::slice("hello", 1, 4), "ell");
        assert_eq!(StringBuiltins::slice("hello", 0, 5), "hello");
        assert_eq!(StringBuiltins::slice("hello", 3, 3), "");
    }

    #[test]
    fn test_case() {
        assert_eq!(StringBuiltins::to_upper_case("Hello"), "HELLO");
        assert_eq!(StringBuiltins::to_lower_case("Hello"), "hello");
    }

    #[test]
    fn test_repeat() {
        assert_eq!(StringBuiltins::repeat("ab", 3), "ababab");
        assert_eq!(StringBuiltins::repeat("x", 0), "");
    }

    #[test]
    fn test_split() {
        assert_eq!(
            StringBuiltins::split("a,b,c", ",", 10),
            vec!["a", "b", "c"]
        );
    }

    #[test]
    fn test_length() {
        assert_eq!(StringBuiltins::length("hello"), 5);
        // Note: length counts UTF-16 code units, not characters
    }
}
