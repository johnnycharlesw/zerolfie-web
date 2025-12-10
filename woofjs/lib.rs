mod token;
mod lexer;
mod ast;
mod host;
mod value;
mod context;
mod runtime;
mod parser_helpers;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use crate::ast::{BinOp, Expr};
use crate::host::WoofJsApi;
use crate::runtime::Runtime;

// LALRPOP-generated parser module
lalrpop_mod!(pub parser);

// Legacy eval for backward compatibility - now uses Runtime
impl Expr {
    pub fn eval(&self) -> Result<i64, String> {
        let runtime = Runtime::new();
        eval_in_context(runtime);
    }

    pub fn eval_in_context(&self, runtime) {
        match runtime.eval_expr(self, None) {
            Ok(val) => Ok(val.to_number() as i64),
            Err(e) => Err(e),
        }
    }
}


#[pyfunction]
fn eval_expr(input: &str) -> PyResult<i64> {
    let lexer = lexer::LexerWrapper {
        inner: token::Token::lexer(input),
    };

    let parser = parser::ExprParser::new();
    match parser.parse(lexer) {
        Ok(result) => Ok(result.eval()?),
        Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
            "Parse error: {:?}",
            e
        ))),
    }
}

#[pymodule]
fn woofjs(py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<WoofJsApi>()?;
    m.add_class::<host::WoofJsIoStream>()?;
    m.add_class::<Runtime>();
    m.add_function(wrap_pyfunction!(eval_expr, m)?)?;
    Ok(())
}