use std::collections::HashMap;

#[derive(Debug, Clone)]
pub enum Expr {
    Number(f64),
    String(String),
    Boolean(bool),
    Identifier(String),
    BinaryOp {
        left: Box<Expr>,
        op: BinOp,
        right: Box<Expr>,
    },
    Call {
        callee: Box<Expr>,
        args: Vec<Expr>,
    },
    Property {
        object: Box<Expr>,
        property: String,
    },
    Object(HashMap<String, Expr>),
    Array(Vec<Expr>),
    Undefined,
    Null,
}

#[derive(Debug, Clone)]
pub enum BinOp {
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    Eq,      // ==
    Neq,     // !=
    StrictEq, // ===
    StrictNeq, // !==
    Lt,
    Gt,
    Lte,
    Gte,
}

#[derive(Debug, Clone)]
pub enum Statement {
    Expr(Expr),
    VarDecl {
        name: String,
        value: Option<Expr>,
        is_const: bool,
    },
    Block(Vec<Statement>),
    If {
        condition: Expr,
        then: Box<Statement>,
        else_: Option<Box<Statement>>,
    },
    While {
        condition: Expr,
        body: Box<Statement>,
    },
    Return(Option<Expr>),
    Function {
        name: String,
        params: Vec<String>,
        body: Vec<Statement>,
    },
}

pub enum VariableDefinitionKind {
    Static,
    NonStatic
}

pub struct VariableDefinition {
    pub name: String,
    pub kind: VariableDefinitionKind,
    pub value: Option<Expr>,
}
