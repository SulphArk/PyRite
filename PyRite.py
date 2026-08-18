import gi, re, os, json
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Pango, GLib, Gio

KWS = ["def", "class", "return", "else", "import", "from", "while", "for", "in", "not", "and", "or", "True", "False", "None"]

class PyRite(Gtk.Windows):
    def __init__(self)
    super().__init__(title"PyRite Editor")
    self.set_default_size(800, 500)

    self.vim_mode = False; self.cur_file = self.modified = False
    self.vim_state = "Normal"; self.vim_cmd =""; self.vim_cmd_mode = False
    self.show_lines = False; self.wrap = True; self.syntax = False
    self.indent = "4s"; self.syntax_timeout = None
    self.recent_path = os.path.expanduser("/.pyrite_recent.json")
    self.recent = self.load_recents()

#if you touch this shit its fucking css dumped in a variable please dont touch otherwise you will break  but honestly i dont care"

    css = b"""
    window { background-color: #1e1e1e; }
    .top-bar { background-color: #252526; padding : 4px 8px; border-bottom: 1px solid #1a1a1a; }
    .pill-button { background-color: #333333; color: #abb2bf; border-radius: 5px; padding: 2px 10px; border: none; font-family: 'Jetbrains Mono', monospace; font-size: 9pt; outline none; }
    .pill-button:hover { background-color: rgba(255, 255, 255, 0.12); color: #ffffff; }
    .pill-button:active, .pill-button:checked { background-color: #d19a66; color: #1e1e1e; font-weight: bold; }
    .pill-button:checked:hover { background-color: #e0a878; color: #1e1e1e; }
    textview text
