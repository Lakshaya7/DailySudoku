import random, json, os
from datetime import date

def is_valid(board, num, pos):
    for i in range(9):
        if board[pos[0]][i] == num and pos[1] != i: return False
        if board[i][pos[1]] == num and pos[0] != i: return False
    br, bc = (pos[0] // 3) * 3, (pos[1] // 3) * 3
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == num and (i, j) != pos: return False
    return True

def solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for n in range(1, 10):
                    if is_valid(board, n, (r, c)):
                        board[r][c] = n
                        if solve(board): return True
                        board[r][c] = 0
                return False
    return True

def get_board():
    today = str(date.today())
    if os.path.exists("sudoku_cache.json"):
        with open("sudoku_cache.json", "r") as f:
            data = json.load(f)
            if data["date"] == today: return data["grid"]
    
    random.seed(today)
    # Basic starting template (0 = empty)
    grid = [[5,3,0,0,7,0,0,0,0],[6,0,0,1,9,5,0,0,0],[0,9,8,0,0,0,0,6,0],
            [8,0,0,0,6,0,0,0,3],[4,0,0,8,0,3,0,0,1],[7,0,0,0,2,0,0,0,6],
            [0,6,0,0,0,0,2,8,0],[0,0,0,4,1,9,0,0,5],[0,0,0,0,8,0,0,7,9]]
    return grid

def save(grid):
    with open("sudoku_cache.json", "w") as f:
        json.dump({"date": str(date.today()), "grid": grid}, f)

if __name__ == "__main__":
    board = get_board()
    print("--- Daily Sudoku ---")
    for row in board: print(row)
    # For now, we save immediately to test the cache
    save(board)
    print("\nBoard saved to cache. Run again to resume!")