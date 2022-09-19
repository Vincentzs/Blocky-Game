"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    copy_colour_list = COLOUR_LIST[:]
    lst = []
    goal = random.choice([PerimeterGoal, BlobGoal])
    for _ in range(num_goals):
        colour = random.choice(copy_colour_list)
        lst.append(goal(colour))
        copy_colour_list.remove(colour)
    return lst


def unit_cell_colour(block: Block, row: int, col: int) -> Tuple[int, int, int]:
    """ Return the colour code of block at  position (row, col)
        Precondition: (row, col) is valid position on block
    """
    x = row
    y = col
    half = 2 ** (block.max_depth - block.level - 1)
    if not block.children:
        return block.colour
    if col < half <= row:
        return unit_cell_colour(block.children[0], x - half, y)
    elif row < half <= col:
        return unit_cell_colour(block.children[2], x, y - half)
    elif row < half and col < half:
        return unit_cell_colour(block.children[1], x, y)
    else:
        return unit_cell_colour(block.children[3], x - half, y - half)


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    length = 2 ** (block.max_depth - block.level)
    list_flatten = [[unit_cell_colour(block, row, col) for col in range(length)]
                    for row in range(length)]
    return list_flatten


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """ The class for PerimeterGoal
    """
    def score(self, board: Block) -> int:
        """Return the total score of PerimeterGoal. The score is the number of
        unit cells of colour c that are on the perimeter(corner cells count
        twice towards the score.
        """
        acc = 0
        board_flatten = _flatten(board)
        board_len = len(board_flatten)
        for row in range(board_len):
            if board_flatten[row][0] == self.colour:
                acc += 1
            if board_flatten[row][-1] == self.colour:
                acc += 1
        for col in range(board_len):
            if board_flatten[0][col] == self.colour:
                acc += 1
            if board_flatten[-1][col] == self.colour:
                acc += 1
        return acc

    def description(self) -> str:
        """Return a description of PerimeterGoal"""
        return 'PerimeterGoal: Perimeter Cell: 1 pt, Corner Cell: 2 pts'


class BlobGoal(Goal):
    """ The class for BlobGoal
    """
    def score(self, board: Block) -> int:
        """Return the total score of BlobGoal. The score is the number of
        connected unit cells of colour c in the largest blob.
        """
        acc = 0
        board_flatten = _flatten(board)
        visited = [[-1 for _ in range(2**board.max_depth)] \
                   for _ in range(2**board.max_depth)]
        for row in range(len(visited)):
            for col in range(len(visited[0])):
                if visited[row][col] == -1:
                    temp = self._undiscovered_blob_size((row, col),
                                                        board_flatten, visited)
                    acc = max(acc, temp)
        return acc

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        x = pos[0]
        y = pos[1]
        acc = 1
        board_len = len(board)
        if (x < 0 or board_len <= x) or (y < 0 or len(board[0]) <= y):
            return 0
        elif board[x][y] != self.colour:
            visited[x][y] = 0
            return 0
        elif visited[x][y] != -1:
            return 0
        visited[x][y] = 1
        acc += self._undiscovered_blob_size((x, y - 1), board, visited)
        acc += self._undiscovered_blob_size((x, y + 1), board, visited)
        acc += self._undiscovered_blob_size((x - 1, y), board, visited)
        acc += self._undiscovered_blob_size((x + 1, y), board, visited)
        return acc

    def description(self) -> str:
        """Return a description of BlobGoal"""
        return 'BlobGoal: Connected Cell: 1 pt (corners excluded).'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
