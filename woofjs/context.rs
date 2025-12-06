// JavaScript Context system for WoofJS
// A Context represents an isolated execution environment with its own variable scope

use std::collections::HashMap;
use std::rc::Rc;
use std::cell::RefCell;
use crate::value::JsValue;

/// A JavaScript execution context - represents a scope for variable storage
#[derive(Clone)]
pub struct JsContext {
    /// Variables stored in this context
    variables: Rc<RefCell<HashMap<String, JsValue>>>,
    /// Parent context (for scope chaining)
    parent: Option<Rc<JsContext>>,
    /// Context identifier (for debugging)
    id: String,
}

impl JsContext {
    /// Create a new root context (no parent)
    pub fn new(id: Option<String>) -> Self {
        Self {
            variables: Rc::new(RefCell::new(HashMap::new())),
            parent: None,
            id: id.unwrap_or_else(|| format!("context_{}", std::process::id())),
        }
    }

    /// Create a new context with a parent (for function scopes, blocks, etc.)
    pub fn new_with_parent(parent: Rc<JsContext>, id: Option<String>) -> Self {
        Self {
            variables: Rc::new(RefCell::new(HashMap::new())),
            parent: Some(parent),
            id: id.unwrap_or_else(|| format!("child_{}", std::process::id())),
        }
    }

    /// Get a variable from this context or parent chain
    pub fn get(&self, name: &str) -> Option<JsValue> {
        // Check current context first
        if let Some(val) = self.variables.borrow().get(name) {
            return Some(val.clone());
        }
        
        // Walk up parent chain
        self.parent.as_ref()
            .and_then(|p| p.get(name))
    }

    /// Set a variable in this context (doesn't check parent - direct assignment)
    pub fn set(&self, name: String, value: JsValue) {
        self.variables.borrow_mut().insert(name, value);
    }

    /// Declare a new variable in this context (checks for duplicates)
    pub fn declare(&self, name: String, value: JsValue, is_const: bool) -> Result<(), String> {
        let mut vars = self.variables.borrow_mut();
        
        // Check if already declared in this scope
        if vars.contains_key(&name) {
            return Err(format!("Variable '{}' already declared in this scope", name));
        }
        
        vars.insert(name, value);
        Ok(())
    }

    /// Update a variable (searches parent chain if not in current scope)
    pub fn update(&self, name: &str, value: JsValue) -> Result<(), String> {
        // Check if exists in current scope
        if self.variables.borrow().contains_key(name) {
            self.variables.borrow_mut().insert(name.to_string(), value);
            return Ok(());
        }
        
        // Try parent
        if let Some(parent) = &self.parent {
            return parent.update(name, value);
        }
        
        Err(format!("ReferenceError: '{}' is not defined", name))
    }

    /// Check if a variable exists in this context or parent chain
    pub fn has(&self, name: &str) -> bool {
        self.variables.borrow().contains_key(name)
            || self.parent.as_ref().map(|p| p.has(name)).unwrap_or(false)
    }

    /// Get all variable names in this context (not including parents)
    pub fn local_names(&self) -> Vec<String> {
        self.variables.borrow().keys().cloned().collect()
    }

    /// Get context ID
    pub fn id(&self) -> &str {
        &self.id
    }

    /// Create a snapshot of all variables (for debugging/inspection)
    pub fn snapshot(&self) -> HashMap<String, JsValue> {
        self.variables.borrow().clone()
    }

    /// Initialize global built-ins
    pub fn init_globals(&self) {
        self.set("undefined".to_string(), JsValue::Undefined);
        self.set("null".to_string(), JsValue::Null);
        self.set("NaN".to_string(), JsValue::Number(f64::NAN));
        self.set("Infinity".to_string(), JsValue::Number(f64::INFINITY));
    }
}

/// Context manager for handling multiple isolated execution contexts
pub struct ContextManager {
    /// Default/global context
    global: Rc<JsContext>,
    /// Active contexts (for multi-context execution)
    contexts: HashMap<String, Rc<JsContext>>,
}

impl ContextManager {
    /// Create a new context manager with a global context
    pub fn new() -> Self {
        let global = Rc::new(JsContext::new(Some("global".to_string())));
        global.init_globals();
        
        let mut manager = Self {
            global: global.clone(),
            contexts: HashMap::new(),
        };
        
        manager.contexts.insert("global".to_string(), global);
        manager
    }

    /// Get the global context
    pub fn global(&self) -> Rc<JsContext> {
        self.global.clone()
    }

    /// Create a new isolated context
    pub fn create_context(&mut self, id: String) -> Rc<JsContext> {
        let context = Rc::new(JsContext::new_with_parent(
            self.global.clone(),
            Some(id.clone())
        ));
        self.contexts.insert(id, context.clone());
        context
    }

    /// Get a context by ID
    pub fn get_context(&self, id: &str) -> Option<Rc<JsContext>> {
        self.contexts.get(id).cloned()
    }

    /// Remove a context
    pub fn remove_context(&mut self, id: &str) -> bool {
        if id == "global" {
            return false; // Can't remove global
        }
        self.contexts.remove(id).is_some()
    }

    /// List all context IDs
    pub fn list_contexts(&self) -> Vec<String> {
        self.contexts.keys().cloned().collect()
    }
}

impl Default for ContextManager {
    fn default() -> Self {
        Self::new()
    }
}

