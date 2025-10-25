import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import math
import qrcode
from PIL import Image, ImageTk, ImageDraw, ImageFont
from barcode import Code128, Code39, EAN13, EAN8, UPCA
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A3, letter, legal
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
import io
import os
import platform
import subprocess
import tempfile
import uuid
import shutil
from pathlib import Path
import threading
import time

# --- Configuration & Global Variables ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Colors
PRIMARY_COLOR = "#3b82f6"
HIGHLIGHT_COLOR = "#2563eb"
SUCCESS_COLOR = "#10b981"
DANGER_COLOR = "#ef4444"
WARNING_COLOR = "#f59e0b"
SECONDARY_COLOR = "#6b7280"
BG_COLOR = "#dbeafe"
WHITE_COLOR = "#ffffff"
TEXT_COLOR = "#1f2937"
RULER_COLOR = "#f0f0f0"
RULER_BORDER_COLOR = "#ccc"
RULER_TICK_COLOR = "#666"
BLACK_COLOR = "#000000"

class NumberingSystemApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Numbering System")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.root.configure(fg_color=BG_COLOR)
        
        # Global variables
        self.current_page = 1
        self.numbering_heads = []
        self.selected_head_id = None
        self.is_dragging = False
        self.drag_item = None
        self.drag_offset = {"x": 0, "y": 0}
        self.zoom_level = 1.0
        self.background_image = None
        self.paper_rotation = 0
        self.paper_orientation = 'portrait'
        self.paper_sizes = {
            'A4': {'width': 210, 'height': 297},
            'A3': {'width': 297, 'height': 420},
            'Letter': {'width': 216, 'height': 279},
            'Legal': {'width': 216, 'height': 356}
        }
        self.available_fonts = self.load_available_fonts()
        self.paper_px_w = 794  # pixels for A4
        self.paper_px_h = 1123
        self.view_width = 800
        self.view_height = 600
        self.scale = 3.78  # pixels per mm
        self.current_unit = 'mm'
        
        # Store references to images to prevent garbage collection
        self.image_references = {}

        # Numbering variables
        self.start_num_var = tk.StringVar(value="1")
        self.step_var = tk.StringVar(value="1")
        self.total_pages_var = tk.StringVar(value="10")
        self.copies_var = tk.StringVar(value="1")
        self.skip_var = tk.StringVar(value="0")
        self.order_var = tk.StringVar(value="Ascending")

        # Scrollbar references
        self.h_scroll = None
        self.v_scroll = None
        self.bl_corner = None
        self.tr_corner = None
        self.br_corner = None

        self.setup_ui()
        self.add_numbering_head()
        self.update_preview()
        
        # Initial setup
        self.root.after_idle(self.initial_fit)
        self.apply_zoom()

    def initial_fit(self):
        self.root.update_idletasks()
        self.view_width = self.horizontal_ruler.winfo_width()
        self.view_height = self.vertical_ruler.winfo_height()

    def validate_numeric_input(self, value):
        """Validate numeric input - allow empty string or numbers"""
        if value == "":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def get_pdf_font(self, head):
        font_map = {
            'Arial': 'Helvetica',
            'Arial Black': 'Helvetica-Bold',
            'Arial Narrow': 'Helvetica',
            'Calibri': 'Helvetica',
            'Cambria': 'Times-Roman',
            'Comic Sans MS': 'Helvetica',
            'Consolas': 'Courier',
            'Courier New': 'Courier',
            'Georgia': 'Times-Roman',
            'Impact': 'Helvetica-Bold',
            'Times New Roman': 'Times-Roman',
            'Trebuchet MS': 'Helvetica',
            'Verdana': 'Helvetica',
            'Helvetica': 'Helvetica',
            'Garamond': 'Times-Roman',
            'Bookman': 'Times-Roman',
            'Avant Garde': 'Helvetica',
            'Futura': 'Helvetica',
            'Optima': 'Helvetica',
            'Baskerville': 'Times-Roman',
            'Didot': 'Times-Roman',
        }
        base_font = font_map.get(head['font'], 'Helvetica')
        if head['bold'] and head['italic']:
            if base_font == 'Helvetica':
                return 'Helvetica-BoldOblique'
            elif base_font == 'Times-Roman':
                return 'Times-BoldItalic'
            elif base_font == 'Courier':
                return 'Courier-BoldOblique'
        elif head['bold']:
            if base_font == 'Helvetica':
                return 'Helvetica-Bold'
            elif base_font == 'Times-Roman':
                return 'Times-Bold'
            elif base_font == 'Courier':
                return 'Courier-Bold'
        elif head['italic']:
            if base_font == 'Helvetica':
                return 'Helvetica-Oblique'
            elif base_font == 'Times-Roman':
                return 'Times-Italic'
            elif base_font == 'Courier':
                return 'Courier-Oblique'
        return base_font

    def load_available_fonts(self):
        # Common fonts
        common_fonts = [
            'Arial', 'Arial Black', 'Arial Narrow', 'Arial Rounded MT Bold',
            'Calibri', 'Cambria', 'Candara', 'Century Gothic',
            'Comic Sans MS', 'Consolas', 'Courier New', 'Georgia',
            'Impact', 'Lucida Console', 'Lucida Sans Unicode', 'Microsoft Sans Serif',
            'Palatino Linotype', 'Segoe UI', 'Tahoma', 'Times New Roman',
            'Trebuchet MS', 'Verdana', 'Symbol', 'Webdings', 'Wingdings',
            'MS Sans Serif', 'MS Serif', 'Helvetica', 'Garamond', 'Bookman',
            'Avant Garde', 'Futura', 'Optima', 'Baskerville', 'Didot'
        ]
        return sorted(common_fonts)

    def setup_ui(self):
        # Configure root grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self.root, fg_color=WHITE_COLOR, corner_radius=10)
        self.header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.header_frame.grid_columnconfigure((0, 1), weight=1)

        title_label = ctk.CTkLabel(self.header_frame, text="Numbering System", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_COLOR)
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        print_btn = ctk.CTkButton(btn_frame, text="Print", command=self.print_preview, fg_color=SUCCESS_COLOR, hover_color="#059669", width=100)
        print_btn.grid(row=0, column=0, padx=5)

        pdf_btn = ctk.CTkButton(btn_frame, text="Export PDF", command=self.export_pdf, fg_color="#8b5cf6", hover_color="#7c3aed", width=100)
        pdf_btn.grid(row=0, column=1, padx=5)

        export_images_btn = ctk.CTkButton(btn_frame, text="Export Images", command=self.export_images, fg_color="#f59e0b", hover_color="#d97706", width=100)
        export_images_btn.grid(row=0, column=2, padx=5)

        reset_btn = ctk.CTkButton(btn_frame, text="Reset", command=self.reset_all, fg_color=DANGER_COLOR, hover_color="#dc2626", width=100)
        reset_btn.grid(row=0, column=3, padx=5)

        add_btn = ctk.CTkButton(btn_frame, text="Add Header", command=self.add_numbering_head, fg_color="#6366f1", hover_color="#4f46e5", width=100)
        add_btn.grid(row=0, column=4, padx=5)

        # Paper Controls
        self.create_paper_controls()

        # Main content
        self.main_content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_content_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.main_content_frame.grid_columnconfigure(0, weight=0)
        self.main_content_frame.grid_columnconfigure(1, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # Left panel - Settings
        self.create_settings_panel()

        # Right Panel - Preview
        self.create_preview_panel()

    def create_paper_controls(self):
        """Creates paper controls section full width."""
        self.paper_controls_frame = ctk.CTkFrame(self.root, fg_color=WHITE_COLOR, corner_radius=8, border_width=0)
        self.paper_controls_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        main_container = ctk.CTkFrame(self.paper_controls_frame, fg_color="transparent")
        main_container.pack(fill="x", padx=10, pady=5)

        # Controls row
        controls_row = ctk.CTkFrame(main_container, fg_color="transparent")
        controls_row.pack(fill="x")
        controls_row.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)
        controls_row.grid_rowconfigure(0, weight=1)

        # Paper Size
        paper_size_frame = ctk.CTkFrame(controls_row, fg_color="transparent")
        paper_size_frame.grid(row=0, column=0, padx=15, pady=2, sticky="ew")
        ctk.CTkLabel(paper_size_frame, text="Paper Size", text_color=TEXT_COLOR).pack(anchor="w")
        self.paper_var = tk.StringVar(value="A4")
        self.paper_combo = ctk.CTkComboBox(paper_size_frame, values=list(self.paper_sizes.keys()) + ["Custom"], variable=self.paper_var, fg_color=WHITE_COLOR, button_color=PRIMARY_COLOR, button_hover_color=HIGHLIGHT_COLOR, text_color=TEXT_COLOR, width=120, command=self.update_paper_size)
        self.paper_combo.pack(pady=(2, 0), fill="x")

        # Orientation
        orientation_frame = ctk.CTkFrame(controls_row, fg_color="transparent")
        orientation_frame.grid(row=0, column=1, padx=15, pady=2, sticky="ew")
        ctk.CTkLabel(orientation_frame, text="Orientation", text_color=TEXT_COLOR).pack(anchor="w")
        orient_btn_frame = ctk.CTkFrame(orientation_frame, fg_color="transparent")
        orient_btn_frame.pack(pady=(2, 0), fill="x")
        self.portrait_btn = ctk.CTkButton(orient_btn_frame, text="Portrait", command=lambda: self.set_orientation('portrait'), fg_color=PRIMARY_COLOR if self.paper_orientation == 'portrait' else WHITE_COLOR, hover_color=HIGHLIGHT_COLOR, text_color=WHITE_COLOR if self.paper_orientation == 'portrait' else TEXT_COLOR, border_width=1, border_color="#d1d5db", width=60)
        self.portrait_btn.pack(side="left", padx=(0, 1))
        self.landscape_btn = ctk.CTkButton(orient_btn_frame, text="Landscape", command=lambda: self.set_orientation('landscape'), fg_color=PRIMARY_COLOR if self.paper_orientation == 'landscape' else WHITE_COLOR, hover_color=HIGHLIGHT_COLOR, text_color=WHITE_COLOR if self.paper_orientation == 'landscape' else TEXT_COLOR, border_width=1, border_color="#d1d5db", width=60)
        self.landscape_btn.pack(side="left", padx=1)

        # Rotation
        rotation_frame = ctk.CTkFrame(controls_row, fg_color="transparent")
        rotation_frame.grid(row=0, column=2, padx=15, pady=2, sticky="ew")
        ctk.CTkLabel(rotation_frame, text="Rotation", text_color=TEXT_COLOR).pack(anchor="w")
        rotation_buttons_frame = ctk.CTkFrame(rotation_frame, fg_color="transparent")
        rotation_buttons_frame.pack(pady=(2, 0), fill="x")
        self.rot_btns = []
        rotations = [0, 90, 180, 270]
        for i, deg in enumerate(rotations):
            btn = ctk.CTkButton(rotation_buttons_frame, text=f"{deg}°", command=lambda d=deg: self.rotate_paper(d), fg_color=PRIMARY_COLOR if self.paper_rotation == deg else WHITE_COLOR, hover_color=HIGHLIGHT_COLOR, text_color=WHITE_COLOR if self.paper_rotation == deg else TEXT_COLOR, border_width=1, border_color="#d1d5db", width=40)
            btn.pack(side="left", padx=0 if i == 0 else 1)
            self.rot_btns.append(btn)

        # Background Color
        bg_color_outer = ctk.CTkFrame(controls_row, fg_color="transparent")
        bg_color_outer.grid(row=0, column=3, padx=15, pady=2, sticky="ew")
        ctk.CTkLabel(bg_color_outer, text="Background Color", text_color=TEXT_COLOR).pack(anchor="w")
        color_input_frame = ctk.CTkFrame(bg_color_outer, fg_color="transparent")
        color_input_frame.pack(pady=(2, 0), fill="x")
        self.color_preview = ctk.CTkFrame(color_input_frame, width=20, height=20, fg_color="#ffffff", border_width=1, border_color="#d1d5db", corner_radius=4)
        self.color_preview.pack(side="left", padx=(0, 2))
        self.color_preview.grid_propagate(False)
        self.bg_color_var = tk.StringVar(value="#ffffff")
        self.bg_color_entry = ctk.CTkEntry(color_input_frame, textvariable=self.bg_color_var, width=60, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR)
        self.bg_color_entry.pack(side="left", padx=(0, 2))
        self.bg_color_entry.bind("<KeyRelease>", self.update_bg_color)
        self.color_btn = ctk.CTkButton(color_input_frame, text="Pick", command=self.pick_color, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR, width=40)
        self.color_btn.pack(side="left")

        # Custom Size
        self.custom_frame = ctk.CTkFrame(controls_row, fg_color="transparent")
        self.custom_frame.grid(row=0, column=4, padx=15, pady=2, sticky="ew")
        ctk.CTkLabel(self.custom_frame, text="Custom Size", text_color=TEXT_COLOR).pack(anchor="w")
        size_inputs_frame = ctk.CTkFrame(self.custom_frame, fg_color="transparent")
        size_inputs_frame.pack(pady=(2, 0), fill="x")
        
        self.paper_width_var = tk.StringVar(value="210")
        ctk.CTkLabel(size_inputs_frame, text="W:", text_color=TEXT_COLOR, width=20).pack(side="left", padx=(0, 1))
        width_entry = ctk.CTkEntry(size_inputs_frame, textvariable=self.paper_width_var, width=50, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR)
        width_entry.pack(side="left", padx=(0, 2))
        width_entry.bind('<KeyRelease>', self.on_custom_size_change)

        self.paper_height_var = tk.StringVar(value="297")
        ctk.CTkLabel(size_inputs_frame, text="H:", text_color=TEXT_COLOR, width=20).pack(side="left", padx=(0, 1))
        height_entry = ctk.CTkEntry(size_inputs_frame, textvariable=self.paper_height_var, width=50, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR)
        height_entry.pack(side="left", padx=(0, 2))
        height_entry.bind('<KeyRelease>', self.on_custom_size_change)

        self.paper_unit_var = tk.StringVar(value="mm")
        ctk.CTkLabel(size_inputs_frame, text="U:", text_color=TEXT_COLOR, width=20).pack(side="left", padx=(0, 1))
        unit_combo = ctk.CTkComboBox(size_inputs_frame, values=["mm", "inch"], variable=self.paper_unit_var, fg_color=WHITE_COLOR, button_color=PRIMARY_COLOR, button_hover_color=HIGHLIGHT_COLOR, text_color=TEXT_COLOR, width=50)
        unit_combo.pack(side="left")
        unit_combo.bind('<<ComboboxSelected>>', self.on_custom_size_change)

        self.custom_frame.grid_remove()

        # Ruler Unit
        ruler_frame = ctk.CTkFrame(controls_row, fg_color="transparent")
        ruler_frame.grid(row=0, column=6, padx=15, pady=2, sticky="ew")
        ctk.CTkLabel(ruler_frame, text="Ruler Unit", text_color=TEXT_COLOR).pack(anchor="w")
        self.ruler_unit_var = tk.StringVar(value="mm")
        ruler_combo = ctk.CTkComboBox(ruler_frame, values=["mm", "cm", "inch"], variable=self.ruler_unit_var, fg_color=WHITE_COLOR, button_color=PRIMARY_COLOR, button_hover_color=HIGHLIGHT_COLOR, text_color=TEXT_COLOR, width=80, command=self.on_ruler_unit_change)
        ruler_combo.pack(pady=(2, 0), fill="x")

        # Background Buttons
        bg_btn_outer = ctk.CTkFrame(controls_row, fg_color="transparent")
        bg_btn_outer.grid(row=0, column=5, padx=(15, 0), pady=2, sticky="ew")
        ctk.CTkLabel(bg_btn_outer, text="Background", text_color=TEXT_COLOR).pack(anchor="w")
        bg_btn_frame = ctk.CTkFrame(bg_btn_outer, fg_color="transparent")
        bg_btn_frame.pack(pady=(2, 0), fill="x")
        upload_btn = ctk.CTkButton(bg_btn_frame, text="Add Background", command=self.upload_background, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR, width=90)
        upload_btn.pack(side="left", padx=(0, 2))
        remove_btn = ctk.CTkButton(bg_btn_frame, text="Remove Background", command=self.remove_background, fg_color=DANGER_COLOR, hover_color="#dc2626", width=90)
        remove_btn.pack(side="left")

    def on_ruler_unit_change(self, value):
        self.update_ruler_ticks(self.view_width, self.view_height)

    def create_settings_panel(self):
        """Creates the left settings panel."""
        self.settings_frame = ctk.CTkScrollableFrame(
            self.main_content_frame, 
            label_text="", 
            width=350, 
            corner_radius=10,
            fg_color=WHITE_COLOR,
            scrollbar_button_color=PRIMARY_COLOR
        )
        self.settings_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="nsew")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        def settings_vertical_scroll(event):
            if hasattr(self.settings_frame, '_parent_canvas'):
                self.settings_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.settings_frame.bind("<MouseWheel>", settings_vertical_scroll)

        # Numbering Settings
        self.create_numbering_settings(self.settings_frame)

        # Heads list
        self.create_heads_list_panel(self.settings_frame)

        # Head Properties
        self.properties_frame = ctk.CTkFrame(self.settings_frame, fg_color=WHITE_COLOR, corner_radius=8, border_width=1)
        self.properties_frame.pack(fill="both", expand=True, padx=10, pady=5)

        def props_vertical_scroll(event):
            if hasattr(self.settings_frame, '_parent_canvas'):
                self.settings_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.properties_frame.bind("<MouseWheel>", props_vertical_scroll)

        props_label = ctk.CTkLabel(self.properties_frame, text="Head Properties", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR)
        props_label.pack(anchor="w", padx=10, pady=(10, 5))

        self.props_container = ctk.CTkFrame(self.properties_frame, fg_color="transparent")
        self.props_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.update_properties_panel(None)

    def create_numbering_settings(self, parent):
        num_settings_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=WHITE_COLOR, border_width=1)
        num_settings_frame.pack(fill="x", pady=5)

        def num_vertical_scroll(event):
            if hasattr(self.settings_frame, '_parent_canvas'):
                self.settings_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        num_settings_frame.bind("<MouseWheel>", num_vertical_scroll)

        num_label = ctk.CTkLabel(num_settings_frame, text="Numbering Settings", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR)
        num_label.pack(anchor="w", padx=10, pady=(10, 5))

        settings = [
            ("Start Number", self.start_num_var, "1"),
            ("Step", self.step_var, "1"),
            ("Total Pages", self.total_pages_var, "10"),
            ("Copies", self.copies_var, "1"),
            ("Skip", self.skip_var, "0")
        ]

        for label_text, var, default in settings:
            row_frame = ctk.CTkFrame(num_settings_frame, fg_color="transparent")
            row_frame.pack(padx=5, pady=2, fill="x")
            label = ctk.CTkLabel(row_frame, text=label_text, text_color=TEXT_COLOR, width=120, anchor="w")
            label.pack(side="left")
            var.set(default)
            entry = ctk.CTkEntry(row_frame, textvariable=var, width=60, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR)
            entry.pack(side="right", padx=5)
            entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
            var.trace_add("write", lambda name, index, mode, v=var: self.safe_update_preview(v))

        # Order
        order_frame = ctk.CTkFrame(num_settings_frame, fg_color="transparent")
        order_frame.pack(padx=5, pady=(2, 10), fill="x")
        label = ctk.CTkLabel(order_frame, text="Order", text_color=TEXT_COLOR, width=120, anchor="w")
        label.pack(side="left")
        self.order_var.set("Ascending")
        order_combo = ctk.CTkComboBox(order_frame, values=["Ascending", "Descending"], variable=self.order_var, fg_color=WHITE_COLOR, button_color=PRIMARY_COLOR, button_hover_color=HIGHLIGHT_COLOR, text_color=TEXT_COLOR, width=120)
        order_combo.pack(side="right", padx=5)
        order_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

    def safe_update_preview(self, var):
        """Safely update preview only if input is valid"""
        try:
            if var.get() == "" or self.validate_numeric_input(var.get()):
                self.update_preview()
        except:
            pass

    def create_heads_list_panel(self, parent):
        heads_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=WHITE_COLOR, border_width=1)
        heads_frame.pack(fill="x", pady=5)

        def heads_frame_vertical_scroll(event):
            if hasattr(self.settings_frame, '_parent_canvas'):
                self.settings_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        heads_frame.bind("<MouseWheel>", heads_frame_vertical_scroll)

        heads_label_frame = ctk.CTkFrame(heads_frame, fg_color="transparent")
        heads_label_frame.pack(fill="x", padx=10, pady=(10, 5))
        heads_label = ctk.CTkLabel(heads_label_frame, text="Numbering Heads", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR)
        heads_label.pack(side="left")

        all_btn = ctk.CTkButton(heads_label_frame, text="All", command=self.select_all_heads, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR, width=50)
        all_btn.pack(side="right", padx=5)
        add_head_btn = ctk.CTkButton(heads_label_frame, text="Add", command=self.add_numbering_head, fg_color=SUCCESS_COLOR, hover_color="#059669", width=50)
        add_head_btn.pack(side="right", padx=5)

        # Heads list
        list_frame = ctk.CTkFrame(heads_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.heads_scroll = ctk.CTkScrollableFrame(list_frame, fg_color=WHITE_COLOR, scrollbar_button_color=PRIMARY_COLOR)
        self.heads_scroll.pack(fill="both", expand=True, padx=1, pady=1)

        def heads_scroll_vertical_scroll(event):
            if hasattr(self.heads_scroll, '_parent_canvas'):
                self.heads_scroll._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.heads_scroll.bind("<MouseWheel>", heads_scroll_vertical_scroll)

    def select_all_heads(self):
        all_selected = all(head['selected'] for head in self.numbering_heads)
        for head in self.numbering_heads:
            head['selected'] = not all_selected
        self.update_heads_list()
        self.update_preview()

    def update_heads_list(self):
        # Clear existing items
        for widget in self.heads_scroll.winfo_children():
            widget.destroy()

        for i, head in enumerate(self.numbering_heads):
            item_frame = ctk.CTkFrame(self.heads_scroll, fg_color="transparent")
            item_frame.pack(fill="x", padx=5, pady=2)

            # Checkbox
            check_var = tk.BooleanVar(value=head['selected'])
            check = ctk.CTkCheckBox(item_frame, text="", variable=check_var, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR,
                                    command=lambda idx=i, v=check_var.get(): self.toggle_head_selection(idx, v))
            check.pack(side="left", padx=(0, 5))

            # Name label
            label_color = PRIMARY_COLOR if i == self.selected_head_id else TEXT_COLOR
            name_label = ctk.CTkLabel(item_frame, text=head['name'], text_color=label_color, anchor="w")
            name_label.pack(side="left", fill="x", expand=True, padx=(0, 5))
            name_label.bind("<Button-1>", lambda e, idx=i: self.select_head(idx))

            # Delete button
            del_btn = ctk.CTkButton(item_frame, text="×", width=25, height=25, fg_color=DANGER_COLOR, hover_color="#dc2626",
                                    command=lambda idx=i: self.delete_head(idx), font=ctk.CTkFont(size=14, weight="bold"))
            del_btn.pack(side="right")

    def toggle_head_selection(self, idx, value):
        self.numbering_heads[idx]['selected'] = value
        self.update_preview()

    def delete_head(self, idx):
        if messagebox.askyesno("Delete Head", f"Are you sure you want to delete {self.numbering_heads[idx]['name']}?"):
            del self.numbering_heads[idx]
            if self.selected_head_id == idx:
                self.selected_head_id = None if not self.numbering_heads else max(0, idx - 1)
            self.update_heads_list()
            self.update_properties_panel(None if self.selected_head_id is None else self.numbering_heads[self.selected_head_id])
            self.update_preview()

    def select_head(self, head_id):
        self.selected_head_id = head_id
        self.update_heads_list()
        if head_id < len(self.numbering_heads):
            head = self.numbering_heads[head_id]
            self.update_properties_panel(head)

    def create_preview_panel(self):
        """Creates the right preview panel with rulers and scrollbars."""
        self.preview_frame = ctk.CTkFrame(self.main_content_frame, corner_radius=10, fg_color=WHITE_COLOR, border_width=0)
        self.preview_frame.grid(row=0, column=1, padx=(10, 0), pady=5, sticky="nsew")
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        # Preview Header
        preview_header = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        preview_header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        preview_header.grid_columnconfigure(0, weight=1)

        preview_label = ctk.CTkLabel(preview_header, text="Preview", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_COLOR)
        preview_label.grid(row=0, column=0, sticky="w")

        nav_frame = ctk.CTkFrame(preview_header, fg_color="transparent")
        nav_frame.grid(row=0, column=1, sticky="e")
        prev_btn = ctk.CTkButton(nav_frame, text="Previous", command=self.previous_page, fg_color=SECONDARY_COLOR, hover_color="#4b5563", width=80)
        prev_btn.grid(row=0, column=0, padx=5)
        self.page_label = ctk.CTkLabel(nav_frame, text="Page 1 of 10", text_color=TEXT_COLOR)
        self.page_label.grid(row=0, column=1, padx=5)
        next_btn = ctk.CTkButton(nav_frame, text="Next", command=self.next_page, fg_color=SECONDARY_COLOR, hover_color="#4b5563", width=80)
        next_btn.grid(row=0, column=2, padx=5)

        # Zoom controls
        self.zoom_label = ctk.CTkLabel(nav_frame, text="100%", text_color=TEXT_COLOR, width=40)
        self.zoom_label.grid(row=0, column=3, padx=(10, 5))
        zoom_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
        zoom_container.grid(row=0, column=4, padx=5)
        zoom_out_btn = ctk.CTkButton(zoom_container, text="-", command=self.zoom_out, width=25, height=25, fg_color=SECONDARY_COLOR, hover_color="#4b5563")
        zoom_out_btn.pack(side="left", padx=(0, 2))
        zoom_in_btn = ctk.CTkButton(zoom_container, text="+", command=self.zoom_in, width=25, height=25, fg_color=SECONDARY_COLOR, hover_color="#4b5563")
        zoom_in_btn.pack(side="left", padx=(0, 2))
        reset_zoom_btn = ctk.CTkButton(zoom_container, text="1:1", command=self.reset_zoom, width=40, height=25, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR)
        reset_zoom_btn.pack(side="left")

        # Preview Area with Rulers and Scrollbars
        self.preview_scroll_frame = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        self.preview_scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.preview_scroll_frame.grid_columnconfigure(0, weight=0, minsize=30)
        self.preview_scroll_frame.grid_columnconfigure(1, weight=1)
        self.preview_scroll_frame.grid_columnconfigure(2, weight=0, minsize=20)
        self.preview_scroll_frame.grid_rowconfigure(0, weight=0, minsize=30)
        self.preview_scroll_frame.grid_rowconfigure(1, weight=1)
        self.preview_scroll_frame.grid_rowconfigure(2, weight=0, minsize=20)

        # Top-left corner
        corner_frame = ctk.CTkFrame(self.preview_scroll_frame, width=30, height=30, 
                                   fg_color=RULER_COLOR, border_width=1, border_color=RULER_BORDER_COLOR)
        corner_frame.grid(row=0, column=0, sticky="nw")
        corner_frame.grid_propagate(False)

        # Horizontal Ruler
        self.horizontal_ruler = tk.Canvas(self.preview_scroll_frame, height=30, bg=RULER_COLOR, highlightthickness=0, bd=1, relief="solid", highlightbackground=RULER_BORDER_COLOR)
        self.horizontal_ruler.grid(row=0, column=1, sticky="ew")

        # Vertical Ruler
        self.vertical_ruler = tk.Canvas(self.preview_scroll_frame, width=30, bg=RULER_COLOR, highlightthickness=0, bd=1, relief="solid", highlightbackground=RULER_BORDER_COLOR)
        self.vertical_ruler.grid(row=1, column=0, sticky="ns")

        # Create container for canvas
        self.preview_container = tk.Frame(self.preview_scroll_frame, bg="#ffffff")
        self.preview_container.grid(row=1, column=1, sticky="nsew")

        # Preview Canvas inside container
        self.preview_canvas = tk.Canvas(self.preview_container, bg="#ffffff", highlightthickness=0)
        self.preview_canvas.pack(fill="both", expand=True)

        # Create scrollbars and corners (initially hidden)
        self.h_scroll = ctk.CTkScrollbar(self.preview_scroll_frame, orientation="horizontal", command=self.preview_canvas.xview)
        self.v_scroll = ctk.CTkScrollbar(self.preview_scroll_frame, orientation="vertical", command=self.preview_canvas.yview)

        self.bl_corner = ctk.CTkFrame(self.preview_scroll_frame, width=30, height=30, fg_color="transparent")
        self.tr_corner = ctk.CTkFrame(self.preview_scroll_frame, width=30, height=30, 
                                     fg_color=RULER_COLOR, border_width=1, border_color=RULER_BORDER_COLOR)
        self.br_corner = ctk.CTkFrame(self.preview_scroll_frame, width=30, height=30, fg_color="transparent")

        # Initially hide all extra
        self.h_scroll.grid_remove()
        self.v_scroll.grid_remove()
        self.bl_corner.grid_remove()
        self.tr_corner.grid_remove()
        self.br_corner.grid_remove()

        # Mouse wheel bindings for scrolling
        def vertical_scroll(event):
            self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def horizontal_scroll(event):
            self.preview_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind to canvas
        self.preview_canvas.bind("<MouseWheel>", vertical_scroll)
        self.preview_canvas.bind("<Shift-MouseWheel>", horizontal_scroll)
        # For Linux
        self.preview_canvas.bind("<Button-4>", lambda e: self.preview_canvas.yview_scroll(-1, "units"))
        self.preview_canvas.bind("<Button-5>", lambda e: self.preview_canvas.yview_scroll(1, "units"))
        self.preview_canvas.bind("<Shift-Button-4>", lambda e: self.preview_canvas.xview_scroll(-1, "units"))
        self.preview_canvas.bind("<Shift-Button-5>", lambda e: self.preview_canvas.xview_scroll(1, "units"))

        # Bind to the entire scroll frame for broader coverage
        self.preview_scroll_frame.bind("<MouseWheel>", vertical_scroll)
        self.preview_scroll_frame.bind("<Shift-MouseWheel>", horizontal_scroll)
        self.preview_scroll_frame.bind("<Button-4>", lambda e: self.preview_canvas.yview_scroll(-1, "units"))
        self.preview_scroll_frame.bind("<Button-5>", lambda e: self.preview_canvas.yview_scroll(1, "units"))
        self.preview_scroll_frame.bind("<Shift-Button-4>", lambda e: self.preview_canvas.xview_scroll(-1, "units"))
        self.preview_scroll_frame.bind("<Shift-Button-5>", lambda e: self.preview_canvas.xview_scroll(1, "units"))

        # Bind resize
        self.preview_scroll_frame.bind("<Configure>", self.on_configure)
        self.preview_canvas.bind("<Configure>", self.update_background)

        # Initial call
        self.update_scrollregion()
        self.update_ruler_ticks(self.view_width, self.view_height)
        self.update_scrollbars()

        # Bind events for drag
        self.preview_canvas.bind("<Button-1>", self.start_drag)
        self.preview_canvas.bind("<B1-Motion>", self.drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.stop_drag)

    def update_background(self, event=None):
        if not self.background_image:
            return
        canvas = self.preview_canvas
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w <= 1 or h <= 1:
            self.root.after(100, self.update_background)
            return
        try:
            bg_resized = self.background_image.resize((w, h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(bg_resized)
            self.image_references['bg_fixed'] = photo
            canvas.delete("bg_fixed")
            canvas.create_image(0, 0, image=photo, anchor="nw", tags="bg_fixed")
            canvas.tag_lower("bg_fixed")
        except Exception as e:
            print(f"Background update error: {e}")

    def zoom_in(self):
        self.zoom_level = min(self.zoom_level * 1.25, 5.0)
        self.apply_zoom()

    def zoom_out(self):
        self.zoom_level = max(self.zoom_level / 1.25, 0.2)
        self.apply_zoom()

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.apply_zoom()

    def apply_zoom(self):
        self.zoom_label.configure(text=f"{int(self.zoom_level * 100)}%")
        self.update_scrollregion()
        self.update_preview()
        self.update_scrollbars()

    def update_scrollregion(self):
        w = self.paper_px_w * self.zoom_level
        h = self.paper_px_h * self.zoom_level
        self.preview_canvas.configure(scrollregion=(0, 0, w, h))

    def on_configure(self, event):
        if event.widget == self.preview_scroll_frame:
            self.root.after_idle(self.update_ruler_after_resize)

    def update_ruler_after_resize(self):
        w = self.horizontal_ruler.winfo_width()
        h = self.vertical_ruler.winfo_height()
        if w > 0 and h > 0 and (w != self.view_width or h != self.view_height):
            self.view_width = w
            self.view_height = h
            self.update_ruler_ticks(w, h)
            self.update_scrollbars()

    def bind_scrollbar_events(self, scrollbar):
        """Bind wheel events to scrollbar."""
        if scrollbar:
            def vertical_scroll(event):
                self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            def horizontal_scroll(event):
                self.preview_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

            scrollbar.bind("<MouseWheel>", vertical_scroll)
            scrollbar.bind("<Shift-MouseWheel>", horizontal_scroll)
            scrollbar.bind("<Button-4>", lambda e: self.preview_canvas.yview_scroll(-1, "units"))
            scrollbar.bind("<Button-5>", lambda e: self.preview_canvas.yview_scroll(1, "units"))
            scrollbar.bind("<Shift-Button-4>", lambda e: self.preview_canvas.xview_scroll(-1, "units"))
            scrollbar.bind("<Shift-Button-5>", lambda e: self.preview_canvas.xview_scroll(1, "units"))

    def update_scrollbars(self):
        """Dynamically updates scrollbars and corners based on current paper size."""
        need_h = self.paper_px_w * self.zoom_level > self.view_width
        need_v = self.paper_px_h * self.zoom_level > self.view_height

        # Manage horizontal scrollbar
        if need_h:
            self.preview_canvas.configure(xscrollcommand=self.h_scroll.set)
            self.h_scroll.grid(row=2, column=1, sticky="ew")
            self.bl_corner.grid(row=2, column=0, sticky="ew")
            self.bind_scrollbar_events(self.h_scroll)
        else:
            self.preview_canvas.configure(xscrollcommand="")
            self.h_scroll.grid_remove()
            self.bl_corner.grid_remove()

        # Manage vertical scrollbar
        if need_v:
            self.preview_canvas.configure(yscrollcommand=self.v_scroll.set)
            self.v_scroll.grid(row=1, column=2, sticky="ns")
            self.tr_corner.grid(row=0, column=2, sticky="nw")
            self.bind_scrollbar_events(self.v_scroll)
        else:
            self.preview_canvas.configure(yscrollcommand="")
            self.v_scroll.grid_remove()
            self.tr_corner.grid_remove()

        # Manage bottom-right corner
        if need_h and need_v:
            self.br_corner.grid(row=2, column=2, sticky="nw")
        else:
            self.br_corner.grid_remove()

    def update_ruler_ticks(self, width, height):
        """Creates ticks and labels for rulers using Canvas for better appearance."""
        # Clear existing ticks
        self.horizontal_ruler.delete("all")
        self.vertical_ruler.delete("all")

        unit = self.ruler_unit_var.get()
        if unit == 'mm':
            unit_to_mm = 1
            minor_step_unit = 1
            major_interval_unit = 5
            label_interval_unit = 10
            div_suffix = 'mm'
        elif unit == 'cm':
            unit_to_mm = 10
            minor_step_unit = 1
            major_interval_unit = 5
            label_interval_unit = 10
            div_suffix = 'cm'
        elif unit == 'inch':
            unit_to_mm = 25.4
            minor_step_unit = 0.25
            major_interval_unit = 1
            label_interval_unit = 2
            div_suffix = '"'

        px_per_unit = self.scale * unit_to_mm
        epsilon = 1e-6

        # Horizontal ruler
        num_steps = int(width / (minor_step_unit * px_per_unit)) + 2
        for k in range(num_steps + 1):
            div = k * minor_step_unit
            pos_px = round(div * px_per_unit)
            if pos_px > width:
                break
            is_major = abs(math.fmod(div, major_interval_unit)) < epsilon
            is_label = abs(math.fmod(div, label_interval_unit)) < epsilon
            tick_len = 5
            if is_major:
                tick_len = 10
            if is_label:
                tick_len = 15
            self.horizontal_ruler.create_line(pos_px, 0, pos_px, tick_len, fill=RULER_TICK_COLOR, width=1)
            if is_label:
                if unit == 'inch':
                    label_text = f"{div:g}{div_suffix}"
                else:
                    label_text = f"{int(div)}{div_suffix}"
                self.horizontal_ruler.create_text(pos_px, tick_len + 6, text=label_text, anchor="n", fill=TEXT_COLOR, font=("Arial", 8))

        # Vertical ruler
        num_steps = int(height / (minor_step_unit * px_per_unit)) + 2
        for k in range(num_steps + 1):
            div = k * minor_step_unit
            pos_py = round(div * px_per_unit)
            if pos_py > height:
                break
            is_major = abs(math.fmod(div, major_interval_unit)) < epsilon
            is_label = abs(math.fmod(div, label_interval_unit)) < epsilon
            tick_len = 5
            if is_major:
                tick_len = 10
            if is_label:
                tick_len = 15
            self.vertical_ruler.create_line(0, pos_py, tick_len, pos_py, fill=RULER_TICK_COLOR, width=1)
            if is_label:
                if unit == 'inch':
                    label_text = f"{div:g}{div_suffix}"
                else:
                    label_text = f"{int(div)}{div_suffix}"
                self.vertical_ruler.create_text(tick_len + 6, pos_py, text=label_text, anchor="w", fill=TEXT_COLOR, font=("Arial", 8))

    def on_custom_size_change(self, event=None):
        try:
            width_str = self.paper_width_var.get()
            height_str = self.paper_height_var.get()
            unit = self.paper_unit_var.get()
            
            width = float(width_str) if width_str.strip() != "" else 210.0
            height = float(height_str) if height_str.strip() != "" else 297.0
            
            self.current_unit = unit
            self.apply_paper_size(width, height, unit)
        except (ValueError, tk.TclError):
            pass

    def set_orientation(self, orient):
        self.paper_orientation = orient
        default_color = WHITE_COLOR
        if orient == 'portrait':
            self.portrait_btn.configure(fg_color=PRIMARY_COLOR, text_color=WHITE_COLOR)
            self.landscape_btn.configure(fg_color=default_color, text_color=TEXT_COLOR)
        else:
            self.landscape_btn.configure(fg_color=PRIMARY_COLOR, text_color=WHITE_COLOR)
            self.portrait_btn.configure(fg_color=default_color, text_color=TEXT_COLOR)
        self.update_paper_size()

    def update_paper_size(self, value=None):
        size = self.paper_var.get()
        if size == "Custom":
            self.custom_frame.grid(row=0, column=4, padx=15, pady=2, sticky="ew")
            self.on_custom_size_change()
        else:
            self.custom_frame.grid_remove()
            self.current_unit = 'mm'
            if size in self.paper_sizes:
                w = self.paper_sizes[size]['width']
                h = self.paper_sizes[size]['height']
                self.apply_paper_size(w, h, 'mm')

    def apply_paper_size(self, width, height, unit):
        scale = 3.78 if unit == 'mm' else 96 if unit == 'inch' else 1
        self.scale = scale
        self.paper_px_w = int(width * scale)
        self.paper_px_h = int(height * scale)
        if self.paper_orientation == 'landscape':
            self.paper_px_w, self.paper_px_h = self.paper_px_h, self.paper_px_w
        if self.paper_rotation in [90, 270]:
            self.paper_px_w, self.paper_px_h = self.paper_px_h, self.paper_px_w
        self.update_scrollregion()
        self.update_ruler_ticks(self.view_width, self.view_height)
        self.update_scrollbars()
        self.update_preview()

    def rotate_paper(self, degrees):
        self.paper_rotation = degrees
        default_color = WHITE_COLOR
        for btn in self.rot_btns:
            deg_text = int(btn.cget("text")[:-1])
            if deg_text == degrees:
                btn.configure(fg_color=PRIMARY_COLOR, text_color=WHITE_COLOR)
            else:
                btn.configure(fg_color=default_color, text_color=TEXT_COLOR)
        self.update_paper_size()

    def update_bg_color(self, event=None):
        try:
            color = self.bg_color_var.get()
            if color and color.startswith('#'):
                self.color_preview.configure(fg_color=color)
                self.preview_canvas.configure(bg=color)
                self.preview_container.configure(bg=color)
                self.update_preview()
        except (ValueError, tk.TclError):
            pass

    def pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.bg_color_var.get())[1]
        if color:
            self.bg_color_var.set(color)
            self.update_bg_color()

    def upload_background(self):
        file = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file:
            try:
                self.background_image = Image.open(file)
                self.root.after(100, self.update_background)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load image: {e}")

    def remove_background(self):
        self.background_image = None
        self.preview_canvas.delete("bg_fixed")
        self.image_references.pop('bg_fixed', None)

    def add_numbering_head(self):
        head_id = len(self.numbering_heads)
        head = {
            'id': head_id,
            'name': f'Head {head_id + 1}',
            'font': 'Arial',
            'size': 16,
            'rotation': 0,
            'x': 100,
            'y': 100,
            'prefix': '',
            'seed': '',
            'add_space_after_prefix': False,
            'zero_pad': 0,
            'suffix': '',
            'show_qr': False,
            'qr_size': 50,
            'qr_space': 10,
            'show_barcode': False,
            'barcode_type': 'CODE128',
            'barcode_height': 50,
            'barcode_width': 2,
            'barcode_display_value': True,
            'barcode_text_space': 5,  # FIXED: Space between barcode and text
            'barcode_space': 10,
            'bold': False,
            'italic': False,
            'underline': False,
            'selected': True
        }
        self.numbering_heads.append(head)
        self.update_heads_list()
        self.select_head(head_id)

    def update_properties_panel(self, head):
        for widget in self.props_container.winfo_children():
            widget.destroy()

        if not head:
            label = ctk.CTkLabel(self.props_container, text="Select a head to edit properties", text_color=SECONDARY_COLOR)
            label.pack(expand=True)
            return

        INPUT_WIDTH = 120

        # Font
        font_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        font_row.pack(fill="x", padx=10, pady=2)
        font_row.grid_columnconfigure(1, weight=1)
        font_label = ctk.CTkLabel(font_row, text="Font", text_color=TEXT_COLOR, anchor="w")
        font_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        font_var = tk.StringVar(value=head['font'])
        font_combo = ctk.CTkComboBox(font_row, values=self.available_fonts, variable=font_var, fg_color=WHITE_COLOR, button_color=PRIMARY_COLOR, button_hover_color=HIGHLIGHT_COLOR, text_color=TEXT_COLOR, width=INPUT_WIDTH, command=lambda v: self.update_head_property('font', v))
        font_combo.grid(row=0, column=1, sticky="e")

        # Text Formatting
        fmt_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        fmt_row.pack(fill="x", padx=10, pady=2)
        fmt_label = ctk.CTkLabel(fmt_row, text="Text Formatting", text_color=TEXT_COLOR, anchor="w")
        fmt_label.pack(side="left", padx=(0, 5))
        fmt_frame = ctk.CTkFrame(fmt_row, fg_color="transparent")
        fmt_frame.pack(side="right", fill="x", expand=True)
        bold_btn = ctk.CTkButton(fmt_frame, text="B", width=30, command=lambda: self.toggle_format('bold'), fg_color=PRIMARY_COLOR if head['bold'] else WHITE_COLOR, hover_color=HIGHLIGHT_COLOR, text_color=WHITE_COLOR if head['bold'] else TEXT_COLOR, border_width=1, border_color="#d1d5db")
        bold_btn.pack(side="right", padx=2)
        italic_btn = ctk.CTkButton(fmt_frame, text="I", width=30, command=lambda: self.toggle_format('italic'), fg_color=PRIMARY_COLOR if head['italic'] else WHITE_COLOR, hover_color=HIGHLIGHT_COLOR, text_color=WHITE_COLOR if head['italic'] else TEXT_COLOR, border_width=1, border_color="#d1d5db")
        italic_btn.pack(side="right", padx=2)
        underline_btn = ctk.CTkButton(fmt_frame, text="U", width=30, command=lambda: self.toggle_format('underline'), fg_color=PRIMARY_COLOR if head['underline'] else WHITE_COLOR, hover_color=HIGHLIGHT_COLOR, text_color=WHITE_COLOR if head['underline'] else TEXT_COLOR, border_width=1, border_color="#d1d5db")
        underline_btn.pack(side="right", padx=2)

        # Size
        size_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        size_row.pack(fill="x", padx=10, pady=2)
        size_row.grid_columnconfigure(1, weight=1)
        size_label = ctk.CTkLabel(size_row, text="Size", text_color=TEXT_COLOR, anchor="w")
        size_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        size_var = tk.StringVar(value=str(head['size']))
        size_entry = ctk.CTkEntry(size_row, textvariable=size_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
        size_entry.grid(row=0, column=1, sticky="e")
        size_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
        size_entry.bind('<KeyRelease>', lambda e: self.update_head_property('size', size_var.get()))

        # Rotation
        rot_label = ctk.CTkLabel(self.props_container, text="Rotation (degrees)", text_color=TEXT_COLOR)
        rot_label.pack(anchor="w", padx=10, pady=(5, 2))
        rot_var = tk.StringVar(value=str(head['rotation']))
        def rot_cmd(v):
            try:
                val = int(float(v))
                self.update_head_property('rotation', val)
                rot_value_label.configure(text=f"{val}°")
            except (ValueError, tk.TclError):
                pass
        rot_slider = ctk.CTkSlider(self.props_container, from_=-180, to=180, command=rot_cmd, progress_color=PRIMARY_COLOR, button_color=PRIMARY_COLOR, button_hover_color=HIGHLIGHT_COLOR)
        rot_slider.set(head['rotation'])
        rot_slider.pack(fill="x", padx=10, pady=2)
        rot_value_label = ctk.CTkLabel(self.props_container, text=f"{head['rotation']}°", text_color=TEXT_COLOR)
        rot_value_label.pack(padx=10, pady=(0, 5))

        # X Position
        x_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        x_row.pack(fill="x", padx=10, pady=2)
        x_row.grid_columnconfigure(1, weight=1)
        x_label = ctk.CTkLabel(x_row, text="X Position", text_color=TEXT_COLOR, anchor="w")
        x_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        x_var = tk.StringVar(value=str(head['x']))
        x_entry = ctk.CTkEntry(x_row, textvariable=x_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
        x_entry.grid(row=0, column=1, sticky="e")
        x_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
        x_entry.bind('<KeyRelease>', lambda e: self.update_head_property('x', x_var.get()))

        # Y Position
        y_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        y_row.pack(fill="x", padx=10, pady=2)
        y_row.grid_columnconfigure(1, weight=1)
        y_label = ctk.CTkLabel(y_row, text="Y Position", text_color=TEXT_COLOR, anchor="w")
        y_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        y_var = tk.StringVar(value=str(head['y']))
        y_entry = ctk.CTkEntry(y_row, textvariable=y_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
        y_entry.grid(row=0, column=1, sticky="e")
        y_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
        y_entry.bind('<KeyRelease>', lambda e: self.update_head_property('y', y_var.get()))

        # Prefix
        prefix_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        prefix_row.pack(fill="x", padx=10, pady=2)
        prefix_row.grid_columnconfigure(1, weight=1)
        prefix_label = ctk.CTkLabel(prefix_row, text="Prefix", text_color=TEXT_COLOR, anchor="w")
        prefix_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        prefix_var = tk.StringVar(value=head['prefix'])
        prefix_entry = ctk.CTkEntry(prefix_row, textvariable=prefix_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
        prefix_entry.grid(row=0, column=1, sticky="e")
        prefix_entry.bind('<KeyRelease>', lambda e: self.update_head_property('prefix', prefix_var.get()))

        # Seed
        seed_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        seed_row.pack(fill="x", padx=10, pady=2)
        seed_row.grid_columnconfigure(1, weight=1)
        seed_label = ctk.CTkLabel(seed_row, text="Seed", text_color=TEXT_COLOR, anchor="w")
        seed_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        seed_var = tk.StringVar(value=head['seed'])
        seed_entry = ctk.CTkEntry(seed_row, textvariable=seed_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
        seed_entry.grid(row=0, column=1, sticky="e")
        seed_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
        seed_entry.bind('<KeyRelease>', lambda e: self.update_head_property('seed', seed_var.get()))

        # Add space after prefix
        space_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        space_row.pack(fill="x", padx=10, pady=2)
        space_row.grid_columnconfigure(1, weight=1)
        space_var = tk.BooleanVar(value=head['add_space_after_prefix'])
        space_check = ctk.CTkCheckBox(space_row, text="", variable=space_var, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR, command=lambda: self.update_head_property('add_space_after_prefix', space_var.get()))
        space_check.grid(row=0, column=0, sticky="w", padx=(0, 5))
        space_label = ctk.CTkLabel(space_row, text="Add space after prefix", text_color=TEXT_COLOR, anchor="w")
        space_label.grid(row=0, column=1, sticky="w")

        # Suffix
        suffix_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        suffix_row.pack(fill="x", padx=10, pady=2)
        suffix_row.grid_columnconfigure(1, weight=1)
        suffix_label = ctk.CTkLabel(suffix_row, text="Suffix", text_color=TEXT_COLOR, anchor="w")
        suffix_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        suffix_var = tk.StringVar(value=head['suffix'])
        suffix_entry = ctk.CTkEntry(suffix_row, textvariable=suffix_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
        suffix_entry.grid(row=0, column=1, sticky="e")
        suffix_entry.bind('<KeyRelease>', lambda e: self.update_head_property('suffix', suffix_var.get()))

        # Zero pad
        zero_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        zero_row.pack(fill="x", padx=10, pady=2)
        zero_row.grid_columnconfigure(1, weight=1)
        zero_label = ctk.CTkLabel(zero_row, text="Zero pad number for a total of", text_color=TEXT_COLOR, anchor="w")
        zero_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
        zero_var = tk.StringVar(value=str(head['zero_pad']))
        zero_entry = ctk.CTkEntry(zero_row, textvariable=zero_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
        zero_entry.grid(row=0, column=1, sticky="w")
        zero_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
        zero_entry.bind('<KeyRelease>', lambda e: self.update_head_property('zero_pad', zero_var.get()))
        zero_digits_label = ctk.CTkLabel(zero_row, text="digits", text_color=TEXT_COLOR, anchor="w")
        zero_digits_label.grid(row=0, column=2, sticky="w", padx=(5, 0))

        # Show QR
        qr_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        qr_row.pack(fill="x", padx=10, pady=2)
        qr_row.grid_columnconfigure(1, weight=1)
        qr_var = tk.BooleanVar(value=head['show_qr'])
        qr_check = ctk.CTkCheckBox(qr_row, text="", variable=qr_var, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR, command=lambda: self.update_head_property('show_qr', qr_var.get()))
        qr_check.grid(row=0, column=0, sticky="w", padx=(0, 5))
        qr_label = ctk.CTkLabel(qr_row, text="Show QR Code", text_color=TEXT_COLOR, anchor="w")
        qr_label.grid(row=0, column=1, sticky="w")

        if head['show_qr']:
            qr_size_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
            qr_size_row.pack(fill="x", padx=10, pady=2)
            qr_size_row.grid_columnconfigure(1, weight=1)
            qr_size_label = ctk.CTkLabel(qr_size_row, text="QR Code Size", text_color=TEXT_COLOR, anchor="w")
            qr_size_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
            qr_size_var = tk.StringVar(value=str(head['qr_size']))
            qr_size_entry = ctk.CTkEntry(qr_size_row, textvariable=qr_size_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
            qr_size_entry.grid(row=0, column=1, sticky="ew")
            qr_size_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
            qr_size_entry.bind('<KeyRelease>', lambda e: self.update_head_property('qr_size', qr_size_var.get()))

            # QR Space
            qr_space_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
            qr_space_row.pack(fill="x", padx=10, pady=2)
            qr_space_row.grid_columnconfigure(1, weight=1)
            qr_space_label = ctk.CTkLabel(qr_space_row, text="QR Space (px)", text_color=TEXT_COLOR, anchor="w")
            qr_space_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
            qr_space_var = tk.StringVar(value=str(head['qr_space']))
            qr_space_entry = ctk.CTkEntry(qr_space_row, textvariable=qr_space_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
            qr_space_entry.grid(row=0, column=1, sticky="ew")
            qr_space_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
            qr_space_entry.bind('<KeyRelease>', lambda e: self.update_head_property('qr_space', qr_space_var.get()))

        # Show Barcode
        bc_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
        bc_row.pack(fill="x", padx=10, pady=2)
        bc_row.grid_columnconfigure(1, weight=1)
        bc_var = tk.BooleanVar(value=head['show_barcode'])
        bc_check = ctk.CTkCheckBox(bc_row, text="", variable=bc_var, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR, command=lambda: self.update_head_property('show_barcode', bc_var.get()))
        bc_check.grid(row=0, column=0, sticky="w", padx=(0, 5))
        bc_label = ctk.CTkLabel(bc_row, text="Show Barcode", text_color=TEXT_COLOR, anchor="w")
        bc_label.grid(row=0, column=1, sticky="w")

        if head['show_barcode']:
            # Barcode Type
            bc_type_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
            bc_type_row.pack(fill="x", padx=10, pady=2)
            bc_type_row.grid_columnconfigure(1, weight=1)
            bc_type_label = ctk.CTkLabel(bc_type_row, text="Barcode Type", text_color=TEXT_COLOR, anchor="w")
            bc_type_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
            bc_type_var = tk.StringVar(value=head['barcode_type'])
            bc_type_combo = ctk.CTkComboBox(bc_type_row, values=['CODE128', 'CODE39', 'EAN13', 'EAN8', 'UPCA'], variable=bc_type_var, fg_color=WHITE_COLOR, button_color=PRIMARY_COLOR, button_hover_color=HIGHLIGHT_COLOR, text_color=TEXT_COLOR, width=INPUT_WIDTH, command=lambda v: self.update_head_property('barcode_type', v))
            bc_type_combo.grid(row=0, column=1, sticky="ew")

            # Barcode Space
            bc_space_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
            bc_space_row.pack(fill="x", padx=10, pady=2)
            bc_space_row.grid_columnconfigure(1, weight=1)
            bc_space_label = ctk.CTkLabel(bc_space_row, text="Barcode Space (px)", text_color=TEXT_COLOR, anchor="w")
            bc_space_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
            bc_space_var = tk.StringVar(value=str(head['barcode_space']))
            bc_space_entry = ctk.CTkEntry(bc_space_row, textvariable=bc_space_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
            bc_space_entry.grid(row=0, column=1, sticky="ew")
            bc_space_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
            bc_space_entry.bind('<KeyRelease>', lambda e: self.update_head_property('barcode_space', bc_space_var.get()))

            # Barcode Height
            bc_height_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
            bc_height_row.pack(fill="x", padx=10, pady=2)
            bc_height_row.grid_columnconfigure(1, weight=1)
            bc_height_label = ctk.CTkLabel(bc_height_row, text="Barcode Height", text_color=TEXT_COLOR, anchor="w")
            bc_height_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
            bc_height_var = tk.StringVar(value=str(head['barcode_height']))
            bc_height_entry = ctk.CTkEntry(bc_height_row, textvariable=bc_height_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
            bc_height_entry.grid(row=0, column=1, sticky="ew")
            bc_height_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
            bc_height_entry.bind('<KeyRelease>', lambda e: self.update_head_property('barcode_height', bc_height_var.get()))

            # Barcode Width
            bc_width_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
            bc_width_row.pack(fill="x", padx=10, pady=2)
            bc_width_row.grid_columnconfigure(1, weight=1)
            bc_width_label = ctk.CTkLabel(bc_width_row, text="Barcode Width", text_color=TEXT_COLOR, anchor="w")
            bc_width_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
            bc_width_var = tk.StringVar(value=str(head['barcode_width']))
            bc_width_entry = ctk.CTkEntry(bc_width_row, textvariable=bc_width_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
            bc_width_entry.grid(row=0, column=1, sticky="ew")
            bc_width_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
            bc_width_entry.bind('<KeyRelease>', lambda e: self.update_head_property('barcode_width', bc_width_var.get()))

            # Display Value
            bc_disp_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
            bc_disp_row.pack(fill="x", padx=10, pady=2)
            bc_disp_row.grid_columnconfigure(1, weight=1)
            bc_disp_var = tk.BooleanVar(value=head['barcode_display_value'])
            bc_disp_check = ctk.CTkCheckBox(bc_disp_row, text="", variable=bc_disp_var, fg_color=PRIMARY_COLOR, hover_color=HIGHLIGHT_COLOR, command=lambda: self.update_head_property('barcode_display_value', bc_disp_var.get()))
            bc_disp_check.grid(row=0, column=0, sticky="w", padx=(0, 5))
            bc_disp_label = ctk.CTkLabel(bc_disp_row, text="Display Value", text_color=TEXT_COLOR, anchor="w")
            bc_disp_label.grid(row=0, column=1, sticky="w")

            # Barcode Text Space (NEW)
            bc_text_space_row = ctk.CTkFrame(self.props_container, fg_color="transparent")
            bc_text_space_row.pack(fill="x", padx=10, pady=2)
            bc_text_space_row.grid_columnconfigure(1, weight=1)
            bc_text_space_label = ctk.CTkLabel(bc_text_space_row, text="Barcode Text Space (px)", text_color=TEXT_COLOR, anchor="w")
            bc_text_space_label.grid(row=0, column=0, sticky="w", padx=(0, 5))
            bc_text_space_var = tk.StringVar(value=str(head['barcode_text_space']))
            bc_text_space_entry = ctk.CTkEntry(bc_text_space_row, textvariable=bc_text_space_var, fg_color=WHITE_COLOR, border_color="#d1d5db", text_color=TEXT_COLOR, width=INPUT_WIDTH)
            bc_text_space_entry.grid(row=0, column=1, sticky="ew")
            bc_text_space_entry.configure(validate="key", validatecommand=(self.root.register(self.validate_numeric_input), '%P'))
            bc_text_space_entry.bind('<KeyRelease>', lambda e: self.update_head_property('barcode_text_space', bc_text_space_var.get()))

    def toggle_format(self, fmt):
        if self.selected_head_id is not None:
            head = self.numbering_heads[self.selected_head_id]
            head[fmt] = not head[fmt]
            self.update_properties_panel(head)
            self.update_preview()

    def update_head_property(self, prop, value):
        if self.selected_head_id is not None:
            head = self.numbering_heads[self.selected_head_id]
            try:
                if prop in ['size', 'zero_pad', 'qr_size', 'barcode_height', 'barcode_space', 'barcode_text_space', 'qr_space']:
                    head[prop] = int(value) if str(value).strip() != '' else 0
                elif prop == 'barcode_width':
                    head[prop] = float(value) if str(value).strip() != '' else 0.0
                elif prop in ['x', 'y']:
                    head[prop] = int(value) if str(value).strip() != '' else 0
                elif prop == 'rotation':
                    head[prop] = int(value) if str(value).strip() != '' else 0
                elif prop == 'seed':
                    head[prop] = value
                else:
                    head[prop] = value
                if prop in ['show_qr', 'show_barcode', 'barcode_display_value']:
                    self.update_properties_panel(head)
                self.update_preview()
            except (ValueError, tk.TclError):
                pass

    def calculate_number_for_page(self, page):
        try:
            start_str = self.start_num_var.get()
            step_str = self.step_var.get()
            skip_str = self.skip_var.get()
            total_str = self.total_pages_var.get()
            
            start = int(start_str) if start_str.strip() != "" else 1
            step = int(step_str) if step_str.strip() != "" else 1
            skip = int(skip_str) if skip_str.strip() != "" else 0
            total = int(total_str) if total_str.strip() != "" else 10
            
            order = "asc" if self.order_var.get() == "Ascending" else "desc"

            if order == "asc":
                number = start + (page - 1) * step
            else:
                number = start + (total - page) * step

            if skip > 0 and number >= skip:
                number += math.floor((number - skip) / skip) + 1

            return number
        except (ValueError, tk.TclError):
            return 1

    def update_preview(self):
        bg_color = self.bg_color_var.get()
        self.preview_canvas.configure(bg=bg_color)
        self.preview_container.configure(bg=bg_color)

        self.preview_canvas.delete("content")

        # Clear image references to prevent memory leaks
        for key in list(self.image_references.keys()):
            if 'head' in key or 'qr' in key or 'bc' in key:
                del self.image_references[key]

        page_num = self.calculate_number_for_page(self.current_page)

        for head in [h for h in self.numbering_heads if h['selected']]:
            seed_str = head['seed']
            seed = int(seed_str) if seed_str and seed_str.strip() != '' else 0
            final_num = page_num + seed
            formatted = str(final_num).zfill(head['zero_pad']) if head['zero_pad'] > 0 else str(final_num)
            full_text = head['prefix']
            if head['add_space_after_prefix'] and head['prefix']:
                full_text += " "
            full_text += formatted + head['suffix']

            # Scaled positions and sizes
            scaled_x = head['x'] * self.zoom_level
            scaled_y = head['y'] * self.zoom_level
            scaled_size = int(head['size'] * self.zoom_level)
            font_list = (head['font'], scaled_size)
            if head['bold']:
                font_list = font_list + ('bold',)
            if head['italic']:
                font_list = font_list + ('italic',)
            text_color = BLACK_COLOR
            self.preview_canvas.create_text(scaled_x, scaled_y, text=full_text, font=font_list, tags=(f"head_{head['id']}", "content"), fill=text_color)

            # QR Code
            if head['show_qr'] and full_text.strip() != '':
                try:
                    qr = qrcode.QRCode(version=1, box_size=10, border=1)
                    qr.add_data(full_text)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    base_size = max(head['qr_size'], 10)
                    scaled_qr_size = int(base_size * self.zoom_level)
                    qr_scaled = qr_img.resize((scaled_qr_size, scaled_qr_size), Image.Resampling.NEAREST)
                    
                    qr_photo = ImageTk.PhotoImage(qr_scaled)
                    qr_key = f"qr_{head['id']}"
                    self.image_references[qr_key] = qr_photo
                    
                    qr_offset_y = scaled_y + head['size'] * self.zoom_level + head['qr_space'] * self.zoom_level
                    self.preview_canvas.create_image(scaled_x, qr_offset_y, image=qr_photo, tags=(f"qr_{head['id']}", "content"))
                except Exception as e:
                    print(f"QR error: {e}")

            # Barcode - FIXED: barcode_text_space အလုပ်လုပ်အောင်ပြင်ဆင်
            if head['show_barcode'] and full_text.strip() != '':
                try:
                    # Generate barcode directly to memory without text
                    barcode_data = full_text
                    barcode_class = {
                        'CODE128': Code128,
                        'CODE39': Code39,
                        'EAN13': EAN13,
                        'EAN8': EAN8,
                        'UPCA': UPCA
                    }.get(head['barcode_type'], Code128)
                    
                    # Create barcode with custom writer settings, no text
                    writer = ImageWriter()
                    writer.set_options({
                        'module_width': head['barcode_width'],
                        'module_height': head['barcode_height'],
                        'font_size': 0,
                        'text_distance': 0,
                        'quiet_zone': 6,
                        'write_text': False
                    })
                    
                    # Generate barcode to bytes buffer
                    bc = barcode_class(barcode_data, writer=writer)
                    buffer = io.BytesIO()
                    bc.write(buffer)
                    buffer.seek(0)
                    
                    # Load and scale barcode image (bars only)
                    bc_img = Image.open(buffer)
                    
                    # Calculate scaled dimensions
                    base_width = max(int(bc_img.width * self.zoom_level), 10)
                    base_height = max(int(bc_img.height * self.zoom_level), 10)
                    
                    bc_img = bc_img.resize((base_width, base_height), Image.Resampling.NEAREST)
                    bc_photo = ImageTk.PhotoImage(bc_img)
                    
                    bc_key = f"bc_{head['id']}"
                    self.image_references[bc_key] = bc_photo
                    
                    # Position for barcode image
                    bc_offset_y = scaled_y + head['size'] * self.zoom_level + head['barcode_space'] * self.zoom_level
                    self.preview_canvas.create_image(scaled_x, bc_offset_y, image=bc_photo, tags=(f"bc_{head['id']}", "content"))
                    
                    # FIXED: Add value text below barcode with proper barcode_text_space
                    if head['barcode_display_value']:
                        value_font_size = int(10 * self.zoom_level)
                        # Use barcode_text_space for spacing between barcode and text
                        value_text_y = bc_offset_y + base_height + head['barcode_text_space'] * self.zoom_level
                        self.preview_canvas.create_text(scaled_x, value_text_y, text=full_text, 
                                                        font=("Arial", value_font_size), 
                                                        fill=BLACK_COLOR, 
                                                        tags=(f"bc_text_{head['id']}", "content"))
                    
                except Exception as e:
                    print(f"Barcode error: {e}")

        total_pages_str = self.total_pages_var.get()
        total_pages = int(total_pages_str) if total_pages_str.strip() != "" else 10
        self.page_label.configure(text=f"Page {self.current_page} of {total_pages}")

    def start_drag(self, event):
        items = self.preview_canvas.find_closest(event.x, event.y)
        if items:
            tags = self.preview_canvas.gettags(items[0])
            for tag in tags:
                if '_' in tag:
                    prefix, hid = tag.rsplit('_', 1)
                    if prefix in ['head', 'qr', 'bc', 'bc_text']:
                        self.is_dragging = True
                        self.drag_head_id = int(hid)
                        cx = self.preview_canvas.canvasx(event.x) / self.zoom_level
                        cy = self.preview_canvas.canvasy(event.y) / self.zoom_level
                        self.drag_offset["x"] = cx - self.numbering_heads[self.drag_head_id]['x']
                        self.drag_offset["y"] = cy - self.numbering_heads[self.drag_head_id]['y']
                        self.selected_head_id = self.drag_head_id
                        self.select_head(self.drag_head_id)
                        break

    def drag(self, event):
        if self.is_dragging and hasattr(self, 'drag_head_id'):
            head_id = self.drag_head_id
            head = self.numbering_heads[head_id]
            old_x = head['x']
            old_y = head['y']
            new_canvas_x = self.preview_canvas.canvasx(event.x)
            new_canvas_y = self.preview_canvas.canvasy(event.y)
            new_x = new_canvas_x / self.zoom_level - self.drag_offset["x"]
            new_y = new_canvas_y / self.zoom_level - self.drag_offset["y"]
            head['x'] = new_x
            head['y'] = new_y
            delta_x = (new_x - old_x) * self.zoom_level
            delta_y = (new_y - old_y) * self.zoom_level
            # Move all items for this head
            for tag_prefix in ["head", "qr", "bc", "bc_text"]:
                items = self.preview_canvas.find_withtag(f"{tag_prefix}_{head_id}")
                for item in items:
                    self.preview_canvas.move(item, delta_x, delta_y)

    def stop_drag(self, event):
        self.is_dragging = False
        if hasattr(self, 'drag_head_id'):
            del self.drag_head_id

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_preview()

    def next_page(self):
        total_pages_str = self.total_pages_var.get()
        total_pages = int(total_pages_str) if total_pages_str.strip() != "" else 10
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_preview()

    def print_preview(self):
        """Implement print functionality by generating temp PDF and printing."""
        temp_path = os.path.join(tempfile.gettempdir(), f"temp_print_{uuid.uuid4().hex[:8]}.pdf")
        try:
            packet = io.BytesIO()
            # Paper size
            pagesize = A4
            if self.paper_var.get() == 'A3':
                pagesize = A3
            elif self.paper_var.get() == 'Letter':
                pagesize = letter
            elif self.paper_var.get() == 'Legal':
                pagesize = legal

            p = canvas.Canvas(packet, pagesize=pagesize)
            width, height = pagesize

            total_pages_str = self.total_pages_var.get()
            total_pages = int(total_pages_str) if total_pages_str.strip() != "" else 10
            
            for page in range(1, total_pages + 1):
                if page > 1:
                    p.showPage()

                p.setFillColor(HexColor(self.bg_color_var.get()))
                p.rect(0, 0, width, height, fill=1, stroke=0)

                page_num = self.calculate_number_for_page(page)
                for head in [h for h in self.numbering_heads if h['selected']]:
                    seed_str = head['seed']
                    seed = int(seed_str) if seed_str and seed_str.strip() != '' else 0
                    final_num = page_num + seed
                    formatted = str(final_num).zfill(head['zero_pad']) if head['zero_pad'] > 0 else str(final_num)
                    full_text = head['prefix']
                    if head['add_space_after_prefix'] and head['prefix']:
                        full_text += " "
                    full_text += formatted + head['suffix']

                    pdf_font = self.get_pdf_font(head)
                    p.setFont(pdf_font, head['size'])
                    p.drawString(head['x'], height - head['y'], full_text)

            p.save()
            packet.seek(0)

            with open(temp_path, "wb") as f:
                f.write(packet.getvalue())

            # Platform-specific print with better error handling
            sys_name = platform.system()
            print_success = False
            print_error_msg = ""
            
            try:
                if sys_name == "Windows":
                    if os.path.exists(temp_path):
                        os.startfile(temp_path, "print")
                        print_success = True
                    else:
                        raise FileNotFoundError("PDF file not created")
                        
                elif sys_name == "Darwin":
                    result = subprocess.run(["lpr", temp_path], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        print_success = True
                    else:
                        print_error_msg = f"lpr failed: {result.stderr}"
                        
                else:
                    try:
                        lpstat_result = subprocess.run(["lpstat", "-p"], capture_output=True, text=True, timeout=10)
                        if lpstat_result.returncode == 0:
                            printers = [line.split()[1] for line in lpstat_result.stdout.split('\n') if line.startswith('printer')]
                        else:
                            printers = []
                    except:
                        printers = []
                    
                    if printers:
                        for printer in printers:
                            try:
                                result = subprocess.run(["lp", "-d", printer, temp_path], 
                                                      capture_output=True, text=True, timeout=30)
                                if result.returncode == 0:
                                    print_success = True
                                    break
                            except:
                                continue
                    
                    if not print_success:
                        try:
                            result = subprocess.run(["lpr", temp_path], capture_output=True, text=True, timeout=30)
                            if result.returncode == 0:
                                print_success = True
                            else:
                                print_error_msg = f"lpr failed: {result.stderr}"
                        except Exception as e:
                            print_error_msg = f"lpr failed: {str(e)}"
                    
                    if not print_success:
                        try:
                            if os.path.exists('/usr/bin/xdg-open'):
                                subprocess.run(["xdg-open", temp_path], timeout=30)
                                print_success = True
                            elif os.path.exists('/usr/bin/evince'):
                                subprocess.run(["evince", "--print", temp_path], timeout=30)
                                print_success = True
                        except:
                            pass

                if print_success:
                    messagebox.showinfo("Print", "Document sent to printer successfully!")
                    self.root.after(3000, lambda: self.cleanup_temp_file(temp_path))
                else:
                    self.handle_print_failure(temp_path, print_error_msg)
                    
            except subprocess.TimeoutExpired:
                self.handle_print_failure(temp_path, "Print operation timed out")
            except Exception as print_error:
                self.handle_print_failure(temp_path, str(print_error))
                
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to create PDF:\n{str(e)}")
            if os.path.exists(temp_path):
                self.cleanup_temp_file(temp_path)

    def handle_print_failure(self, temp_path, error_msg):
        """Handle print failure by offering options to user."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Print Options")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_reqwidth()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_reqheight()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        error_label = ctk.CTkLabel(
            main_frame, 
            text=f"Automatic printing failed:\n{error_msg}",
            text_color=WARNING_COLOR,
            wraplength=400
        )
        error_label.pack(pady=(10, 20))
        
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)
        
        def open_pdf():
            try:
                sys_name = platform.system()
                if sys_name == "Windows":
                    os.startfile(temp_path)
                elif sys_name == "Darwin":
                    subprocess.run(["open", temp_path])
                else:
                    subprocess.run(["xdg-open", temp_path])
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open PDF: {str(e)}")
        
        open_btn = ctk.CTkButton(
            options_frame,
            text="📄 Open PDF for Manual Printing",
            command=open_pdf,
            fg_color=PRIMARY_COLOR,
            hover_color=HIGHLIGHT_COLOR,
            height=40
        )
        open_btn.pack(fill="x", pady=5)
        
        def save_pdf():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save PDF As"
            )
            if file_path:
                try:
                    shutil.copy2(temp_path, file_path)
                    messagebox.showinfo("Success", f"PDF saved to:\n{file_path}")
                    dialog.destroy()
                    self.cleanup_temp_file(temp_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
        
        save_btn = ctk.CTkButton(
            options_frame,
            text="💾 Save PDF to Location",
            command=save_pdf,
            fg_color=SUCCESS_COLOR,
            hover_color="#059669",
            height=40
        )
        save_btn.pack(fill="x", pady=5)
        
        def setup_printer():
            try:
                sys_name = platform.system()
                if sys_name == "Windows":
                    subprocess.run(["control", "printers"])
                elif sys_name == "Darwin":
                    subprocess.run(["open", "system-preferences://printers"])
                else:
                    for cmd in ["system-config-printer", "lpadmin"]:
                        try:
                            subprocess.run([cmd])
                            break
                        except:
                            continue
                    else:
                        messagebox.showinfo("Printer Setup", 
                                          "Please set up a printer through your system's printer settings.")
            except Exception as e:
                messagebox.showinfo("Printer Setup", 
                                  "Please set up a printer through your system's printer settings.")
        
        setup_btn = ctk.CTkButton(
            options_frame,
            text="🖨️ Open Printer Setup",
            command=setup_printer,
            fg_color=SECONDARY_COLOR,
            hover_color="#4b5563",
            height=40
        )
        setup_btn.pack(fill="x", pady=5)
        
        def cancel_and_cleanup():
            self.cleanup_temp_file(temp_path)
            dialog.destroy()
        
        cancel_btn = ctk.CTkButton(
            options_frame,
            text="Cancel",
            command=cancel_and_cleanup,
            fg_color=DANGER_COLOR,
            hover_color="#dc2626",
            height=35
        )
        cancel_btn.pack(fill="x", pady=(10, 5))
        
        path_label = ctk.CTkLabel(
            main_frame,
            text=f"PDF location: {temp_path}",
            text_color=SECONDARY_COLOR,
            font=ctk.CTkFont(size=10),
            wraplength=400
        )
        path_label.pack(pady=(10, 5))

    def export_images(self):
        """Export QR codes and barcodes as separate image files"""
        try:
            export_dir = filedialog.askdirectory(title="Select Export Directory")
            if not export_dir:
                return
            
            qr_dir = Path(export_dir) / "QR_Codes"
            barcode_dir = Path(export_dir) / "Barcodes"
            
            qr_dir.mkdir(exist_ok=True)
            barcode_dir.mkdir(exist_ok=True)
            
            total_pages_str = self.total_pages_var.get()
            total_pages = int(total_pages_str) if total_pages_str.strip() != "" else 10
            
            exported_qr = 0
            exported_barcodes = 0
            
            for page in range(1, total_pages + 1):
                page_num = self.calculate_number_for_page(page)
                
                for head in [h for h in self.numbering_heads if h['selected']]:
                    seed_str = head['seed']
                    seed = int(seed_str) if seed_str and seed_str.strip() != '' else 0
                    final_num = page_num + seed
                    formatted = str(final_num).zfill(head['zero_pad']) if head['zero_pad'] > 0 else str(final_num)
                    full_text = head['prefix']
                    if head['add_space_after_prefix'] and head['prefix']:
                        full_text += " "
                    full_text += formatted + head['suffix']
                    
                    # Export QR Code
                    if head['show_qr'] and full_text.strip() != '':
                        try:
                            qr = qrcode.QRCode(version=1, box_size=10, border=1)
                            qr.add_data(full_text)
                            qr.make(fit=True)
                            qr_img = qr.make_image(fill_color="black", back_color="white")
                            
                            qr_filename = f"{head['name']}_page{page}_{full_text}.png"
                            qr_filepath = qr_dir / qr_filename
                            qr_img.save(qr_filepath)
                            exported_qr += 1
                        except Exception as e:
                            print(f"QR export error: {e}")
                    
                    # Export Barcode
                    if head['show_barcode'] and full_text.strip() != '':
                        try:
                            barcode_data = full_text
                            if head['barcode_type'] == 'CODE128':
                                bc = Code128(barcode_data, writer=ImageWriter())
                            elif head['barcode_type'] == 'CODE39':
                                bc = Code39(barcode_data, writer=ImageWriter())
                            elif head['barcode_type'] == 'EAN13':
                                bc = EAN13(barcode_data, writer=ImageWriter())
                            elif head['barcode_type'] == 'EAN8':
                                bc = EAN8(barcode_data, writer=ImageWriter())
                            elif head['barcode_type'] == 'UPCA':
                                bc = UPCA(barcode_data, writer=ImageWriter())
                            else:
                                bc = Code128(barcode_data, writer=ImageWriter())
                            
                            barcode_filename = f"{head['name']}_page{page}_{full_text}.png"
                            barcode_filepath = barcode_dir / barcode_filename
                            bc.save(barcode_filepath)
                            exported_barcodes += 1
                        except Exception as e:
                            print(f"Barcode export error: {e}")
            
            messagebox.showinfo(
                "Export Complete", 
                f"Images exported successfully!\n\n"
                f"QR Codes: {exported_qr} files\n"
                f"Barcodes: {exported_barcodes} files\n\n"
                f"Location: {export_dir}"
            )
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export images:\n{str(e)}")

    def export_pdf(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF As"
        )
        if not file_path:
            return

        try:
            packet = io.BytesIO()
            pagesize = A4
            if self.paper_var.get() == 'A3':
                pagesize = A3
            elif self.paper_var.get() == 'Letter':
                pagesize = letter
            elif self.paper_var.get() == 'Legal':
                pagesize = legal

            p = canvas.Canvas(packet, pagesize=pagesize)
            width, height = pagesize

            total_pages_str = self.total_pages_var.get()
            total_pages = int(total_pages_str) if total_pages_str.strip() != "" else 10
            
            for page in range(1, total_pages + 1):
                if page > 1:
                    p.showPage()

                p.setFillColor(HexColor(self.bg_color_var.get()))
                p.rect(0, 0, width, height, fill=1, stroke=0)

                page_num = self.calculate_number_for_page(page)
                for head in [h for h in self.numbering_heads if h['selected']]:
                    seed_str = head['seed']
                    seed = int(seed_str) if seed_str and seed_str.strip() != '' else 0
                    final_num = page_num + seed
                    formatted = str(final_num).zfill(head['zero_pad']) if head['zero_pad'] > 0 else str(final_num)
                    full_text = head['prefix']
                    if head['add_space_after_prefix'] and head['prefix']:
                        full_text += " "
                    full_text += formatted + head['suffix']

                    pdf_font = self.get_pdf_font(head)
                    p.setFont(pdf_font, head['size'])
                    p.drawString(head['x'], height - head['y'], full_text)

            p.save()
            packet.seek(0)

            with open(file_path, "wb") as f:
                f.write(packet.getvalue())

            messagebox.showinfo("PDF Export", f"PDF exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export PDF:\n{str(e)}")

    def reset_all(self):
        if messagebox.askyesno("Reset", "Are you sure you want to reset all settings?"):
            self.current_page = 1
            self.numbering_heads = []
            self.selected_head_id = None
            self.background_image = None
            self.paper_rotation = 0
            self.paper_orientation = 'portrait'
            self.paper_var.set("A4")
            self.bg_color_var.set("#ffffff")
            self.update_paper_size()
            self.rotate_paper(0)
            self.set_orientation('portrait')
            self.remove_background()
            self.start_num_var.set("1")
            self.step_var.set("1")
            self.total_pages_var.set("10")
            self.copies_var.set("1")
            self.skip_var.set("0")
            self.order_var.set("Ascending")
            self.add_numbering_head()
            self.update_preview()
            self.zoom_level = 1.0
            self.apply_zoom()

    def cleanup_temp_file(self, file_path):
        """Clean up temporary files"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NumberingSystemApp()
    app.run()