// Execution engine for WoofJS
use std::rc::Rc;
use crate::ast::{Expr, Statement, BinOp};
use crate::value::{JsValue, JsObject, JsFunction};
use crate::context::{JsContext, ContextManager};

pub struct Runtime {
    /// Context manager for handling multiple execution contexts
    pub context_manager: ContextManager,
    /// Current active context
    current_context: Rc<JsContext>,
}

impl Runtime {
    /// Create a new runtime with a global context
    pub fn new() -> Self {
        let context_manager = ContextManager::new();
        let current_context = context_manager.global();
        
        Self {
            context_manager,
            current_context,
        }
    }

    /// Create a new runtime with a custom context manager
    pub fn with_context_manager(context_manager: ContextManager) -> Self {
        let current_context = context_manager.global();
        Self {
            context_manager,
            current_context,
        }
    }

    /// Get the current active context
    pub fn current_context(&self) -> Rc<JsContext> {
        self.current_context.clone()
    }

    /// Switch to a different context
    pub fn switch_context(&mut self, context_id: &str) -> Result<(), String> {
        let context = self.context_manager.get_context(context_id)
            .ok_or_else(|| format!("Context '{}' not found", context_id))?;
        self.current_context = context;
        Ok(())
    }

    /// Create a new isolated context
    pub fn create_context(&mut self, id: String) -> Rc<JsContext> {
        self.context_manager.create_context(id)
    }

    /// Evaluate an expression in the current context
    pub fn eval_expr(&self, expr: &Expr, ctx: Option<Rc<JsContext>>) -> Result<JsValue, String> {
        let ctx = ctx.unwrap_or_else(|| self.current_context.clone());
        self._eval_expr(expr, ctx)
    }

    fn _eval_expr(&self, expr: &Expr, ctx: Rc<JsContext>) -> Result<JsValue, String> {
        match expr {
            Expr::Number(n) => Ok(JsValue::Number(*n)),
            Expr::String(s) => Ok(JsValue::String(s.clone())),
            Expr::Boolean(b) => Ok(JsValue::Boolean(*b)),
            Expr::Undefined => Ok(JsValue::Undefined),
            Expr::Null => Ok(JsValue::Null),
            Expr::Identifier(name) => {
                ctx.get(name)
                    .ok_or_else(|| format!("ReferenceError: '{}' is not defined", name))
            }
            Expr::BinaryOp { left, op, right } => {
                let l_val = self._eval_expr(left, ctx.clone())?;
                let r_val = self._eval_expr(right, ctx.clone())?;
                self.eval_binop(op, &l_val, &r_val)
            }
            Expr::Call { callee, args } => {
                let callee_val = self._eval_expr(callee, ctx.clone())?;
                let arg_vals: Result<Vec<JsValue>, String> = args.iter()
                    .map(|arg| self._eval_expr(arg, ctx.clone()))
                    .collect();
                self.call_function(callee_val, arg_vals?, ctx)
            }
            Expr::Property { object, property } => {
                let obj_val = self._eval_expr(object, ctx.clone())?;
                self.get_property(&obj_val, property)
            }
            Expr::Object(props) => {
                let mut js_obj = JsObject::new();
                for (key, expr) in props {
                    let value = self._eval_expr(expr, ctx.clone())?;
                    js_obj.set(key.clone(), value);
                }
                Ok(JsValue::Object(Rc::new(js_obj)))
            }
            Expr::Array(elements) => {
                let values: Result<Vec<JsValue>, String> = elements.iter()
                    .map(|e| self._eval_expr(e, ctx.clone()))
                    .collect();
                Ok(JsValue::Array(values?))
            }
        }
    }

    fn eval_binop(&self, op: &BinOp, left: &JsValue, right: &JsValue) -> Result<JsValue, String> {
        match op {
            BinOp::Add => {
                // String concatenation or numeric addition
                if let (JsValue::String(l), _) | (_, JsValue::String(r)) = (left, right) {
                    Ok(JsValue::String(format!("{}{}", left.to_string(), right.to_string())))
                } else {
                    Ok(JsValue::Number(left.to_number() + right.to_number()))
                }
            }
            BinOp::Sub => Ok(JsValue::Number(left.to_number() - right.to_number())),
            BinOp::Mul => Ok(JsValue::Number(left.to_number() * right.to_number())),
            BinOp::Div => {
                let r = right.to_number();
                if r == 0.0 {
                    Err("Cannot divide by 0 - it does not make sense in math".to_string())
                } else {
                    Ok(JsValue::Number(left.to_number() / r))
                }
            }
            BinOp::Mod => Ok(JsValue::Number(left.to_number() % right.to_number())),
            BinOp::Eq => Ok(JsValue::Boolean(self.loose_eq(left, right))),
            BinOp::Neq => Ok(JsValue::Boolean(!self.loose_eq(left, right))),
            BinOp::StrictEq => Ok(JsValue::Boolean(self.strict_eq(left, right))),
            BinOp::StrictNeq => Ok(JsValue::Boolean(!self.strict_eq(left, right))),
            BinOp::Lt => Ok(JsValue::Boolean(left.to_number() < right.to_number())),
            BinOp::Gt => Ok(JsValue::Boolean(left.to_number() > right.to_number())),
            BinOp::Lte => Ok(JsValue::Boolean(left.to_number() <= right.to_number())),
            BinOp::Gte => Ok(JsValue::Boolean(left.to_number() >= right.to_number())),
        }
    }

    fn loose_eq(&self, left: &JsValue, right: &JsValue) -> bool {
        match (left, right) {
            (JsValue::Null, JsValue::Undefined) | (JsValue::Undefined, JsValue::Null) => true,
            (JsValue::Number(l), JsValue::Number(r)) => l == r,
            (JsValue::String(l), JsValue::String(r)) => l == r,
            (JsValue::Boolean(l), JsValue::Boolean(r)) => l == r,
            _ => false,
        }
    }

    fn strict_eq(&self, left: &JsValue, right: &JsValue) -> bool {
        match (left, right) {
            (JsValue::Number(l), JsValue::Number(r)) => l == r,
            (JsValue::String(l), JsValue::String(r)) => l == r,
            (JsValue::Boolean(l), JsValue::Boolean(r)) => l == r,
            (JsValue::Null, JsValue::Null) => true,
            (JsValue::Undefined, JsValue::Undefined) => true,
            _ => false,
        }
    }

    fn get_property(&self, obj: &JsValue, prop: &str) -> Result<JsValue, String> {
        match obj {
            JsValue::Object(o) => {
                o.get(prop)
                    .ok_or_else(|| format!("Property '{}' not found", prop))
            }
            _ => Err(format!("Cannot read property '{}' of {}", prop, obj.to_string())),
        }
    }

    fn call_function(&self, callee: JsValue, args: Vec<JsValue>, ctx: Rc<JsContext>) -> Result<JsValue, String> {
        match callee {
            JsValue::Function(f) => {
                // Create new context for function call (child of closure context)
                let call_ctx = Rc::new(JsContext::new_with_parent(
                    f.closure.clone(),
                    Some(format!("fn_{}", f.name))
                ));
                
                // Bind parameters
                for (param, arg) in f.params.iter().zip(args.iter()) {
                    call_ctx.set(param.clone(), arg.clone());
                }
                
                // Execute function body
                let mut result = JsValue::Undefined;
                for stmt in &f.body {
                    result = self._eval_stmt(stmt, call_ctx.clone())?;
                }
                Ok(result)
            }
            _ => Err(format!("{} is not a function", callee.to_string())),
        }
    }

    /// Evaluate a statement in the current context
    pub fn eval_stmt(&self, stmt: &Statement, ctx: Option<Rc<JsContext>>) -> Result<JsValue, String> {
        let ctx = ctx.unwrap_or_else(|| self.current_context.clone());
        self._eval_stmt(stmt, ctx)
    }

    fn _eval_stmt(&self, stmt: &Statement, ctx: Rc<JsContext>) -> Result<JsValue, String> {
        match stmt {
            Statement::Expr(expr) => self._eval_expr(expr, ctx),
            Statement::VarDecl { name, value, is_const } => {
                let val = if let Some(expr) = value {
                    self._eval_expr(expr, ctx.clone())?
                } else {
                    JsValue::Undefined
                };
                ctx.declare(name.clone(), val.clone(), *is_const)?;
                Ok(val)
            }
            Statement::Block(stmts) => {
                // Create a new block scope
                let block_ctx = Rc::new(JsContext::new_with_parent(
                    ctx.clone(),
                    Some(format!("block_{}", std::process::id()))
                ));
                let mut result = JsValue::Undefined;
                for stmt in stmts {
                    result = self._eval_stmt(stmt, block_ctx.clone())?;
                }
                Ok(result)
            }
            Statement::If { condition, then, else_ } => {
                let cond_val = self._eval_expr(condition, ctx.clone())?;
                if cond_val.to_boolean() {
                    self._eval_stmt(then, ctx)
                } else if let Some(else_stmt) = else_ {
                    self._eval_stmt(else_stmt, ctx)
                } else {
                    Ok(JsValue::Undefined)
                }
            }
            Statement::While { condition, body } => {
                loop {
                    let cond_val = self._eval_expr(condition, ctx.clone())?;
                    if !cond_val.to_boolean() {
                        break;
                    }
                    self._eval_stmt(body, ctx.clone())?;
                }
                Ok(JsValue::Undefined)
            }
            Statement::Return(expr) => {
                let val = if let Some(e) = expr {
                    self._eval_expr(e, ctx)?
                } else {
                    JsValue::Undefined
                };
                Ok(val)
            }
            Statement::Function { name, params, body } => {
                let func = JsFunction {
                    name: name.clone(),
                    params: params.clone(),
                    body: body.clone(),
                    closure: ctx.clone(),
                };
                let func_val = JsValue::Function(Rc::new(func));
                // Store function in context
                ctx.set(name.clone(), func_val.clone());
                Ok(func_val)
            }
        }
    }
}

