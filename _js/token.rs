// src/token.rs
use logos::Logos;

#[derive(Logos, Debug, PartialEq, Clone)]
pub enum Token {
    #[regex(r"[ \t\n\f]+", logos::skip)]  // skip whitespace
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

    #[error]
    Error,
}