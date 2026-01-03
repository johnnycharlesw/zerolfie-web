import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

class CSSTokenType(Enum):
    IDENTIFIER = "identifier"
    FUNCTION = "function"
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

class CSSMediaRule:
    def __init__(self, media: str, rules: List['CSSRule']):
        self.media = media  # raw media query text (e.g., 'screen and (min-width: 600px)')
        self.rules = rules

@dataclass
class CSSCounterStyle:
    """Represents a @counter-style rule definition"""
    name: str
    system: Optional[str] = None
    symbols: Optional[str] = None
    additive_symbols: Optional[str] = None
    negative: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    range: Optional[str] = None
    pad: Optional[str] = None
    speak_as: Optional[str] = None
    fallback: Optional[str] = None

class CSSStyleSheet:
    def __init__(self, isPrinting: bool):
        self.rules: List[CSSRule] = []
        self.media_rules: List[CSSMediaRule] = []
        self.imports: List[str] = []
        self.counter_styles: Dict[str, CSSCounterStyle] = {}  # name -> counter style
        self.is_printing = isPrinting
        
    def add_rule(self, rule: 'CSSRule'):
        self.rules.append(rule)

    def add_media_rule(self, media_rule: 'CSSMediaRule'):
        self.media_rules.append(media_rule)
    
    def add_counter_style(self, counter_style: CSSCounterStyle):
        """Add a counter style definition"""
        self.counter_styles[counter_style.name] = counter_style
    
    def get_counter_style(self, name: str) -> Optional[CSSCounterStyle]:
        """Get a counter style by name"""
        return self.counter_styles.get(name)
        
    def get_styles_for_element(self, element, parent=None, media_context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Get all applicable styles for an element.
        If media_context is provided, include matching @media rules.
        media_context example: { 'prefers-color-scheme': 'dark', 'media-type': 'screen' }
        Resolves CSS custom properties using :root definitions (including matching @media blocks).
        """
        styles: Dict[str, str] = {}
        specificity_scores: Dict[str, Tuple[int, int, int, int]] = {}
        
        if media_context is None:
            media_context = default_media_context(self.is_printing)
        
        # Apply default styles for document element (like Gecko's Document)
        # Note: document element is not rendered, so only inheritable properties are set
        # These serve as the root for inheritance to child elements
        if hasattr(element, 'tagName') and element.tagName == 'document':
            default_document_styles = {
                'font-family': 'sans-serif',
                'font-size': '16px',
                'color': '#000000',
            }
            styles.update(default_document_styles)
        
        # Collect custom properties from :root (base + matching media)
        vars_map = self._collect_root_custom_properties(media_context)
        
        # 1) Apply base rules
        for rule in self.rules:
            if rule.matches_element(element, parent):
                specificity = rule.get_specificity()
                for property_name, property_value in rule.declarations.items():
                    if (property_name not in specificity_scores or 
                        self._compare_specificity(specificity, specificity_scores[property_name]) > 0):
                        resolved = self._resolve_vars(property_value, vars_map)
                        styles[property_name] = resolved
                        specificity_scores[property_name] = specificity
        
        # 2) Apply media rules that match
        for mr in self.media_rules:
            if self._media_matches(mr.media, media_context):
                for rule in mr.rules:
                    if rule.matches_element(element, parent):
                        specificity = rule.get_specificity()
                        for property_name, property_value in rule.declarations.items():
                            if (property_name not in specificity_scores or 
                                self._compare_specificity(specificity, specificity_scores[property_name]) > 0):
                                resolved = self._resolve_vars(property_value, vars_map)
                                styles[property_name] = resolved
                                specificity_scores[property_name] = specificity
        
        # Synthesize background-color from background if needed and possible
        if 'background-color' not in styles and 'background' in styles:
            bg = styles['background']
            if self._looks_like_color(bg):
                styles['background-color'] = bg
        
        # Sanitize unresolved var(...) for critical color properties
        for key in ('background-color', 'color', 'border-color', 'background'):
            if key in styles and isinstance(styles[key], str) and 'var(' in styles[key]:
                # Apply safe defaults
                if key in ('background', 'background-color'):
                    styles[key] = '#ffffff'
                elif key == 'color':
                    styles[key] = '#000000'
                elif key == 'border-color':
                    styles[key] = '#000000'
        
        return styles

    def _collect_root_custom_properties(self, media_context: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Collect custom properties defined on :root from base and matching @media rules."""
        result: Dict[str, str] = {}
        # Define a helper to test if a rule targets :root
        def rule_targets_root(rule: 'CSSRule') -> bool:
            for sel in rule.selectors:
                if len(sel.parts) == 1:
                    p = sel.parts[0]
                    # :root matches document element (our artificial wrapper, like Gecko's Document)
                    if (p.type == 'pseudo' and p.value == 'root') or (p.type == 'element' and p.value.lower() in ('document', 'html')):
                        return True
            return False
        
        # Base rules
        for rule in self.rules:
            if rule_targets_root(rule):
                for k, v in rule.declarations.items():
                    if k.startswith('--'):
                        result[k] = v
        
        # Media rules
        if media_context is None:
            media_context = {}
        for mr in self.media_rules:
            if self._media_matches(mr.media, media_context):
                for rule in mr.rules:
                    if rule_targets_root(rule):
                        for k, v in rule.declarations.items():
                            if k.startswith('--'):
                                result[k] = v
        return result

    def _resolve_vars(self, value: str, vars_map: Dict[str, str], depth: int = 0) -> str:
        """Resolve var(--name[, fallback]) references in value using vars_map.
        Limits recursion depth to prevent cycles.
        """
        if not value or 'var(' not in value:
            return value
        if depth > 8:
            return value
        
        def replace_var(match: re.Match) -> str:
            inner = match.group(1)
            # split on first comma not inside parentheses (simple approach: split once)
            name = inner
            fallback = None
            # handle nested functions in fallback by scanning manually
            paren = 0
            comma_index = -1
            for i, ch in enumerate(inner):
                if ch == '(':
                    paren += 1
                elif ch == ')':
                    paren = max(paren - 1, 0)
                elif ch == ',' and paren == 0:
                    comma_index = i
                    break
            if comma_index != -1:
                name = inner[:comma_index].strip()
                fallback = inner[comma_index + 1 :].strip()
            else:
                name = inner.strip()
            if name.startswith('--') and name in vars_map:
                return self._resolve_vars(vars_map[name], vars_map, depth + 1)
            # If variable missing, use fallback if provided
            if fallback is not None:
                return self._resolve_vars(fallback, vars_map, depth + 1)
            # No fallback; keep original var() to signal unresolved
            return match.group(0)
        
        # Regex to capture content inside var(...)
        pattern = re.compile(r"var\(\s*(.*?)\s*\)")
        # Replace iteratively until no change or depth exceeded
        prev = None
        cur = value
        iter_count = 0
        while cur != prev and iter_count < 10 and 'var(' in cur:
            prev = cur
            cur = pattern.sub(replace_var, cur)
            iter_count += 1
        return cur

    def _looks_like_color(self, s: str) -> bool:
        if not isinstance(s, str):
            return False
        st = s.strip().lower()
        if st.startswith('#'):
            return True
        if st.startswith('rgb(') or st.startswith('rgba('):
            return True
        # basic named colors
        if st in ('white','black','red','green','blue','gray','grey','silver','navy','teal','purple','yellow','orange','magenta','cyan'):
            return True
        return False

    def _media_matches(self, media_text: str, ctx: Dict[str, Any]) -> bool:
        """Very small media evaluator supporting prefers-color-scheme and optional media type.
        Examples matched:
          (prefers-color-scheme: dark)
          screen and (prefers-color-scheme: light)
          all and (prefers-color-scheme: dark)
        Unrecognized conditions default to False to avoid accidental matches.
        """
        if not media_text:
            return False
        text = ' '.join(media_text.strip().split())  # normalize spaces
        text_lower = text.lower()

        # Extract optional media type before 'and'
        media_type = None
        cond_part = text_lower
        if ' and ' in text_lower:
            first, rest = text_lower.split(' and ', 1)
            # basic media types
            if first in ('all', 'screen', 'print'):  # extend as needed
                media_type = first
                cond_part = rest
        
        # If media type is present, optionally compare to context (default to screen if unknown)
        wanted_type = ctx.get('media-type')
        if media_type is not None and wanted_type is not None:
            if media_type != 'all' and media_type != wanted_type:
                return False
        
        # Now handle prefers-color-scheme condition
        # Expected forms like: (prefers-color-scheme: dark) or multiple ands (we only parse one key condition now)
        m = re.search(r"\(\s*prefers-color-scheme\s*:\s*(dark|light)\s*\)", cond_part)
        if m:
            need = m.group(1)
            have = str(ctx.get('prefers-color-scheme') or '').lower()
            if need and have:
                return need == have
            # If we have a need but no context, don't match
            return False
        
        # If there was no known condition, be conservative
        return False

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
    type: str  # 'element', 'class', 'id', 'universal', 'pseudo'
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
        elif self.type == 'pseudo':
            # Support :root matching: matches document element (like Gecko's implicit Document)
            if self.value == 'root':
                try:
                    tag = getattr(element, 'tagName', '')
                    if isinstance(tag, str):
                        tag_lower = tag.lower()
                        # :root matches the document element (our artificial wrapper)
                        if tag_lower == 'document':
                            return True
                        # Also support html as root for compatibility
                        if tag_lower == 'html':
                            return True
                except Exception:
                    pass
                return not hasattr(element, 'parent') or getattr(element, 'parent') is None
            # Unknown pseudo-class not supported
            return False
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
        """Consume identifier or delimiter; recognize function tokens like linear-gradient("""
        start = self.position
        text = self.css_text
        n = len(text)
        
        # Check if it's a valid identifier start
        if (text[self.position].isalpha() or 
            text[self.position] in '-_' or
            ord(text[self.position]) > 127):  # Non-ASCII
            # Consume identifier
            while (self.position < n and 
                   (text[self.position].isalnum() or 
                    text[self.position] in '-_' or
                    ord(text[self.position]) > 127)):
                self.position += 1
            ident = text[start:self.position]
            # If immediately followed by '(', it's a function token
            if self.position < n and text[self.position] == '(':
                self._add_token(CSSTokenType.FUNCTION, ident)
                self._add_token(CSSTokenType.LEFT_PAREN, '(')
                self.position += 1
            else:
                self._add_token(CSSTokenType.IDENTIFIER, ident)
        else:
            # Single character delimiter
            self._add_token(CSSTokenType.DELIM, text[self.position])
            self.position += 1
            
    def _add_token(self, token_type: CSSTokenType, value: str):
        """Add a token to the list"""
        self.tokens.append(CSSToken(token_type, value, self.position))

class CSSParser:
    def __init__(self, css_text: str):
        self.tokenizer = CSSTokenizer(css_text)
        self.tokens = []
        self.position = 0
        
    def parse(self, isPrinting) -> CSSStyleSheet:
        """Parse CSS text into a stylesheet"""
        self.tokens = self.tokenizer.tokenize()
        self.position = 0
        
        stylesheet = CSSStyleSheet(isPrinting)
        
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
                        break
                elif v == '*':
                    pos += 1
                    parts.append(CSSSelectorPart('universal', '*'))
                elif v == ':':
                    # Pseudo-class like :root
                    pos += 1
                    if pos < n and tokens[pos].type == T.IDENTIFIER:
                        parts.append(CSSSelectorPart('pseudo', tokens[pos].value))
                        pos += 1
                    else:
                        # Unknown or malformed pseudo; stop
                        break
                else:
                    break
            else:
                break
        return parts, pos
        
    def _parse_declarations(self) -> Dict[str, str]:
        """Parse CSS declarations; support custom properties starting with --"""
        declarations = {}
        T = CSSTokenType
        
        while not self._is_eof():
            self._consume_whitespace()
            
            if self._peek_type() == T.RIGHT_BRACE:
                break
                
            # Parse property name: identifier or custom property beginning with '--'
            prop_name = None
            if self._peek_type() == T.IDENTIFIER:
                prop_name = self._consume_token().value
            elif self._peek_type() == T.DELIM and self._peek_value() == '-':
                # Check for '--'
                # Lookahead: two hyphens followed by identifier characters
                start_pos = self.position
                d1 = self._consume_token().value  # first '-'
                if self._peek_type() == T.DELIM and self._peek_value() == '-':
                    self._consume_token()  # second '-'
                    # Collect name characters
                    name_chars = ['--']
                    while self._peek_type() in (T.IDENTIFIER, T.DELIM):
                        # IDENTIFIER tokens may contain sequences; DELIM may bring '-'
                        t = self._consume_token()
                        name_chars.append(t.value)
                        # Stop if we hit a colon
                        if self._peek_type() == T.COLON:
                            break
                    prop_name = ''.join(name_chars)
                else:
                    # Not a custom property; revert and skip token
                    self.position = start_pos
            
            if not prop_name:
                # Not a property; consume one token to avoid infinite loop
                if not self._is_eof():
                    self._consume_token()
                continue
                
            self._consume_whitespace()
            
            if not self._consume_token_if_type(T.COLON):
                continue
                
            self._consume_whitespace()
            
            # Parse property value (balance parentheses so gradients/functions work)
            property_value = self._parse_property_value()
            
            declarations[prop_name] = property_value
            
            self._consume_whitespace()
            
            # Consume semicolon if present
            self._consume_token_if_type(T.SEMICOLON)
                
        return declarations
        
    def _parse_property_value(self) -> str:
        """Parse a CSS property value; keep content until semicolon or '}' with balanced parens"""
        parts = []
        paren_depth = 0
        T = CSSTokenType
        
        while not self._is_eof():
            tt = self._peek_type()
            if tt == T.SEMICOLON and paren_depth == 0:
                break
            if tt == T.RIGHT_BRACE and paren_depth == 0:
                break
            if tt == T.WHITESPACE:
                parts.append(' ')
                self._consume_token()
                continue
            t = self._consume_token()
            if t.type == T.LEFT_PAREN:
                paren_depth += 1
                parts.append(t.value)
            elif t.type == T.RIGHT_PAREN:
                paren_depth = max(paren_depth - 1, 0)
                parts.append(t.value)
            else:
                parts.append(t.value)
        return ''.join(parts).strip()
        
    def _parse_at_rule(self, stylesheet: CSSStyleSheet):
        """Parse @-rules like @import, @media, and @counter-style"""
        peek_val = self._peek_value().lower()
        if peek_val == '@import':
            self._parse_import_rule(stylesheet)
            return
        if peek_val == '@media':
            self._parse_media_rule(stylesheet)
            return
        if peek_val == '@counter-style':
            self._parse_counter_style_rule(stylesheet)
            return
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

    def _parse_media_rule(self, stylesheet: CSSStyleSheet):
        """Parse @media rule with nested style rules"""
        # Consume '@media'
        self._consume_token()
        # Collect media query prelude until '{'
        media_parts: List[str] = []
        brace_found = False
        while not self._is_eof():
            tt = self._peek_type()
            if tt == CSSTokenType.LEFT_BRACE:
                self._consume_token()
                brace_found = True
                break
            # normalize whitespace to single spaces
            if tt == CSSTokenType.WHITESPACE:
                media_parts.append(' ')
                self._consume_token()
            else:
                media_parts.append(self._consume_token().value)
        media_text = ''.join(media_parts).strip()

        # Parse nested rules until matching '}'
        nested_rules: List[CSSRule] = []
        while not self._is_eof():
            self._consume_whitespace()
            if self._peek_type() == CSSTokenType.RIGHT_BRACE:
                self._consume_token()
                break
            if self._peek_type() == CSSTokenType.AT_KEYWORD:
                # For simplicity, skip nested at-rules inside @media (could be extended)
                self._parse_at_rule(stylesheet)
                continue
            # Parse a normal rule inside media
            start_pos = self.position
            if self._looks_like_selector(self.position):
                rule = self._parse_rule()
                if rule:
                    nested_rules.append(rule)
                if self.position == start_pos:
                    self._consume_token()
            else:
                self._consume_token()

        stylesheet.add_media_rule(CSSMediaRule(media_text, nested_rules))
    
    def _parse_counter_style_rule(self, stylesheet: CSSStyleSheet):
        """Parse @counter-style rule with descriptors"""
        # Consume '@counter-style'
        self._consume_token()
        self._consume_whitespace()
        
        # Parse counter style name (identifier)
        counter_name = None
        if self._peek_type() == CSSTokenType.IDENTIFIER:
            counter_name = self._consume_token().value
        else:
            # Invalid; skip this rule
            return
        
        self._consume_whitespace()
        
        # Consume '{'
        if not self._consume_token_if_type(CSSTokenType.LEFT_BRACE):
            return
        
        # Parse descriptors (similar to parsing declarations)
        descriptors: Dict[str, str] = {}
        T = CSSTokenType
        
        while not self._is_eof():
            self._consume_whitespace()
            
            if self._peek_type() == T.RIGHT_BRACE:
                self._consume_token()
                break
            
            # Parse descriptor name (identifier or descriptor starting with '-')
            desc_name = None
            if self._peek_type() == T.IDENTIFIER:
                desc_name = self._consume_token().value
            elif self._peek_type() == T.DELIM and self._peek_value() == '-':
                # Descriptor starting with '-' (like 'additive-symbols')
                name_chars = ['-']
                self._consume_token()  # consume the '-'
                while self._peek_type() in (T.IDENTIFIER, T.DELIM):
                    t = self._consume_token()
                    name_chars.append(t.value)
                    if self._peek_type() == T.COLON:
                        break
                desc_name = ''.join(name_chars)
            
            if not desc_name:
                # Not a descriptor; consume one token to avoid infinite loop
                if not self._is_eof():
                    self._consume_token()
                continue
            
            self._consume_whitespace()
            
            if not self._consume_token_if_type(T.COLON):
                continue
            
            self._consume_whitespace()
            
            # Parse descriptor value
            desc_value = self._parse_property_value()
            descriptors[desc_name.lower()] = desc_value
            
            self._consume_whitespace()
            
            # Consume semicolon if present
            self._consume_token_if_type(T.SEMICOLON)
        
        # Create CSSCounterStyle object
        counter_style = CSSCounterStyle(
            name=counter_name,
            system=descriptors.get('system'),
            symbols=descriptors.get('symbols'),
            additive_symbols=descriptors.get('additive-symbols'),
            negative=descriptors.get('negative'),
            prefix=descriptors.get('prefix'),
            suffix=descriptors.get('suffix'),
            range=descriptors.get('range'),
            pad=descriptors.get('pad'),
            speak_as=descriptors.get('speak-as'),
            fallback=descriptors.get('fallback')
        )
        stylesheet.add_counter_style(counter_style)
        
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

    def import_css_media_handlers():
        pass

@lru_cache(maxsize=8)
def parse_css(css_text: str, isPrinting: bool) -> CSSStyleSheet:
    """Parse CSS text and return a stylesheet object"""
    parser = CSSParser(css_text)
    return parser.parse(isPrinting)

# Media context helpers
def default_media_context(is_printing: bool) -> Dict[str, Any]:
    """Build a default media context using darkdetect if available.
    Returns keys: 'prefers-color-scheme' ('dark'|'light'), 'media-type' ('screen').
    """
    scheme = None
    try:
        import darkdetect  # type: ignore
        scheme = 'dark' if getattr(darkdetect, 'isDark', lambda: False)() else 'light'
    except Exception:
        # Default to light if detection is unavailable
        scheme = 'light'
    if is_printing:
        media_type="print"
    else:
        media_type='screen'
    
    return {
        'prefers-color-scheme': scheme,
        'media-type': media_type,
    }

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

    @media print {
        header, footer, aside {
            display:none;
        }
    }
    
    div > p {
        margin-bottom: 10px;
    }
    """
    import sys
    if "--printCSS" in sys.argv:
        isPrinting=True
    else:
        isPrinting=False
    print("Testing CSS Parser...")
    stylesheet = parse_css(css_text, isPrinting)
    
    print(f"Parsed {len(stylesheet.rules)} CSS rules")
    for i, rule in enumerate(stylesheet.rules):
        print(f"\nRule {i + 1}:")
        for selector in rule.selectors:
            print(f"  Selectors: {[f'{p.type}:{p.value}' for p in selector.parts]}")
        for prop, value in rule.declarations.items():
            print(f"  {prop}: {value}")


if __name__ == "__main__":
    test_css_parser()
