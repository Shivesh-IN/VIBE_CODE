import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import math
import requests
import threading
import time
import random

# --- Splash Screen Code (Added from code.py) ---
class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Loading...")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.root.configure(bg='#2c3e50')

        # Remove window decorations
        self.root.overrideredirect(True)

        # Center the splash screen
        self.center_window()

        # Create splash content
        self.create_splash_content()

        # Schedule the animation to start after the window is drawn
        self.root.after(100, self.animate_loading)

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 400) // 2
        y = (self.root.winfo_screenheight() - 300) // 2
        self.root.geometry(f"400x300+{x}+{y}")

    def create_splash_content(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="🚀 Investment Calculator Pro",
                              font=('Arial', 18, 'bold'),
                              fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(20, 10))

        # Subtitle
        subtitle_label = tk.Label(main_frame, text="Professional Trading & Investment Analysis",
                                 font=('Arial', 10),
                                 fg='#bdc3c7', bg='#2c3e50')
        subtitle_label.pack()

        # Loading animation area
        self.loading_frame = tk.Frame(main_frame, bg='#2c3e50')
        self.loading_frame.pack(expand=True, fill='both', pady=20)

        # Progress bar
        self.progress_var = tk.StringVar()
        self.progress_label = tk.Label(self.loading_frame, textvariable=self.progress_var,
                                      font=('Arial', 10), fg='#3498db', bg='#2c3e50')
        self.progress_label.pack(pady=10)

        # Loading dots
        self.dots_var = tk.StringVar()
        self.dots_label = tk.Label(self.loading_frame, textvariable=self.dots_var,
                                  font=('Arial', 16), fg='#3498db', bg='#2c3e50')
        self.dots_label.pack()

        # Version info
        version_label = tk.Label(main_frame, text="Version 2.0 - With Live Data",
                                font=('Arial', 8),
                                fg='#7f8c8d', bg='#2c3e50')
        version_label.pack(side='bottom')

    def animate_loading(self):
        loading_messages = [
            "Initializing components...",
            "Loading calculation engines...",
            "Connecting to live data feed...",
            "Setting up user interface...",
            "Configuring fee structures...",
            "Finalizing setup..."
        ]

        dots_animation = ["|", "/", "-", "\\", "|", "/", "-", "\\", "|", "/"]

        # Use root.after for a non-blocking animation loop
        def update_step(i=0, j=0):
            if i < len(loading_messages):
                self.progress_var.set(loading_messages[i])
                self.dots_var.set(dots_animation[j % len(dots_animation)])
                self.root.update_idletasks()
                if j < 10: # Animation cycles per message
                    self.root.after(50, update_step, i, j + 1)
                else:
                    self.root.after(50, update_step, i + 1, 0)
            else:
                self.finish_loading()

        update_step()

    def finish_loading(self):
        # Show completion message
        self.progress_var.set("Ready to launch!")
        self.dots_var.set("DONE")
        self.root.update()
        self.root.after(500)

        # Close splash and open main app
        self.root.destroy()

        # Launch main application
        app = InvestmentCalculator()
        app.run()


class InvestmentCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.crypto_data = []
        self.search_var = tk.StringVar()
        self.crypto_update_thread = None
        self.stop_crypto_thread = threading.Event()

        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.create_widgets()
        self.center_window()

        self.trading_data = {
            'buy_quantity': 0,
            'buy_price': 0,
            'total_invested': 0
        }
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window closing event."""
        self.stop_crypto_thread.set()
        if self.crypto_update_thread and self.crypto_update_thread.is_alive():
            self.crypto_update_thread.join(timeout=1)
        self.root.destroy()

    def setup_window(self):
        self.root.title("🚀 Investment & Trading Calculator Pro")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        self.root.configure(bg='#f0f0f0')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        self.style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        self.style.configure('Info.TLabel', font=('Arial', 10), foreground='#7f8c8d')
        self.style.configure('Success.TLabel', font=('Arial', 10, 'bold'), foreground='#27ae60')
        self.style.configure('Warning.TLabel', font=('Arial', 10, 'bold'), foreground='#e74c3c')
        self.style.configure('Accent.TButton', font=('Arial', 11, 'bold'))
        self.style.configure('Success.TButton', font=('Arial', 10, 'bold'))
        self.style.configure('Danger.TButton', font=('Arial', 10, 'bold'))
        # Custom styles for crypto details
        self.style.configure('Crypto.TFrame', background='#34495e', borderwidth=1, relief='raised')
        self.style.configure('Market.TLabel', font=('Arial', 14, 'bold'), foreground='white', background='#34495e')
        self.style.configure('Change.TLabel', font=('Arial', 11, 'bold'), background='#34495e')
        self.style.configure('Price.TLabel', font=('Arial', 12), foreground='white', background='#34495e')
        self.style.configure('Detail.TLabel', font=('Arial', 9), foreground='#ecf0f1', background='#34495e')

    def setup_variables(self):
        self.principal_var = tk.StringVar()
        self.target_investable_var = tk.StringVar()
        self.buy_quantity_var = tk.StringVar()
        self.buy_price_var = tk.StringVar()
        self.sell_price_var = tk.StringVar()
        self.sell_quantity_var = tk.StringVar()
        self.risk_percentage_var = tk.StringVar()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        main_frame.rowconfigure(1, weight=1)
        # Configure for 2 columns: Controls | Resizable Panes
        main_frame.columnconfigure(0, weight=0, minsize=400)
        main_frame.columnconfigure(1, weight=1)

        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        ttk.Label(title_frame, text="💰 Investment & Trading Calculator Pro", style='Title.TLabel').pack(pady=10)

        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=1, column=0, sticky='nswe', padx=(0, 10))
        left_panel.grid_propagate(False)

        # Create a resizable paned window for results and crypto
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.grid(row=1, column=1, sticky='nsew')
        
        # --- Left Pane (Detailed Results) ---
        results_container = ttk.Frame(paned_window, relief="groove")
        paned_window.add(results_container, weight=3) # Initially larger
        self.create_results_area(results_container)

        # --- Right Pane (Crypto Prices) ---
        crypto_container = ttk.Frame(paned_window, relief="groove")
        paned_window.add(crypto_container, weight=1) # Initially smaller
        self.create_crypto_panel(crypto_container)

        # Create the calculator tabs
        self.notebook = ttk.Notebook(left_panel)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        self.create_tab1a()
        self.create_tab1b()
        self.create_tab2()
        self.create_portfolio_tab()
        self.create_bottom_buttons(left_panel)

    def _bind_mousewheel(self, widget, canvas):
        """Binds mouse wheel scrolling to a widget and its children."""
        command = self._on_mousewheel_factory(canvas)
        widget.bind("<MouseWheel>", command) # Windows, MacOS
        widget.bind("<Button-4>", command) # Linux
        widget.bind("<Button-5>", command) # Linux
        for child in widget.winfo_children():
            self._bind_mousewheel(child, canvas)
            
    def _on_mousewheel_factory(self, canvas):
        """Factory to create a scroll command for a specific canvas."""
        def _on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return _on_mousewheel

    def create_results_area(self, parent):
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)
        ttk.Label(parent, text="📋 Detailed Results", style='Title.TLabel').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        
        text_frame = ttk.Frame(parent)
        text_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self.results_text = tk.Text(text_frame, font=('Courier', 10), wrap=tk.WORD, bg='#2c3e50', fg='#ecf0f1', relief='flat')
        self.results_text.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.insert(tk.END, self.format_welcome_message())
        self.results_text.bind("<MouseWheel>", self._on_mousewheel_factory(self.results_text))
        self.results_text.bind("<Button-4>", self._on_mousewheel_factory(self.results_text))
        self.results_text.bind("<Button-5>", self._on_mousewheel_factory(self.results_text))
        
    def create_crypto_panel(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)
        
        ttk.Label(parent, text="📈 Live Crypto Prices", style='Title.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.search_var.trace("w", self.filter_crypto_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Arial', 11))
        search_entry.pack(fill='x', expand=True)
        search_entry.insert(0, "🔍 Search e.g., BTC, ETH...")

        canvas_frame = ttk.Frame(parent)
        canvas_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=(0, 5))
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        
        self.crypto_canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.crypto_canvas.yview)
        self.crypto_scrollable_frame = ttk.Frame(self.crypto_canvas)

        self.crypto_scrollable_frame.bind("<Configure>", lambda e: self.crypto_canvas.configure(scrollregion=self.crypto_canvas.bbox("all")))
        self.crypto_canvas.create_window((0, 0), window=self.crypto_scrollable_frame, anchor="nw")
        self.crypto_canvas.configure(yscrollcommand=scrollbar.set)

        self.crypto_canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        self._bind_mousewheel(self.crypto_scrollable_frame, self.crypto_canvas)
        self._bind_mousewheel(self.crypto_canvas, self.crypto_canvas)

        self.crypto_update_thread = threading.Thread(target=self.fetch_and_display_data, daemon=True)
        self.crypto_update_thread.start()
        
    def fetch_and_display_data(self):
        api_url = "https://api.coindcx.com/exchange/ticker"
        while not self.stop_crypto_thread.is_set():
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    all_data = response.json()
                    inr_data = [d for d in all_data if d['market'].endswith('INR')]
                    
                    def sort_key(d):
                        try:
                            return float(d.get('change_24_hour', '0'))
                        except (ValueError, TypeError):
                            return -float('inf')
                            
                    inr_data.sort(key=sort_key, reverse=True)
                    self.crypto_data = inr_data
                    
                    if self.root.winfo_exists():
                        self.root.after(0, self.update_crypto_list_ui)
                
                time.sleep(60)
            except requests.RequestException:
                time.sleep(30)
            except Exception:
                break
                
    def update_crypto_list_ui(self):
        if not self.root.winfo_exists(): return
        
        y_pos = self.crypto_canvas.yview()[0]
        
        for widget in self.crypto_scrollable_frame.winfo_children():
            widget.destroy()

        for item in self.crypto_data:
            self.create_crypto_item_widget(item)

        self.root.after(100, lambda: self.crypto_canvas.yview_moveto(y_pos))
        self._bind_mousewheel(self.crypto_scrollable_frame, self.crypto_canvas)
        self.filter_crypto_list()

    def create_crypto_item_widget(self, item_data):
        item_frame = ttk.Frame(self.crypto_scrollable_frame, style='Crypto.TFrame', padding=10)
        
        market = item_data.get('market', '').replace('INR', '')
        try:
            change_24h = float(item_data.get('change_24_hour', '0'))
            color = '#2ecc71' if change_24h > 0 else '#e74c3c' if change_24h < 0 else '#bdc3c7'
        except ValueError:
            change_24h = 0.0
            color = '#bdc3c7'
        
        try: last_price = float(item_data.get('last_price', '0'))
        except ValueError: last_price = 0.0
        try: high = float(item_data.get('high', '0'))
        except ValueError: high = 0.0
        try: low = float(item_data.get('low', '0'))
        except ValueError: low = 0.0
        try: volume = float(item_data.get('volume', '0'))
        except ValueError: volume = 0.0

        item_frame.columnconfigure(1, weight=1)
        ttk.Label(item_frame, text=market, style='Market.TLabel').grid(row=0, column=0, sticky='w')
        change_label = ttk.Label(item_frame, text=f"{change_24h:+.2f}%", style='Change.TLabel', foreground=color)
        change_label.grid(row=0, column=1, sticky='e')
        
        ttk.Label(item_frame, text=f"₹{last_price:,.4f}", style='Price.TLabel').grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 0))

        detail_frame = ttk.Frame(item_frame, style='Crypto.TFrame')
        detail_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(5,0))
        
        ttk.Label(detail_frame, text=f"H: {high:,.4f}", style='Detail.TLabel').pack(side='left', expand=True, fill='x')
        ttk.Label(detail_frame, text=f"L: {low:,.4f}", style='Detail.TLabel').pack(side='left', expand=True, fill='x')
        ttk.Label(detail_frame, text=f"Vol: {volume:,.2f}", style='Detail.TLabel').pack(side='right', expand=True, fill='x')

        item_frame.market_name = market.lower()
        item_frame.pack(fill='x', padx=5, pady=3)
        return item_frame

    def filter_crypto_list(self, *args):
        search_term = self.search_var.get().lower().replace("🔍 search e.g., btc, eth...", "")
        if not self.root.winfo_exists() or not hasattr(self, 'crypto_scrollable_frame'): return
            
        for child in self.crypto_scrollable_frame.winfo_children():
            if search_term in child.market_name:
                child.pack(fill='x', padx=5, pady=3)
            else:
                child.pack_forget()

    def create_tab1a(self):
        tab1a = ttk.Frame(self.notebook)
        self.notebook.add(tab1a, text="📊 Investable Amount")
        info_frame = ttk.LabelFrame(tab1a, text="💡 Fee Structure Information", padding=10)
        info_frame.pack(fill='x', pady=(0, 10))
        info_text = "• Platform Fee: 0.5% of principal\n• GST on Platform Fee: 18%\n• Final investable amount = Principal - Fees"
        ttk.Label(info_frame, text=info_text, style='Info.TLabel').pack(anchor='w')
        input_frame = ttk.LabelFrame(tab1a, text="📝 Input Details", padding=10)
        input_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(input_frame, text="Principal Amount (₹):", style='Subtitle.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(input_frame, textvariable=self.principal_var, font=('Arial', 11), width=20).grid(row=0, column=1, padx=(10, 0), pady=5)
        ttk.Button(input_frame, text="🧮 Calculate", command=self.calculate_investable_amount, style='Accent.TButton').grid(row=1, column=0, columnspan=2, pady=10)

    def create_tab1b(self):
        tab1b = ttk.Frame(self.notebook)
        self.notebook.add(tab1b, text="🔄 Required Principal")
        info_frame = ttk.LabelFrame(tab1b, text="💡 Reverse Calculation", padding=10)
        info_frame.pack(fill='x', pady=(0, 10))
        info_text = "• Enter your target investable amount\n• Calculate the principal needed"
        ttk.Label(info_frame, text=info_text, style='Info.TLabel').pack(anchor='w')
        input_frame = ttk.LabelFrame(tab1b, text="📝 Input Details", padding=10)
        input_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(input_frame, text="Target Amount (₹):", style='Subtitle.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(input_frame, textvariable=self.target_investable_var, font=('Arial', 11), width=20).grid(row=0, column=1, padx=(10, 0), pady=5)
        ttk.Button(input_frame, text="🔄 Calculate", command=self.calculate_required_principal, style='Accent.TButton').grid(row=1, column=0, columnspan=2, pady=10)

    def create_tab2(self):
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="📈 Trading")
        buy_frame = ttk.LabelFrame(tab2, text="📊 Step 1: Buy Details", padding=10)
        buy_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(buy_frame, text="Quantity:", style='Subtitle.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(buy_frame, textvariable=self.buy_quantity_var, font=('Arial', 11), width=15).grid(row=0, column=1, padx=(10, 0), pady=5)
        ttk.Label(buy_frame, text="Price (₹):", style='Subtitle.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(buy_frame, textvariable=self.buy_price_var, font=('Arial', 11), width=15).grid(row=1, column=1, padx=(10, 0), pady=5)
        ttk.Button(buy_frame, text="💰 Record Buy", command=self.calculate_investment, style='Success.TButton').grid(row=2, column=0, columnspan=2, pady=10)
        sell_frame = ttk.LabelFrame(tab2, text="📊 Step 2: Sell Details", padding=10)
        sell_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(sell_frame, text="Price (₹):", style='Subtitle.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(sell_frame, textvariable=self.sell_price_var, font=('Arial', 11), width=15).grid(row=0, column=1, padx=(10, 0), pady=5)
        ttk.Label(sell_frame, text="Quantity:", style='Subtitle.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(sell_frame, textvariable=self.sell_quantity_var, font=('Arial', 11), width=15).grid(row=1, column=1, padx=(10, 0), pady=5)
        ttk.Button(sell_frame, text="📈 Calculate P&L", command=self.calculate_trading_pnl, style='Accent.TButton').grid(row=2, column=0, columnspan=2, pady=10)

    def create_portfolio_tab(self):
        portfolio_tab = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_tab, text="💼 Portfolio")
        stats_frame = ttk.LabelFrame(portfolio_tab, text="⚡ Quick Stats", padding=10)
        stats_frame.pack(fill='x', pady=(0, 10))
        self.portfolio_value_var = tk.StringVar(value="₹0.00")
        self.total_profit_var = tk.StringVar(value="₹0.00")
        self.roi_var = tk.StringVar(value="0.00%")
        ttk.Label(stats_frame, text="Portfolio Value:", style='Subtitle.TLabel').grid(row=0, column=0, sticky='w', pady=2)
        ttk.Label(stats_frame, textvariable=self.portfolio_value_var, style='Success.TLabel').grid(row=0, column=1, sticky='w', padx=(10, 0), pady=2)
        ttk.Label(stats_frame, text="Total P&L:", style='Subtitle.TLabel').grid(row=1, column=0, sticky='w', pady=2)
        ttk.Label(stats_frame, textvariable=self.total_profit_var, style='Success.TLabel').grid(row=1, column=1, sticky='w', padx=(10, 0), pady=2)
        ttk.Label(stats_frame, text="ROI:", style='Subtitle.TLabel').grid(row=2, column=0, sticky='w', pady=2)
        ttk.Label(stats_frame, textvariable=self.roi_var, style='Success.TLabel').grid(row=2, column=1, sticky='w', padx=(10, 0), pady=2)
        risk_frame = ttk.LabelFrame(portfolio_tab, text="⚠️ Risk Calculator", padding=10)
        risk_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(risk_frame, text="Risk %:", style='Subtitle.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(risk_frame, textvariable=self.risk_percentage_var, font=('Arial', 11), width=10).grid(row=0, column=1, padx=(10, 0), pady=5)
        ttk.Button(risk_frame, text="⚠️ Calculate Risk", command=self.calculate_risk_analysis, style='Danger.TButton').grid(row=1, column=0, columnspan=2, pady=10)

    def create_bottom_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=10, side='bottom')
        ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_results, style='Danger.TButton').pack(side='left', expand=True, fill='x', padx=2)
        ttk.Button(button_frame, text="💾 Save", command=self.save_results, style='Success.TButton').pack(side='left', expand=True, fill='x', padx=2)
        ttk.Button(button_frame, text="📊 Export", command=self.export_data, style='Accent.TButton').pack(side='left', expand=True, fill='x', padx=2)

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
    def validate_input(self, value, field_name):
        try:
            num_value = float(value)
            if num_value <= 0:
                messagebox.showerror("Invalid Input", f"{field_name} must be a positive number!")
                return None
            return num_value
        except ValueError:
            messagebox.showerror("Invalid Input", f"{field_name} must be a valid number!")
            return None
            
    def format_currency(self, amount): return f"₹{amount:,.2f}"
    def format_percentage(self, percentage): return f"{percentage:.2f}%"
    def format_welcome_message(self):
        return """
+======================================================================+
|           INVESTMENT & TRADING CALCULATOR PRO                        |
+======================================================================+
|                                                                      |
|  Welcome to your comprehensive investment analysis tool!             |
|                                                                      |
|  - Calculate investable amounts with detailed fee breakdown          |
|  - Complete trading P&L analysis                                     |
|  - Portfolio analytics and risk assessment                           |
|  - Check live crypto prices on the right!                            |
|                                                                      |
+======================================================================+
"""
    def calculate_investable_amount(self):
        principal = self.validate_input(self.principal_var.get(), "Principal Amount")
        if principal is None: return
        platform_fee = principal * 0.005
        gst_on_fee = platform_fee * 0.18
        total_fees = platform_fee + gst_on_fee
        investable_amount = principal - total_fees
        result = f"""
+----------------------------------------------------------+
|             INVESTABLE AMOUNT CALCULATION                |
+----------------------------------------------------------+
| PRINCIPAL:          {self.format_currency(principal):>25} |
|                                                          |
| FEE BREAKDOWN:                                           |
|  - Platform Fee:    {self.format_currency(platform_fee):>25} |
|  - GST on Fee:      {self.format_currency(gst_on_fee):>25} |
|  - Total Fees:      {self.format_currency(total_fees):>25} |
|                                                          |
| FINAL INVESTABLE:   {self.format_currency(investable_amount):>25} |
+----------------------------------------------------------+
"""
        self.display_result(result)
        
    def calculate_required_principal(self):
        target_investable = self.validate_input(self.target_investable_var.get(), "Target Investable Amount")
        if target_investable is None: return
        required_principal = target_investable / 0.9941
        result = f"""
+----------------------------------------------------------+
|            REQUIRED PRINCIPAL CALCULATION                |
+----------------------------------------------------------+
| TARGET INVESTABLE:  {self.format_currency(target_investable):>25} |
| REQUIRED PRINCIPAL: {self.format_currency(required_principal):>25} |
+----------------------------------------------------------+
"""
        self.display_result(result)

    def calculate_investment(self):
        quantity = self.validate_input(self.buy_quantity_var.get(), "Quantity")
        price = self.validate_input(self.buy_price_var.get(), "Average Price")
        if quantity is None or price is None: return
        self.trading_data['buy_quantity'] = quantity
        self.trading_data['buy_price'] = price
        self.trading_data['total_invested'] = quantity * price
        result = f"\n✅ Buy recorded: {quantity:.4f} units at {self.format_currency(price)} each.\nTotal Investment: {self.format_currency(self.trading_data['total_invested'])}\n"
        self.display_result(result)

    def get_risk_level(self, risk_percentage):
        if risk_percentage <= 5: return "CONSERVATIVE"
        elif risk_percentage <= 10: return "MODERATE"
        elif risk_percentage <= 15: return "AGGRESSIVE"
        else: return "VERY HIGH RISK"

    def update_portfolio_stats(self, portfolio_value, profit_loss, investment):
        self.portfolio_value_var.set(self.format_currency(portfolio_value))
        self.total_profit_var.set(f"{self.format_currency(profit_loss)}")
        roi = (profit_loss / investment * 100) if investment > 0 else 0
        self.roi_var.set(f"{self.format_percentage(roi)}")
        
    def calculate_trading_pnl(self):
        if self.trading_data['total_invested'] == 0:
            messagebox.showwarning("Missing Data", "Please calculate investment details first!")
            return
        sell_price = self.validate_input(self.sell_price_var.get(), "Selling Price")
        sell_quantity = self.validate_input(self.sell_quantity_var.get(), "Sell Quantity")
        if sell_price is None or sell_quantity is None: return
        if sell_quantity > self.trading_data['buy_quantity']:
            messagebox.showerror("Invalid Quantity", "Cannot sell more than you own!")
            return
            
        gross_selling_amount = sell_quantity * sell_price
        selling_platform_fee = gross_selling_amount * 0.005
        gst_on_selling_fee = selling_platform_fee * 0.18
        amount_after_platform_fees = gross_selling_amount - selling_platform_fee - gst_on_selling_fee
        tds = amount_after_platform_fees * 0.01
        final_withdrawal_amount = amount_after_platform_fees - tds
        proportional_invested = (sell_quantity / self.trading_data['buy_quantity']) * self.trading_data['total_invested']
        profit_loss = final_withdrawal_amount - proportional_invested
        result = f"""
+----------------------------------------------------------+
|                  TRADING P&L ANALYSIS                    |
+----------------------------------------------------------+
| GROSS SELL AMT:     {self.format_currency(gross_selling_amount):>25} |
| FINAL WITHDRAWAL:   {self.format_currency(final_withdrawal_amount):>25} |
| PROPORTIONAL COST:  {self.format_currency(proportional_invested):>25} |
|----------------------------------------------------------|
| NET P&L:            {self.format_currency(profit_loss):>25} |
+----------------------------------------------------------+
"""
        self.display_result(result)
        self.update_portfolio_stats(final_withdrawal_amount, profit_loss, proportional_invested)
        
    def calculate_risk_analysis(self):
        risk_percentage = self.validate_input(self.risk_percentage_var.get(), "Risk Percentage")
        if risk_percentage is None: return
        if self.trading_data['total_invested'] == 0:
            messagebox.showinfo("No Data", "Calculate investment first!")
            return
        total_investment = self.trading_data['total_invested']
        risk_amount = total_investment * (risk_percentage / 100)
        stop_loss_price = self.trading_data['buy_price'] * (1 - risk_percentage / 100)
        result = f"""
+----------------------------------------------------------+
|                   RISK ANALYSIS REPORT                   |
+----------------------------------------------------------+
| RISK LEVEL:         {self.get_risk_level(risk_percentage):>25} |
| RISK AMOUNT:        {self.format_currency(risk_amount):>25} |
| SUGGESTED STOP-LOSS:{self.format_currency(stop_loss_price):>25} |
+----------------------------------------------------------+
"""
        self.display_result(result)
    
    def display_result(self, result):
        self.results_text.insert(tk.END, result + "\n")
        self.results_text.see(tk.END)
        
    def clear_results(self):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, self.format_welcome_message())
        
    def save_results(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.results_text.get(1.0, tk.END))
            messagebox.showinfo("Success", "Results saved!")

    def export_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            data = {"trading_data": self.trading_data, "calculations": {k:v.get() for k,v in self.__dict__.items() if isinstance(v, tk.StringVar)}}
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Data exported!")

    def run(self):
        self.root.mainloop()

# --- Updated Main Execution Block ---
def main():
    # Show splash screen first, which then launches the main app
    splash = SplashScreen()
    splash.root.mainloop()

if __name__ == "__main__":
    main()