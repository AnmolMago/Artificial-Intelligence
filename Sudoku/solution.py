from collections import defaultdict

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [ a + b for a in A for b in B ]

def zipcross(A, B):
    return [ a + b for a, b in zip(A, B) ]

def get_peers(cell):
    peers = set()
    for unit in UNITLIST:
        if cell in unit:
            peers.update(unit)
    return peers - set([cell])

assignments = []

COLS_STR = "123456789"
ROWS_STR = "ABCDEFGHI"

CELLS = cross(ROWS_STR, COLS_STR)
ROWS = [ cross(r, COLS_STR) for r in ROWS_STR ]
COLS = [ cross(ROWS_STR, c) for c in COLS_STR ]
SECTIONS = [ cross(row_sec, col_sec) for row_sec in ("ABC", "DEF", "GHI")
                for col_sec in ("123", "456", "789") ]
DIAGONALS = [ zipcross(ROWS_STR, cols) for cols in [COLS_STR, COLS_STR[::-1] ]]

UNITLIST = ROWS + COLS + DIAGONALS + SECTIONS

PEERS = dict([ (cell, get_peers(cell)) for cell in CELLS ])

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    for unit in UNITLIST:
        # Find all instances of naked twins
        len_two_vals = defaultdict(list)
        for cell in unit:
            val = values[cell]
            if len(val) == 2:
                len_two_vals[val].append(cell)

        twins_list = [ (val,cells) for val, cells in len_two_vals.items() if len(cells) == 2 ]

        # Eliminate the naked twins as possibilities for their peers
        for val, twins in twins_list:
            for peer in [peer for peer in unit if peer not in twins]:
                assign_value(values, peer, values[peer].replace(val[0], ''))
                assign_value(values, peer, values[peer].replace(val[1], ''))
                
    return values

def grid_values(grid_str):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'.
                If the box has no value, then the value will be '123456789'.
    """

    def get_pair(cell, val):
        return (cell, COLS_STR) if val == '.' else (cell, val)

    return dict([ get_pair(cell, val) for cell, val in zip(CELLS, grid_str) ])


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    if values is False:
        print("Sudoku is unsolveable! (or code is broken)")

    width = 1+max(len(values[s]) for s in CELLS)
    line = '+'.join(['-'*(width*3)]*3)
    for r in ROWS_STR:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in COLS_STR))
        if r in 'CF':
            print(line)
    print

def eliminate(values):
    """
    Eliminate values of solved cells from their peers.
    Args:
        values(dict): a dictionary of the form {'cell_name': '123456789', ...}
    Returns:
        the values dictionary with impossible values eliminated 
    """
    solved_cells = [ cell for cell, val in values.items() if len(val) == 1 ]
    for cell in solved_cells:
        for peer in PEERS[cell]:
            if values[cell] in values[peer]:
                assign_value(values, peer, values[peer].replace(values[cell], ''))
    return values

def only_choice(values):
    """
    Assign values when there is only one possible cell where they may go.
    Args:
        values(dict): a dictionary of the form {'cell_name': '123456789', ...}
    Returns:
        the values dictionary with the new values assigned
    """
    for unit in UNITLIST:
        for digit in '123456789':
            possible_cells = [ cell for cell in unit if digit in values[cell] ]
            if len(possible_cells) == 1:
                assign_value(values, possible_cells[0], digit)
    return values

def reduce_puzzle(values):
    """
    Iteratively eliminate values and assign only_choices until no more changes are detected.
    Args:
        values(dict): a dictionary of the form {'cell_name': '123456789', ...}
    Returns:
        the values dictionary with the new values assigned
    """
    solved_values_before = len([ cell for cell in values.keys() if len(values[cell]) == 1 ])
    stall = False #lobw
    while not stall:
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([ cell for cell in values.keys() if len(values[cell]) == 1 ])
        stall = (solved_values_before == solved_values_after)
        solved_values_before = solved_values_after
        if any([ len(values[cell]) == 0 for cell in values.keys() ]):
            return False
    return values


def search(values):
    """
    Implement Depth First Search to find a solution to the grid.
    Args:
        values(dict): a dictionary of the form {'cell_name': '123456789', ...}
    Returns:
        the values dictionary with the new values assigned
    """
    values = reduce_puzzle(values) #iterate eliminate and only_choice
    if all(len(values[cell]) == 1 for cell in CELLS) or values is False:
        # solved or unsolvable(False)
        return values

    _, cell = min([(len(values[cell]), cell) for cell in CELLS if len(values[cell]) > 1])
    for value in values[cell]:
        new_sudoku = values.copy()
        new_sudoku[cell] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

    return values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # print("PRINTING", solve(diag_sudoku_grid))
    display(solve(diag_sudoku_grid))
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
