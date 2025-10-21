import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import webbrowser
from typing import Optional
import onlinehtml
import htmlm
import psutil, os
import cProfile, io, pstats

class ZerolfieWebView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌐 Zerolfie Web Browser")
        self.root.geometry("1200x800")
        
        # Initialize browser engine
        self.browser = onlinehtml.WebBrowser()
        self.current_page = None
        
        # Create GUI components
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Navigation frame
        self.nav_frame = ttk.Frame(self.root)
        
        # Navigation buttons
        self.back_btn = ttk.Button(self.nav_frame, text="⬅️", command=self.go_back, width=3)
        self.forward_btn = ttk.Button(self.nav_frame, text="➡️", command=self.go_forward, width=3)
        self.refresh_btn = ttk.Button(self.nav_frame, text="🔄", command=self.refresh_page, width=3)
        self.home_btn = ttk.Button(self.nav_frame, text="🏠", command=self.go_home, width=3)
        
        # Address bar
        self.address_var = tk.StringVar()
        self.address_var.set("https://example.com")
        self.address_entry = ttk.Entry(self.nav_frame, textvariable=self.address_var, font=('Arial', 10))
        self.address_entry.bind('<Return>', self.navigate_from_address)
        
        # Go button
        self.go_btn = ttk.Button(self.nav_frame, text="Go", command=self.navigate_from_address)
        
        # Main content area
        self.content_frame = ttk.Frame(self.root)
        
        # Page display area
        self.page_display = scrolledtext.ScrolledText(
            self.content_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 10),
            bg='white',
            fg='black'
        )
        
        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_frame, 
            variable=self.progress_var, 
            mode='indeterminate'
        )
        
        # Tab control for different views
        self.notebook = ttk.Notebook(self.content_frame)
        
        # Page view tab
        self.page_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.page_frame, text="🌐 Page")
        self.page_display.pack(fill=tk.BOTH, expand=True, in_=(self.page_frame,))
        
        # DOM view tab
        self.dom_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dom_frame, text="🌳 DOM")
        self.dom_display = scrolledtext.ScrolledText(
            self.dom_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 9),
            bg='#f0f0f0'
        )
        self.dom_display.pack(fill=tk.BOTH, expand=True)
        
        # CSS view tab
        self.css_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.css_frame, text="🎨 CSS")
        self.css_display = scrolledtext.ScrolledText(
            self.css_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 9),
            bg='#f8f8f8'
        )
        self.css_display.pack(fill=tk.BOTH, expand=True)
        
        # Links view tab
        self.links_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.links_frame, text="🔗 Links")
        
        # Links listbox with scrollbar
        self.links_list_frame = ttk.Frame(self.links_frame)
        self.links_listbox = tk.Listbox(self.links_list_frame, font=('Arial', 10))
        self.links_scrollbar = ttk.Scrollbar(self.links_list_frame, orient=tk.VERTICAL, command=self.links_listbox.yview)
        self.links_listbox.configure(yscrollcommand=self.links_scrollbar.set)
        
        self.links_listbox.bind('<Double-Button-1>', self.follow_selected_link)
        
        # Links frame layout
        self.links_list_frame.pack(fill=tk.BOTH, expand=True)
        self.links_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.links_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Info tab
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="📊 Info")
        self.info_display = scrolledtext.ScrolledText(
            self.info_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 9),
            bg='#fafafa'
        )
        self.info_display.pack(fill=tk.BOTH, expand=True)
        
        self.notebook.pack(fill=tk.BOTH, expand=True, in_=(self.content_frame,))
        
    def setup_layout(self):
        """Setup the layout of all widgets"""
        # Navigation frame
        self.nav_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.back_btn.pack(side=tk.LEFT, padx=2)
        self.forward_btn.pack(side=tk.LEFT, padx=2)
        self.refresh_btn.pack(side=tk.LEFT, padx=2)
        self.home_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self.nav_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.go_btn.pack(side=tk.LEFT, padx=2)
        
        # Content frame
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status frame
        self.status_frame.pack(fill=tk.X, padx=5, pady=2)
        self.status_label.pack(side=tk.LEFT)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
    def navigate_from_address(self, event=None):
        """Navigate to the URL in the address bar"""
        url = self.address_var.get().strip()
        if url:
            self.navigate_to_url(url)
    
    def navigate_to_url(self, url: str):
        """Navigate to a URL in a separate thread"""
        self.status_var.set(f"Loading {url}...")
        self.progress_bar.start()
        
        # Disable navigation buttons
        self.back_btn.config(state='disabled')
        self.forward_btn.config(state='disabled')
        self.go_btn.config(state='disabled')
        
        # Run navigation in a separate thread to avoid blocking GUI
        thread = threading.Thread(target=self._navigate_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _navigate_thread(self, url: str):
        """Navigation thread function"""
        try:
            # Use the browser engine to navigate
            page = self.browser.navigate(url)
            
            # Update GUI in main thread
            self.root.after(0, self._update_page_display, page)
            
        except Exception as e:
            self.root.after(0, self._show_error, f"Error loading page: {e}")
    
    def _update_page_display(self, page):
        """Update the page display with loaded content"""
        self.current_page = page
        
        if page:
            # Update address bar
            self.address_var.set(page.url)
            
            # Update status
            self.status_var.set(f"Loaded: {page.title or page.url}")
            
            # Display page content
            self.display_page_content(page)
            self.display_dom_tree(page)
            self.display_css_info(page)
            self.display_links(page)
            self.display_page_info(page)
        else:
            self.status_var.set("Failed to load page")
            self.page_display.delete(1.0, tk.END)
            self.page_display.insert(tk.END, "Failed to load page content.")
        
        # Re-enable navigation buttons
        self.progress_bar.stop()
        self.back_btn.config(state='normal')
        self.forward_btn.config(state='normal')
        self.go_btn.config(state='normal')
    
    def _show_error(self, error_msg):
        """Show error message"""
        self.status_var.set("Error")
        self.progress_bar.stop()
        self.back_btn.config(state='normal')
        self.forward_btn.config(state='normal')
        self.go_btn.config(state='normal')
        messagebox.showerror("Error", error_msg)
    
    def display_page_content(self, page):
        """Display the page content in a readable format"""
        self.page_display.delete(1.0, tk.END)
        
        if page and page.dom:
            content = self._format_html_for_display(page.dom)
            self.page_display.insert(tk.END, content)
    
    def _format_html_for_display(self, element, indent=0):
        """Format HTML content for display"""
        content = ""
        spaces = "  " * indent
        
        if isinstance(element, htmlm.HTMLElement):
            # Get element styles
            styles = element.get_all_computed_styles()
            style_info = ""
            if styles:
                style_info = f" [styles: {len(styles)}]"
            
            # Format element
            attrs = ""
            if element.attributes:
                attrs = " " + " ".join([f'{k}="{v}"' for k, v in element.attributes.items()])
            
            content += f"{spaces}<{element.tagName}{attrs}>{style_info}\n"
            
            # Add text content if it's short
            text_content = element.textContent.strip()
            if text_content and len(text_content) < 100:
                content += f"{spaces}  {text_content}\n"
            
            # Add children
            for child in element.childNodes:
                content += self._format_html_for_display(child, indent + 1)
            
            content += f"{spaces}</{element.tagName}>\n"
            
        elif isinstance(element, htmlm.HTMLTextNode):
            if element.text.strip():
                content += f"{spaces}{element.text}\n"
        
        return content
    
    def display_dom_tree(self, page):
        """Display the DOM tree"""
        self.dom_display.delete(1.0, tk.END)
        
        if page and page.dom:
            # Use the existing DOM tree printer
            import io
            import sys
            
            # Capture the output
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            try:
                htmlm.print_dom_tree(page.dom, show_styles=True)
                dom_content = buffer.getvalue()
            finally:
                sys.stdout = old_stdout
            
            self.dom_display.insert(tk.END, dom_content)
    
    def display_css_info(self, page):
        """Display CSS information"""
        self.css_display.delete(1.0, tk.END)
        
        if page:
            css_info = f"🎨 CSS Information for {page.url}\n"
            css_info += "=" * 50 + "\n\n"
            
            css_info += f"Stylesheets found: {len(page.stylesheets)}\n"
            for i, stylesheet in enumerate(page.stylesheets):
                css_info += f"  {i+1}. {stylesheet['url']}\n"
            
            css_info += f"\nScripts found: {len(page.scripts)}\n"
            for i, script in enumerate(page.scripts):
                css_info += f"  {i+1}. {script['url']}\n"
            
            css_info += "\n" + "=" * 50 + "\n"
            css_info += "Element Styles:\n\n"
            
            # Show styles for some elements
            if page.dom:
                buf = []
                self._add_element_styles_to_info(page.dom, buf, 0)
                css_info += ''.join(buf)
            
            self.css_display.insert(tk.END, css_info)
    
    def _add_element_styles_to_info(self, element, buf, depth):
        """Add element styles to CSS info display. Accumulate into buf list."""
        if isinstance(element, htmlm.HTMLElement):
            styles = element.get_all_computed_styles()
            if styles:
                spaces = "  " * depth
                buf.append(f"{spaces}<{element.tagName}>:\n")
                for prop, value in styles.items():
                    buf.append(f"{spaces}  {prop}: {value}\n")
                buf.append("\n")
            
            # Limit depth to avoid too much output
            if depth < 3:
                for child in element.children:
                    self._add_element_styles_to_info(child, buf, depth + 1)

    def display_links(self, page):
        """Display page links"""
        self.links_listbox.delete(0, tk.END)
        
        if page and page.links:
            for i, link in enumerate(page.links):
                display_text = f"{i+1}. {link['text'][:50]}... -> {link['url']}"
                self.links_listbox.insert(tk.END, display_text)
        else:
            self.links_listbox.insert(tk.END, "No links found on this page")
    
    def display_page_info(self, page):
        """Display page information"""
        self.info_display.delete(1.0, tk.END)
        
        if page:
            info = f"📊 Page Information\n"
            info += "=" * 50 + "\n\n"
            
            page_info = self.browser.get_page_info()
            for key, value in page_info.items():
                info += f"{key.replace('_', ' ').title()}: {value}\n"
            
            info += "\n" + "=" * 50 + "\n"
            info += "Response Headers:\n\n"
            
            if hasattr(page, 'headers'):
                for header_name, header_value in page.headers:
                    info += f"{header_name}: {header_value}\n"
            
            self.info_display.insert(tk.END, info)
    
    def follow_selected_link(self, event):
        """Follow the selected link"""
        selection = self.links_listbox.curselection()
        if selection and self.current_page:
            link_index = selection[0]
            if link_index < len(self.current_page.links):
                link_url = self.current_page.links[link_index]['url']
                self.navigate_to_url(link_url)
    
    def go_back(self):
        """Go back in history"""
        page = self.browser.back()
        if page:
            self._update_page_display(page)
    
    def go_forward(self):
        """Go forward in history (not implemented yet)"""
        messagebox.showinfo("Info", "Forward navigation not yet implemented")
    
    def refresh_page(self):
        """Refresh the current page"""
        if self.current_page:
            self.navigate_to_url(self.current_page.url)
    
    def go_home(self):
        """Go to home page"""
        self.navigate_to_url("https://example.com")
    
    def run(self):
        """Start the GUI application"""
        # Set initial page
        self.navigate_to_url("https://example.com")
        
        # Start the main loop
        self.root.mainloop()

def main():
    """Main function to start the GUI browser"""
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)
    profiler = cProfile.Profile()
    profiler.enable()
    print("🌐 Starting Zerolfie Web Browser GUI...")
    app = ZerolfieWebView()
    app.run()
    profiler.disable()
    profiler.dump_stats('profile_results.prof')
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # top 20 functions
    print(stream.getvalue())

if __name__ == "__main__":
    main()
