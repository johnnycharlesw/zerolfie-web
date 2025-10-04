// src/token.rs
// A work-in-progress tokenizer for JavaScript using the logos crate
use logos::Logos;

#[derive(Logos, Debug, PartialEq, Clone)]
pub enum Token {
    // General syntax
    #[regex(r"[ \t\f]+", logos::skip)]  // skip whitespace
    Whitespace,

    #[token("+")]
    Plus,

    #[token("-")]
    Minus,

    #[token("*")]
    Star,

    #[token("/")]
    Slash,

    #[token("(")]
    LParen,

    #[token(")")]
    RParen,

    #[regex(r"[0-9]+")]
    Number,

    #[regex(r"[a-zA-Z_][a-zA-Z0-9_]*")]
    Identifier,

    // Variables
    #[token("=")]
    Equal,

    #[regex(r"(var|let)")]
    VariableDefinitionNonStatic,

    #[regex(r"const")]
    VariableDefinitionStatic,

    // Line endings
    #[token("\n")]
    UnixStyleLineEnding,

    #[token(";")]
    Semicolon,

    // Keywords (not predefined variables)
    #[token("if")]
    KeywordIfStatementBegin,

    #[token("else")]
    KeywordElseStatementBegin,

    #[regex("\bfor")]
    KeywordForStatementBegin,

    #[token("while")]
    KeywordWhileStatementBegin,

    #[token("function")]
    KeywordFunctionDefinitionBegin,

    #[token("async")]
    KeywordEnableAsyncForFunction,

    #[token("return")],
    KeywordReturnFromFunction,

    #[token("import")]
    KeywordImportModule,

    #[token("from")]
    KeywordImportFromModule,

    #[token("class")]
    KeywordClassDefinitionBegin,

    #[token("try")]
    KeywordTryBlockBegin,

    #[token("catch")]
    KeywordCatchBlockBegin,

    // Catch any error

    #[error]
    Error,
}