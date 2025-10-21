import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

class CSSTokenType(Enum):
    IDENTIFIER = "identifier"
    STRING = "string"
    NUMBER = "number"
    PERCENTAGE = "percentage"
    DIMENSION = "dimension"
    HASH = "hash"
    DELIM = "delim"
    WHITESPACE = "whitespace"
    LEFT_PAREN = "left_paren"
    RIGHT_PAREN = "right_paren"
    LEFT_BRACE = "left_brace"
    RIGHT_BRACE = "right_brace"
    LEFT_BRACKET = "left_bracket"
    RIGHT_BRACKET = "right_bracket"
    COLON = "colon"
    SEMICOLON = "semicolon"
    COMMA = "comma"
    AT_KEYWORD = "at_keyword"
    COMMENT = "comment"
    EOF = "eof"

@dataclass
class CSSToken:
    type: CSSTokenType
    value: str
    position: int = 0

class CSSStyleSheet:
    def __init__(self):
        self.rules: List[CSSRule] = []
        self.imports: List[str] = []
        
    def add_rule(self, rule: 'CSSRule'):
        self.rules.append(rule)
        
    def get_styles_for_element(self, element, parent=None) -> Dict[str, str]:
        """Get all applicable styles for an element"""
        styles = {}
        specificity_scores = {}
        
        for rule in self.rules:
            if rule.matches_element(element, parent):
                specificity = rule.get_specificity()
                for property_name, property_value in rule.declarations.items():
                    # Higher specificity overwrites lower specificity
                    if (property_name not in specificity_scores or 
                        self._compare_specificity(specificity, specificity_scores[property_name]) > 0):
                        styles[property_name] = property_value
                        specificity_scores[property_name] = specificity
                        
        return styles

    def _compare_specificity(self, spec1: Tuple[int, int, int, int], spec2: Tuple[int, int, int, int]) -> int:
        """Compare two specificity tuples. Returns 1 if spec1 > spec2, -1 if spec1 < spec2, 0 if equal"""
        for i in range(4):
            if spec1[i] > spec2[i]:
                return 1
            elif spec1[i] < spec2[i]:
                return -1
        return 0

class CSSRule:
    def __init__(self, selectors: List['CSSSelector'], declarations: Dict[str, str]):
        self.selectors = selectors
        self.declarations = declarations
        
    def matches_element(self, element, parent=None) -> bool:
        """Check if this rule matches the given element"""
        for selector in self.selectors:
            if selector.matches(element, parent):
                return True
        return False
        
    def get_specificity(self) -> Tuple[int, int, int, int]:
        """Calculate specificity for this rule (inline, IDs, classes, elements)"""
        if not self.selectors:
            return (0, 0, 0, 0)
            
        # Use the highest specificity among all selectors
        max_specificity = (0, 0, 0, 0)
        for selector in self.selectors:
            specificity = selector.get_specificity()
            if self._compare_specificity(specificity, max_specificity) > 0:
                max_specificity = specificity
        return max_specificity
        
    def _compare_specificity(self, spec1: Tuple[int, int, int, int], spec2: Tuple[int, int, int, int]) -> int:
        """Compare two specificity tuples"""
        for i in range(4):
            if spec1[i] > spec2[i]:
                return 1
            elif spec1[i] < spec2[i]:
                return -1
        return 0

class CSSSelector:
    def __init__(self, parts: List['CSSSelectorPart']):
        self.parts = parts
        
    def matches(self, element, parent=None) -> bool:
        """Check if this selector matches the element"""
        if not self.parts:
            return False
            
        # Simple selector matching - check if all parts match
        current_element = element
        
        for part in reversed(self.parts):  # Match from right to left
            if not part.matches(current_element):
                return False
            current_element = current_element.parent if hasattr(current_element, 'parent') else None
            if current_element is None and len(self.parts) > 1:
                return False
                
        return True
        
    def get_specificity(self) -> Tuple[int, int, int, int]:
        """Calculate specificity: (inline, IDs, classes, elements)"""
        inline = 0  # We don't handle inline styles in this basic implementation
        ids = 0
        classes = 0
        elements = 0
        
        for part in self.parts:
            if part.type == 'id':
                ids += 1
            elif part.type == 'class':
                classes += 1
            elif part.type == 'element':
                elements += 1
                
        return (inline, ids, classes, elements)

@dataclass
class CSSSelectorPart:
    type: str  # 'element', 'class', 'id', 'universal'
    value: str
    combinator: Optional[str] = None  # ' ', '>', '+', '~'

    def matches(self, element) -> bool:
        """Check if this selector part matches the element"""
        if self.type == 'universal':
            return True
        elif self.type == 'element':
            return element.tagName == self.value
        elif self.type == 'class':
            class_attr = element.getAttribute('class')
            if class_attr:
                classes = class_attr.split()
                return self.value in classes
            return False
        elif self.type == 'id':
            id_attr = element.getAttribute('id')
            return id_attr == self.value
        return False

class CSSTokenizer:
    def __init__(self, css_text: str):
        self.css_text = css_text
        self.position = 0
        self.tokens: List[CSSToken] = []
        
    def tokenize(self) -> List[CSSToken]:
        """Main tokenization method"""
        while self.position < len(self.css_text):
            char = self.css_text[self.position]
            
            if char.isspace():
                self._consume_whitespace()
            elif char == '/' and self.position + 1 < len(self.css_text) and self.css_text[self.position + 1] == '*':
                self._consume_comment()
            elif char == '"' or char == "'":
                self._consume_string()
            elif char.isdigit() or char == '.':
                self._consume_number_or_dimension()
            elif char == '#':
                self._consume_hash()
            elif char == '@':
                self._consume_at_keyword()
            elif char == '(':
                self._add_token(CSSTokenType.LEFT_PAREN, char)
                self.position += 1
            elif char == ')':
                self._add_token(CSSTokenType.RIGHT_PAREN, char)
                self.position += 1
            elif char == '{':
                self._add_token(CSSTokenType.LEFT_BRACE, char)
                self.position += 1
            elif char == '}':
                self._add_token(CSSTokenType.RIGHT_BRACE, char)
                self.position += 1
            elif char == '[':
                self._add_token(CSSTokenType.LEFT_BRACKET, char)
                self.position += 1
            elif char == ']':
                self._add_token(CSSTokenType.RIGHT_BRACKET, char)
                self.position += 1
            elif char == ':':
                self._add_token(CSSTokenType.COLON, char)
                self.position += 1
            elif char == ';':
                self._add_token(CSSTokenType.SEMICOLON, char)
                self.position += 1
            elif char == ',':
                self._add_token(CSSTokenType.COMMA, char)
                self.position += 1
            else:
                self._consume_identifier_or_delim()
                
        self._add_token(CSSTokenType.EOF, "")
        return self.tokens
        
    def _consume_whitespace(self):
        """Consume whitespace characters"""
        start = self.position
        while self.position < len(self.css_text) and self.css_text[self.position].isspace():
            self.position += 1
        if self.position > start:
            self._add_token(CSSTokenType.WHITESPACE, self.css_text[start:self.position])
            
    def _consume_comment(self):
        """Consume and skip CSS comment /* ... */ (do not emit a token)"""
        self.position += 2  # Skip /*
        while self.position < len(self.css_text) - 1:
            if (self.css_text[self.position] == '*' and 
                self.css_text[self.position + 1] == '/'):
                self.position += 2  # Skip */
                break
            self.position += 1
        
    def _consume_string(self):
        """Consume quoted string"""
        quote_char = self.css_text[self.position]
        start = self.position
        self.position += 1  # Skip opening quote
        
        while self.position < len(self.css_text):
            if self.css_text[self.position] == quote_char:
                self.position += 1  # Skip closing quote
                break
            elif self.css_text[self.position] == '\\':
                self.position += 2  # Skip escaped character
            else:
                self.position += 1
                
        self._add_token(CSSTokenType.STRING, self.css_text[start:self.position])
        
    def _consume_number_or_dimension(self):
        """Consume number or dimension"""
        start = self.position
        
        # Consume number part
        while (self.position < len(self.css_text) and 
               (self.css_text[self.position].isdigit() or 
                self.css_text[self.position] == '.')):
            self.position += 1
            
        # Check for unit
        unit_start = self.position
        while (self.position < len(self.css_text) and 
               self.css_text[self.position].isalpha()):
            self.position += 1
            
        if self.position > unit_start:
            # It's a dimension
            self._add_token(CSSTokenType.DIMENSION, self.css_text[start:self.position])
        else:
            # It's a number
            self._add_token(CSSTokenType.NUMBER, self.css_text[start:self.position])
            
    def _consume_hash(self):
        """Consume hash token #ident"""
        start = self.position
        self.position += 1  # Skip #
        
        while (self.position < len(self.css_text) and 
               (self.css_text[self.position].isalnum() or 
                self.css_text[self.position] in '-_')):
            self.position += 1
            
        self._add_token(CSSTokenType.HASH, self.css_text[start:self.position])
        
    def _consume_at_keyword(self):
        """Consume @keyword"""
        start = self.position
        self.position += 1  # Skip @
        
        while (self.position < len(self.css_text) and 
               (self.css_text[self.position].isalnum() or 
                self.css_text[self.position] in '-_')):
            self.position += 1
            
        self._add_token(CSSTokenType.AT_KEYWORD, self.css_text[start:self.position])
        
    def _consume_identifier_or_delim(self):
        """Consume identifier or delimiter"""
        start = self.position
        
        # Check if it's a valid identifier start
        if (self.css_text[self.position].isalpha() or 
            self.css_text[self.position] in '-_' or
            ord(self.css_text[self.position]) > 127):  # Non-ASCII
            # Consume identifier
            while (self.position < len(self.css_text) and 
                   (self.css_text[self.position].isalnum() or 
                    self.css_text[self.position] in '-_' or
                    ord(self.css_text[self.position]) > 127)):
                self.position += 1
            self._add_token(CSSTokenType.IDENTIFIER, self.css_text[start:self.position])
        else:
            # Single character delimiter
            self._add_token(CSSTokenType.DELIM, self.css_text[self.position])
            self.position += 1
            
    def _add_token(self, token_type: CSSTokenType, value: str):
        """Add a token to the list"""
        self.tokens.append(CSSToken(token_type, value, self.position))

class CSSParser:
    def __init__(self, css_text: str):
        self.tokenizer = CSSTokenizer(css_text)
        self.tokens = []
        self.position = 0
        
    def parse(self) -> CSSStyleSheet:
        """Parse CSS text into a stylesheet"""
        self.tokens = self.tokenizer.tokenize()
        self.position = 0
        
        stylesheet = CSSStyleSheet()
        
        while not self._is_eof():
            self._consume_whitespace()
            
            if self._peek_type() == CSSTokenType.AT_KEYWORD:
                self._parse_at_rule(stylesheet)
            elif self._peek_type() == CSSTokenType.LEFT_BRACE:
                self._consume_token()  # Skip unexpected {
            else:
                start_pos = self.position
                if self._looks_like_selector(self.position):
                    rule = self._parse_rule()
                    if rule:
                        stylesheet.add_rule(rule)
                    # If parsing did not consume anything, advance by one to avoid a tight loop
                    if self.position == start_pos:
                        self._consume_token()
                else:
                    # Not a selector start; advance to avoid re-attempting on each token
                    self._consume_token()
                    
        return stylesheet
        
    def _looks_like_selector(self, pos: int) -> bool:
        """Heuristic: return True if a '{' appears ahead before a ';' or '}'.
        This avoids attempting to parse a rule inside a declaration block."""
        tokens = self.tokens
        n = len(tokens)
        T = CSSTokenType
        i = pos
        # Skip whitespace
        while i < n and tokens[i].type == T.WHITESPACE:
            i += 1
        # Scan forward for a definitive delimiter
        while i < n:
            tt = tokens[i].type
            if tt == T.LEFT_BRACE:
                return True
            if tt in (T.SEMICOLON, T.RIGHT_BRACE, T.EOF):
                return False
            i += 1
        return False

    def _find_next_token(self, token_type: CSSTokenType, start: int) -> int:
        """Return the index of the next occurrence of token_type at or after start, or -1."""
        tokens = self.tokens
        n = len(tokens)
        i = start
        while i < n:
            if tokens[i].type == token_type:
                return i
            i += 1
        return -1

    def _parse_selectors_between(self, start: int, end: int) -> Tuple[List[CSSSelector], int]:
        """Parse selectors delimited by [start, end) where end points to the '{'.
        Returns (selectors, pos=end)."""
        selectors: List[CSSSelector] = []
        tokens = self.tokens
        pos = start
        n = len(tokens)
        T = CSSTokenType

        # Consume leading whitespace
        while pos < end and tokens[pos].type == T.WHITESPACE:
            pos += 1

        while pos < end:
            parts, pos = self._parse_simple_selector_from(tokens, pos)
            if not parts:
                break
            selectors.append(CSSSelector(parts))

            # Skip any remaining selector syntax until comma or end
            while pos < end and tokens[pos].type not in (T.COMMA,):
                pos += 1
            if pos < end and tokens[pos].type == T.COMMA:
                pos += 1
                # Skip whitespace after comma
                while pos < end and tokens[pos].type == T.WHITESPACE:
                    pos += 1
                # Continue parsing next selector in group
                continue
            else:
                break

        # Clamp to end
        pos = end
        return selectors, pos
        
    def _parse_rule(self) -> Optional[CSSRule]:
        """Parse a CSS rule by scanning ahead to the next '{' and
        parsing selectors only within that range to avoid repeated attempts."""
        start = self.position
        tokens = self.tokens
        n = len(tokens)
        T = CSSTokenType

        # Skip leading whitespace
        while start < n and tokens[start].type == T.WHITESPACE:
            start += 1
        if start >= n:
            return None

        # Find the next '{' ahead
        lb = self._find_next_token(T.LEFT_BRACE, start)
        if lb == -1:
            # No block found; nothing to parse
            return None

        # Parse selectors between [start, lb)
        selectors, pos = self._parse_selectors_between(start, lb)
        if not selectors:
            # Advance past '{' to avoid stalling
            self.position = min(lb + 1, n)
            return None

        # Set parser position to just after '{'
        self.position = lb + 1

        # Parse declarations until the closing '}'
        declarations = self._parse_declarations()

        # Consume the closing '}' if present; otherwise skip forward to it
        if not self._consume_token_if_type(T.RIGHT_BRACE):
            while self.position < n and tokens[self.position].type != T.RIGHT_BRACE:
                self.position += 1
            self._consume_token_if_type(T.RIGHT_BRACE)

        return CSSRule(selectors, declarations)
        
    def _parse_selectors(self) -> List[CSSSelector]:
        """Parse CSS selectors (optimized: minimize helper calls)"""
        selectors: List[CSSSelector] = []
        tokens = self.tokens
        pos = self.position
        n = len(tokens)
        T = CSSTokenType

        while True:
            # Parse a simple selector from current position
            parts, pos = self._parse_simple_selector_from(tokens, pos)
            if not parts:
                break
            selectors.append(CSSSelector(parts))

            # After a first simple selector, skip through any additional selector tokens
            # until we hit a separator (',' or '{'). This tolerates unsupported combinators
            # and prevents parser stalls on complex selectors.
            while pos < n and tokens[pos].type not in (T.COMMA, T.LEFT_BRACE):
                pos += 1

            # Consume whitespace
            while pos < n and tokens[pos].type == T.WHITESPACE:
                pos += 1

            # Handle separator/combinator
            if pos < n and tokens[pos].type == T.COMMA:
                pos += 1
                while pos < n and tokens[pos].type == T.WHITESPACE:
                    pos += 1
                # Continue parsing next selector in the list
                continue
            elif pos < n and tokens[pos].type == T.LEFT_BRACE:
                break
            else:
                break

        # Commit consumed position
        self.position = pos
        return selectors
        
    def _parse_simple_selector(self) -> List[CSSSelectorPart]:
        """Parse a simple selector (optimized wrapper)"""
        parts, new_pos = self._parse_simple_selector_from(self.tokens, self.position)
        self.position = new_pos
        return parts

    def _parse_simple_selector_from(self, tokens: List[CSSToken], pos: int) -> Tuple[List[CSSSelectorPart], int]:
        """Fast-path parser for a simple selector starting at tokens[pos].
        Returns (parts, new_pos) without touching self.position."""
        parts: List[CSSSelectorPart] = []
        n = len(tokens)
        T = CSSTokenType

        while pos < n:
            t = tokens[pos]
            tt = t.type
            if tt == T.IDENTIFIER:
                # Element selector
                parts.append(CSSSelectorPart('element', t.value))
                pos += 1
            elif tt == T.HASH:
                # ID selector (#id)
                parts.append(CSSSelectorPart('id', t.value[1:]))  # Remove leading '#'
                pos += 1
            elif tt == T.DELIM:
                v = t.value
                if v == '.':
                    pos += 1  # skip '.'
                    if pos < n and tokens[pos].type == T.IDENTIFIER:
                        parts.append(CSSSelectorPart('class', tokens[pos].value))
                        pos += 1
                    else:
                        # Lone '.' is invalid here; stop parsing this simple selector
                        break
                elif v == '*':
                    pos += 1
                    parts.append(CSSSelectorPart('universal', '*'))
                else:
                    break
            else:
                break
        return parts, pos
        
    def _parse_declarations(self) -> Dict[str, str]:
        """Parse CSS declarations"""
        declarations = {}
        
        while not self._is_eof():
            self._consume_whitespace()
            
            if self._peek_type() == CSSTokenType.RIGHT_BRACE:
                break
                
            # Parse property name
            if self._peek_type() == CSSTokenType.IDENTIFIER:
                property_name = self._consume_token().value
                
                self._consume_whitespace()
                
                if not self._consume_token_if_type(CSSTokenType.COLON):
                    continue
                    
                self._consume_whitespace()
                
                # Parse property value
                property_value = self._parse_property_value()
                
                declarations[property_name] = property_value
                
                self._consume_whitespace()
                
                # Consume semicolon if present
                self._consume_token_if_type(CSSTokenType.SEMICOLON)
                
        return declarations
        
    def _parse_property_value(self) -> str:
        """Parse a CSS property value"""
        value_parts = []
        
        while not self._is_eof():
            token_type = self._peek_type()
            
            if token_type in [CSSTokenType.SEMICOLON, CSSTokenType.RIGHT_BRACE]:
                break
            elif token_type == CSSTokenType.WHITESPACE:
                value_parts.append(' ')
                self._consume_token()
            else:
                token = self._consume_token()
                value_parts.append(token.value)
                
        return ''.join(value_parts).strip()
        
    def _parse_at_rule(self, stylesheet: CSSStyleSheet):
        """Parse @-rules like @import"""
        if self._peek_value().lower() == '@import':
            self._parse_import_rule(stylesheet)
        else:
            # Skip unknown @-rules
            while not self._is_eof() and self._peek_type() != CSSTokenType.SEMICOLON:
                self._consume_token()
            self._consume_token_if_type(CSSTokenType.SEMICOLON)
            
    def _parse_import_rule(self, stylesheet: CSSStyleSheet):
        """Parse @import rule"""
        self._consume_token()  # Skip @import
        self._consume_whitespace()
        
        if self._peek_type() == CSSTokenType.STRING:
            url_token = self._consume_token()
            url = url_token.value[1:-1]  # Remove quotes
            stylesheet.imports.append(url)
            
        self._consume_token_if_type(CSSTokenType.SEMICOLON)
        
    # Helper methods
    def _is_eof(self) -> bool:
        return self.position >= len(self.tokens) or self._peek_type() == CSSTokenType.EOF
        
    def _peek_type(self) -> CSSTokenType:
        if self.position >= len(self.tokens):
            return CSSTokenType.EOF
        return self.tokens[self.position].type
        
    def _peek_value(self) -> str:
        if self.position >= len(self.tokens):
            return ""
        return self.tokens[self.position].value
        
    def _consume_token(self) -> CSSToken:
        if self.position >= len(self.tokens):
            return CSSToken(CSSTokenType.EOF, "")
        token = self.tokens[self.position]
        self.position += 1
        return token
        
    def _consume_token_if_type(self, expected_type: CSSTokenType) -> bool:
        # Fast path: avoid helper calls
        if self.position < len(self.tokens) and self.tokens[self.position].type == expected_type:
            self.position += 1
            return True
        return False
        
    def _consume_whitespace(self):
        # Fast path: avoid _peek_type/_consume_token overhead
        tokens = self.tokens
        pos = self.position
        n = len(tokens)
        T = CSSTokenType
        while pos < n and tokens[pos].type == T.WHITESPACE:
            pos += 1
        self.position = pos

@lru_cache(maxsize=8)
def parse_css(css_text: str) -> CSSStyleSheet:
    """Parse CSS text and return a stylesheet object"""
    parser = CSSParser(css_text)
    return parser.parse()

def test_css_parser():
    """Test function for the CSS parser"""
    css_text = """
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 20px;
        background-color: #ffffff;
    }
    
    h1 {
        color: blue;
        font-size: 24px;
    }
    
    .highlight {
        background-color: yellow;
        font-weight: bold;
    }
    
    #main-content {
        max-width: 800px;
        margin: 0 auto;
    }
    
    div > p {
        margin-bottom: 10px;
    }
    """
    
    print("Testing CSS Parser...")
    stylesheet = parse_css(css_text)
    
    print(f"Parsed {len(stylesheet.rules)} CSS rules")
    for i, rule in enumerate(stylesheet.rules):
        print(f"\nRule {i + 1}:")
        for selector in rule.selectors:
            print(f"  Selectors: {[f'{p.type}:{p.value}' for p in selector.parts]}")
        for prop, value in rule.declarations.items():
            print(f"  {prop}: {value}")

if __name__ == "__main__":
    test_css_parser()
