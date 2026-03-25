import tkinter as tk
from tkinter import ttk, Toplevel, Frame, Label, Button, Entry, filedialog
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import math

class NavigableKeyboard:
    def __init__(self, master, calculator):
        self.master = master
        self.calculator = calculator
        self.keyboard_window = None
        self.current_entry = None
        self.current_row = 0
        self.current_col = 0
    
    def toggle_keyboard(self):
        if self.keyboard_window is None or not self.keyboard_window.winfo_exists():
            self.show_keyboard()
        else:
            self.hide_keyboard()
    
    def show_keyboard(self):
        self.keyboard_window = Toplevel(self.master)
        self.keyboard_window.title("Options Keyboard")
        self.keyboard_window.resizable(0, 0)
        
        # Position keyboard
        x = self.master.winfo_x() - 59
        y = self.master.winfo_y() + 930
        self.keyboard_window.geometry(f"+{x}+{y}")
        
        # Current field indicator
        self.field_label = Label(self.keyboard_window, text="Click any field to start", 
                                font=('Helvetica', 5, 'bold'), bg='lightblue')
        self.field_label.grid(row=0, column=0, columnspan=3)
        
        # Framea
        arrow_frame = Frame(self.keyboard_window)
        arrow_frame.grid(row=1, column = 0, pady = 20, padx = 120, sticky = 'w')
        num_frame =  Frame(self.keyboard_window)
        num_frame.grid(row = 1, column = 1, sticky = 'w', padx = 10)
        key_frame =  Frame(self.keyboard_window)
        key_frame.grid(row = 2, column = 0, columnspan = 2)
        
        # Paste frame (below keyboard)
        paste_frame = Frame(self.keyboard_window)
        paste_frame.grid(row = 3, column = 0, columnspan = 2, pady = 10, padx = 10, sticky = 'ns')
        
        # Paste text field
        Label(paste_frame, text="Paste pairs:", font=('Helvetica', 8)).grid(row=0, column=0, sticky='s')
        self.paste_entry = Entry(paste_frame, width=41, font=('Helvetica', 8))
        self.paste_entry.grid(row=1, column=0, columnspan=2, sticky='news', pady=5)
        
        # Paste buttons
        paste_btn_style = {
            'width': 8, 'height': 2, 'font': ('Helvetica', 8, 'bold'),
            'relief': 'raised'
        }
        
        calls_btn = Button(paste_frame, text="CALLS", bg='#4CAF50', fg='white',
                          command=self.paste_calls, **paste_btn_style)
        calls_btn.grid(row=2, column=0, padx=5, pady=5)
        
        puts_btn = Button(paste_frame, text="PUTS", bg='#f44336', fg='white',
                         command=self.paste_puts, **paste_btn_style)
        puts_btn.grid(row=2, column=1, padx=5, pady=5)
        
        
        # Navigation buttons
        nav_style = {'width': 1, 'height': 1, 'font': ('Helvetica', 9)}
        nav_style2 = {'width': 1, 'height': 1, 'font': ('Arial', 10, 'bold')}
        nav_style3 = {'width': 1, 'height': 1, 'font': ('Arial', 11, 'bold')}
        nav_style4 = {'width': 1, 'height': 1, 'font': ('Arial', 12, 'bold')}
        
        Button(arrow_frame, text="↑", command=self.move_up, **nav_style).grid(row=0, column=1)
        Button(arrow_frame, text="←", command=self.move_left, **nav_style).grid(row=1, column=0)
        Button(arrow_frame, text="⿴", command=self.show_cost_graph, **nav_style2).grid(row=1, column=1)
        Button(arrow_frame, text="→", command=self.move_right, **nav_style3).grid(row=1, column=2)
        Button(arrow_frame, text="↓", command=self.move_down, **nav_style4).grid(row=2, column=1)
        
        
        # Keyboard layout
        numboard_layout = [
            [],[],
            ['1', '2', '3'],
            [ '4', '5', '6'],
            ['7', '8', '9'],
            ['.', '0'],
            [],
            []
        ]
        keyboard_layout = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '/'],
            ['SPACE', 'CLEAR', 'BACKSPACE']
        ]
        
        button_style1 = {
            'width': 2, 'height': 1, 'font': ('Roman', 5, 'bold'),
            'relief': 'raised', 'bg': '#f0f0f0', 'activebackground': '#e0e0e0'
        }
        button_style2 = {
            'width': 1, 'height': 1, 'font': ('Latin', 5, 'italic'),
            'relief': 'raised', 'bg': '#f0f0f0', 'activebackground': '#e0e0e0'
        }
        for row in numboard_layout:
            frame = Frame(num_frame)
            frame.pack(pady=2)
            
            for key in row:
                btn = Button(frame, text=key, **button_style1, 
                               command=lambda k=key: self.type_char(k))
                btn.pack(side = 'left', padx=1)
        
        
        for row in keyboard_layout:
            frame = Frame(key_frame)
            frame.pack(pady=2)
            
            for key in row:
                if key == 'CLEAR':
                    btn = Button(frame, text=key, width=8, **{k:v for k,v in button_style2.items() if k != 'width'}, 
                               command=self.clear_field)
                elif key == 'BACKSPACE':
                    btn = Button(frame, text='⌫', width=8, **{k:v for k,v in button_style2.items() if k != 'width'}, 
                               command=self.backspace)
                elif key == 'SPACE':
                    btn = Button(frame, text=key, width=8, **{k:v for k,v in button_style2.items() if k != 'width'}, 
                               command=lambda: self.type_char(' '))
                else:
                    btn = Button(frame, text=key, **button_style2, 
                               command=lambda k=key: self.type_char(k))
                btn.pack(side='left', anchor = 'sw', padx=1)
    
    def hide_keyboard(self):
        if self.keyboard_window:
            self.keyboard_window.destroy()
            self.keyboard_window = None
    
    def set_current_field(self, entry_widget, row, col):
        self.current_entry = entry_widget
        self.current_row = row
        self.current_col = col
        self.update_field_label()
        entry_widget.focus()
    
    def update_field_label(self):
        if self.keyboard_window and self.current_entry:
            # Check if we're in header fields (negative row indices)
            if self.current_row < 0:
                # Grid: Row -1: [Ticker, Share Price], Row -2: [From Strike, To Strike]
                header_field_names = {
                    (-1, 0): "Ticker",
                    (-1, 1): "Share Price", 
                    (-2, 0): "From Strike",
                    (-2, 1): "To Strike"
                }
                field_name = header_field_names.get((self.current_row, self.current_col), "Header Field")
                self.field_label.config(text=f"Header: {field_name}")
            else:
                field_names = ["Vol:call", "Oi:call", "Vol:put", "Oi:put"]
                field_name = field_names[self.current_col] if self.current_col < 4 else "Field"
                self.field_label.config(text=f"Row {self.current_row + 1}: {field_name}")
    
    def move_up(self):
        if not self.current_entry:
            return
        
        # If we're in the table rows
        if self.current_row >= 0:
            if self.current_row > 0:
                # Move up within table
                new_row = self.current_row - 1
                entries = self.calculator.entries[new_row]
                if self.current_col < len(entries):
                    self.set_current_field(entries[self.current_col], new_row, self.current_col)
            else:
                # Move from first table row to bottom of header grid
                grid = self.calculator.header_fields_grid
                bottom_row = len(grid) - 1
                # Stay in column 0 when going up to headers
                next_field = grid[bottom_row][0]
                self.set_current_field(next_field, -(bottom_row + 1), 0)
        # If we're in header fields
        elif self.current_row < 0:
            grid = self.calculator.header_fields_grid
            header_row = abs(self.current_row) - 1
            
            # If we can move up within the header grid
            if header_row > 0:
                prev_row = header_row - 1
                prev_field = grid[prev_row][self.current_col]
                self.set_current_field(prev_field, -(prev_row + 1), self.current_col)
    
    def move_down(self):
        if not self.current_entry:
            return
        
        # If we're in header fields (row < 0)
        if self.current_row < 0:
            grid = self.calculator.header_fields_grid
            header_row = abs(self.current_row) - 1  # -1 -> 0, -2 -> 1
            
            # If we can move down within the header grid
            if header_row < len(grid) - 1:
                next_row = header_row + 1
                next_field = grid[next_row][self.current_col]
                self.set_current_field(next_field, -(next_row + 1), self.current_col)
            else:
                # We're at bottom of header grid, move to first table row
                entries = self.calculator.entries[0]
                if len(entries) > 0:
                    self.set_current_field(entries[0], 0, 0)
        # If we're in the table rows
        elif self.current_row < len(self.calculator.entries) - 1:
            new_row = self.current_row + 1
            entries = self.calculator.entries[new_row]
            if self.current_col < len(entries):
                self.set_current_field(entries[0], new_row, self.current_col)
    
    def move_left(self):
        if not self.current_entry:
            return
        
        # In header fields
        if self.current_row < 0:
            if self.current_col > 0:
                grid = self.calculator.header_fields_grid
                header_row = abs(self.current_row) - 1
                prev_field = grid[header_row][self.current_col - 1]
                self.set_current_field(prev_field, self.current_row, self.current_col - 1)
            return
        
        # In table rows
        if self.current_col > 0:
            new_col = self.current_col - 1
            entries = self.calculator.entries[self.current_row]
            self.set_current_field(entries[new_col], self.current_row, new_col)
    
    def move_right(self):
        if not self.current_entry:
            return
        
        # In header fields
        if self.current_row < 0:
            grid = self.calculator.header_fields_grid
            header_row = abs(self.current_row) - 1
            if self.current_col < len(grid[header_row]) - 1:
                next_field = grid[header_row][self.current_col + 1]
                self.set_current_field(next_field, self.current_row, self.current_col + 1)
            return
        
        # In table rows
        if self.current_col < len(self.calculator.entries[self.current_row]) - 1:
            new_col = self.current_col + 1
            entries = self.calculator.entries[self.current_row]
            self.set_current_field(entries[new_col], self.current_row, new_col)
    
    def type_char(self, char):
        if self.current_entry:
            self.current_entry.config(state='normal')
            self.current_entry.insert('end', char)
            
            # If in header fields, trigger appropriate actions
            if self.current_row < 0:
                # Current price changed
                if self.current_row == -3:
                    self.calculator.calculate_ccv()
                # From/To strike changed
                elif self.current_row in [-2, -1]:
                    self.calculator.populate_strikes()
            else:
                # In table, always recalculate CCV
                self.calculator.calculate_ccv()
    
    def clear_field(self):
        if self.current_entry:
            self.current_entry.config(state='normal')
            self.current_entry.delete(0, 'end')
            
            # If in header fields, trigger appropriate actions
            if self.current_row < 0:
                # Current price changed
                if self.current_row == -3:
                    self.calculator.calculate_ccv()
                # From/To strike changed
                elif self.current_row in [-2, -1]:
                    self.calculator.populate_strikes()
            else:
                # In table, always recalculate CCV
                self.calculator.calculate_ccv()
    
    def backspace(self):
        if self.current_entry:
            self.current_entry.config(state='normal')
            current_text = self.current_entry.get()
            if current_text:
                self.current_entry.delete(len(current_text)-1, 'end')
                
                # If in header fields, trigger appropriate actions
                if self.current_row < 0:
                    # Current price changed
                    if self.current_row == -3:
                        self.calculator.calculate_ccv()
                    # From/To strike changed
                    elif self.current_row in [-2, -1]:
                        self.calculator.populate_strikes()
                else:
                    # In table, always recalculate CCV
                    self.calculator.calculate_ccv()
    
    def show_cost_graph(self):
        """Display a graph showing CCV values as a function of share price across strike range."""
        # Collect all strikes and their data once
        strike_data = []
        for i, strike_label in enumerate(self.calculator.strike_labels):
            strike_text = strike_label.cget("text")
            if not strike_text:
                continue
            try:
                strike = float(strike_text.replace('$', ''))
                call_oi_entry, call_vol_entry, put_oi_entry, put_vol_entry = self.calculator.entries[i]
                strike_data.append({
                    'strike':   strike,
                    'call_oi':  float(call_oi_entry.get()  or 0),
                    'call_vol': float(call_vol_entry.get() or 0),
                    'put_oi':   float(put_oi_entry.get()   or 0),
                    'put_vol':  float(put_vol_entry.get()  or 0),
                })
            except (ValueError, AttributeError):
                continue
        
        if not strike_data:
            return

        # Create graph window
        ticker = self.calculator.ticker_entry.get().strip().upper() or "?"
        graph_window = Toplevel(self.master)
        graph_window.title(f"[{ticker}] Max Pain vs Share Price")
        graph_window.geometry("1000x800+12+290")

        # ── Controls bar ────────────────────────────────────────────────
        ctrl_frame = tk.Frame(graph_window)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Mirror the main slider variable so both stay in sync
        vol_var = self.calculator.vol_fraction  # shared DoubleVar

        canvas = tk.Canvas(graph_window, bg='white')
        canvas.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        def draw_graph():
            canvas.delete('all')
            graph_window.update()

            frac = vol_var.get()

            share_prices, ccv_puts_values, ccv_calls_values = [], [], []
            for price_point in strike_data:
                cp = price_point['strike']
                share_prices.append(cp)
                cp_puts = cp_calls = 0.0
                for d in strike_data:
                    s = d['strike']
                    call_val = d['call_oi'] + d['call_vol'] * frac
                    put_val  = d['put_oi']  + d['put_vol']  * frac
                    if s > cp:
                        cp_puts  += (s - cp) * put_val  * 100
                    if s < cp:
                        cp_calls += (cp - s) * call_val * 100
                ccv_puts_values.append(cp_puts)
                ccv_calls_values.append(cp_calls)

            total_ccv_values = [c + p for c, p in zip(ccv_calls_values, ccv_puts_values)]

            w = canvas.winfo_width()
            h = canvas.winfo_height()
            ml, mr, mt, mb = 80, 40, 40, 60
            gw = w - ml - mr
            gh = h - mt - mb

            min_p, max_p = min(share_prices), max(share_prices)
            max_ccv = max(max(ccv_calls_values), max(ccv_puts_values), max(total_ccv_values)) or 1

            def tx(price):
                if max_p == min_p: return ml + gw / 2
                return ml + (price - min_p) / (max_p - min_p) * gw

            def ty(ccv):
                return mt + gh - ccv / max_ccv * gh

            # Axes
            canvas.create_line(ml, mt + gh, ml + gw, mt + gh, width=2)
            canvas.create_line(ml, mt, ml, mt + gh, width=2)

            # Y grid + labels
            for i in range(6):
                yv = max_ccv * i / 5
                yp = ty(yv)
                canvas.create_line(ml, yp, ml - 5, yp)
                canvas.create_text(ml - 7, yp, text=f"${yv:,.0f}", anchor='e', font=('Arial', 3))
                canvas.create_line(ml, yp, ml + gw, yp, fill='lightgray', dash=(2, 4))

            # X labels
            step = max(1, len(share_prices) // 10)
            for i in range(0, len(share_prices), step):
                xp = tx(share_prices[i])
                canvas.create_line(xp, mt + gh, xp, mt + gh + 5)
                canvas.create_text(xp, mt + gh + 10, text=f"${share_prices[i]:.2f}",
                                   angle=45, anchor='w', font=('Arial', 4))

            # Lines
            for i in range(len(share_prices) - 1):
                canvas.create_line(tx(share_prices[i]), ty(ccv_calls_values[i]),
                                   tx(share_prices[i+1]), ty(ccv_calls_values[i+1]),
                                   fill='blue', width=2)
                canvas.create_line(tx(share_prices[i]), ty(ccv_puts_values[i]),
                                   tx(share_prices[i+1]), ty(ccv_puts_values[i+1]),
                                   fill='red', width=2)
                canvas.create_line(tx(share_prices[i]), ty(total_ccv_values[i]),
                                   tx(share_prices[i+1]), ty(total_ccv_values[i+1]),
                                   fill='green', width=2)

            # Max pain marker
            min_total = min(total_ccv_values)
            min_idx   = total_ccv_values.index(min_total)
            max_pain_price = share_prices[min_idx]
            xmp = tx(max_pain_price)
            canvas.create_line(xmp, mt, xmp, mt + gh, fill='purple', width=2, dash=(4, 3))
            canvas.create_text(xmp, mt + 20,
                               text=f"Max Pain: ${max_pain_price:.2f}, ${min_total:,.0f}",
                               font=('Arial', 5, 'bold'), fill='purple')
            
            # Current price marker
            try:
                actual_price = float(self.calculator.current_price_entry.get())
                if min_p <= actual_price <= max_p:
                    xc = tx(actual_price)
                    # Find total CCV at actual price (closest point)
                    closest_idx = min(range(len(share_prices)), key=lambda i: abs(share_prices[i] - actual_price))
                    current_cost = total_ccv_values[closest_idx]
                    canvas.create_line(xc, mt, xc, mt + gh, fill='orange', width=2, dash=(5, 5))
                    canvas.create_text(xc, mt - 20,
                                       text=f"Current: ${actual_price:.2f}, ${current_cost:,.0f}",
                                       font=('Arial', 5, 'bold'), fill='orange')
            except ValueError:
                pass

            # Legend
            lx, ly = ml + 10, mt + 300
            for color, label in [('green','Total \n'), ('blue','Calls'), ('red','Puts')]:
                canvas.create_line(lx, ly, lx + 25, ly, fill=color, width=5)
                canvas.create_text(lx + 28, ly, text=label, anchor='w', font=('Arial', 3))
                ly += 18

            canvas.create_text(ml + gw / 7, h - 30, text='Share Price', font=('Arial', 4, 'bold'))
            canvas.create_text(25, mt + gh / 2, text='Pain ($)', font=('Arial', 4, 'bold'), angle=90)

            # Date-time stamp (bottom-right corner)
            now = datetime.now()
            day = now.day
            suffix = 'th' if 11 <= day <= 13 else {1:'st',2:'nd',3:'rd'}.get(day % 10, 'th')
            line1 = now.strftime(f"%I:%M %p %a, %B {day}{suffix}, %Y")
            canvas.create_text(ml + gw, h - 14, text=line1,
                               anchor='e', font=('Arial', 5), fill='gray')

        def on_slider(val):
            pct = int(float(val) * 100)
            pct_lbl.config(text=f"{pct}%")
            self.calculator.calculate_ccv()
            draw_graph()

        # ── Controls bar ────────────────────────────────────────────────
        tk.Label(ctrl_frame, text="Vol included:", font=('Arial', 7)).pack(side=tk.LEFT, padx=4)
        vol_slider = tk.Scale(ctrl_frame, variable=vol_var,
                              from_=0.0, to=1.0, resolution=0.01,
                              orient=tk.HORIZONTAL, length=525,
                              showvalue=False, command=on_slider)
        vol_slider.pack(side=tk.LEFT)
        pct_lbl = tk.Label(ctrl_frame, text="0%", font=('Arial', 8, 'bold'), width=5)
        pct_lbl.pack(side=tk.LEFT, padx=2)

        graph_window.update()
        draw_graph()
    
    def parse_pairs(self, text):
        """
        Parse (volume, oi) pairs from a flat space-separated string.
        Expected format: vol oi vol oi ...
        Example: 4 32 0 5 0 4 0 0 0 4 0 0 0 1978 ...
        """
        import re
        numbers = re.findall(r'\d+', text)
        pairs = []
        for i in range(0, len(numbers) - 1, 2):
            pairs.append((int(numbers[i]), int(numbers[i + 1])))
        return pairs
    
    def paste_calls(self):
        """Paste pairs into CALLS columns"""
        text = self.paste_entry.get().strip()
        if not text:
            return
        
        pairs = self.parse_pairs(text)
        if not pairs:
            return
        
        active_rows = sum(1 for lbl in self.calculator.strike_labels if lbl.cget("text"))
        
        # Clear calls columns
        for i in range(active_rows):
            self.calculator.entries[i][0].config(state='normal')
            self.calculator.entries[i][0].delete(0, tk.END)
            self.calculator.entries[i][0].config(state='readonly')
            self.calculator.entries[i][1].config(state='normal')
            self.calculator.entries[i][1].delete(0, tk.END)
            self.calculator.entries[i][1].config(state='readonly')
        
        # pairs[0] = highest strike → last row; pairs[-1] = lowest strike → row 0
        pairs_to_use = pairs[:active_rows]
        for input_idx, (vol, oi) in enumerate(pairs_to_use):
            row_idx = active_rows - 1 - input_idx
            self.calculator.entries[row_idx][0].config(state='normal')
            self.calculator.entries[row_idx][0].insert(0, str(vol))
            self.calculator.entries[row_idx][0].config(state='readonly')
            self.calculator.entries[row_idx][1].config(state='normal')
            self.calculator.entries[row_idx][1].insert(0, str(oi))
            self.calculator.entries[row_idx][1].config(state='readonly')
        
        self.paste_entry.delete(0, tk.END)
        self.calculator.calculate_ccv()
    
    def paste_puts(self):
        """Paste pairs into PUTS columns"""
        text = self.paste_entry.get().strip()
        if not text:
            return
        
        pairs = self.parse_pairs(text)
        if not pairs:
            return
        
        active_rows = sum(1 for lbl in self.calculator.strike_labels if lbl.cget("text"))
        
        # Clear puts columns  
        for i in range(active_rows):
            self.calculator.entries[i][2].config(state='normal')
            self.calculator.entries[i][2].delete(0, tk.END)
            self.calculator.entries[i][2].config(state='readonly')
            self.calculator.entries[i][3].config(state='normal')
            self.calculator.entries[i][3].delete(0, tk.END)
            self.calculator.entries[i][3].config(state='readonly')
        
        # pairs[0] = highest strike → last row; pairs[-1] = lowest strike → row 0
        pairs_to_use = pairs[:active_rows]
        for input_idx, (vol, oi) in enumerate(pairs_to_use):
            row_idx = active_rows - 1 - input_idx
            self.calculator.entries[row_idx][2].config(state='normal')
            self.calculator.entries[row_idx][2].insert(0, str(vol))
            self.calculator.entries[row_idx][2].config(state='readonly')
            self.calculator.entries[row_idx][3].config(state='normal')
            self.calculator.entries[row_idx][3].insert(0, str(oi))
            self.calculator.entries[row_idx][3].config(state='readonly')
        
        self.paste_entry.delete(0, tk.END)
        self.calculator.calculate_ccv()


class OptionsChainCalculator:
    def __init__(self):
        self.setup_gui()
    
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Options Chain Calculator")
        self.root.resizable(True, True)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="7")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize keyboard
        self.keyboard = NavigableKeyboard(self.root, self)
        
        # Volume fraction 0.0=OI-only, 1.0=full OI+Vol
        self.vol_fraction = tk.DoubleVar(value=0.0)
        
        # Top section - Input fields
        input_frame = ttk.LabelFrame(main_frame, text="Options Data", padding="10")
        input_frame.grid(row=0, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Ticker
        ttk.Label(input_frame, text="Ticker:", font=("Arial", 8, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.ticker_entry = ttk.Entry(input_frame, width=10)
        self.ticker_entry.grid(row=0, column=1, padx=5)
        self.ticker_entry.bind('<FocusIn>', lambda e: self.on_header_field_focus(e, -1, 0))
        self.ticker_entry.config(state='readonly')
        self.ticker_entry.bind('<Button-1>', lambda e: self.enable_header_field_for_keyboard(e, -1, 0))
        
        # Current Price
        ttk.Label(input_frame, text="Share Price:", font=("Arial", 6, "bold")).grid(row=0, column=2, sticky=tk.W, padx=5)
        
        # Frame to hold price entry and buttons
        price_frame = Frame(input_frame)
        price_frame.grid(row=0, column=3, padx=3, sticky='w')
        
        self.current_price_entry = ttk.Entry(price_frame, width=9)
        self.current_price_entry.grid(row=0, column=0, rowspan=2)
        self.current_price_entry.bind('<FocusIn>', lambda e: self.on_header_field_focus(e, -1, 1))
        self.current_price_entry.config(state='readonly')
        self.current_price_entry.bind('<Button-1>', lambda e: self.enable_header_field_for_keyboard(e, -1, 1))
        
        # Increment button (+)
        inc_button = Button(price_frame, text="+", width=0, height=1, 
                           command=self.increment_price, font=('Helvetica', 5, "bold"))
        inc_button.grid(row=0, column=1, padx=0)
        
        # Decrement button (-)
        dec_button = Button(price_frame, text="-", width=0, height=1,
                           command=self.decrement_price, font=('Helvetica', 5, "bold"))
        dec_button.grid(row=1, column=1, padx=0)
        
        # From Strike
        ttk.Label(input_frame, text="From Strike:", font=("Arial", 6, "bold")).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.from_strike_entry = ttk.Entry(input_frame, width=6)
        self.from_strike_entry.grid(row=1, column=1, padx=3)
        self.from_strike_entry.bind('<FocusIn>', lambda e: self.on_header_field_focus(e, -2, 0))
        self.from_strike_entry.config(state='readonly')
        self.from_strike_entry.bind('<Button-1>', lambda e: self.enable_header_field_for_keyboard(e, -2, 0))
        
        # To Strike
        ttk.Label(input_frame, text="To Strike:", font=("Arial", 6, "bold")).grid(row=1, column=2, sticky=tk.W, padx=0)
        self.to_strike_entry = ttk.Entry(input_frame, width=6)
        self.to_strike_entry.grid(row=1, column=3, padx=0)
        self.to_strike_entry.bind('<FocusIn>', lambda e: self.on_header_field_focus(e, -2, 1))
        self.to_strike_entry.config(state='readonly')
        self.to_strike_entry.bind('<Button-1>', lambda e: self.enable_header_field_for_keyboard(e, -2, 1))
        
        # Store header fields in a 2x2 grid for keyboard navigation
        # Grid layout: [[Ticker, Share Price], [From Strike, To Strike]]
        self.header_fields_grid = [
            [self.ticker_entry, self.current_price_entry],      # Row 0
            [self.from_strike_entry, self.to_strike_entry]      # Row 1
        ]
        
        # Keep flat list for backwards compatibility
        self.header_fields = [
            self.ticker_entry,
            self.current_price_entry,
            self.from_strike_entry,
            self.to_strike_entry
        ]
        
        # Populate button
        populate_btn = ttk.Button(input_frame, text="Add Strikes", command=self.populate_strikes)
        #populate_btn.grid(row=2, column=2, padx=7)
        
        # Keyboard toggle
        style = ttk.Style()
        style.configure('Mini.TButton', font=('Helvetica', 7, 'bold'))
        keyboard_btn = ttk.Button(main_frame, style='Mini.TButton', text=" ⧇⧇⧇⧇\n⧇⧇⧇⧇⧇",command=self.keyboard.toggle_keyboard)
        keyboard_btn.grid(row=1, column=0, pady=20, sticky=tk.NS)
        
        # CCV Results display
        ccv_frame = ttk.LabelFrame(main_frame, text="Current Price Cost Value:", padding="10")
        ccv_frame.grid(row=4, column=0, columnspan=5, pady=20, sticky=(tk.W, tk.E))
        
        ttk.Label(ccv_frame, text="CCV Puts:", font=("Arial", 7, "bold")).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.ccv_puts_label = ttk.Label(ccv_frame, text="$0.00", font=("Arial", 6, "bold"), foreground="red")
        self.ccv_puts_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(ccv_frame, text="CCV Calls:", font=("Arial", 7, "bold")).grid(row=0, column=2, sticky=tk.W, padx=5)
        self.ccv_calls_label = ttk.Label(ccv_frame, text="$0.00", font=("Arial", 6, "bold"), foreground="green")
        self.ccv_calls_label.grid(row=0, column=3, padx=5)
        
        ttk.Label(ccv_frame, text="Total CCV:", font=("Arial", 7, "bold")).grid(row=0, column=4, sticky=tk.W, padx=5)
        self.ccv_total_label = ttk.Label(ccv_frame, text="$0.00", font=("Arial", 6, "bold"), foreground="blue")
        self.ccv_total_label.grid(row=0, column=5, padx=5)
        
        # Volume fraction slider: 0% = OI-only, 100% = OI+full Vol
        tk.Label(ccv_frame, text="Vol%:", font=("Arial", 5)).grid(row=0, column=6, padx=(8,0))
        vol_slider = tk.Scale(ccv_frame, variable=self.vol_fraction,
                              from_=0.0, to=1.0, resolution=0.01,
                              orient=tk.HORIZONTAL, length=80,
                              showvalue=False, command=lambda _: self.calculate_ccv())
        vol_slider.grid(row=0, column=7, padx=2)
        self.vol_pct_label = tk.Label(ccv_frame, text="0%", font=("Arial", 5), width=4)
        self.vol_pct_label.grid(row=0, column=8, padx=(0,4))
        
        # Image display section
        image_frame = ttk.LabelFrame(main_frame, text="Screenshots", padding="5")
        image_frame.grid(row=5, column=0, columnspan=5, pady=0, sticky=(tk.W, tk.E))
        
        # Left image panel
        left_image_container = ttk.Frame(image_frame, relief="sunken", borderwidth=2)
        left_image_container.grid(row=0, column=0, padx=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.left_image_label = ttk.Label(left_image_container, text="Left Screenshot\n(Click to load)", 
                                         anchor="center", relief="ridge", background="lightgray")
        self.left_image_label.pack(fill="both", expand=True, padx=2, pady=2, ipadx=10, ipady=10)
        self.left_image_label.bind('<Button-1>', lambda e: self.load_image('left'))
        
        # Right image panel
        right_image_container = ttk.Frame(image_frame, relief="sunken", borderwidth=2)
        right_image_container.grid(row=0, column=1, padx=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.right_image_label = ttk.Label(right_image_container, text="Right Screenshot\n(Click to load)", 
                                          anchor="center", relief="ridge", background="lightgray")
        self.right_image_label.pack(fill="both", expand=True, padx=2, pady=2, ipadx=10, ipady=10)
        self.right_image_label.bind('<Button-1>', lambda e: self.load_image('right'))
        
        # Configure image frame grid weights
        image_frame.columnconfigure(0, weight=1)
        image_frame.columnconfigure(1, weight=1)
        
        # Store references to loaded images (prevent garbage collection)
        self.left_photo = None
        self.right_photo = None
        
        # Table frame with scrollbar
        table_container = ttk.Frame(main_frame)
        table_container.grid(row=3, column=0, columnspan=6, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas and scrollbar for scrolling
        canvas = tk.Canvas(table_container, height=700, width = 1000)
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=False)
        scrollbar.pack(side="left", fill="y")
        
        # Table headers
        headers = ["Strikes", "Vol:call", "Oi:call", "Vol:put", "Oi:put"]
        for i, header in enumerate(headers):
            ttk.Label(scrollable_frame, text=header, font=("Arial", 9, "bold"), 
                     relief="raised", borderwidth=1).grid(row=0, column=i, padx=1, pady=1, sticky=(tk.W, tk.E))
        
        # Create entry fields for strike data
        self.entries = []
        self.strike_labels = []
        
        # Create 40 rows (adjustable)
        for i in range(40):
            row = i + 1
            
            # Strike price (read-only, auto-populated)
            strike_label = ttk.Label(scrollable_frame, text="", width=8, relief="sunken", 
                                    anchor="center", background="lightgray")
            strike_label.grid(row=row, column=0, padx=2, pady=2)
            self.strike_labels.append(strike_label)
            
            # Call OI
            call_oi_entry = ttk.Entry(scrollable_frame, width=8)
            call_oi_entry.grid(row=row, column=1, padx=2, pady=2)
            call_oi_entry.bind('<FocusIn>', lambda e, r=i, c=0: self.on_field_focus(e, r, c))
            call_oi_entry.config(state='readonly')
            call_oi_entry.bind('<Button-1>', lambda e, r=i, c=0: self.enable_field_for_keyboard(e, r, c))
            
            # Call Volume
            call_vol_entry = ttk.Entry(scrollable_frame, width=8)
            call_vol_entry.grid(row=row, column=2, padx=2, pady=2)
            call_vol_entry.bind('<FocusIn>', lambda e, r=i, c=1: self.on_field_focus(e, r, c))
            call_vol_entry.config(state='readonly')
            call_vol_entry.bind('<Button-1>', lambda e, r=i, c=1: self.enable_field_for_keyboard(e, r, c))
            
            # Put OI
            put_oi_entry = ttk.Entry(scrollable_frame, width=8)
            put_oi_entry.grid(row=row, column=3, padx=2, pady=2)
            put_oi_entry.bind('<FocusIn>', lambda e, r=i, c=2: self.on_field_focus(e, r, c))
            put_oi_entry.config(state='readonly')
            put_oi_entry.bind('<Button-1>', lambda e, r=i, c=2: self.enable_field_for_keyboard(e, r, c))
            
            # Put Volume
            put_vol_entry = ttk.Entry(scrollable_frame, width=8)
            put_vol_entry.grid(row=row, column=4, padx=2, pady=2)
            put_vol_entry.bind('<FocusIn>', lambda e, r=i, c=3: self.on_field_focus(e, r, c))
            put_vol_entry.config(state='readonly')
            put_vol_entry.bind('<Button-1>', lambda e, r=i, c=3: self.enable_field_for_keyboard(e, r, c))
            
            self.entries.append((call_oi_entry, call_vol_entry, put_oi_entry, put_vol_entry))
        
        # Configure grid weights for resizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def populate_strikes(self):
        """Populate strike prices based on From and To range with 0.50 increments"""
        try:
            from_strike = float(self.from_strike_entry.get())
            to_strike = float(self.to_strike_entry.get())
            
            if from_strike >= to_strike:
                return
            
            # Generate strikes in 0.50 increments
            strikes = []
            current = from_strike
            while current <= to_strike:
                strikes.append(current)
                current += 0.50
            
            # Populate the strike labels
            for i, strike in enumerate(strikes):
                if i < len(self.strike_labels):
                    self.strike_labels[i].config(text=f"${strike:.2f}")
            
            # Clear any remaining labels
            for i in range(len(strikes), len(self.strike_labels)):
                self.strike_labels[i].config(text="")
                
        except ValueError:
            pass
    
    def on_field_focus(self, event, row, col):
        """Called when a field gets focus - updates keyboard navigation"""
        if self.keyboard.keyboard_window and self.keyboard.keyboard_window.winfo_exists():
            self.keyboard.set_current_field(event.widget, row, col)
    
    def enable_field_for_keyboard(self, event, row, col):
        """Enable field for keyboard input"""
        widget = event.widget
        widget.config(state='normal')
        self.on_field_focus(event, row, col)
    
    def on_header_field_focus(self, event, row_id, col):
        """Called when a header field gets focus"""
        if self.keyboard.keyboard_window and self.keyboard.keyboard_window.winfo_exists():
            self.keyboard.set_current_field(event.widget, row_id, col)
    
    def enable_header_field_for_keyboard(self, event, row_id, col):
        """Enable header field for keyboard input"""
        widget = event.widget
        widget.config(state='normal')
        self.on_header_field_focus(event, row_id, col)
    
    def increment_price(self):
        """Increment the current price by $0.01"""
        try:
            current_value = float(self.current_price_entry.get() or 0)
            new_value = current_value + 0.01
            
            # Temporarily enable the entry to update it
            self.current_price_entry.config(state='normal')
            self.current_price_entry.delete(0, tk.END)
            self.current_price_entry.insert(0, f"{new_value:.2f}")
            self.current_price_entry.config(state='readonly')
            
            # Recalculate CCV
            self.calculate_ccv()
        except ValueError:
            pass
    
    def decrement_price(self):
        """Decrement the current price by $0.01"""
        try:
            current_value = float(self.current_price_entry.get() or 0)
            new_value = max(0, current_value - 0.01)  # Don't go below 0
            
            # Temporarily enable the entry to update it
            self.current_price_entry.config(state='normal')
            self.current_price_entry.delete(0, tk.END)
            self.current_price_entry.insert(0, f"{new_value:.2f}")
            self.current_price_entry.config(state='readonly')
            
            # Recalculate CCV
            self.calculate_ccv()
        except ValueError:
            pass
    
    def calculate_ccv(self):
        """Calculate Current Cost Value. Vol fraction 0.0=OI-only, 1.0=OI+full Vol."""
        try:
            current_price = float(self.current_price_entry.get())
        except (ValueError, AttributeError):
            return
        
        frac = self.vol_fraction.get()
        # Update the % label
        if hasattr(self, 'vol_pct_label'):
            self.vol_pct_label.config(text=f"{int(frac*100)}%")

        ccv_puts = 0.0
        ccv_calls = 0.0
        
        for i, strike_label in enumerate(self.strike_labels):
            strike_text = strike_label.cget("text")
            if not strike_text:
                continue
            try:
                strike = float(strike_text.replace('$', ''))
                call_oi_entry, call_vol_entry, put_oi_entry, put_vol_entry = self.entries[i]
                call_oi  = float(call_oi_entry.get()  or 0)
                call_vol = float(call_vol_entry.get() or 0) * frac
                put_oi   = float(put_oi_entry.get()   or 0)
                put_vol  = float(put_vol_entry.get()  or 0) * frac

                if strike > current_price:
                    ccv_puts  += (strike - current_price) * (put_oi  + put_vol)  * 100
                if strike < current_price:
                    ccv_calls += (current_price - strike) * (call_oi + call_vol) * 100
            except (ValueError, AttributeError):
                continue
        
        self.ccv_puts_label.config(text=f"${ccv_puts:,.0f}")
        self.ccv_calls_label.config(text=f"${ccv_calls:,.0f}")
        self.ccv_total_label.config(text=f"${ccv_puts + ccv_calls:,.0f}")
    
    def load_image(self, position):
        
        """Load and display an image in the specified position (left or right)"""
        # Default directory for screenshots
        default_dir = "/storage/emulated/0/DCIM/Screenshots"
        
        filename = filedialog.askopenfilename(
            title=f"Select {position.capitalize()} Screenshot",
            initialdir=default_dir,
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")])
        
        if filename:
            try:
                # Load and resize image
                image = Image.open(filename)
                
                # Calculate dimensions to fit in the display area (max 375x1000)
                max_width = 450
                max_height = 700
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Update the appropriate label
                if position == 'left':
                    self.left_photo = photo  # Keep reference
                    self.left_image_label.config(image=photo, text="")
                else:
                    self.right_photo = photo  # Keep reference
                    self.right_image_label.config(image=photo, text="")
                    
            except Exception as e:
                print(f"Error loading image: {e}")
    
    def run(self):
        self.root.mainloop()

# Run the app
if __name__ == "__main__":
    app = OptionsChainCalculator()
    app.run()
