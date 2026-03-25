#!/usr/bin/env python3
"""
Cloud OCR Tool - Works on Android using free OCR.space API
No local installation needed!
"""

import requests
import base64
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import re
import io

class CloudOCRTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cloud OCR Tool")
        
        # Free OCR.space API key (you can get your own at ocr.space/ocrapi)
        self.api_key = "K87899142388957"  # Free tier key
        
        self.image_path = None
        self.photo = None
        self.crop_start = None
        self.crop_rect = None
        self.cropped_region = None
        
        self.setup_gui()
        
    def setup_gui(self):
        # Top controls
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        load_btn = tk.Button(top_frame, text="Load Image", 
                            command=self.load_image,
                            font=('Arial', 13), bg='#4CAF50', fg='white',
                            padx=15, pady=8)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        self.extract_btn = tk.Button(top_frame, text="Extract with Cloud OCR", 
                                     command=self.extract_with_cloud_ocr,
                                     font=('Arial', 11), bg='#2196F3', fg='white',
                                     padx=15, pady=8, state=tk.DISABLED)
        self.extract_btn.pack(side=tk.LEFT, padx=5)
        
        # Main area with two columns
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left - Image
        left_frame = tk.Frame(main_frame, bg='gray', relief=tk.SUNKEN, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.canvas = tk.Canvas(left_frame, bg='gray', cursor='cross')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_crop_start)
        self.canvas.bind("<B1-Motion>", self.on_crop_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_crop_end)
        
        # Right - Results
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="Results:", font=('Arial', 6, 'bold')).pack()
        
        self.results_text = scrolledtext.ScrolledText(
            right_frame, width=33, height=16, 
            font=('Courier', 5), bg='#f5f5f5')
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Accumulator textbox label + clear button on same row
        accum_header = tk.Frame(right_frame)
        accum_header.pack(fill=tk.X)
        tk.Label(accum_header, text="Accumulator:", font=('Arial', 6, 'bold')).pack(side=tk.LEFT)
        clear_btn = tk.Button(accum_header, text="Clear", command=self.clear_accumulator,
                              font=('Arial', 6), bg='#f44336', fg='white', padx=6, pady=2)
        clear_btn.pack(side=tk.RIGHT, padx=2)

        self.accum_text = scrolledtext.ScrolledText(
            right_frame, width=33, height=8,
            font=('Courier', 5), bg='#fff9e6')
        self.accum_text.pack(fill=tk.X, pady=(0, 4))

        # Row: Numpad button + Add to Textbox button
        add_row = tk.Frame(right_frame)
        add_row.pack(pady=(0, 4))

        numpad_btn = tk.Button(add_row, text="Numpad",
                               command=self.open_numpad,
                               font=('Arial', 7), bg='#9C27B0', fg='white',
                               padx=10, pady=6)
        numpad_btn.pack(side=tk.LEFT, padx=(0, 4))
        
        
        # Copy to Clipboard button (now copies from accumulator)
        copy_btn = tk.Button(right_frame, text="Copy to Clipboard",
                             command=self.copy_results,
                             font=('Arial', 8), bg='#4CAF50', fg='white',
                             padx=20, pady=6)
        copy_btn.pack(pady=(0, 6))


        add_btn = tk.Button(add_row, text="Add to Textbox",
                            command=self.add_to_accumulator,
                            font=('Arial', 8), bg='#FF9800', fg='white',
                            padx=20, pady=6)
        add_btn.pack(side=tk.LEFT)


        # Column selector
        col_frame = tk.Frame(left_frame)
        col_frame.pack(pady=5)
        
        tk.Label(col_frame, text="Columns:", font=('Arial', 5)).pack(side=tk.LEFT, padx=5)
        
        self.num_cols_var = tk.IntVar(value=2)
        for i in range(2, 4):
            tk.Radiobutton(col_frame, text=str(i), variable=self.num_cols_var, 
                          value=i, font=('Arial', 7)).pack(side=tk.LEFT)
        
        # Reading mode selector
        mode_frame = tk.Frame(left_frame)
        mode_frame.pack(pady=5)
        
        tk.Label(mode_frame, text="Read:", font=('Arial', 6)).pack(side=tk.LEFT, padx=5)
        
        self.read_mode_var = tk.StringVar(value='vertical')
        tk.Radiobutton(mode_frame, text="Horizontal (→)", variable=self.read_mode_var, 
                      value='horizontal', font=('Arial', 5)).pack(side=tk.LEFT, anchor = 'w')
        tk.Radiobutton(mode_frame, text="Vertical (↓)", variable=self.read_mode_var, 
                      value='vertical', font=('Arial', 5)).pack(side=tk.LEFT, anchor = 'w')
        
        # Status
        self.status_label = tk.Label(self.root, text="Ready", 
                                     font=('Arial', 8), fg='green', bd=1, relief=tk.SUNKEN)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_image(self):
        default_dir = "/storage/emulated/0/DCIM/Screenshots"
        file_path = filedialog.askopenfilename(
            title="Select Screenshot",
            initialdir=default_dir,
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")])
        
        if not file_path:
            return
        
        self.image_path = file_path
        
        try:
            # Load image
            self.original_image = Image.open(file_path)
            
            # Resize to fit canvas
            canvas_width = 600
            canvas_height = 900
            
            img_ratio = self.original_image.width / self.original_image.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = canvas_width
                new_height = int(canvas_width / img_ratio)
            else:
                new_height = canvas_height
                new_width = int(canvas_height * img_ratio)
            
            self.display_image = self.original_image.resize((new_width, new_height), 
                                                            Image.Resampling.LANCZOS)
            
            self.scale_x = self.original_image.width / new_width
            self.scale_y = self.original_image.height / new_height
            
            self.photo = ImageTk.PhotoImage(self.display_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(width=new_width, height=new_height)
            
            self.extract_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Image loaded. Drag to select table area", fg='blue')
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")
    
    def on_crop_start(self, event):
        if self.photo is None:
            return
        self.crop_start = (event.x, event.y)
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
    
    def on_crop_drag(self, event):
        if self.crop_start is None:
            return
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_start[0], self.crop_start[1], event.x, event.y,
            outline='red', width=3)
    
    def on_crop_end(self, event):
        if self.crop_start is None:
            return
        
        # Calculate crop coordinates in original image
        x1 = int(min(self.crop_start[0], event.x) * self.scale_x)
        y1 = int(min(self.crop_start[1], event.y) * self.scale_y)
        x2 = int(max(self.crop_start[0], event.x) * self.scale_x)
        y2 = int(max(self.crop_start[1], event.y) * self.scale_y)
        
        # Ensure within bounds
        x1 = max(0, min(x1, self.original_image.width))
        x2 = max(0, min(x2, self.original_image.width))
        y1 = max(0, min(y1, self.original_image.height))
        y2 = max(0, min(y2, self.original_image.height))
        
        if x2 - x1 > 10 and y2 - y1 > 10:
            self.cropped_region = (x1, y1, x2, y2)
            self.status_label.config(text=f"Selected: ({x2-x1}x{y2-y1})", fg='green')
        else:
            self.cropped_region = None
    
    def extract_with_cloud_ocr(self):
        if self.original_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        self.status_label.config(text="Processing with cloud OCR...", fg='orange')
        self.root.update()
        
        try:
            # Get image to process
            if self.cropped_region:
                x1, y1, x2, y2 = self.cropped_region
                image_to_process = self.original_image.crop((x1, y1, x2, y2))
            else:
                image_to_process = self.original_image
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image_to_process.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Encode as base64
            base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
            
            # Call OCR.space API
            url = "https://api.ocr.space/parse/image"
            payload = {
                'apikey': self.api_key,
                'base64Image': f'data:image/png;base64,{base64_image}',
                'language': 'eng',
                'isOverlayRequired': False,
                'OCREngine': 2,  # Engine 2 is better for numbers
            }
            
            response = requests.post(url, data=payload, timeout=30)
            result = response.json()
            
            if result.get('OCRExitCode') != 1:
                error_msg = result.get('ErrorMessage', ['Unknown error'])[0]
                raise Exception(f"OCR failed: {error_msg}")
            
            # Extract text
            text = result['ParsedResults'][0]['ParsedText']
            
            # Process the text
            self.process_ocr_result(text)
            
            self.status_label.config(text="OCR complete!", fg='green')
            
        except requests.exceptions.Timeout:
            messagebox.showerror("Error", "OCR request timed out. Try again.")
            self.status_label.config(text="Timeout error", fg='red')
        except Exception as e:
            messagebox.showerror("Error", f"OCR failed: {e}")
            self.status_label.config(text="OCR failed", fg='red')
    
    def process_ocr_result(self, text):
        # Remove commas from text first
        text = text.replace(',', '')
        
        # Extract all numbers
        numbers = re.findall(r'\d+', text)
        
        if not numbers:
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert('1.0', "No numbers found in image")
            return
        
        num_cols = self.num_cols_var.get()
        read_mode = self.read_mode_var.get()
        
        # Build output
        output = f"EXTRACTED {len(numbers)} NUMBERS\n"
        output += "="*50 + "\n\n"
        
        # Show raw numbers (in order extracted)
        output += "RAW NUMBERS (as extracted by OCR):\n"
        output += " ".join(numbers) + "\n\n"
        
        if num_cols == 2:
            pairs = []
            
            if read_mode == 'horizontal':
                # Horizontal reading: every 2 consecutive numbers = one pair
                # e.g., [1,2,3,4,5,6] → (1,2), (3,4), (5,6)
                output += "FORMATTED AS PAIRS (horizontal: →):\n"
                output += "-"*50 + "\n"
                
                for i in range(0, len(numbers)-1, 2):
                    left = numbers[i]
                    right = numbers[i+1]
                    output += f"{left:>8s}  {right:>8s}\n"
                    pairs.append((left, right))
                    
            else:  # vertical
                # Vertical reading: split into columns, then pair row-by-row
                # e.g., [1,3,5,2,4,6] with 2 cols → Col1:[1,3,5] Col2:[2,4,6] → (1,2), (3,4), (5,6)
                output += "FORMATTED AS PAIRS (vertical: ↓):\n"
                output += "-"*50 + "\n"
                
                # Calculate how many rows we have
                num_rows = len(numbers) // num_cols
                
                # Split into columns
                col1 = numbers[0:num_rows]
                col2 = numbers[num_rows:num_rows*2] if len(numbers) >= num_rows*2 else []
                
                # Pair them up
                for i in range(min(len(col1), len(col2))):
                    left = col1[i]
                    right = col2[i]
                    output += f"{left:>8s}  {right:>8s}\n"
                    pairs.append((left, right))
            
            output += "\n\nPASTE INTO CALCULATOR:\n"
            output += "-"*50 + "\n"
            paste_text = " ".join([f"{l} {r}" for l, r in pairs])
            output += paste_text
            
            self.paste_output = paste_text
        else:
            self.paste_output = " ".join(numbers)
        
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert('1.0', output)
    
    def add_to_accumulator(self):
        if hasattr(self, 'paste_output'):
            current = self.accum_text.get('1.0', tk.END).rstrip('\n')
            if current:
                new_content = self.paste_output + " " + current
            else:
                new_content = self.paste_output
            self.accum_text.delete('1.0', tk.END)
            self.accum_text.insert('1.0', new_content)
            self.status_label.config(text="Added to textbox!", fg='green')
        else:
            messagebox.showinfo("Info", "No data to add — run OCR first")

    def clear_accumulator(self):
        self.accum_text.delete('1.0', tk.END)
        self.status_label.config(text="Accumulator cleared", fg='blue')

    def copy_results(self):
        content = self.accum_text.get('1.0', tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Success", "Textbox content copied to clipboard!")
        else:
            messagebox.showinfo("Info", "Textbox is empty — nothing to copy")
    
    def open_numpad(self):
        """Open a popup numpad for editing the accumulator textbox."""
        popup = tk.Toplevel(self.root)
        popup.title("Numpad")
        popup.resizable(False, False)
        popup.grab_set()  # Modal

        # --- helper: insert text at cursor in accum_text ---
        def insert(val):
            self.accum_text.insert(tk.INSERT, val)
            self.accum_text.see(tk.INSERT)
            self.accum_text.focus_set()

        def backspace():
            try:
                sel_start = self.accum_text.index(tk.SEL_FIRST)
                sel_end   = self.accum_text.index(tk.SEL_LAST)
                self.accum_text.delete(sel_start, sel_end)
            except tk.TclError:
                pos = self.accum_text.index(tk.INSERT)
                if pos != '1.0':
                    self.accum_text.delete(f"{pos} - 1c", pos)
            self.accum_text.see(tk.INSERT)
            self.accum_text.focus_set()

        def move(direction):
            pos = self.accum_text.index(tk.INSERT)
            if direction == 'left':
                self.accum_text.mark_set(tk.INSERT, f"{pos} - 1c")
            elif direction == 'right':
                self.accum_text.mark_set(tk.INSERT, f"{pos} + 1c")
            elif direction == 'home':
                self.accum_text.mark_set(tk.INSERT, f"{pos} - 250c")
            elif direction == 'end':
                self.accum_text.mark_set(tk.INSERT, f"{pos} + 50l")
            self.accum_text.see(tk.INSERT)
            self.accum_text.focus_set()

        # ── Shared button style ──────────────────────────────────────────
        def make_btn(parent, text, cmd, bg='#e0e0e0', fg='black',
                     w=3, h=1, font_size=12):
            return tk.Button(parent, text=text, command=cmd,
                             width=w, height=h,
                             font=('Arial', font_size, 'bold'),
                             bg=bg, fg=fg, relief=tk.RAISED, bd=2)

        # ── Title label ─────────────────────────────────────────────────
        tk.Label(popup, text="Edit Accumulator",
                 font=('Arial', 9, 'bold'), pady=4).pack()

        pad = tk.Frame(popup, padx=8, pady=8)
        pad.pack()

        # ── Row 0 : 7  8  9  ← (backspace) ──────────────────────────────
        r0 = tk.Frame(pad); r0.pack(pady=2)
        make_btn(r0, '7', lambda: insert('7')).pack(side=tk.LEFT, padx=2)
        make_btn(r0, '8', lambda: insert('8')).pack(side=tk.LEFT, padx=2)
        make_btn(r0, '9', lambda: insert('9')).pack(side=tk.LEFT, padx=2)
        make_btn(r0, '⌫', backspace, bg='#ef5350', fg='white').pack(side=tk.LEFT, padx=2)

        # ── Row 1 : 4  5  6  ↑ ───────────────────────────────────────────
        r1 = tk.Frame(pad); r1.pack(pady=2)
        make_btn(r1, '4', lambda: insert('4')).pack(side=tk.LEFT, padx=2)
        make_btn(r1, '5', lambda: insert('5')).pack(side=tk.LEFT, padx=2)
        make_btn(r1, '6', lambda: insert('6')).pack(side=tk.LEFT, padx=2)
        make_btn(r1, '▲', lambda: move('home'), bg='#90CAF9').pack(side=tk.LEFT, padx=2)

        # ── Row 2 : 1  2  3  ↓ ───────────────────────────────────────────
        r2 = tk.Frame(pad); r2.pack(pady=2)
        make_btn(r2, '1', lambda: insert('1')).pack(side=tk.LEFT, padx=2)
        make_btn(r2, '2', lambda: insert('2')).pack(side=tk.LEFT, padx=2)
        make_btn(r2, '3', lambda: insert('3')).pack(side=tk.LEFT, padx=2)
        make_btn(r2, '▼', lambda: move('end'), bg='#90CAF9').pack(side=tk.LEFT, padx=2)

        # ── Row 3 : 0 (wide)  ←  → ───────────────────────────────────────
        r3 = tk.Frame(pad); r3.pack(pady=2)
        make_btn(r3, '0', lambda: insert('0'), w=3).pack(side=tk.LEFT, padx=2)
        make_btn(r3, '◀', lambda: move('left'), bg='#90CAF9').pack(side=tk.LEFT, padx=2)
        make_btn(r3, '▶', lambda: move('right'), bg='#90CAF9').pack(side=tk.LEFT, padx=2)

        # ── Row 4 : SPACE (full width) ────────────────────────────────────
        r4 = tk.Frame(pad); r4.pack(pady=2)
        tk.Button(r4, text='SPACE', command=lambda: insert(' '),
                  width=14, height=1,
                  font=('Arial', 10, 'bold'),
                  bg='#e0e0e0', relief=tk.RAISED, bd=2).pack()

        # ── Row 5 : Toggle Pairs ──────────────────────────────────────────
        r5 = tk.Frame(pad); r5.pack(pady=2)

        def toggle_pairs():
            content = self.accum_text.get('1.0', tk.END).strip()
            if not content:
                return

            import re as _re

            # Detect if already in paired format: contains "(n, n)"
            if _re.search(r'\(\s*[\d.]+\s*,\s*[\d.]+\s*\)', content):
                # Paired → Plain: extract all numbers from (a, b) groups
                nums = _re.findall(r'[\d.]+', content)
                new_content = ' '.join(nums)
                toggle_btn.config(text='→ Pairs')
            else:
                # Plain → Paired: split tokens and group by 2
                tokens = content.split()
                pairs = []
                for i in range(0, len(tokens) - 1, 2):
                    pairs.append(f'({tokens[i]}, {tokens[i+1]})')
                # If odd token left over, append it plain
                if len(tokens) % 2 == 1:
                    pairs.append(tokens[-1])
                new_content = ' '.join(pairs)
                toggle_btn.config(text='→ Plain')

            self.accum_text.delete('1.0', tk.END)
            self.accum_text.insert('1.0', new_content)
            self.accum_text.see(tk.INSERT)

        toggle_btn = tk.Button(r5, text='→ Pairs', command=toggle_pairs,
                               width=14, height=1,
                               font=('Arial', 10, 'bold'),
                               bg='#FF6F00', fg='white', relief=tk.RAISED, bd=2)
        toggle_btn.pack()

        # ── Close button ─────────────────────────────────────────────────
        tk.Button(popup, text="Close", command=popup.destroy,
                  font=('Arial', 9), bg='#607D8B', fg='white',
                  padx=20, pady=4).pack(pady=(4, 8))

    def run(self):
        self.root.geometry("1000x650")
        self.root.mainloop()

if __name__ == "__main__":
    app = CloudOCRTool()
    app.run()
