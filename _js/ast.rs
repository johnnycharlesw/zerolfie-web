#[derive(Debug)]
pub enum Expr {
    Number(i64),
    Identifier(String),
    BinaryOp {
        left: Box<Expr>,
        op: BinOp,
        right: Box<Expr>,
    },
}

#[derive(Debug)]
pub enum BinOp {
    Add,
    Sub,
    Mul,
    Div,
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

pub enum StatementEndingKind {
    Semicolon,
    Newline,
}

pub struct StatementEnding {
    pub kind: StatementEndingKind,
    pub name: String,
}

pub struct NumberToken {
    pub kind: String,
    pub value: i64,
    pub name: String,
}