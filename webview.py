import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from tkinter import font as tkfont
import threading
import webbrowser
from typing import Optional
import onlinehtml
import htmlm
import psutil, os
import csv
import cProfile, io, pstats

class ZerolfieWebView:
    def __init__(self):
        self.root = tk.Tk()
        self.root.iconphoto(False, tk.PhotoImage('zerolfiw-web-logo.png'))
        self.root.title("Zerolfie Web")
        self.root.geometry("1200x800")
        
        # Initialize browser engine
        self.browser = onlinehtml.WebBrowser()
        self.current_page = None
        self._page_canvas_ready = False

        # Create GUI components
        self.create_widgets()
        self.setup_layout()
        # page_canvas is created in create_widgets

        
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
        self.address_var.set("about:newtab")
        self.address_entry = ttk.Entry(self.nav_frame, textvariable=self.address_var, font=('Inter', 10))
        self.address_entry.bind('<Return>', self.navigate_from_address)
        
        # Go button
        self.go_btn = ttk.Button(self.nav_frame, text="Go", command=self.navigate_from_address)
        
        # Main content area
        self.content_frame = ttk.Frame(self.root)
        
        # Page render area (Canvas with scrollbar)
        self.page_canvas_container = ttk.Frame(self.content_frame)
        self.page_canvas = tk.Canvas(self.page_canvas_container, bg='white')
        self.page_scrollbar = ttk.Scrollbar(self.page_canvas_container, orient=tk.VERTICAL, command=self.page_canvas.yview)
        self.page_canvas.configure(yscrollcommand=self.page_scrollbar.set)
        self.page_canvas.bind_all('<MouseWheel>', lambda e: self.page_canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
        
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
        self.notebook.add(self.page_frame, text="Page")
        
        # Assemble canvas + scrollbar inside the page tab
        self.page_canvas_container.pack(fill=tk.BOTH, expand=True)
        self.page_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.page_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.page_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        print(f"Canvas size: {self.page_canvas.winfo_width()}x{self.page_canvas.winfo_height()}")
        
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
            
            # Render visual page: if canvas ready, render now; else defer
            if self._page_canvas_ready:
                self.render_page(page)
            else:
                self.root.after(30, lambda p=page: self.render_page(p))
            #self.display_css_info(page)
            self.display_links(page)
            self.display_page_info(page)
        else:
            self.status_var.set("Failed to load page")
            # Clear canvas when no page content is available
            self.page_canvas.delete('all')
            self.page_canvas.configure(scrollregion=(0, 0, 0, 0))
        
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
        """Deprecated: text view no longer used for Page tab"""
        pass
    
    def _format_html_for_display(self, element, indent=0):
        """Deprecated helper kept for reference."""
        return ""
    
    
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
        self.navigate_to_url("about:newtab")
    
    def run(self):
        """Start the GUI application"""
        # When the canvas resizes, re-render current page with new width
        def on_resize(event):
            # Mark canvas as ready once we have a reasonable width
            if not self._page_canvas_ready and event.width > 50:
                self._page_canvas_ready = True
            if self.current_page and self._page_canvas_ready:
                self.render_page(self.current_page)
        self.page_canvas.bind('<Configure>', on_resize)

        # Set initial page
        self.navigate_to_url("about:newtab")
        
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

# --- Minimal layout/paint engine ---

class BorderPiece:
    def __init__(self, name):
        self.name=name
        self.style = "none"
        self.width = "0px"
        self.color = "#000000"

class Border:
    def __init__(self, node):
        self.pieces = {
            "top": BorderPiece("top"),
            "right": BorderPiece("right"),
            "bottom": BorderPiece("bottom"),
            "left": BorderPiece("left")
        }
        self.radius = "0px"
        

class PageRenderer:
    def __init__(self, tk_root):
        self.tk_root = tk_root
        # Fonts are created lazily to ensure a Tk root exists
        self.font_cache = {}

    def _get_font(self, size=16, weight='normal'):
        key = (size, weight)
        if key not in self.font_cache:
            self.font_cache[key] = tkfont.Font(family='Inter', size=size, weight=weight)
        return self.font_cache[key]

    def _parse_px(self, value, default=0):
        try:
            if isinstance(value, (int, float)):
                return int(value)
            if value and value.endswith('px'):
                return int(float(value[:-2]))
            if value and value.isdigit():
                return int(value)
        except Exception:
            pass
        return int(default)

    def _parse_color(self, value, default='#000000'):
        if not value:
            return default
        return value

    def layout_and_paint(self, canvas: tk.Canvas, root_element: htmlm.HTMLElement, viewport_width: int):
        canvas.delete('all')
        x = 8
        y = 8
        max_width = max(100, viewport_width - 16)
        total_height = self._layout_block(canvas, root_element, x, y, max_width)
        canvas.configure(scrollregion=(0, 0, viewport_width, total_height + 8))

    def _layout_block(self, canvas, element, x, y, width):
        if not isinstance(element, htmlm.HTMLElement):
            return y
        # Skip the artificial document wrapper; render its children
        if element.tagName == 'document':
            # Optional: draw page title as sanity visibility line
            # Find <title> text if present
            title_text = ''
            try:
                for child in element.childNodes:
                    if isinstance(child, htmlm.HTMLElement) and child.tagName == 'html':
                        for head_child in child.childNodes:
                            if isinstance(head_child, htmlm.HTMLElement) and head_child.tagName == 'head':
                                for t in head_child.childNodes:
                                    if isinstance(t, htmlm.HTMLElement) and t.tagName == 'title':
                                        title_text = t.textContent.strip()
                                        break
            except Exception:
                pass
            if title_text:
                self.title_text=title_text
                debug_font = self._get_font(size=18, weight='bold')
                canvas.create_text(x, y, text=title_text, anchor='nw', font=debug_font, fill='#111')
                y += debug_font.metrics('linespace') + 8
            for child in element.childNodes:
                y = self._layout_block(canvas, child, x, y, width)
            return y

        styles = element.get_all_computed_styles() or {}
        # Basic defaults and tag-based font sizes
        tag = element.tagName
        base_size = 16
        if tag == 'h1':
            base_size = 32
        elif tag == 'h2':
            base_size = 24
        elif tag == 'h3':
            base_size = 20

        # Handle rendering

        # Step 1: Deal with font sizes and colors
        size = self._parse_px(styles.get('font-size'), base_size)
        weight = 'bold' if str(styles.get('font-weight', '')).lower() in ('bold', '700', '800', '900') else 'normal'
        color = self._parse_color(styles.get('color'), '#000000')
        bg = self._parse_color(styles.get('background-color'), None)

        # Step 2: Deal with margins

        # Deal with margin shorthand
        if styles.get("margin") != None:
            margin_top = self._parse_px(styles.get('margin'), 0)
            margin_bottom = self._parse_px(styles.get('margin'), 8)
            margin_left = self._parse_px(styles.get('margin'), 0)
            margin_right = self._parse_px(styles.get('margin'), 0)
        else:
            # Deal with seperate margins
            margin_top = self._parse_px(styles.get('margin-top'), 0)
            margin_bottom = self._parse_px(styles.get('margin-bottom'), 8)
            margin_left = self._parse_px(styles.get('margin-left'), 0)
            margin_right = self._parse_px(styles.get('margin-right'), 0)

        # Step 3: Handle padding

        # Deal with padding shorthand
        if styles.get("padding") != None:
            padding_top = self._parse_px(styles.get('padding'), 0)
            padding_bottom = self._parse_px(styles.get('padding'), 0)
            padding_left = self._parse_px(styles.get('padding'), 0)
            padding_right = self._parse_px(styles.get('padding'), 0)
        else:
            padding_top = self._parse_px(styles.get('padding-top'), 0)
            padding_bottom = self._parse_px(styles.get('padding-bottom'), 0)
            padding_left = self._parse_px(styles.get('padding-left'), 0)
            padding_right = self._parse_px(styles.get('padding-right'), 0)
        

        x0 = x + margin_left
        y0 = y + margin_top
        content_x = x0 + padding_left
        content_y = y0 + padding_top
        content_width = max(10, width - margin_left - margin_right - padding_left - padding_right)

        # Background box
        if bg and bg != 'transparent':
            box_top = y0
            box_bottom = box_top  # will be updated after children
        else:
            box_top = box_bottom = None

        # Determine list marker context for li
        is_list_item = (tag == 'li') and (str(styles.get('display', '')).lower() == 'list-item' or True)
        parent = getattr(element, 'parent', None)
        parent_tag = parent.tagName if isinstance(parent, htmlm.HTMLElement) else ''
        is_ul = parent_tag == 'ul'
        is_ol = parent_tag == 'ol'
        list_style_type = (styles.get('list-style-type') or ('disc' if is_ul else 'decimal' if is_ol else None))
        list_style_position = (styles.get('list-style-position') or 'outside')

        # Marker preparation
        marker_text = None
        marker_gap = 8
        font = self._get_font(size=size, weight=weight)
        line_height = font.metrics('linespace')
        marker_width = 0

        if is_list_item and (is_ul or is_ol):
            if is_ul:
                if list_style_type in (None, 'disc', 'initial'):
                    marker_text = '•'
                else:
                    marker_text = '•'
            elif is_ol:
                # Compute index among previous li siblings
                idx = 1
                if hasattr(parent, 'childNodes'):
                    idx = 0
                    for ch in parent.childNodes:
                        if isinstance(ch, htmlm.HTMLElement) and ch.tagName == 'li':
                            idx += 1
                        if ch is element:
                            break
                marker_text = f"{idx}."
            if marker_text:
                marker_width = tkfont.Font.measure(font, marker_text)
                if list_style_position == 'outside':
                    content_x += (marker_width + marker_gap)
                    content_width = max(10, content_width - (marker_width + marker_gap))

        y_cursor = content_y

        # Render text content only for typical text blocks
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li'):
            text = element.textContent.strip()
            if text:
                # Draw marker if inside positioning
                if marker_text and list_style_position == 'inside':
                    canvas.create_text(content_x, y_cursor, text=marker_text, anchor='nw', font=font, fill=color)
                    mxw = marker_width or tkfont.Font.measure(font, marker_text)
                    canvas.create_text(content_x + mxw + marker_gap, y_cursor, text=text, anchor='nw', font=font, fill=color)
                    y_cursor += line_height
                else:
                    canvas.create_text(content_x, y_cursor, text=text, anchor='nw', font=font, fill=color)
                    y_cursor += line_height

        # Render children blocks
        for child in element.childNodes:
            if isinstance(child, htmlm.HTMLElement) or isinstance(child, htmlm.HTMLTextNode):
                y_cursor = self._layout_child(canvas, child, content_x, y_cursor, content_width, font, color)

        # Ensure empty blocks still take some space
        if y_cursor == content_y:
            y_cursor += max(4, line_height // 2)

        # Compute element bottom including padding and margin
        content_height = y_cursor - content_y
        total_height = padding_top + content_height + padding_bottom
        element_bottom = y0 + total_height

        # Draw background now that we know height
        if bg and bg != 'transparent':
            canvas.create_rectangle(x0, y0, x0 + padding_left + content_width + padding_right, element_bottom, fill=bg, outline='')

        # Draw outside marker after computing geometry so we know the y-position
        if marker_text and list_style_position == 'outside':
            marker_x = content_x - (marker_width + marker_gap)
            marker_y = content_y
            canvas.create_text(marker_x, marker_y, text=marker_text, anchor='nw', font=font, fill=color)

        # Compute border
        border = Border()
        if styles.get("border"):
            shorthand = "border"
            shorthand_value = styles.get(shorthand)
            reader = csv.reader(shorthand_value, delimeter=" ")
                    
            for property_ in ["width", "style", "color"]:
                for border_part_name in ["top", "right", "bottom", "left"]:
                    styles.update({
                        f"border-{border_part_name}-{property}"
                    })

        
        for border_part_name in ["top", "right", "bottom", "left"]:
            shorthand = f"border-{border_part_name}"
            if styles.get(shorthand):
                shorthand_value = styles.get(shorthand)
                reader = csv.reader(shorthand_value, delimeter=" ")
                border.pieces[border_part_name].width = reader[0]
                border.pieces[border_part_name].style = reader[1]
                border.pieces[border_part_name].color = reader[3]
            else:
                if styles.get(shorthand+"-color"):
                    border.pieces[border_part_name].color=styles.get(shorthand+"-color")

                if styles.get(shorthand+"-style"):
                    border.pieces[border_part_name].style=styles.get(shorthand+"-style")
                
                if styles.get(shorthand+"-width"):
                    border.pieces[border_part_name].color=styles.get(shorthand+"-width")

        # Draw the border
        

        return element_bottom + margin_bottom

    def _layout_child(self, canvas, node, x, y, width, parent_font, parent_color):
        if isinstance(node, htmlm.HTMLTextNode):
            if node.text.strip():
                canvas.create_text(x, y, text=node.text.strip(), anchor='nw', font=parent_font, fill=parent_color)
                return y + parent_font.metrics('linespace')
            return y
        elif isinstance(node, htmlm.HTMLElement):
            return self._layout_block(canvas, node, x, y, width)
        return y


# Integrate renderer into the app
Z_RENDERER = None

def _ensure_renderer(root=None):
    global Z_RENDERER
    if Z_RENDERER is None:
        Z_RENDERER = PageRenderer(root)


# Add render_page method to ZerolfieWebView
def render_page(self, page):
    if not page or not page.dom:
        self.page_canvas.delete('all')
        self.page_canvas.configure(scrollregion=(0, 0, 0, 0))
        return
    width = self.page_canvas.winfo_width()
    if width < 50:
        # Canvas not laid out yet; try again shortly with a small delay
        self.root.after(30, lambda p=page: self.render_page(p))
        return
    _ensure_renderer(self.root)
    Z_RENDERER.layout_and_paint(self.page_canvas, page.dom, width)

# Bind method to class
ZerolfieWebView.render_page = render_page


if __name__ == "__main__":
    main()
