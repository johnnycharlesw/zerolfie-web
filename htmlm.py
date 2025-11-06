import html as htmlescaper
import re
import css

class HTMLTextNode:
    """Represents a text node in the DOM"""
    def __init__(self, text: str):
        self.text = text
        self.nodeType = 3  # TEXT_NODE

class HTMLElement:
    def __init__(self, tagName: str, parent=None):
        self.tagName = tagName.lower()
        self.attributes = {}
        self.childNodes = []
        self.parent = parent
        self.nodeType = 1  # ELEMENT_NODE
        self._computed_styles = {}
        self._stylesheet = None
        
    def getAttribute(self, name: str):
        return self.attributes.get(name.lower())
        
    def setAttribute(self, name: str, value):
        self.attributes[name.lower()] = value
        
    def removeAttribute(self, name: str):
        key = name.lower()
        if key in self.attributes:
            del self.attributes[key]

    @property
    def textContent(self):
        text = ""
        for child in self.childNodes:
            if isinstance(child, HTMLTextNode):
                text += child.text
            elif isinstance(child, HTMLElement):
                text += child.textContent
        return text

    @textContent.setter
    def textContent(self, value):
        # Clear existing children and replace with text node
        self.childNodes = [HTMLTextNode(str(value))]

    def appendChild(self, child):
        if isinstance(child, (HTMLElement, HTMLTextNode)):
            child.parent = self
            self.childNodes.append(child)

    @property
    def children(self):
        """Return only element children, not text nodes"""
        return [child for child in self.childNodes if isinstance(child, HTMLElement)]
    
    def set_stylesheet(self, stylesheet):
        """Set the CSS stylesheet for this element"""
        self._stylesheet = stylesheet
        self._computed_styles = {}
        
    def get_computed_style(self, property_name: str) -> str:
        """Get the computed CSS style for a property"""
        if not self._computed_styles and self._stylesheet:
            self._compute_styles()
        return self._computed_styles.get(property_name, "")
    
    def get_all_computed_styles(self) -> dict:
        """Get all computed CSS styles for this element"""
        if not self._computed_styles and self._stylesheet:
            self._compute_styles()
        return self._computed_styles.copy()
    
    def _compute_styles(self):
        """Compute all CSS styles for this element"""
        if not self._stylesheet:
            return
            
        # Get styles from stylesheet
        styles = self._stylesheet.get_styles_for_element(self, self.parent)
        
        # Handle inline styles (style attribute)
        inline_style = self.getAttribute('style')
        if inline_style:
            inline_styles = self._parse_inline_styles(inline_style)
            # Inline styles have highest specificity
            styles.update(inline_styles)
            
        self._computed_styles = styles
    
    def _parse_inline_styles(self, style_text: str) -> dict:
        """Parse inline style attribute"""
        styles = {}
        if not style_text:
            return styles
            
        # Simple inline style parsing
        declarations = style_text.split(';')
        for declaration in declarations:
            if ':' in declaration:
                property_name, property_value = declaration.split(':', 1)
                property_name = property_name.strip()
                property_value = property_value.strip()
                styles[property_name] = property_value
        return styles
    
    def has_class(self, class_name: str) -> bool:
        """Check if element has a specific CSS class"""
        class_attr = self.getAttribute('class')
        if not class_attr:
            return False
        classes = class_attr.split()
        return class_name in classes
    
    def add_class(self, class_name: str):
        """Add a CSS class to the element"""
        current_classes = self.getAttribute('class') or ''
        classes = current_classes.split()
        if class_name not in classes:
            classes.append(class_name)
            self.setAttribute('class', ' '.join(classes))
    
    def remove_class(self, class_name: str):
        """Remove a CSS class from the element"""
        current_classes = self.getAttribute('class') or ''
        classes = current_classes.split()
        if class_name in classes:
            classes.remove(class_name)
            if classes:
                self.setAttribute('class', ' '.join(classes))
            else:
                self.removeAttribute('class')

class HTMLToken:
    def __init__(self, type, value, start_pos=0, end_pos=0):
        self.type = type  # 'TAG_OPEN', 'TAG_CLOSE', 'TAG_SELF_CLOSE', 'TEXT', 'COMMENT', 'DOCTYPE'
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos

class HTMLTokenizer:
    def __init__(self, html: str):
        self.html = html
        self.pos = 0
        self.tokens = []
        
    def tokenize(self):
        """Main tokenization method"""
        while self.pos < len(self.html):
            char = self.html[self.pos]
            
            if char == '<':
                self._parse_tag()
            else:
                self._parse_text()
                
        return self.tokens
    
    def _parse_tag(self):
        """Parse HTML tags, comments, and DOCTYPE"""
        start_pos = self.pos
        
        # Check for comments <!-- -->
        if self.html[self.pos:self.pos+4] == '<!--':
            self._parse_comment()
            return
            
        # Check for DOCTYPE
        if self.html[self.pos:self.pos+9].upper() == '<!DOCTYPE':
            self._parse_doctype()
            return
            
        # Regular tag
        self.pos += 1  # Skip '<'
        
        # Check if it's a closing tag
        if self.pos < len(self.html) and self.html[self.pos] == '/':
            self.pos += 1  # Skip '/'
            tag_name = self._read_tag_name()
            self._skip_whitespace()
            if self.pos < len(self.html) and self.html[self.pos] == '>':
                self.pos += 1
                self.tokens.append(HTMLToken('TAG_CLOSE', tag_name, start_pos, self.pos))
            return
            
        # Opening tag or self-closing tag
        tag_name = self._read_tag_name()
        attributes = self._parse_attributes()
        
        # Check for self-closing tag
        is_self_closing = False
        if self.pos < len(self.html) and self.html[self.pos] == '/':
            self.pos += 1
            is_self_closing = True
            
        self._skip_whitespace()
        if self.pos < len(self.html) and self.html[self.pos] == '>':
            self.pos += 1
            
        if is_self_closing:
            self.tokens.append(HTMLToken('TAG_SELF_CLOSE', {'name': tag_name, 'attributes': attributes}, start_pos, self.pos))
        else:
            self.tokens.append(HTMLToken('TAG_OPEN', {'name': tag_name, 'attributes': attributes}, start_pos, self.pos))
    
    def _read_tag_name(self):
        """Read the tag name"""
        name = ""
        while self.pos < len(self.html) and self.html[self.pos] not in ' \t\n\r/>':
            name += self.html[self.pos]
            self.pos += 1
        return name.lower()
    
    def _parse_attributes(self):
        """Parse tag attributes"""
        attributes = {}
        
        while self.pos < len(self.html) and self.html[self.pos] not in '/>':
            self._skip_whitespace()
            
            if self.pos >= len(self.html) or self.html[self.pos] in '/>':
                break
                
            # Parse attribute name
            attr_name = ""
            while self.pos < len(self.html) and self.html[self.pos] not in ' \t\n\r=/>':
                attr_name += self.html[self.pos]
                self.pos += 1
                
            if not attr_name:
                break
                
            self._skip_whitespace()
            
            # Check for attribute value
            attr_value = ""
            if self.pos < len(self.html) and self.html[self.pos] == '=':
                self.pos += 1
                self._skip_whitespace()
                
                # Check for quoted value
                if self.pos < len(self.html) and self.html[self.pos] in '"\'':
                    quote = self.html[self.pos]
                    self.pos += 1
                    while self.pos < len(self.html) and self.html[self.pos] != quote:
                        attr_value += self.html[self.pos]
                        self.pos += 1
                    if self.pos < len(self.html):
                        self.pos += 1  # Skip closing quote
            else:
                    # Unquoted value
                    while self.pos < len(self.html) and self.html[self.pos] not in ' \t\n\r/>':
                        attr_value += self.html[self.pos]
                        self.pos += 1
            
            attributes[attr_name.lower()] = attr_value
            
        return attributes
    
    def _parse_text(self):
        """Parse text content"""
        start_pos = self.pos
        text = ""
        
        while self.pos < len(self.html) and self.html[self.pos] != '<':
            text += self.html[self.pos]
            self.pos += 1
            
        if text.strip():  # Only add non-empty text
            self.tokens.append(HTMLToken('TEXT', text, start_pos, self.pos))
    
    def _parse_comment(self):
        """Parse HTML comments <!-- -->"""
        start_pos = self.pos
        self.pos += 4  # Skip '<!--'
        
        comment = ""
        while self.pos < len(self.html) - 2:
            if self.html[self.pos:self.pos+3] == '-->':
                self.pos += 3
                break
            comment += self.html[self.pos]
            self.pos += 1
            
        self.tokens.append(HTMLToken('COMMENT', comment, start_pos, self.pos))
    
    def _parse_doctype(self):
        """Parse DOCTYPE declaration"""
        start_pos = self.pos
        self.pos += 9  # Skip '<!DOCTYPE'
        
        doctype = ""
        while self.pos < len(self.html):
            if self.html[self.pos] == '>':
                self.pos += 1
                break
            doctype += self.html[self.pos]
            self.pos += 1
            
        self.tokens.append(HTMLToken('DOCTYPE', doctype, start_pos, self.pos))
    
    def _skip_whitespace(self):
        """Skip whitespace characters"""
        while self.pos < len(self.html) and self.html[self.pos] in ' \t\n\r':
            self.pos += 1
    
class HTMLDomInitializer:
    def __init__(self, html: str, stylesheets: list = None):
        self.html = html
        self.tokens = []
        self.document = None
        self.current_element = None
        self.stack = []
        self.stylesheets = stylesheets or []
        self.master_stylesheet = css.CSSStyleSheet()
        
        # Self-closing tags
        self.self_closing_tags = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }

        # Basic insertion mode flags
        self.in_head = False
        self.seen_html = False
        self.seen_head = False
        self.seen_body = False
        
        self.parse()
        self._post_process_structure()
        self._load_css()
        self._apply_styles()
    
    def parse(self):
        """Main parsing method"""
        tokenizer = HTMLTokenizer(self.html)
        self.tokens = tokenizer.tokenize()
        
        # Create document root (wrapper), not an <html> element
        self.document = HTMLElement('document')
        self.current_element = self.document
        self.stack = [self.document]
        
        # Ensure an <html> element exists as top-level container
        html_el = HTMLElement('html', self.document)
        self.document.appendChild(html_el)
        self.stack.append(html_el)
        self.current_element = html_el
        self.seen_html = True
        self.in_head = True  # start expecting head
        
        # Parse tokens
        for token in self.tokens:
            if token.type == 'TAG_OPEN':
                self._handle_open_tag(token)
            elif token.type == 'TAG_CLOSE':
                self._handle_close_tag(token)
            elif token.type == 'TAG_SELF_CLOSE':
                self._handle_self_closing_tag(token)
            elif token.type == 'TEXT':
                self._handle_text(token)
            elif token.type == 'COMMENT':
                self._handle_comment(token)
            elif token.type == 'DOCTYPE':
                self._handle_doctype(token)
    
    def _handle_open_tag(self, token):
        """Handle opening tags with minimal insertion-mode logic"""
        tag_info = token.value
        tag_name = tag_info['name']
        attributes = tag_info['attributes']
        tag_name = tag_name.lower()

        # Handle duplicate or misplaced <html>
        if tag_name == 'html':
            existing_html = self._find_in_stack('html')
            if existing_html is not None:
                # Switch context to existing html and do not create a new one
                self.current_element = existing_html
                # Ensure stack has [document, html]
                self.stack = [self.stack[0], existing_html]
                return
        
        # Ensure head/body containers
        if tag_name == 'head':
            # Reuse existing head if present
            self._ensure_head()
            self.current_element = self._find_in_stack('head')
            # Reset stack to [document, html, head]
            self.stack = [self.stack[0], self._find_in_stack('html'), self.current_element]
            self.in_head = True
            self.seen_head = True
            return
        if tag_name == 'body':
            # Leaving head if we are in it
            if self.in_head:
                self._close_until('html')
                self.in_head = False
            # Reuse existing body if present
            self._ensure_body()
            self.current_element = self._find_in_stack('body')
            # Reset stack to [document, html, body]
            self.stack = [self.stack[0], self._find_in_stack('html'), self.current_element]
            self.seen_body = True
            return

        # If we are in head and encounter a body-content tag, close head
        if self.in_head and tag_name not in ('meta', 'title', 'style', 'link', 'base', 'head'):
            self._ensure_head()
            self._close_until('html')
            self.in_head = False
            self._ensure_body()
            self.current_element = self._find_in_stack('body')

        # Create new element under current
        element = HTMLElement(tag_name, self.current_element)
        for attr_name, attr_value in attributes.items():
            element.setAttribute(attr_name, attr_value)
        self.current_element.appendChild(element)

        # Auto-close paragraphs when a new block starts
        if tag_name in ('div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table'):
            self._auto_close('p')

        # Push to stack and set as current (unless it's self-closing)
        if tag_name not in self.self_closing_tags:
            self.stack.append(element)
            self.current_element = element
    
    def _handle_close_tag(self, token):
        """Handle closing tags with minimal implied rules"""
        tag_name = token.value.lower()

        # Implied end tags for <p>
        if tag_name == 'p' and self._find_in_stack('p') is None:
            return

        # Special handling for closing html: pop to html if present
        if tag_name == 'html':
            html_el = self._find_in_stack('html')
            if html_el is None:
                return
            # Reduce stack to [document]
            self.stack = [self.stack[0]]
            self.current_element = self.stack[-1]
            return

        # Find matching opening tag in stack
        for i in range(len(self.stack) - 1, -1, -1):
            if isinstance(self.stack[i], HTMLElement) and self.stack[i].tagName == tag_name:
                # Pop stack up to and including this element
                self.stack = self.stack[:i]
                self.current_element = self.stack[-1] if self.stack else self.document
                # Leaving head when head closes
                if tag_name == 'head':
                    self.in_head = False
                return
        # If not found, ignore
        return
    
    def _handle_self_closing_tag(self, token):
        """Handle self-closing tags"""
        tag_info = token.value
        tag_name = tag_info['name'].lower()
        attributes = tag_info['attributes']
        
        # Create new element
        element = HTMLElement(tag_name, self.current_element)
        
        # Set attributes
        for attr_name, attr_value in attributes.items():
            element.setAttribute(attr_name, attr_value)
        
        # Add to current element (don't push to stack)
        self.current_element.appendChild(element)
    
    def _handle_text(self, token):
        """Handle text content"""
        text = token.value
        # Preserve whitespace between inline text for renderer; trim only purely whitespace nodes
        if text and text.strip():
            text_node = HTMLTextNode(text)
            self.current_element.appendChild(text_node)
    
    def _handle_comment(self, token):
        """Handle HTML comments (currently ignored)"""
        pass
    
    def _handle_doctype(self, token):
        """Handle DOCTYPE declaration (currently ignored)"""
        pass
    
    def _load_css(self):
        """Load CSS from stylesheets and style tags"""
        # Load external stylesheets
        for stylesheet_content in self.stylesheets:
            try:
                parsed_css = css.parse_css(stylesheet_content)
                self._merge_stylesheet(parsed_css)
            except Exception as e:
                print(f"Error parsing CSS: {e}")
        
        # Load CSS from <style> tags in the document
        style_elements = self._find_elements_by_tag('style')
        for style_element in style_elements:
            style_content = style_element.textContent
            if style_content:
                try:
                    parsed_css = css.parse_css(style_content)
                    self._merge_stylesheet(parsed_css)
                except Exception as e:
                    print(f"Error parsing style tag: {e}")
    
    def _merge_stylesheet(self, stylesheet):
        """Merge a parsed stylesheet into the master stylesheet"""
        for rule in stylesheet.rules:
            self.master_stylesheet.add_rule(rule)
    
    def _apply_styles(self):
        """Apply CSS styles to all elements in the document"""
        self._apply_styles_recursive(self.document)
    
    def _apply_styles_recursive(self, element):
        """Recursively apply styles to element and its children"""
        if isinstance(element, HTMLElement):
            element.set_stylesheet(self.master_stylesheet)
            for child in element.children:
                self._apply_styles_recursive(child)
    
    def _find_elements_by_tag(self, tag_name: str) -> list:
        """Find all elements with a specific tag name"""
        elements = []
        self._find_elements_recursive(self.document, tag_name, elements)
        return elements
    
    def _find_elements_recursive(self, element: HTMLElement, tag_name: str, results: list):
        """Recursively find elements by tag name"""
        if isinstance(element, HTMLElement):
            if element.tagName == tag_name:
                results.append(element)
            for child in element.children:
                self._find_elements_recursive(child, tag_name, results)
    
    def get_document(self):
        """Return the parsed document"""
        return self.document

    # --- helpers for minimal tree construction ---
    def _ensure_head(self):
        if self._find_in_stack('head') is None:
            html_el = self._find_in_stack('html') or self.stack[0]
            head = HTMLElement('head', html_el)
            html_el.appendChild(head)
    def _ensure_body(self):
        if self._find_in_stack('body') is None:
            html_el = self._find_in_stack('html') or self.stack[0]
            body = HTMLElement('body', html_el)
            html_el.appendChild(body)
    def _find_in_stack(self, tag):
        for el in reversed(self.stack):
            if isinstance(el, HTMLElement) and el.tagName == tag:
                return el
        # Also scan children of html for existing head/body
        if tag in ('head','body','html'):
            root = self.stack[0]
            for child in getattr(root, 'childNodes', []):
                if isinstance(child, HTMLElement) and child.tagName == 'html':
                    for c in child.childNodes:
                        if isinstance(c, HTMLElement) and c.tagName == tag:
                            return c
        return None
    def _close_until(self, tag):
        # Pop until we reach tag or document
        while len(self.stack) > 1:
            if isinstance(self.stack[-1], HTMLElement) and self.stack[-1].tagName == tag:
                break
            self.stack.pop()
        self.current_element = self.stack[-1]
    def _auto_close(self, tag):
        # Close tag if present on stack
        for i in range(len(self.stack) - 1, -1, -1):
            if isinstance(self.stack[i], HTMLElement) and self.stack[i].tagName == tag:
                self.stack = self.stack[:i]
                self.current_element = self.stack[-1]
                return
    def _post_process_structure(self):
        # Ensure head/body exist under html
        html_el = None
        for child in self.document.childNodes:
            if isinstance(child, HTMLElement) and child.tagName == 'html':
                html_el = child
                break
        if html_el is None:
            html_el = HTMLElement('html', self.document)
            self.document.appendChild(html_el)
        # Move stray body/head under html
        head = None
        body = None
        for c in list(html_el.childNodes):
            if isinstance(c, HTMLElement) and c.tagName == 'head':
                head = c
            if isinstance(c, HTMLElement) and c.tagName == 'body':
                body = c
        if head is None:
            head = HTMLElement('head', html_el)
            html_el.appendChild(head)
        if body is None:
            body = HTMLElement('body', html_el)
            html_el.appendChild(body)

def print_dom_tree(element, indent=0, show_styles=False):
    """Helper function to print DOM tree structure"""
    spaces = "  " * indent
    if isinstance(element, HTMLElement):
        # Skip printing the 'document' wrapper; just print its children
        if element.tagName == 'document':
            for child in element.childNodes:
                print_dom_tree(child, indent, show_styles)
            return
        
        attrs = ""
        if element.attributes:
            attrs = " " + " ".join([f'{k}="{v}"' for k, v in element.attributes.items()])
        
        print(f"{spaces}<{element.tagName}{attrs}>")
        
        if show_styles:
            styles = element.get_all_computed_styles()
            if styles:
                print(f"{spaces}  🎨 Styles:")
                for prop, value in styles.items():
                    print(f"{spaces}    {prop}: {value}")
        
        for child in element.childNodes:
            print_dom_tree(child, indent + 1, show_styles)
        print(f"{spaces}</{element.tagName}>")
    elif isinstance(element, HTMLTextNode):
        if element.text.strip():
            print(f"{spaces}{element.text}")

if __name__ == "__main__":
    # Test the parser with the HTML file
    with open("default.css.test.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Load CSS files
    css_files = []
    try:
        with open("default.css", "r", encoding="utf-8") as f:
            css_files.append(f.read())
    except FileNotFoundError:
        print("No default.css found")
    
    try:
        with open("default.css.test.css", "r", encoding="utf-8") as f:
            css_files.append(f.read())
    except FileNotFoundError:
        print("No default.css.test.css found")
    
    print("Parsing HTML with CSS...")
    parser = HTMLDomInitializer(html_content, css_files)
    document = parser.get_document()
    
    print("\nParsed DOM Tree with Styles:")
    print_dom_tree(document, show_styles=True)
    
    print("\n\nCSS Test - Finding styled elements:")
    # Find elements with specific styles
    body_elements = parser._find_elements_by_tag('body')
    if body_elements:
        body = body_elements[0]
        print(f"Body styles: {body.get_all_computed_styles()}")
    
    h1_elements = parser._find_elements_by_tag('h1')
    if h1_elements:
        h1 = h1_elements[0]
        print(f"H1 styles: {h1.get_all_computed_styles()}")