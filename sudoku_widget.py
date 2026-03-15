import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from datetime import date

class DailySudokuWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Sudoku")
        
        # --- WIDGET MODE SETTINGS ---
        self.root.overrideredirect(True) # Removes window borders/title bar
        self.root.attributes("-topmost", True) # Keeps it above other windows
        self.root.configure(bg="#1e1e1e")
        
        self.cache_file = "sudoku_cache.json"
        self.cells = {}
        self.board = []
        self.original_puzzle = []
        
        self.load_or_generate_data()
        self.create_grid()
        self.create_controls()
        
        # Initial position: Right side of screen
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"300x420+{screen_width - 320}+50")

        # Make the widget draggable
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def get_seed(self):
        return int(date.today().strftime("%Y%m%d"))

    def generate_puzzle(self):
        random.seed(self.get_seed())
        base, side = 3, 9
        def pattern(r, c): return (base * (r % base) + r // base + c) % side
        def shuffle(s): return random.sample(s, len(s))
        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, side + 1))
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        for p in random.sample(range(side*side), int(side*side * 0.7)):
            board[p // side][p % side] = 0
        return board

    def load_or_generate_data(self):
        new_puzzle = self.generate_puzzle()
        today_str = str(date.today())
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if data.get("date") == today_str:
                        self.board = data.get("current_state")
                        self.original_puzzle = data.get("original")
                        return
            except: pass
        self.board = [row[:] for row in new_puzzle]
        self.original_puzzle = [row[:] for row in new_puzzle]

    def save_cache(self):
        current_state = []
        for r in range(9):
            row = []
            for c in range(9):
                val = self.cells[(r, c)].get()
                row.append(int(val) if val.isdigit() else 0)
            current_state.append(row)
        data = {"date": str(date.today()), "original": self.original_puzzle, "current_state": current_state}
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)

    def create_grid(self):
        main_frame = tk.Frame(self.root, bg="#333333", padx=2, pady=2)
        main_frame.pack(pady=10)
        for r in range(9):
            for c in range(9):
                is_orig = self.original_puzzle[r][c] != 0
                val = self.board[r][c]
                px = (1, 1) if (c + 1) % 3 != 0 else (1, 3)
                py = (1, 1) if (r + 1) % 3 != 0 else (1, 3)
                entry = tk.Entry(main_frame, width=2, font=('Consolas', 14, 'bold'), 
                                 justify='center', bd=0, bg="#2d2d2d", fg="#ffffff")
                entry.grid(row=r, column=c, padx=px, pady=py)
                if val != 0: entry.insert(0, str(val))
                if is_orig: entry.config(state='readonly', readonlybackground='#444444', fg="#00ffcc")
                self.cells[(r, c)] = entry

    def create_controls(self):
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(fill='x', padx=10)
        style = {"bg": "#444", "fg": "white", "font": ("Arial", 8, "bold"), "bd": 0, "pady": 3}
        tk.Button(btn_frame, text="SAVE", command=self.save_cache, **style).pack(side='left', expand=True, fill='x', padx=1)
        tk.Button(btn_frame, text="SOLVE", command=self.handle_solve, **style).pack(side='left', expand=True, fill='x', padx=1)
        # Added an EXIT button since window borders are gone
        tk.Button(btn_frame, text="X", command=self.root.destroy, bg="#900", fg="white", bd=0).pack(side='left', padx=1)

    def handle_solve(self):
        solution = [row[:] for row in self.original_puzzle]
        if self.solve_backtrack(solution):
            for r in range(9):
                for c in range(9):
                    if self.original_puzzle[r][c] == 0:
                        self.cells[(r, c)].config(state='normal')
                        self.cells[(r, c)].delete(0, tk.END)
                        self.cells[(r, c)].insert(0, str(solution[r][c]))
                        self.cells[(r, c)].config(fg="#ffcc00")
            self.save_cache()

    def solve_backtrack(self, b):
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for n in range(1, 10):
                        if self.is_valid(b, r, c, n):
                            b[r][c] = n
                            if self.solve_backtrack(b): return True
                            b[r][c] = 0
                    return False
        return True

    def is_valid(self, b, r, c, n):
        for i in range(9):
            if b[r][i] == n or b[i][c] == n: return False
        sr, sc = (r//3)*3, (c//3)*3
        for i in range(sr, sr+3):
            for j in range(sc, sc+3):
                if b[i][j] == n: return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = DailySudokuWidget(root)
    root.mainloop()