// JavaScript value system for WoofJS
use std::collections::HashMap;
use std::rc::Rc;
use regex::Regex;

#[derive(Debug, Clone)]
pub enum JsValue {
    Number(f64),
    String(String),
    Boolean(bool),
    Undefined,
    Null,
    Object(Rc<JsObject>),
    Function(Rc<JsFunction>),
    Array(Vec<JsValue>),
    RegExp(Rc<JsRegExp>),
}

#[derive(Debug, Clone)]
pub struct JsObject {
    pub properties: HashMap<String, JsValue>,
    pub prototype: Option<Rc<JsObject>>,
}

impl JsObject {
    pub fn new() -> Self {
        Self {
            properties: HashMap::new(),
            prototype: None,
        }
    }

    pub fn get(&self, key: &str) -> Option<JsValue> {
        self.properties.get(key).cloned()
            .or_else(|| {
                self.prototype.as_ref()
                    .and_then(|p| p.get(key))
            })
    }

    pub fn set(&mut self, key: String, value: JsValue) {
        self.properties.insert(key, value);
    }
}

#[derive(Debug, Clone)]
pub struct JsFunction {
    pub name: String,
    pub params: Vec<String>,
    pub body: Vec<crate::ast::Statement>,
    pub closure: Rc<crate::context::JsContext>,
}

#[derive(Debug, Clone)]
pub struct JsRegExp {
    pub pattern: String,
    pub flags: String,
    pub regex: Regex,
    pub global: bool,
    pub case_insensitive: bool,
    pub multiline: bool,
    pub last_index: usize,
}

impl JsRegExp {
    pub fn new(pattern: &str, flags: &str) -> Result<Self, String> {
        let mut regex_flags = String::new();
        let mut global = false;
        let mut case_insensitive = false;
        let mut multiline = false;

        for c in flags.chars() {
            match c {
                'g' => global = true,
                'i' => {
                    case_insensitive = true;
                    regex_flags.push('i');
                }
                'm' => {
                    multiline = true;
                    regex_flags.push('m');
                }
                's' => regex_flags.push('s'),
                'u' | 'y' | 'd' => {
                    // unicode, sticky, indices flags - not fully supported yet
                }
                _ => return Err(format!("Unknown regex flag: {}", c)),
            }
        }

        let regex = if regex_flags.is_empty() {
            Regex::new(pattern)
        } else {
            Regex::new(&format!("(?{}:{}", regex_flags, pattern))
        }
        .map_err(|e| format!("Invalid regex pattern: {}", e))?;

        Ok(JsRegExp {
            pattern: pattern.to_string(),
            flags: flags.to_string(),
            regex,
            global,
            case_insensitive,
            multiline,
            last_index: 0,
        })
    }

    pub fn test(&self, input: &str) -> bool {
        self.regex.is_match(input)
    }

    pub fn exec(&self, input: &str) -> Option<Vec<String>> {
        self.regex
            .captures(input)
            .map(|caps| caps.iter().map(|m| m.unwrap().as_str().to_string()).collect())
    }
}

impl JsValue {
    pub fn to_string(&self) -> String {
        match self {
            JsValue::Number(n) => n.to_string(),
            JsValue::String(s) => s.clone(),
            JsValue::Boolean(b) => b.to_string(),
            JsValue::Undefined => "undefined".to_string(),
            JsValue::Null => "null".to_string(),
            JsValue::Object(_) => "[object Object]".to_string(),
            JsValue::Function(_) => "[Function]".to_string(),
            JsValue::Array(arr) => {
                let items: Vec<String> = arr.iter().map(|v| v.to_string()).collect();
                format!("[{}]", items.join(", "))
            }
            JsValue::RegExp(re) => format!("/{}/{}", re.pattern, re.flags),
        }
    }

    pub fn to_number(&self) -> f64 {
        match self {
            JsValue::Number(n) => *n,
            JsValue::String(s) => s.parse().unwrap_or(f64::NAN),
            JsValue::Boolean(true) => 1.0,
            JsValue::Boolean(false) => 0.0,
            JsValue::Null => 0.0,
            JsValue::Undefined => f64::NAN,
            _ => f64::NAN,
        }
    }

    pub fn to_boolean(&self) -> bool {
        match self {
            JsValue::Boolean(b) => *b,
            JsValue::Number(n) => *n != 0.0 && !n.is_nan(),
            JsValue::String(s) => !s.is_empty(),
            JsValue::Null => false,
            JsValue::Undefined => false,
            JsValue::Object(_) => true,
            JsValue::Function(_) => true,
            JsValue::Array(arr) => !arr.is_empty(),
            JsValue::RegExp(_) => true,
        }
    }
}

