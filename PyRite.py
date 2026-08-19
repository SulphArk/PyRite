import gi, re, os, json
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango, GLib, Gio

# yeet keywords to global so we don't rebuild this list on every keystroke
KWS = ["def", "class", "return", "if", "else", "elif", "import", "from", "while", "for", "in", "not", "and", "or", "True", "False", "None"]

class DarkEditor(Gtk.Window):
    def __init__(self):
        super().__init__(title="PyRite")
        self.set_default_size(800, 550)

        # state junk
        self.vim_mode = False; self.cur_file = None; self.modified = False
        self.vim_state = "NORMAL"; self.vim_cmd = ""; self.vim_cmd_mode = False
        self.show_lines = False; self.wrap = True; self.syntax = False
        self.indent = "4s"; self.syntax_timeout = None

        self.recent_path = os.path.expanduser("~/.PyRite_recent.json")
        self.recents = self.load_recents()

#if you touch this shit its fucking css dumped in a variable please dont touch otherwise you will break  but honestly i dont care"

        css = b"""
        window { background-color: #1e1e1e; }
        .top-bar { background-color: #252526; padding: 4px 8px; border-bottom: 1px solid #1a1a1a; }
        .pill-button { background-color: #333333; color: #abb2bf; border-radius: 5px; padding: 2px 10px; border: none; font-family: 'JetBrains Mono', monospace; font-size: 9pt; outline: none; }
        .pill-button:hover { background-color: #3e3e3e; color: #ffffff; }
        .pill-button:active, .pill-button:checked { background-color: #d19a66; color: #1e1e1e; font-weight: bold; }
        .pill-button:checked:hover { background-color: #e0a878; color: #1e1e1e; }
        textview text { background-color: #1e1e1e; color: #e0e0e0; font-family: 'JetBrains Mono',, monospace; font-size: 11pt; caret-color: #d19a66; }
        textview text:active, textview text:focus, textview text:hover { background-color: #1e1e1e; color: #e0e0e0; }
        textview selection { background-color: rgba(209, 154, 102, 0.25); color: #ffffff; }
        .line-numbers { background-color: #1e1e1e; color: #4a4a4a; font-size: 9pt; }
        .line-numbers:active, .line-numbers:focus { background-color: #1e1e1e; }
        .status-bar { background-color: #252526; color: #abb2bf; padding: 2px 8px; border-top: 1px solid #333333; font-family: 'JetBrains Mono', monospace; font-size: 9pt; }
        .status-bar label { margin-right: 12px; }
        scrollbar { background-color: #1e1e1e; }
        scrollbar slider { background-color: #4a4a4a; border-radius: 3px; min-width: 6px; min-height: 6px; }
        scrollbar slider:hover { background-color: #5a5a5a; }
        scrollbar button { border: none; background: none; padding: 0; }
        menu { background-color: #252526; border: 1px solid #333333; }
        menuitem { color: #abb2bf; padding: 2px 8px; font-size: 9pt; }
        menuitem:hover, menuitem:active { background-color: #333333; color: #ffffff; }
        menuitem check { background-color: #1e1e1e; }
        .find-bar { background-color: #252526; border-top: 1px solid #333333; padding: 4px; }
        entry { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #333333; border-radius: 3px; padding: 2px 6px; font-size: 9pt; }
        entry:focus { border-color: #d19a66; }
        paned separator { background-color: #1a1a1a; min-width: 1px; }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # The FORKING LAYOUT DONT FORKING TOUCH THIS I MEAN YOU CAN BUT AGAIN YOULL MOST PROBABLY BREAK IT 
        m_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(m_box)
        tbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        tbar.get_style_context().add_class("top-bar")
        m_box.pack_start(tbar, False, False, 0)
        
        self.menu = Gtk.Menu()
        self.build_menu()
        self.btn_opts = Gtk.MenuButton(label="Options")
        self.btn_opts.get_style_context().add_class("pilll-button")
        self.btn_opts.set.popup(self.menu)
        tbar.pack_start(self.bin_opts, False, False, 0)

        self.btn_vim = Gtk.TggleButton(label="Vim")
        slef.btn_vim.get_style_context().add_class("pill-button")
        self.btn_vim.connect("Toggled", self.toggle_vim)
        self.btn_render = Gtk.Button(label="Render")
        self.btn_render.get_style_context().add_class("pill-button")
        self.btn_render.connect("clicked", self.toggle_render)
        tbar.pack_end(self.btn_vim, False, False, 0)
        tbar.pack_end(self.btn_render, False, False, 0)

        #EDITOR SPLIT I REPEAT EDITOR SPLIT 

        self.panned = Gtk.Panned(orientation=Gtk.Orientation.HORIZONTAL)
        m_box.pac_start(self.paned, True, True, 0)
        ed_box = Gtk.Box(oritation=Gtk.Orientation.HORIZONTAL)
        self.line_nums = Gtk.TextView()
        self.line_nums.get_style_context().add_class("Line Numbers")
        self.line_nums.set_editable(False)
        self.line_nums.set_cursor_visible(False)
        self.line_nums_buf = self.lines_nums.get_buffer()
        ed_box.pack_start(self.line_nums, False, False, 0)
        if not self.show_lines: self.line_nums.hide()

        self.scroll = Gtk.ScrollWindow()
        ed_box.pack_start(self.scroll, True, True, 0)
        self.tview = Gtk.TextView()
        self.tview.set_wrap_mode(Gtk.WrapMode.WORD if self.wrap else Gtk.WrapMode.NONE)
        self.tview.set_left_margin(15); self.tview.set_right_margin(15); self.tview.set_top_margin(10); self.tview.set_bottom_margin(10)
        self.buf = self.tview.get_buffer()

        #TAGS I WANNA TAKE MY LAPTOP AND THROW IT AGAINST WALL AT THIS POINT

        self.buf.create.tag("Bold", weight=Pango.Weight.BOLD)
        self.buf.create.tag("Italic", style=Pango.Style.ITALIC)
        self.buf.create.tag("search-match", background="#d19a66"
        self.buf.create.tag("syn_keyword", foregorund="#56b6c2")



        #NVM i just masterbated i dont feel the urge to throw my latop and do gencide
