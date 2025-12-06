use logos::Lexer;

use crate::token::Token;

pub struct LexerWrapper<'source> {
    pub inner: Lexer<'source, Token>,
}

impl<'source> Iterator for LexerWrapper<'source> {
    type Item = (Token, &'source str);

    fn next(&mut self) -> Option<Self::Item> {
        let token = self.inner.next()?;
        let slice = self.inner.slice();
        Some((token, slice))
    }
}