import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import ast
import re

class WaveGridPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Wave Grid Plotter")
        self.root.geometry("800x800")
        
        # Initialize state variables
        self.grid_dims = None
        self.wave_points = None
        self.fig = None
        self.canvas = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial label and input for grid dimensions
        self.dynamic_label = ttk.Label(
            main_frame, 
            text="Specify Wavegrid as [Rows, Columns]",
            font=('Arial', 12)
        )
        self.dynamic_label.grid(row=0, column=0, pady=10)
        
        # Input box
        self.input_var = tk.StringVar()
        self.input_box = ttk.Entry(
            main_frame,
            textvariable=self.input_var,
            width=40
        )
        self.input_box.grid(row=1, column=0, pady=5)
        
        # Enter button
        self.enter_button = ttk.Button(
            main_frame,
            text="Enter",
            command=self.process_input
        )
        self.enter_button.grid(row=2, column=0, pady=10)
        
        # Frame for matplotlib
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.grid(row=3, column=0, pady=10)
        
        # Initialize state
        self.current_stage = 0
        
    def show_connector_options(self):
        options = """Connector Options:
        
(0a: stairstep right/vert)
(0b: stairstep vert/right)
(1: linear)
(2a: prequadratic connector)
(2b: postquadratic connector)
(3.x: sine wave connector)

For sine wave connector (3.x):
- d = distance between wavepts
- wavelength = d/x
- wave amplitude = wavelength"""
        
        messagebox.showinfo("Connector Options", options)
    
    def create_plot(self):
        if self.fig is None:
            self.fig = Figure(figsize=(8, 6))
        else:
            self.fig.clear()
        
        ax = self.fig.add_subplot(111)
        ax.grid(True)
        
        if self.grid_dims:
            ax.set_xlim(-1, self.grid_dims[1] + 1)
            ax.set_ylim(-1, self.grid_dims[0] + 1)
        
        if self.canvas is None:
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=0)
        else:
            self.canvas.draw()
            
    def plot_grid(self):
        ax = self.fig.gca()
        rows, cols = self.grid_dims
        
        # Plot grid points
        for i in range(rows):
            for j in range(cols):
                ax.plot(j, i, 'k.', markersize=5)
        
        self.canvas.draw()
    
    def plot_wave_points(self, points):
        ax = self.fig.gca()
        x_coords = [p[1] for p in points]
        y_coords = [p[0] for p in points]
        ax.plot(x_coords, y_coords, 'ro', markersize=8)
        self.canvas.draw()
    
    def plot_connectors(self, connector_types):
        ax = self.fig.gca()
        points = self.wave_points
        
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            connector_type = connector_types[i]
            
            self.plot_connector(ax, p1, p2, connector_type)
        
        self.canvas.draw()
    
    def plot_connector(self, ax, p1, p2, connector_type):
        x1, y1 = p1[1], p1[0]
        x2, y2 = p2[1], p2[0]
        
        if connector_type == "0a":  # Stairstep right/vert
            ax.plot([x1, x2, x2], [y1, y1, y2], 'b-')
        
        elif connector_type == "0b":  # Stairstep vert/right
            ax.plot([x1, x1, x2], [y1, y2, y2], 'b-')
        
        elif connector_type == "1":  # Linear
            ax.plot([x1, x2], [y1, y2], 'b-')
        
        elif connector_type.startswith("2"):  # Quadratic
            t = np.linspace(0, 1, 100)
            if connector_type == "2a":  # Prequadratic
                control_x = x1
                control_y = y2
            else:  # 2b - Postquadratic
                control_x = x2
                control_y = y1
            
            x = (1-t)**2 * x1 + 2*(1-t)*t * control_x + t**2 * x2
            y = (1-t)**2 * y1 + 2*(1-t)*t * control_y + t**2 * y2
            ax.plot(x, y, 'b-')
        
        elif connector_type.startswith("3"):  # Sine wave
            try:
                x_factor = float(connector_type[2:])
                dx = x2 - x1
                wavelength = abs(dx) / x_factor
                amplitude = wavelength
                
                x = np.linspace(x1, x2, 100)
                t = (x - x1) / dx * 2 * np.pi * x_factor
                y = np.linspace(y1, y2, 100) + amplitude * np.sin(t)
                ax.plot(x, y, 'b-')
            except:
                messagebox.showerror("Error", "Invalid sine wave parameter")
    
    def process_input(self):
        if self.current_stage == 0:
            try:
                # Parse grid dimensions
                input_text = self.input_var.get()
                dims = ast.literal_eval(input_text)
                if len(dims) != 2:
                    raise ValueError("Need exactly 2 dimensions")
                
                self.grid_dims = dims
                self.create_plot()
                self.plot_grid()
                
                # Update UI for next stage
                self.dynamic_label.config(
                    text="Specify wavegrid wavepts as\n[(r1,1), ..., (rc,C)]:"
                )
                self.input_var.set("")
                self.current_stage = 1
                
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
        
        elif self.current_stage == 1:
            try:
                # Parse wave points
                input_text = self.input_var.get()
                points = ast.literal_eval(input_text)
                self.wave_points = points
                self.plot_wave_points(points)
                
                # Show connector options and update UI for next stage
                self.show_connector_options()
                self.dynamic_label.config(
                    text="Enter connectors [S0, S1, S2, ..., SC-1]:"
                )
                self.input_var.set("")
                self.current_stage = 2
                
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
        
        elif self.current_stage == 2:
            try:
                # Parse connector types
                input_text = self.input_var.get()
                connectors = ast.literal_eval(input_text)
                self.plot_connectors(connectors)
                
                # Reset for new plot if desired
                self.dynamic_label.config(
                    text="Plot complete! Enter new grid dimensions to start over."
                )
                self.input_var.set("")
                self.current_stage = 0
                
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")

def main():
    root = tk.Tk()
    app = WaveGridPlotter(root)
    root.mainloop()

if __name__ == "__main__":
    main()