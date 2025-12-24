import random

import kociemba


def get_permutation_parity(perm: list[int]) -> int:
    """
    Calculates the parity of a permutation.
    Returns 0 for even parity, 1 for odd parity.
    """
    n = len(perm)
    visited = [False] * n
    cycles = 0
    for i in range(n):
        if not visited[i]:
            cycles += 1
            j = i
            while not visited[j]:
                visited[j] = True
                j = perm[j]
    return (n - cycles) % 2


def generate_random_state_string() -> str:
    """
    Generates a random, valid Rubik's cube state as a facelet string
    suitable for Kociemba's solver.
    """
    solved_chars = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"

    # Sticker indexes for a cube state string
    # Ref: https://github.com/muodov/kociemba
    corner_stickers = [
        [8, 9, 20],  # URF (U9, R1, F3)
        [6, 18, 38],  # UFL (U7, F1, L3)
        [0, 36, 47],  # ULB (U1, L1, B3)
        [2, 45, 11],  # UBR (U3, B1, R3)
        [29, 26, 15],  # DFR (D3, F9, R7)
        [27, 44, 24],  # DLF (D1, L9, F7)
        [33, 53, 42],  # DBL (D7, B9, L7)
        [35, 17, 51],  # DRB (D9, R9, B7)
    ]

    edge_stickers = [
        [7, 19],  # UF (U8, F2)
        [5, 10],  # UR (U6, R2)
        [1, 46],  # UB (U2, B2)
        [3, 37],  # UL (U4, L2)
        [23, 12],  # FR (F6, R4)
        [21, 41],  # FL (F4, L6)
        [48, 14],  # BR (B4, R6)
        [50, 39],  # BL (B6, L4)
        [28, 25],  # DF (D2, F8)
        [32, 16],  # DR (D6, R8)
        [34, 52],  # DB (D8, B8)
        [30, 43],  # DL (D4, L8)
    ]

    # Generate random corner/edge permutations
    cp = list(range(8))
    random.shuffle(cp)
    ep = list(range(12))
    random.shuffle(ep)

    # Generate corner orientations (0,1,2). Last orientation determined by others for validity
    co = [random.randint(0, 2) for _ in range(7)]
    co.append((3 - (sum(co) % 3)) % 3)

    # Same for edge orientations (0 or 1)
    eo = [random.randint(0, 1) for _ in range(11)]
    eo.append((2 - (sum(eo) % 2)) % 2)

    # Swaps edges if corner and edge parity don't match
    if get_permutation_parity(cp) != get_permutation_parity(ep):
        ep[0], ep[1] = ep[1], ep[0]

    # Construct facelet string for scramble
    facelets = [""] * 54

    # Apply corner permutations and orientations
    for i in range(8):
        target_piece_idx = cp[i]  # This piece goes to the position of target_piece_idx
        orientation = co[i]  # With this orientation

        original_sticker_indices = corner_stickers[i]
        target_facelet_positions = corner_stickers[target_piece_idx]

        for k in range(3):  # For each of the 3 stickers on the corner piece
            original_char = solved_chars[original_sticker_indices[k]]
            # Apply orientation: (k + orientation) % 3 determines which sticker of the
            # original piece goes to which position of the target piece.
            target_facelet_idx = target_facelet_positions[(k + orientation) % 3]
            facelets[target_facelet_idx] = original_char

    # Apply edge permutations and orientations
    for i in range(12):  # For each original edge piece
        target_piece_idx = ep[i]  # This piece goes to the position of target_piece_idx
        orientation = eo[i]  # With this orientation

        original_sticker_indices = edge_stickers[i]
        target_facelet_positions = edge_stickers[target_piece_idx]

        for k in range(2):  # For each of the 2 stickers on the edge piece
            original_char = solved_chars[original_sticker_indices[k]]
            target_facelet_idx = target_facelet_positions[(k + orientation) % 2]
            facelets[target_facelet_idx] = original_char

    # Fill centers
    # U5(4), R5(13), F5(22), D5(31), L5(40), B5(49)
    center_indices = [4, 13, 22, 31, 40, 49]
    for idx in center_indices:
        facelets[idx] = solved_chars[idx]

    # Check for any empty slots (debugging check)
    if "" in facelets:
        missing_indices = [i for i, x in enumerate(facelets) if x == ""]
        raise ValueError(
            f"Generated facelet string has missing values at indices: {missing_indices}"
        )

    return "".join(facelets)


def invert_move(move: str) -> str:
    """Inverts a single move notation (e.g. U -> U', U' -> U, U2 -> U2)."""
    if move.endswith("'"):
        return move[:-1]
    elif move.endswith("2"):
        return move
    else:
        return move + "'"


def invert_solution(solution: str) -> str:
    """Inverts a solution string to get the scramble sequence."""
    if not solution:
        return ""
    moves = solution.split()
    inverted_moves = [invert_move(m) for m in reversed(moves)]
    return " ".join(inverted_moves)


def get_scramble() -> str:
    """Generates a random state scramble using Kociemba's algorithm."""
    state = ""
    try:
        state = generate_random_state_string()
        print(f"DEBUG: Generated State: {state}")

        solution = kociemba.solve(state)
        print(f"DEBUG: Kociemba Solution: {solution}")

        scramble = invert_solution(solution)
        print(f"DEBUG: Final Scramble: {scramble}")
        return scramble
    except Exception as e:
        print(f"ERROR: {e}")
        # Return error with state for debugging
        return f"Error generating scramble: {e} | State: {state}"
