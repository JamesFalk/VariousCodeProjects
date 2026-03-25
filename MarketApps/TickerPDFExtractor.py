import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import PyPDF2
import re
from typing import List
import pandas as pd
import os

class TickerExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Ticker Extractor")
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TFrame', padding=10)
        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # File selection area
        self.file_frame = ttk.Frame(main_frame)
        self.file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=0, padx=(0, 5))
        self.browse_button = ttk.Button(self.file_frame, text="@Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=1)
        
        # Button frame for all action buttons
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.grid(row=1, column=0, pady=(0, 10))
        
        # Extract button
        self.extract_button = ttk.Button(self.button_frame, text="㊂ Extract", command=self.extract_text)
        self.extract_button.grid(row=0, column=1, padx=5)
        
        # Filter Tickers button
        self.filter_button = ttk.Button(self.button_frame, text="ꘜ Filter", command=self.filter_tickers)
        self.filter_button.grid(row=1, column=0, padx=5)
        
        # Save as Text button
        self.save_button = ttk.Button(self.button_frame, text="⍍ Save", command=self.save_as_text)
        self.save_button.grid(row=3, column=2, padx=5)
        
        # Copy button
        self.copy_button = ttk.Button(self.button_frame, text="❐ Copy", command=self.copy_to_clipboard)
        self.copy_button.grid(row=2, column=1, padx=5)
        
        # Output area
        self.output_frame = ttk.Frame(main_frame)
        self.output_frame.grid(row=2, column=0, sticky="nsew")
        
        # Add a label above the text widget
        self.output_label = ttk.Label(self.output_frame, text="Extracted Text:")
        self.output_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Create text widget and scrollbar
        self.output_text = tk.Text(self.output_frame, height=15, width=60, wrap=tk.WORD)
        self.scrollbar = ttk.Scrollbar(self.output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.scrollbar.set)
        self.output_text.grid(row=1, column=0, sticky="nsew")
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)

    def browse_file(self):
        """Opens file dialog and sets the chosen file path"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.PDF"), ("All files", "*.*")])
        if filename:
            self.file_path.set(filename)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extracts text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            messagebox.showerror("Error", f"Error reading PDF file: {str(e)}")
            return ""

    def extract_text(self):
        """Main extraction function"""
        pdf_path = self.file_path.get()
        if not pdf_path:
            messagebox.showwarning("Warning", "Please select a PDF file first.")
            return
        
        # Clear previous output
        self.output_text.delete(1.0, tk.END)
        
        # Extract text from PDF
        text_content = self.extract_text_from_pdf(pdf_path)
        if text_content:
            self.output_text.insert(tk.END, text_content)
            self.output_label.config(text="Extracted Text:")

    def filter_tickers(self):
        """Filters and displays only uppercase words"""
        text = self.output_text.get(1.0, tk.END)
        if not text.strip():
            messagebox.showwarning("Warning", "No text to filter!")
            return
        
        # Find all uppercase words (2 or more characters)
        tickers = re.findall(r'\b[A-Z]{2,}\b', text)
        
        # Remove duplicates and sort
        unique_tickers = sorted(set(tickers))
        
        # Clear and update display
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, ' '.join(unique_tickers))
        self.output_label.config(text="Filtered Tickers:")

    def save_as_text(self):
        """Saves the current content to a text file"""
        text = self.output_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No content to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save As"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text)
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")

    def copy_to_clipboard(self):
        """Copies output text to clipboard"""
        text = self.output_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Success", "Content copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No content to copy!")

def main():
    root = tk.Tk()
    app = TickerExtractorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()