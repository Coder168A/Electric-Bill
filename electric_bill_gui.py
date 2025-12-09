from tkinter import *
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime
import pandas as pd
import csv
import os
from pdf_maker import generate_bill_pdf

# ========== STYLE CONSTANTS ==========
BG_COLOR = "#525561"  # Main background
CONTAINER_BG = "#272A37"  # Container background
TEXT_COLOR = "#FFFFFF"  # White text
ACCENT_COLOR = "#1D90F5"  # Blue accent
ENTRY_BG = "#3D404B"  # Entry field background
BUTTON_BG = "#1D90F5"  # Button background
BUTTON_HOVER = "#206DB4"  # Button hover
DANGER_COLOR = "#FF6B6B"  # Red for delete/clear
SUCCESS_COLOR = "#4CAF50"  # Green for success
FONT_FAMILY = "yu gothic ui"
FONT_BOLD = (FONT_FAMILY, 12, "bold")
FONT_NORMAL = (FONT_FAMILY, 11)
FONT_SMALL = (FONT_FAMILY, 10)

# ========== HISTORY MANAGER CLASS ==========

class HistoryManager:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.session_history = []  # List to store calculation records

        # Create history frame with modern style
        self.history_frame = Frame(parent_frame, bg=CONTAINER_BG, relief=FLAT, borderwidth=2)
        self.history_frame.pack(fill='both', expand=True, pady=(10, 0))

        # Header for history
        history_header = Frame(self.history_frame, bg=CONTAINER_BG)
        history_header.pack(fill=X, pady=(0, 10))

        Label(history_header, text="Calculation History",
              font=("yu gothic ui bold", 14),
              fg=TEXT_COLOR, bg=CONTAINER_BG).pack(side=LEFT)

        # Create text widget for history display with dark theme
        text_frame = Frame(self.history_frame, bg=CONTAINER_BG)
        text_frame.pack(fill='both', expand=True)

        self.history_box = Text(text_frame, width=85, height=12,
                               state='disabled', bg=ENTRY_BG, fg=TEXT_COLOR,
                               font=("Consolas", 10), relief=FLAT,
                               insertbackground=TEXT_COLOR)
        self.history_box.pack(side=LEFT, fill='both', expand=True, padx=(0, 5))

        # Add scrollbar with custom style
        scrollbar = Scrollbar(text_frame, command=self.history_box.yview,
                             bg=ENTRY_BG, troughcolor=CONTAINER_BG,
                             activebackground=ACCENT_COLOR)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.history_box.config(yscrollcommand=scrollbar.set)

        # Summary label with modern style
        self.summary_label = Label(self.history_frame,
                                  text="Total Calculations: 0 | Total kWh: 0.00 | Total Cost: ₱0.00",
                                  font=("yu gothic ui", 10, "bold"),
                                  fg=TEXT_COLOR, bg=CONTAINER_BG,
                                  relief=FLAT, borderwidth=2)
        self.summary_label.pack(fill=X, pady=(10, 5))

        # Buttons frame with modern buttons
        button_frame = Frame(self.history_frame, bg=CONTAINER_BG)
        button_frame.pack(pady=(0, 10))

        # Modern button style function
        def create_modern_button(parent, text, command, bg_color, hover_color):
            btn = Button(parent, text=text, command=command,
                        font=FONT_BOLD, fg=TEXT_COLOR, bg=bg_color,
                        relief=FLAT, bd=0, cursor="hand2",
                        activebackground=hover_color,
                        activeforeground=TEXT_COLOR,
                        padx=20, pady=8)

            # Hover effect
            def on_enter(e):
                btn['background'] = hover_color
            def on_leave(e):
                btn['background'] = bg_color

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            return btn

        # Create buttons
        clear_btn = create_modern_button(button_frame, "Clear History",
                                        self.clear_history, DANGER_COLOR, "#FF5252")
        clear_btn.pack(side=LEFT, padx=5)

        export_btn = create_modern_button(button_frame, "Export to TXT",
                                         self.export_txt, SUCCESS_COLOR, "#45a049")
        export_btn.pack(side=LEFT, padx=5)

        refresh_btn = create_modern_button(button_frame, "Refresh",
                                          self.render_history, ACCENT_COLOR, BUTTON_HOVER)
        refresh_btn.pack(side=LEFT, padx=5)

    def add_calculation(self, customer_name, account, kwh_used, total_cost, customer_type,
                       discount_value, discount_amount, billing_month):
        """Add a new calculation to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            'timestamp': timestamp,
            'customer_name': customer_name,
            'account': account,
            'kwh_used': kwh_used,
            'total_cost': total_cost,
            'customer_type': customer_type,
            'discount_value': discount_value,
            'discount_amount': discount_amount,
            'billing_month': billing_month
        }
        self.session_history.append(record)
        self.render_history()

    def render_history(self):
        """Update the history display"""
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", END)

        if not self.session_history:
            self.history_box.insert(END, "No calculation history yet.\n")
            self.history_box.insert(END, "Generate some bills to see them here.")
            self.summary_label.config(text="Total Calculations: 0 | Total kWh: 0.00 | Total Cost: ₱0.00")
            self.history_box.configure(state="disabled")
            return

        # Create header (wider for discount columns)
        header = f"{'Timestamp':19} {'Name':15} {'Account':12} {'kWh':>6} {'Cost':>10} {'Type':>10} {'Disc':>8} {'Disc Amt':>10}\n"
        header += "-" * 105 + "\n"
        lines = [header]

        # Add each record
        for r in self.session_history:
            # Truncate long names/accounts
            name_display = r['customer_name'][:14] if len(r['customer_name']) > 14 else r['customer_name']
            account_display = r['account'][:11] if len(r['account']) > 11 else r['account']
            discount_type = r['discount_value'][:5] if r['discount_value'] != "None" else "None"

            line = f"{r['timestamp']:19} {name_display:15} {account_display:12} " \
                   f"{r['kwh_used']:6.2f} ₱{r['total_cost']:9.2f} {r['customer_type'][:8]:>10} " \
                   f"{discount_type:>8} ₱{r['discount_amount']:8.2f}\n"
            lines.append(line)

        self.history_box.insert("1.0", "".join(lines))
        self.history_box.configure(state="disabled")

        # Update summary
        total_kwh = sum(r["kwh_used"] for r in self.session_history)
        total_cost = sum(r["total_cost"] for r in self.session_history)
        total_calc = len(self.session_history)

        self.summary_label.config(
            text=f"Total Calculations: {total_calc} | "
                 f"Total kWh: {total_kwh:.2f} | "
                 f"Total Cost: ₱{total_cost:.2f}"
        )

    def export_txt(self):
        """Export history to TXT file with formatted output"""
        if not self.session_history:
            messagebox.showinfo("No Data", "No calculation history to export.")
            return

        # Create default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default = f"electric_bill_history_{timestamp}.txt"

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write("ELECTRIC BILL CALCULATION HISTORY\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Records: {len(self.session_history)}\n")
                f.write("-" * 80 + "\n\n")

                # Write table header
                f.write(f"{'Timestamp':19} {'Customer Name':20} {'Account':15} {'kWh':>8} {'Cost':>12} {'Type':>10} {'Discount':>12} {'Disc Amt':>10}\n")
                f.write("-" * 120 + "\n")

                # Write each record
                for r in self.session_history:
                    f.write(f"{r['timestamp']:19} {r['customer_name'][:18]:20} {r['account'][:14]:15} "
                           f"{r['kwh_used']:8.2f} ₱{r['total_cost']:10.2f} {r['customer_type'][:8]:>10} "
                           f"{r['discount_value'][:10]:>12} ₱{r['discount_amount']:8.2f}\n")

                # Write summary
                f.write("\n" + "=" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 80 + "\n")
                total_kwh = sum(r["kwh_used"] for r in self.session_history)
                total_cost = sum(r["total_cost"] for r in self.session_history)
                f.write(f"Total Calculations: {len(self.session_history)}\n")
                f.write(f"Total kWh Consumed: {total_kwh:.2f}\n")
                f.write(f"Total Amount: ₱{total_cost:.2f}\n")
                f.write("=" * 80 + "\n")

            messagebox.showinfo("Success", f"History exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export TXT:\n{str(e)}")

    def clear_history(self):
        """Clear all history records"""
        if not self.session_history:
            return

        if messagebox.askyesno("Clear History", "Are you sure you want to clear all calculation history?"):
            self.session_history.clear()
            self.render_history()

    def get_session_history(self):
        """Get the session history for CSV export"""
        return self.session_history


# ========== ELECTRIC BILL FUNCTIONS ==========
def tiered(u, tiers):
    cost = 0
    applied_rates = 0
    for limits, rate in tiers:
        if u <= 0:
            break
        use = min(u, limits)
        cost += use * rate
        applied_rates = rate
        u -= use
    return cost, applied_rates

def calculate_bill(units, customer_type, is_senior=False):
    """Calculate bill with optional senior discount"""
    if customer_type == "residential":
        tiers = [
            (50, 5.0),
            (50, 6.5),
            (100, 8.0),
            (float("inf"), 10.0),
        ]
        fixed = 40
    else:
        tiers = [
            (100, 3.5),
            (200, 5.0),
            (500, 6.5),
            (float("inf"), 7.5),
        ]
        fixed = 100

    energy, applied_rates = tiered(units, tiers)
    vat = energy * 0.12
    env_fee = energy * 0.0025
    total = energy + fixed + vat + env_fee

    # Apply discount only for seniors
    discount_amount = 0
    if is_senior:
        discount_amount = total * 0.05  # 5% discount
        total = total - discount_amount

    return (round(energy, 2), round(fixed, 2), round(vat, 2),
            round(env_fee, 2), round(applied_rates, 2),
            round(total, 2), round(discount_amount, 2))

# ========== MODERN STYLED ENTRY FIELD ==========
def create_modern_entry(parent, label_text, row):
    """Create a modern entry field with label"""
    # Label
    label = Label(parent, text=label_text, font=FONT_BOLD,
                 fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    label.grid(row=row, column=0, sticky="w", pady=(15, 5), padx=20)

    # Entry container frame
    entry_frame = Frame(parent, bg=CONTAINER_BG)
    entry_frame.grid(row=row+1, column=0, sticky="ew", pady=(0, 10), padx=20)

    # Actual entry field
    entry = Entry(entry_frame, font=FONT_NORMAL, fg=TEXT_COLOR,
                 bg=ENTRY_BG, relief=FLAT, bd=0, insertbackground=TEXT_COLOR)
    entry.pack(fill=X, ipady=8, ipadx=10)

    # Underline effect
    underline = Frame(entry_frame, height=2, bg=ACCENT_COLOR)
    underline.pack(fill=X)

    return entry

# ========== MODERN STYLED COMBOBOX ==========
def create_modern_combobox(parent, label_text, values, row, default_index=0):
    """Create a modern combobox with label"""
    # Label
    label = Label(parent, text=label_text, font=FONT_BOLD,
                 fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    label.grid(row=row, column=0, sticky="w", pady=(15, 5), padx=20)

    # Combobox container
    combo_frame = Frame(parent, bg=CONTAINER_BG)
    combo_frame.grid(row=row+1, column=0, sticky="ew", pady=(0, 10), padx=20)

    # Style for combobox
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Modern.TCombobox",
                   fieldbackground=ENTRY_BG,
                   background=ENTRY_BG,
                   foreground=TEXT_COLOR,
                   arrowcolor=TEXT_COLOR,
                   bordercolor=CONTAINER_BG,
                   lightcolor=CONTAINER_BG,
                   darkcolor=CONTAINER_BG)
    style.map('Modern.TCombobox',
             fieldbackground=[('readonly', ENTRY_BG)],
             selectbackground=[('readonly', ACCENT_COLOR)])

    # Combobox
    combo = ttk.Combobox(combo_frame, values=values,
                         state="readonly", style="Modern.TCombobox",
                         font=FONT_NORMAL)
    combo.pack(fill=X, ipady=8)
    combo.current(default_index)

    return combo

# ========== MODERN BUTTON FUNCTION ==========
def create_modern_button(parent, text, command, bg_color=BUTTON_BG, hover_color=BUTTON_HOVER, width=12):
    """Create a modern styled button with hover effect"""
    btn = Button(parent, text=text, command=command,
                font=FONT_BOLD, fg=TEXT_COLOR, bg=bg_color,
                relief=FLAT, bd=0, cursor="hand2",
                activebackground=hover_color,
                activeforeground=TEXT_COLOR,
                padx=15, pady=10, width=width)

    # Hover effect
    def on_enter(e):
        btn['background'] = hover_color
    def on_leave(e):
        btn['background'] = bg_color

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def open_main_app(parent=None, on_logout=None):
    """
    Open the main electric bill calculator application.
    """
    if parent is None:
        win = Tk()
        owns_root = True
        win.title("Electric Bill Calculator")
        win.geometry("1000x750")
        win.configure(bg=BG_COLOR)

        # Center window
        window_width = 1000
        window_height = 750
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        position_top = int(screen_height / 4 - window_height / 4)
        position_right = int(screen_width / 2 - window_width / 2)
        win.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

        frame = Frame(win, bg=BG_COLOR)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
    else:
        owns_root = False
        frame = Frame(parent, bg=BG_COLOR)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

    # App Title
    title_frame = Frame(frame, bg=BG_COLOR)
    title_frame.pack(fill=X, pady=(0, 20))

    Label(title_frame, text="Electric Bill Calculator",
          font=("yu gothic ui bold", 24),
          fg=TEXT_COLOR, bg=BG_COLOR).pack()

    # Create Notebook with custom style
    style = ttk.Style()
    style.theme_use('clam')

    # Configure Notebook style
    style.configure("Modern.TNotebook",
                   background=BG_COLOR,
                   borderwidth=0)
    style.configure("Modern.TNotebook.Tab",
                   background=CONTAINER_BG,
                   foreground=TEXT_COLOR,
                   padding=[20, 10],
                   font=("yu gothic ui", 11, "bold"))
    style.map("Modern.TNotebook.Tab",
             background=[("selected", ACCENT_COLOR)],
             foreground=[("selected", TEXT_COLOR)])

    notebook = ttk.Notebook(frame, style="Modern.TNotebook")
    notebook.pack(fill='both', expand=True)

    # Calculator Tab
    calc_frame = Frame(notebook, bg=CONTAINER_BG)
    notebook.add(calc_frame, text="Bill Calculator")

    # History Tab
    history_frame = Frame(notebook, bg=BG_COLOR)
    notebook.add(history_frame, text="History")

    # Initialize History Manager
    history_manager = HistoryManager(history_frame)

    # ========== CALCULATOR TAB LAYOUT ==========
    # Main container for calculator - using grid
    main_calc_frame = Frame(calc_frame, bg=CONTAINER_BG)
    main_calc_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    calc_frame.grid_rowconfigure(0, weight=1)
    calc_frame.grid_columnconfigure(0, weight=1)

    # Left side - Input fields (using grid)
    left_container = Frame(main_calc_frame, bg=CONTAINER_BG)
    left_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    # Right side - Output and buttons (using grid)
    right_container = Frame(main_calc_frame, bg=CONTAINER_BG)
    right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    # Configure main_calc_frame grid weights
    main_calc_frame.grid_rowconfigure(0, weight=1)
    main_calc_frame.grid_columnconfigure(0, weight=1)
    main_calc_frame.grid_columnconfigure(1, weight=1)

    # ========== LEFT SIDE - INPUT FIELDS ==========
    # Customer Information Section - using pack for vertical stacking
    input_frame = Frame(left_container, bg=CONTAINER_BG)
    input_frame.pack(fill='both', expand=True)

    # Create a canvas and scrollbar for the input form
    canvas = Canvas(input_frame, bg=CONTAINER_BG, highlightthickness=0)
    scrollbar = Scrollbar(input_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg=CONTAINER_BG)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Section Title
    Label(scrollable_frame, text="Customer Information",
          font=("yu gothic ui bold", 16),
          fg=TEXT_COLOR, bg=CONTAINER_BG).pack(anchor="w", pady=(0, 20), padx=20)

    # Create input fields using modern functions - all using pack in their own frames
    name_label = Label(scrollable_frame, text="Customer Name:", font=FONT_BOLD,
                      fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    name_label.pack(anchor="w", pady=(15, 5), padx=20)

    name_entry_frame = Frame(scrollable_frame, bg=CONTAINER_BG)
    name_entry_frame.pack(fill=X, pady=(0, 10), padx=20)
    name_entry = Entry(name_entry_frame, font=FONT_NORMAL, fg=TEXT_COLOR,
                      bg=ENTRY_BG, relief=FLAT, bd=0, insertbackground=TEXT_COLOR)
    name_entry.pack(fill=X, ipady=8, ipadx=10)
    Frame(name_entry_frame, height=2, bg=ACCENT_COLOR).pack(fill=X)

    # Account Number
    acc_label = Label(scrollable_frame, text="Account Number:", font=FONT_BOLD,
                     fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    acc_label.pack(anchor="w", pady=(15, 5), padx=20)

    acc_entry_frame = Frame(scrollable_frame, bg=CONTAINER_BG)
    acc_entry_frame.pack(fill=X, pady=(0, 10), padx=20)
    acc_entry = Entry(acc_entry_frame, font=FONT_NORMAL, fg=TEXT_COLOR,
                     bg=ENTRY_BG, relief=FLAT, bd=0, insertbackground=TEXT_COLOR)
    acc_entry.pack(fill=X, ipady=8, ipadx=10)
    Frame(acc_entry_frame, height=2, bg=ACCENT_COLOR).pack(fill=X)

    # Address
    addr_label = Label(scrollable_frame, text="Address:", font=FONT_BOLD,
                      fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    addr_label.pack(anchor="w", pady=(15, 5), padx=20)

    addr_entry_frame = Frame(scrollable_frame, bg=CONTAINER_BG)
    addr_entry_frame.pack(fill=X, pady=(0, 10), padx=20)
    addr_entry = Entry(addr_entry_frame, font=FONT_NORMAL, fg=TEXT_COLOR,
                      bg=ENTRY_BG, relief=FLAT, bd=0, insertbackground=TEXT_COLOR)
    addr_entry.pack(fill=X, ipady=8, ipadx=10)
    Frame(addr_entry_frame, height=2, bg=ACCENT_COLOR).pack(fill=X)

    # Customer Type Combobox
    type_label = Label(scrollable_frame, text="Customer Type:", font=FONT_BOLD,
                      fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    type_label.pack(anchor="w", pady=(15, 5), padx=20)

    type_frame = Frame(scrollable_frame, bg=CONTAINER_BG)
    type_frame.pack(fill=X, pady=(0, 10), padx=20)

    # Style for combobox
    combo_style = ttk.Style()
    combo_style.theme_use('clam')
    combo_style.configure("Modern.TCombobox",
                         fieldbackground=ENTRY_BG,
                         background=ENTRY_BG,
                         foreground=TEXT_COLOR,
                         arrowcolor=TEXT_COLOR,
                         bordercolor=CONTAINER_BG)
    combo_style.map('Modern.TCombobox',
                   fieldbackground=[('readonly', ENTRY_BG)],
                   selectbackground=[('readonly', ACCENT_COLOR)])

    type_box = ttk.Combobox(type_frame, values=["Residential", "Commercial"],
                           state="readonly", style="Modern.TCombobox",
                           font=FONT_NORMAL)
    type_box.pack(fill=X, ipady=8)
    type_box.current(0)

    # Discount Combobox
    discount_label = Label(scrollable_frame, text="Discount (if applicable):", font=FONT_BOLD,
                          fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    discount_label.pack(anchor="w", pady=(15, 5), padx=20)

    discount_frame = Frame(scrollable_frame, bg=CONTAINER_BG)
    discount_frame.pack(fill=X, pady=(0, 10), padx=20)

    discount_combo = ttk.Combobox(discount_frame, values=["None", "Senior Citizen (5%)"],
                                 state="readonly", style="Modern.TCombobox",
                                 font=FONT_NORMAL)
    discount_combo.pack(fill=X, ipady=8)
    discount_combo.current(0)

    # Billing Month
    month_label = Label(scrollable_frame, text="Billing Month:", font=FONT_BOLD,
                       fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    month_label.pack(anchor="w", pady=(15, 5), padx=20)

    month_frame = Frame(scrollable_frame, bg=CONTAINER_BG)
    month_frame.pack(fill=X, pady=(0, 10), padx=20)

    month_entry = DateEntry(month_frame, width=33, background='darkblue',
                           foreground='white', borderwidth=0, font=FONT_NORMAL)
    month_entry.pack(fill=X, ipady=8)

    # kWh Used
    units_label = Label(scrollable_frame, text="kWh Used:", font=FONT_BOLD,
                       fg=TEXT_COLOR, bg=CONTAINER_BG, anchor="w")
    units_label.pack(anchor="w", pady=(15, 5), padx=20)

    units_entry_frame = Frame(scrollable_frame, bg=CONTAINER_BG)
    units_entry_frame.pack(fill=X, pady=(0, 10), padx=20)
    units_entry = Entry(units_entry_frame, font=FONT_NORMAL, fg=TEXT_COLOR,
                       bg=ENTRY_BG, relief=FLAT, bd=0, insertbackground=TEXT_COLOR)
    units_entry.pack(fill=X, ipady=8, ipadx=10)
    Frame(units_entry_frame, height=2, bg=ACCENT_COLOR).pack(fill=X)

    # Clear Form Button
    clear_btn_frame = Frame(scrollable_frame, bg=CONTAINER_BG)
    clear_btn_frame.pack(pady=(20, 0), padx=20)

    clear_btn = create_modern_button(clear_btn_frame, "Clear Form",
                                    lambda: clear_form(), DANGER_COLOR, "#FF5252", 15)
    clear_btn.pack()

       # ========== RIGHT SIDE - OUTPUT & BUTTONS ==========
    # Configure right_container to have two rows: one for output, one for buttons
    right_container.grid_rowconfigure(0, weight=1)  # output will expand
    right_container.grid_rowconfigure(1, weight=0)  # buttons will not expand
    right_container.grid_columnconfigure(0, weight=1)

    # Output Section
    output_frame = Frame(right_container, bg=CONTAINER_BG)
    output_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

    # Section Title
    Label(output_frame, text="Bill Calculation",
          font=("yu gothic ui bold", 16),
          fg=TEXT_COLOR, bg=CONTAINER_BG).pack(anchor="w", pady=(0, 15), padx=20)

    # Output Text Box with Scrollbar
    text_frame = Frame(output_frame, bg=CONTAINER_BG)
    text_frame.pack(fill='both', expand=True, padx=20)

    output_box = Text(text_frame, width=45, height=20,
                     state='disabled', bg=ENTRY_BG, fg=TEXT_COLOR,
                     font=("Consolas", 10), relief=FLAT,
                     wrap=WORD, padx=10, pady=10)
    output_box.pack(side=LEFT, fill='both', expand=True)

    # Scrollbar
    scrollbar = Scrollbar(text_frame, command=output_box.yview,
                         bg=ENTRY_BG, troughcolor=CONTAINER_BG,
                         activebackground=ACCENT_COLOR)
    scrollbar.pack(side=RIGHT, fill=Y)
    output_box.config(yscrollcommand=scrollbar.set)

    # Buttons Frame
    button_frame = Frame(right_container, bg=CONTAINER_BG)
    button_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

    # Create buttons in a horizontal layout
    buttons_container = Frame(button_frame, bg=CONTAINER_BG)
    buttons_container.pack(pady=10)

    # Generate Bill Button
    generate_btn = create_modern_button(buttons_container, "Generate Bill",
                                       lambda: generate_bill(), SUCCESS_COLOR, "#45a049")
    generate_btn.grid(row=0, column=0, padx=5)

    # Download PDF Button
    pdf_btn = create_modern_button(buttons_container, "Download PDF",
                                  lambda: download_pdf(), ACCENT_COLOR, BUTTON_HOVER)
    pdf_btn.grid(row=0, column=1, padx=5)

    # Export CSV Button
    csv_btn = create_modern_button(buttons_container, "Export CSV",
                                  lambda: export_csv(), "#9B59B6", "#8E44AD")
    csv_btn.grid(row=0, column=2, padx=5)

    # Logout button (only shown in orchestrator mode)
    if not owns_root and callable(on_logout):
        logout_btn = create_modern_button(buttons_container, "Logout",
                                         on_logout, DANGER_COLOR, "#FF5252")
        logout_btn.grid(row=0, column=3, padx=5)

    # ========== CALLBACK FUNCTIONS ==========
    def clear_form():
        """Clear all input fields and output box"""
        # Clear all entry fields
        name_entry.delete(0, END)
        acc_entry.delete(0, END)
        addr_entry.delete(0, END)
        units_entry.delete(0, END)

        # Reset comboboxes to default values
        type_box.current(0)
        discount_combo.current(0)

        # Clear output box
        output_box.config(state='normal')
        output_box.delete("1.0", END)
        output_box.config(state='disabled')

        # Set focus to first field
        name_entry.focus_set()

    def generate_bill():
        name = name_entry.get()
        account = acc_entry.get()
        address = addr_entry.get()
        customer_type = type_box.get().lower()
        discount_value = discount_combo.get()
        billing_month = month_entry.get()

        # Check if senior discount applies
        is_senior = discount_value == "Senior Citizen (5%)"

        try:
            units = float(units_entry.get())
        except Exception:
            output_box.config(state='normal')
            output_box.delete("1.0", END)
            output_box.insert(END, "Error: Invalid kWh input. Please enter a valid number.\n")
            output_box.config(state='disabled')
            return

        # Calculate bill (now returns 7 values)
        energy, fixed, vat, env_fee, applied_rates, total, discount_amount = calculate_bill(
            units, customer_type, is_senior
        )

        # Display Output
        output_box.config(state='normal')
        output_box.delete("1.0", END)
        output_box.insert(END, "=" * 50 + "\n")
        output_box.insert(END, "ELECTRIC BILL STATEMENT\n")
        output_box.insert(END, "=" * 50 + "\n\n")
        output_box.insert(END, f"Customer Name: {name}\n")
        output_box.insert(END, f"Account Number: {account}\n")
        output_box.insert(END, f"Address: {address}\n")
        output_box.insert(END, f"Consumer Type: {customer_type}\n")
        output_box.insert(END, f"Discount Applied: {discount_value}\n")
        output_box.insert(END, f"Billing Month: {billing_month}\n")
        output_box.insert(END, "-" * 40 + "\n")
        output_box.insert(END, f"Total kWh Used: {units} kWh\n")
        output_box.insert(END, f"kWh Rate: ₱{applied_rates}/kWh\n")
        output_box.insert(END, f"Fixed Fee: ₱{fixed:.2f}\n")
        output_box.insert(END, f"Base Charge: ₱{energy:.2f}\n")
        output_box.insert(END, f"Environmental Fee: ₱{env_fee:.2f}\n")
        output_box.insert(END, f"VAT (12%): ₱{vat:.2f}\n")

        # Show discount if applied
        if is_senior:
            output_box.insert(END, f"Senior Discount (5%): -₱{discount_amount:.2f}\n")

        output_box.insert(END, "-" * 40 + "\n")
        output_box.insert(END, f"TOTAL AMOUNT DUE: ₱{total:.2f}\n")
        output_box.insert(END, "=" * 50 + "\n")
        output_box.config(state='disabled')

        # ADD TO HISTORY - AFTER calculating all values
        history_manager.add_calculation(
            customer_name=name,
            account=account,
            kwh_used=units,
            total_cost=total,
            customer_type=customer_type,
            discount_value=discount_value,
            discount_amount=discount_amount,
            billing_month=billing_month
        )

    def download_pdf():
        file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not file:
            return

        try:
            units = float(units_entry.get())
        except Exception:
            output_box.config(state='normal')
            output_box.insert(END, "\nError: Invalid kWh input for PDF.\n")
            output_box.config(state='disabled')
            return

        customer_type = type_box.get().lower()
        discount_value = discount_combo.get()
        is_senior = discount_value == "Senior Citizen (5%)"

        # Calculate with discount if applicable
        energy, fixed, vat, env_fee, applied_rates, total, discount_amount = calculate_bill(
            units, customer_type, is_senior
        )

        data = {
            "name": name_entry.get(),
            "account": acc_entry.get(),
            "address": addr_entry.get(),
            "type": type_box.get(),
            "discount": discount_value,
            "discount_amount": discount_amount,
            "month": month_entry.get(),
            "kwh": units,
            "rate": applied_rates,
            "fixed": fixed,
            "base": energy,
            "env": env_fee,
            "vat": vat,
            "total": total
        }

        generate_bill_pdf(data, file)

    def export_csv():
        """Export all history to CSV file (from calculator tab)"""
        history_data = history_manager.get_session_history()

        if not history_data:
            messagebox.showinfo("No Data", "No calculation history to export.")
            return

        # Create default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default = f"electric_bill_history_{timestamp}.csv"

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow([
                    "Timestamp", "Customer Name", "Account Number",
                    "kWh Used", "Total Cost", "Customer Type",
                    "Discount Type", "Discount Amount", "Billing Month"
                ])
                # Write data
                for r in history_data:
                    writer.writerow([
                        r['timestamp'], r['customer_name'], r['account'],
                        r['kwh_used'], r['total_cost'], r['customer_type'],
                        r['discount_value'], r['discount_amount'], r['billing_month']
                    ])

            messagebox.showinfo("Success", f"CSV exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{str(e)}")

    if owns_root:
        win.mainloop()

    return frame

if __name__ == "__main__":
    open_main_app()
