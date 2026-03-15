import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from datetime import date

class DailySudokuWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Sudoku Widget")
        self.root.geometry("400x500")
        self.root.attributes("-topmost", True)  # Keep as a widget on top
        
        self.cache_file = "sudoku_cache.json"
        self.cells = {} # Dictionary to store Entry widgets
        self.board = [] # Current state
        self.original_puzzle = [] # The starting board for the day
        
        self.setup_daily_puzzle()
        self.create_grid()
        self.create_controls()

    def get_seed(self):
        """Generates a unique integer seed based on the current date."""
        return int(date.today().strftime("%Y%m%d"))

    def generate_puzzle(self):
        """
        Generates a valid (but simple) Sudoku for the day.
        Real Sudoku generation is complex; here we use a seeded shuffle 
        of a base pattern to ensure a new valid puzzle every day.
        """
        random.seed(self.get_seed())
        base = 3
        side = base * base

        def pattern(r, c): return (base * (r % base) + r // base + c) % side
        def shuffle(s): return random.sample(s, len(s))
        
        r_base = range(base)
        rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
        cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
        nums = shuffle(range(1, side + 1))

        # Produce board using randomized pattern
        board = [[nums[pattern(r, c)] for c in cols] for r in rows]
        
        # Remove numbers to create the puzzle (Difficulty adjustment)
        squares = side * side
        empties = squares * 3 // 4
        for p in random.sample(range(squares), empties):
            board[p // side][p % side] = 0
            
        return board

    def setup_daily_puzzle(self):
        """Loads from cache or generates a new one if it's a new day."""
        new_puzzle = self.generate_puzzle()
        today_str = str(date.today())

        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                # If cache is from today, load it
                if data.get("date") == today_str:
                    self.board = data.get("current_state")
                    self.original_puzzle = data.get("original")
                    return

        # If no cache or old cache, start fresh
        self.board = [row[:] for row in new_puzzle]
        self.original_puzzle = [row[:] for row in new_puzzle]
        self.save_cache()

    def save_cache(self):
        """Saves current board state to JSON."""
        # Update board data from entries before saving
        for r in range(9):
            for c in range(9):
                val = self.cells[(r, c)].get()
                self.board[r][c] = int(val) if val.isdigit() else 0

        data = {
            "date": str(date.today()),
            "original": self.original_puzzle,
            "current_state": self.board
        }
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)

    def create_grid(self):
        """Creates the 9x9 GUI grid."""
        container = tk.Frame(self.root, bg="black", bd=2)
        container.pack(pady=20, padx=20)

        for r in range(9):
            for c in range(9):
                # Add thicker borders for 3x3 subgrids
                padx = (1, 1) if (c + 1) % 3 != 0 else (1, 3)
                pady = (1, 1) if (r + 1) % 3 != 0 else (1, 3)
                
                cell_val = self.board[r][c]
                is_original = self.original_puzzle[r][c] != 0
                
                entry = tk.Entry(container, width=2, font=('Arial', 18), 
                                 justify='center', bd=1)
                entry.grid(row=r, column=c, padx=padx, pady=pady)
                
                if cell_val != 0:
                    entry.insert(0, str(cell_val))
                
                if is_original:
                    entry.config(state='readonly', readonlybackground='#e0e0e0')
                
                self.cells[(r, c)] = entry

    def solve_logic(self, board):
        """Standard Backtracking Algorithm."""
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    for n in range(1, 10):
                        if self.is_valid(board, r, c, n):
                            board[r][c] = n
                            if self.solve_logic(board):
                                return True
                            board[r][c] = 0
                    return False
        return True

    def is_valid(self, board, r, c, n):
        # Check row
        if n in board[r]: return False
        # Check col
        if n in [board[i][c] for i in range(9)]: return False
        # Check 3x3 box
        sr, sc = (r // 3) * 3, (c // 3) * 3
        for i in range(sr, sr + 3):
            for j in range(sc, sc + 3):
                if board[i][j] == n: return False
        return True

    def handle_solve(self):
        """Triggered by the Solve button."""
        # Work on a copy of the original to find the solution
        solution = [row[:] for row in self.original_puzzle]
        if self.solve_logic(solution):
            for r in range(9):
                for c in range(9):
                    if self.original_puzzle[r][c] == 0:
                        self.cells[(r, c)].delete(0, tk.END)
                        self.cells[(r, c)].insert(0, str(solution[r][c]))
                        self.cells[(r, c)].config(fg="blue")
            self.save_cache()
        else:
            messagebox.showerror("Error", "No solution exists for this puzzle.")

    def create_controls(self):
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill='x', padx=20)

        save_btn = tk.Button(btn_frame, text="Save Progress", command=self.save_cache)
        save_btn.pack(side='left', expand=True, fill='x', padx=5)

        solve_btn = tk.Button(btn_frame, text="Solve Daily", command=self.handle_solve)
        solve_btn.pack(side='left', expand=True, fill='x', padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = DailySudokuWidget(root)
    root.mainloop()