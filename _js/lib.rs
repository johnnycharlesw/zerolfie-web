mod token;
mod lexer;
larlpop_mod!(pub parser);
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod ast;

use crate::ast::{Expr, BinOp};


/*
fn main() {
    let input = "3 + 4 * (2 - 1)";
    let lexer = lexer::LexerWrapper {
        inner: token::Token::lexer(input),
    };

    let parser = parser::ExprParser::new();
    match parser.parse(lexer) {
        Ok(result) => println!("Parsed result: {}", result),
        Err(e) => println!("Error parsing: {:?}", e),
    }
}
*/

impl Expr {
    pub fn eval(&self) -> Result<i64, String> {
        match self {
            Expr::Number(n) => Ok(*n),
            Expr::Identifier(_) => Err("Identifiers not supported in eval".to_string()),
            Expr::BinaryOp { left, op, right } => {
                let l_val = left.eval()?;
                let r_val = right.eval()?;
                match op {
                    BinOp::Add => Ok(l_val + r_val),
                    BinOp::Sub => Ok(l_val - r_val),
                    BinOp::Mul => Ok(l_val * r_val),
                    BinOp::Div => {
                        if r_val == 0 {
                            Err("Cannot divide by zero".to_string())
                        }else{
                            Ok(l_val / r_val)
                        }
                    },
                }
            }
        }
    }
}

fn eval(input: &str) {
    let lexer = lexer::LexerWrapper {
        inner: token::Token::lexer(input),
    };

    let parser = parser::ExprParser::new();
    match parser.parse(lexer) {
        Ok(result) => println!("Parsed result: {}", result),
        Err(e) => println!("Error parsing: {:?}", e),
    }
}

#[pymodule]
fn woofjs(_py: Python, m: &PyModule) -> PyResult<i64> {
    m.add_function(wrap_pyfunction(eval, m));
}