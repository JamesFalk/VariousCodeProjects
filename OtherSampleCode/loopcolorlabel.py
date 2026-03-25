import tkinter as tk

def create_colored_labels(root, color_list):
    row_num = 0
    for colors in color_list:
        for col_num, color in enumerate(colors):
            label = tk.Label(root, width=10, height=2, text="color", bg=get_color(color))
            label.grid(row=row_num, column=col_num)
        row_num += 1

def get_color(color_code):
    color_map = {1: 'red', 2: 'yellow', 3: 'green'}
    return color_map.get(color_code, 'white')  # Default to white for unknown codes

# Example usage:
color_list = [[1], [2, 3], [1, 2, 3]]  # A list of lists, each inner list representing a row's colors

root = tk.Tk()
create_colored_labels(root, color_list)
root.mainloop()
