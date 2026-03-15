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
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e1e")
        
        self.cache_file = "sudoku_cache.json"
        self.cells = {}
        self.board = []
        self.original_puzzle = []
        
        # 1. Generate or load the puzzle data first
        self.load_or_generate_data()
        
        # 2. Build the visual grid (this populates self.cells)
        self.create_grid()
        
        # 3. Add buttons
        self.create_controls()
        
        # Position window on right side
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"360x480+{screen_width - 400}+50")

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
        # Remove roughly 75% of numbers
        for p in random.sample(range(side*side), int(side*side * 0.7)):
            board[p // side][p % side] = 0
        return board

    def load_or_generate_data(self):
        """Loads data from file or creates a fresh daily board."""
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
            except Exception:
                pass # If file is broken, just generate new

        self.board = [row[:] for row in new_puzzle]
        self.original_puzzle = [row[:] for row in new_puzzle]

    def save_cache(self):
        """Saves current entries to the JSON file."""
        # Update our internal board list from the UI entries
        current_state = []
        for r in range(9):
            row_data = []
            for c in range(9):
                val = self.cells[(r, c)].get()
                row_data.append(int(val) if val.isdigit() else 0)
            current_state.append(row_data)

        data = {
            "date": str(date.today()),
            "original": self.original_puzzle,
            "current_state": current_state
        }
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)
        print("Progress saved!")

    def create_grid(self):
        main_frame = tk.Frame(self.root, bg="#333333", padx=5, pady=5)
        main_frame.pack(pady=10)

        for r in range(9):
            for c in range(9):
                is_orig = self.original_puzzle[r][c] != 0
                val = self.board[r][c]
                
                # Thick borders for 3x3 blocks
                px = (1, 1) if (c + 1) % 3 != 0 else (1, 4)
                py = (1, 1) if (r + 1) % 3 != 0 else (1, 4)
                
                entry = tk.Entry(main_frame, width=2, font=('Consolas', 18, 'bold'), 
                                 justify='center', bd=0, bg="#2d2d2d", fg="#ffffff")
                entry.grid(row=r, column=c, padx=px, pady=py)
                
                if val != 0:
                    entry.insert(0, str(val))
                
                if is_orig:
                    entry.config(state='readonly', readonlybackground='#444444', fg="#00ffcc")
                
                self.cells[(r, c)] = entry

    def create_controls(self):
        btn_frame = tk.Frame(self.root, bg="#1e1e1e")
        btn_frame.pack(fill='x', padx=20)

        style = {"bg": "#007acc", "fg": "white", "font": ("Arial", 10, "bold"), "bd": 0, "pady": 5}
        
        tk.Button(btn_frame, text="SAVE", command=self.save_cache, **style).pack(side='left', expand=True, fill='x', padx=2)
        tk.Button(btn_frame, text="SOLVE", command=self.handle_solve, **style).pack(side='left', expand=True, fill='x', padx=2)

    def handle_solve(self):
        solution = [row[:] for row in self.original_puzzle]
        if self.solve_backtrack(solution):
            for r in range(9):
                for c in range(9):
                    if self.original_puzzle[r][c] == 0:
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