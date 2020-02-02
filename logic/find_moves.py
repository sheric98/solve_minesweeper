import random
from operator import itemgetter
import itertools

class Solver:
    to_flag = set()
    to_reveal = set()

    blocks = {}
    intersections = {}
    unique_blocks = set()
    rand = random.Random()

    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def __init__(self, board):
        self.board = board
        self.to_check = set()

    def clear_updates(self):
        self.to_reveal.clear()
        self.to_flag.clear()

    def reset_blocks(self):
        self.blocks.clear()
        self.unique_blocks.clear()
        self.intersections.clear()

    def find_update(self):
        self.clear_updates()
        self.reset_blocks()
        self.check_update()
        if not self.to_flag and not self.to_reveal:
            # print("random choice")
            # coord = self.board.empties[self.rand.randrange(len(self.board.empties))]
            coord = self.get_best_prob()
            return [coord], [], "random"
        else:
            return self.to_reveal, self.to_flag, "not random"

    def check_update(self):
        to_remove = set()

        for opened in self.to_check:
            unknowns, flags, nums = self.get_neighbors(opened)
            bombs = int(self.get_status(opened))
            unseen_bombs = bombs - len(flags)
            if len(unknowns) == unseen_bombs:
                self.to_flag.update(unknowns)
            elif len(flags) == bombs:
                self.to_reveal.update(unknowns)
                to_remove.add(opened)
            else:
                if len(unknowns) > 0:
                    block = Block(unknowns, unseen_bombs)
                    clearable, flaggable = self.check_blocks(block)
                    self.to_reveal.update(clearable)
                    self.to_flag.update(flaggable)
                    self.unique_blocks.add(block)

        for item in to_remove:
            self.to_check.remove(item)

    def get_best_prob(self):
        empty_probs, empties = self.assign_probs()
        other_mines = 0
        for prob in empty_probs:
            other_mines += prob[1]
        remaining_mines = max(0, self.board.mines - other_mines)
        if len(empties) == 0:
            # print("prob is " + str(empty_probs[0][1]))
            return empty_probs[0][0]
        default_prob = remaining_mines / len(empties)
        if len(empty_probs) > 0 and empty_probs[0][1] <= default_prob:
            # print("prob is " + str(empty_probs[0][1]))
            return empty_probs[0][0]
        else:
            # print("prob is " + str(default_prob))
            return empties[self.rand.randrange(len(empties))]

    def assign_probs(self):
        chains = self.create_bcs()
        empty_probs = []
        empties = self.board.empties.copy()
        for chain in chains:
            seen = set()
            counts = {}
            self.go_through_chain(chain, seen, counts)
            total = counts["total"] if "total" in counts else 0
            counts.pop("total", None)
            for square in counts.keys():
                square_prob = counts[square] / total
                empty_probs.append([square, square_prob])
                empties.remove(square)
        empty_probs.sort(key=itemgetter(1))
        return empty_probs, empties

    def go_through_chain(self, chain, seen, counts):
        squares = chain.block.squares.copy()
        mines = chain.block.num_bombs
        nexts = chain.nexts
        if chain.prev is not None:
            conns = chain.prev[1]
            for conn in conns:
                if conn in seen:
                    mines -= 1
                squares.remove(conn)
        mines = max(mines, 0)
        for comb in itertools.combinations(squares, mines):
            cpy_seen = seen.copy()
            cpy_seen.update(comb)

            if len(nexts) > 0:
                for nxt_chain in nexts:
                    self.go_through_chain(nxt_chain, cpy_seen, counts)
            else:
                for square in cpy_seen:
                    if square in counts:
                        counts[square] += 1
                    else:
                        counts[square] = 1
                if "total" in counts:
                    counts["total"] += 1
                else:
                    counts["total"] = 1

    def create_bcs(self):
        ret = []
        while len(self.unique_blocks) > 0:
            head = self.unique_blocks.pop()
            chain = self.bc_chain(head, None)
            ret.append(chain)
        return ret

    def bc_chain(self, b1, prev):
        all_conns = self.intersections[b1] if b1 in self.intersections else {}
        nexts = set()
        for conn in all_conns.keys():
            if conn in self.unique_blocks:
                self.unique_blocks.remove(conn)
                common_squares = all_conns[conn]
                conn_bc = self.bc_chain(conn, [b1, common_squares])
                nexts.add(conn_bc)
        bc = BlockChain(b1, prev, nexts)
        return bc

    def check_blocks(self, block):
        clears = set()
        flags = set()

        for square in block.squares:
            if square in self.blocks:
                commons = self.blocks[square]
                for block2 in commons:
                    msg, clearable, flaggable = block.inter_logic(block2)
                    if msg == "same":
                        return clears, flags
                    else:
                        clears.update(clearable)
                        flags.update(flaggable)
                        self.add_intersection(block, block2, square)
                        self.add_intersection(block2, block, square)
                commons.append(block)
            else:
                self.blocks[square] = [block]

        return clears, flags

    def add_intersection(self, b1, b2, square):
        if b1 in self.intersections:
            b1_inters = self.intersections[b1]
            if b2 in b1_inters:
                b1_b2 = b1_inters[b2]
                b1_b2.add(square)
            else:
                b1_inters[b2] = {square}
        else:
            self.intersections[b1] = {b2: {square}}

    def get_status(self, coord):
        i, j = coord
        return self.board.squares[i][j]

    def in_board(self, coord):
        i, j = coord
        rows = self.board.rows
        cols = self.board.cols
        return (0 <= i < rows) and (0 <= j < cols)

    def get_neighbors(self, coord):
        empties = []
        flags = set()
        nums = set()
        i, j = coord

        for relative in self.neighbors:
            x, y = relative
            neigh_coord = (i+x, y+j)
            if self.in_board(neigh_coord):
                status = self.get_status(neigh_coord)
                if status == 'E':
                    empties.append(neigh_coord)
                elif status == 'F':
                    flags.add(neigh_coord)
                elif status != '0':
                    nums.add(neigh_coord)

        return empties, flags, nums


class Block:
    def __init__(self, squares, bombs):
        self.num_bombs = bombs
        self.squares = squares
        self.squares.sort(key=itemgetter(0, 1))

    def __key(self):
        return tuple(self.squares)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, b2):
        return self.__key() == b2.__key()

    def intersection(self, block2):
        inter = set()
        b1 = set(self.squares)
        b2 = set(block2.squares)
        for square in self.squares:
            if square in block2.squares:
                inter.add(square)
                b1.remove(square)
                b2.remove(square)
        return inter, b1, b2

    def inter_logic(self, block2):
        clearable = set()
        flaggable = set()

        inter, b1, b2 = self.intersection(block2)
        b1_bombs = self.num_bombs
        b2_bombs = block2.num_bombs

        if len(b1) == len(b2) == 0 and b1_bombs == b2_bombs:
            return "same", clearable, flaggable

        inter_must = max(0, b1_bombs - len(b1), b2_bombs - len(b2))
        inter_can = min(b1_bombs, b2_bombs, len(inter))

        if len(inter) == inter_must:
            flaggable.update(inter)
            clearable.update(b1)
            clearable.update(b2)
        if inter_must >= b1_bombs:
            clearable.update(b1)
        if inter_must >= b2_bombs:
            clearable.update(b2)
        if inter_can < b1_bombs:
            if b1_bombs - inter_can == len(b1):
                flaggable.update(b1)
        if inter_can < b2_bombs:
            if b2_bombs - inter_can == len(b2):
                flaggable.update(b2)

        return "diff", clearable, flaggable


class BlockChain:
    def __init__(self, block, prev, nexts):
        self.block = block
        self.prev = prev
        self.nexts = nexts

    def __eq__(self, bc2):
        b1 = self.block
        b2 = bc2.block
        inter, b1, b2 = b1.intersection(b2)
        return len(b1) == len(b2) == 0

    def __hash__(self):
        return self.block.__hash__()
