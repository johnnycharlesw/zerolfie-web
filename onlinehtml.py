import httpm
import htmlm
from urllib.parse import urljoin, urlparse
import re
from typing import Optional, Dict, Any

class WebPage:
    """Represents a complete web page with its DOM and metadata"""
    def __init__(self, url: str, dom: htmlm.HTMLElement, response_data: Dict[str, Any]):
        self.url = url
        self.dom = dom
        self.status_code = response_data.get('status', 0)
        self.headers = response_data.get('headers', [])
        self.content_type = self._get_content_type()
        self.title = self._extract_title()
        self.links = self._extract_links()
        self.scripts = self._extract_scripts()
        self.stylesheets = self._extract_stylesheets()
        
    def _get_content_type(self) -> str:
        """Extract content type from headers"""
        for header_name, header_value in self.headers:
            if header_name.lower() == 'content-type':
                return header_value.split(';')[0].strip()
        return 'text/html'
    
    def _extract_title(self) -> str:
        """Extract page title from DOM"""
        title_elements = self._find_elements_by_tag('title')
        if title_elements:
            return title_elements[0].textContent.strip()
        return ""
    
    def _extract_links(self) -> list:
        """Extract all links from the page"""
        links = []
        link_elements = self._find_elements_by_tag('a')
        for link in link_elements:
            href = link.getAttribute('href')
            if href:
                absolute_url = urljoin(self.url, href)
                links.append({
                    'url': absolute_url,
                    'text': link.textContent.strip(),
                    'element': link
                })
        return links
    
    def _extract_scripts(self) -> list:
        """Extract all script sources from the page"""
        scripts = []
        script_elements = self._find_elements_by_tag('script')
        for script in script_elements:
            src = script.getAttribute('src')
            if src:
                absolute_url = urljoin(self.url, src)
                scripts.append({
                    'url': absolute_url,
                    'element': script
                })
        return scripts
    
    def _extract_stylesheets(self) -> list:
        """Extract all stylesheet links from the page"""
        stylesheets = []
        link_elements = self._find_elements_by_tag('link')
        for link in link_elements:
            rel = link.getAttribute('rel')
            if rel and 'stylesheet' in rel.lower():
                href = link.getAttribute('href')
                if href:
                    absolute_url = urljoin(self.url, href)
                    stylesheets.append({
                        'url': absolute_url,
                        'element': link
                    })
        return stylesheets
    
    def _find_elements_by_tag(self, tag_name: str) -> list:
        """Find all elements with a specific tag name"""
        elements = []
        self._find_elements_recursive(self.dom, tag_name, elements)
        return elements
    
    def _find_elements_recursive(self, element: htmlm.HTMLElement, tag_name: str, results: list):
        """Recursively find elements by tag name"""
        if element.tagName == tag_name:
            results.append(element)
        for child in element.children:
            self._find_elements_recursive(child, tag_name, results)

class WebBrowser:
    """Main browser class that combines HTTP client and HTML parser"""
    
    def __init__(self):
        self.current_page: Optional[WebPage] = None
        self.history = []
        self.cookies = {}
        self._original_html_content = ""
        
    def navigate(self, url: str) -> WebPage:
        """Navigate to a URL and return the parsed page. Handles redirects."""
        print(f"🌐 Navigating to: {url}")
        
        try:
            # Parse URL to determine protocol and port
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = 'http://' + url
                parsed_url = urlparse(url)
            
            # Make HTTP request with redirect handling
            print(f"📡 Fetching content...")
            response, final_url = self._http_get_follow_redirects(url)
            
            if response['status'] != 200:
                print(f"⚠️  HTTP {response['status']}: {response['reason']}")
                return None
            
            # Decode content
            content = response['content']
            if isinstance(content, bytes):
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    content = content.decode('latin-1')
            
            print(f"📄 Content length: {len(content)} characters")
            
            # Store original HTML content for CSS re-parsing
            self._original_html_content = content
            
            # Parse HTML
            print(f"🔍 Parsing HTML...")
            parser = htmlm.HTMLDomInitializer(content)
            dom = parser.get_document()
            
            # Create WebPage object
            self.current_page = WebPage(final_url, dom, response)
            self.history.append(self.current_page)
            
            print(f"✅ Page loaded successfully!")
            print(f"📋 Title: {self.current_page.title}")
            print(f"🔗 Found {len(self.current_page.links)} links")
            print(f"📜 Found {len(self.current_page.scripts)} scripts")
            print(f"🎨 Found {len(self.current_page.stylesheets)} stylesheets")
            
            # Load CSS stylesheets
            if self.current_page.stylesheets:
                print(f"🎨 Loading {len(self.current_page.stylesheets)} stylesheets...")
                self._load_css_stylesheets(self.current_page.stylesheets, base_url=final_url)
            
            return self.current_page
            
        except Exception as e:
            print(f"❌ Error loading page: {e}")
            return None
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get information about the current page"""
        if not self.current_page:
            return {"error": "No page loaded"}
        
        return {
            "url": self.current_page.url,
            "title": self.current_page.title,
            "status_code": self.current_page.status_code,
            "content_type": self.current_page.content_type,
            "links_count": len(self.current_page.links),
            "scripts_count": len(self.current_page.scripts),
            "stylesheets_count": len(self.current_page.stylesheets)
        }
    
    def find_links(self, text_filter: str = None) -> list:
        """Find links, optionally filtered by text content"""
        if not self.current_page:
            return []
        
        links = self.current_page.links
        if text_filter:
            return [link for link in links if text_filter.lower() in link['text'].lower()]
        return links
    
    def follow_link(self, link_index: int) -> WebPage:
        """Follow a link by its index in the links list"""
        if not self.current_page or link_index >= len(self.current_page.links):
            print("❌ Invalid link index")
            return None
        
        link_url = self.current_page.links[link_index]['url']
        return self.navigate(link_url)
    
    def back(self) -> WebPage:
        """Go back in history"""
        if len(self.history) > 1:
            self.history.pop()  # Remove current page
            self.current_page = self.history[-1]
            print(f"⬅️  Went back to: {self.current_page.url}")
            return self.current_page
        else:
            print("❌ No history to go back to")
            return None
    
    def _load_css_stylesheets(self, stylesheets, base_url: str = None):
        """Load CSS stylesheets from URLs, following redirects."""
        import httpm
        css_contents = []
        
        for stylesheet in stylesheets:
            try:
                css_url = stylesheet['url']
                if base_url:
                    css_url = urljoin(base_url, css_url)
                print(f"  📥 Loading CSS: {css_url}")
                response, css_final_url = self._http_get_follow_redirects(css_url)
                if response['status'] == 200:
                    content = response['content']
                    if isinstance(content, bytes):
                        content = content.decode('utf-8', errors='replace')
                    css_contents.append(content)
                    print(f"  ✅ Loaded CSS ({len(content)} characters)")
                else:
                    print(f"  ⚠️  Failed to load CSS: HTTP {response['status']}")
            except Exception as e:
                print(f"  ❌ Error loading CSS: {e}")
        
        # Apply CSS to the current page
        if css_contents:
            print(f"🎨 Applying {len(css_contents)} stylesheets...")
            original_html = self._get_original_html_content()
            parser = htmlm.HTMLDomInitializer(original_html, css_contents)
            self.current_page.dom = parser.get_document()

    def _get_original_html_content(self) -> str:
        """Get the original HTML content for re-parsing with CSS"""
        return self._original_html_content

    def _http_get_follow_redirects(self, url: str, max_redirects: int = 10):
        """GET a URL and follow HTTP redirects (301, 302, 303, 307, 308). Returns (response, final_url)."""
        current_url = url
        for _ in range(max_redirects):
            response = httpm.request(url=current_url, method="GET")
            status = response.get('status', 0)
            if status in (301, 302, 303, 307, 308):
                # Find Location header
                location = None
                for name, value in response.get('headers', []):
                    if name.lower() == 'location':
                        location = value
                        break
                if not location:
                    break
                # Resolve relative redirects
                current_url = urljoin(current_url, location)
                print(f"  ↪️ Redirect to: {current_url}")
                continue
            return response, current_url
        # Give up after max redirects
        return response, current_url

    def print_dom_tree(self, max_depth: int = 3, show_styles: bool = False):
        """Print the DOM tree structure"""
        if not self.current_page:
            print("❌ No page loaded")
            return
        
        print(f"\n🌳 DOM Tree for {self.current_page.url}:")
        htmlm.print_dom_tree(self.current_page.dom, max_depth, show_styles)
    
    def _print_element(self, element: htmlm.HTMLElement, depth: int, max_depth: int):
        """Recursively print element structure"""
        if depth > max_depth:
            return
        
        indent = "  " * depth
        attrs = ""
        if element.attributes:
            attrs = " " + " ".join([f'{k}="{v}"' for k, v in element.attributes.items()])
        
        print(f"{indent}<{element.tagName}{attrs}>")
        
        # Print text content if it exists
        text_content = element.textContent.strip()
        if text_content and len(text_content) < 100:  # Only show short text
            print(f"{indent}  {text_content}")
        
        # Print children
        for child in element.children:
            self._print_element(child, depth + 1, max_depth)
        
        print(f"{indent}</{element.tagName}>")

def main():
    """Interactive browser session"""
    browser = WebBrowser()
    
    print("🌐 Zerolfie Web Browser")
    print("Commands: navigate <url>, info, links, follow <index>, back, dom, styles, quit")
    print("Example: navigate https://example.com")
    
    while True:
        try:
            command = input("\n>>> ").strip().split()
            if not command:
                continue
                
            if command[0] == "quit":
                break
            elif command[0] == "navigate" and len(command) > 1:
                url = command[1]
                browser.navigate(url)
            elif command[0] == "info":
                info = browser.get_page_info()
                for key, value in info.items():
                    print(f"{key}: {value}")
            elif command[0] == "links":
                links = browser.find_links()
                for i, link in enumerate(links):
                    print(f"{i}: {link['text']} -> {link['url']}")
            elif command[0] == "follow" and len(command) > 1:
                try:
                    index = int(command[1])
                    browser.follow_link(index)
                except ValueError:
                    print("❌ Invalid link index")
            elif command[0] == "back":
                browser.back()
            elif command[0] == "dom":
                browser.print_dom_tree()
            elif command[0] == "styles":
                browser.print_dom_tree(show_styles=True)
            else:
                print("❌ Unknown command")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()