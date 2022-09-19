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

This file contains the Block class, the main data structure used in the game.
"""
from __future__ import annotations
from typing import Optional, Tuple, List
import random
import math

from settings import colour_name, COLOUR_LIST


def generate_board(max_depth: int, size: int) -> Block:
    """Return a new game board with a depth of <max_depth> and dimensions of
    <size> by <size>.

    >>> board = generate_board(3, 750)
    >>> board.max_depth
    3
    >>> board.size
    750
    >>> len(board.children) == 4
    True
    """
    board = Block((0, 0), size, random.choice(COLOUR_LIST), 0, max_depth)
    board.smash()

    return board


class Block:
    """A square Block in the Blocky game, represented as a tree.

    In addition to its tree-related attributes, a Block also contains attributes
    that describe how the Block appears on a Cartesian plane. All positions
    describe the upper left corner (row, col), and the origin is at (0, 0). All
    positions and sizes are in the unit of pixels.

    When a block has four children, the order of its children impacts each
    child's position. Indices 0, 1, 2, and 3 are the upper-right child,
    upper-left child, lower-left child, and lower-right child, respectively.

    === Public Attributes ===
    position:
        The (row, col) coordinates of the upper left corner of this Block.
    size:
        The height and width of this square Block.
    colour:
        If this block is not subdivided, <colour> stores its colour. Otherwise,
        <colour> is None.
    level:
        The level of this block within the overall block structure.
        The outermost block, corresponding to the root of the tree,
        is at level zero. If a block is at level i, its children are at
        level i+1.
    max_depth:
        The deepest level allowed in the overall block structure.
    children:
        The blocks into which this block is subdivided. The children are
        stored in this order: upper-right child, upper-left child,
        lower-left child, lower-right child.

    === Representation Invariants===
    - len(children) == 0 or len(children) == 4
    - If this Block has children:
        - their max_depth is the same as that of this Block.
        - their size is half that of this Block.
        - their level is one greater than that of this Block.
        - their position is determined by the position and size of this Block,
          and their index in this Block's list of children.
        - this Block's colour is None.
    - If this Block has no children:
        - its colour is not None.
    - level <= max_depth
    """
    position: Tuple[int, int]
    size: int
    colour: Optional[Tuple[int, int, int]]
    level: int
    max_depth: int
    children: List[Block]

    def __init__(self, position: Tuple[int, int], size: int,
                 colour: Optional[Tuple[int, int, int]], level: int,
                 max_depth: int) -> None:
        """Initialize this block with <position>, dimensions <size> by <size>,
        the given <colour>, at <level>, and with no children.

        Preconditions:
            - position[0] >= 0 and position[1] >= 0
            - size > 0
            - level >= 0
            - max_depth >= level
        """
        self.position = position
        self.size = size
        self.colour = colour
        self.level = level
        self.max_depth = max_depth
        self.children = []

    def __str__(self) -> str:
        """Return this Block in a string format.

        >>> block = Block((0, 0), 750, (0, 0, 0), 0, 1)
        >>> str(block)
        'Leaf: colour=Black, pos=(0, 0), size=750, level=0\\n'
        """
        if len(self.children) == 0:
            indents = '\t' * self.level
            colour = colour_name(self.colour)
            return f'{indents}Leaf: colour={colour}, pos={self.position}, ' \
                   f'size={self.size}, level={self.level}\n'
        else:
            indents = '\t' * self.level
            result = f'{indents}Parent: pos={self.position},' \
                     f'size={self.size}, level={self.level}\n'

            for child in self.children:
                result += str(child)

            return result

    def __eq__(self, other: Block) -> bool:
        """Return True iff this Block and all its descendents are equivalent to
        the <other> Block and all its descendents.
        """
        if len(self.children) == 0 and len(other.children) == 0:
            # Both self and other are leaves.
            return self.position == other.position and \
                   self.size == other.size and \
                   self.colour == other.colour and \
                   self.level == other.level and \
                   self.max_depth == other.max_depth
        elif len(self.children) != len(other.children):
            # One of self or other is a leaf while the other is not.
            return False
        else:
            # Both self and other have four children.
            for i in range(4):
                # The != operator also uses the __eq__ special method.
                if self.children[i] != other.children[i]:
                    return False

            return True

    def _child_size(self) -> int:
        """Return the size of this Block's children.
        """
        return round(self.size / 2.0)

    def _children_positions(self) -> List[Tuple[int, int]]:
        """Return the positions of this Block's four children.

        The positions are returned in this order: upper-right child, upper-left
        child, lower-left child, lower-right child.
        """
        x = self.position[0]
        y = self.position[1]
        size = self._child_size()

        return [(x + size, y), (x, y), (x, y + size), (x + size, y + size)]

    def _update_children_positions(self, position: Tuple[int, int]) -> None:
        """Set the position of this Block to <position> and update all its
        descendants to have positions consistent with this Block's.

        <position> is the (row, col) coordinates of the upper-left corner
         of this Block.
        """
        x = position[0]
        y = position[1]
        size = self._child_size()
        if not self.children:
            self.position = position
        else:
            self.position = position
            self.children[0].position = (x + size, y)
            self.children[1].position = (x, y)
            self.children[2].position = (x, y + size)
            self.children[3].position = (x + size, y + size)
            # recurse again to update positions for children of children
            self.children[0]._update_children_positions((x + size, y))
            self.children[1]._update_children_positions((x, y))
            self.children[2]._update_children_positions((x, y + size))
            self.children[3]._update_children_positions((x + size, y + size))

    def smashable(self) -> bool:
        """Return True iff this block can be smashed.

        A block can be smashed if it has no children and its level is not at
        max_depth.
        """
        return self.level != self.max_depth and len(self.children) == 0

    def smash(self) -> bool:
        """Sub-divide this block so that it has four randomly generated
        children.

        If this Block's level is <max_depth>, do nothing. If this block has
        children, do nothing.

        Return True iff the smash was performed.
        """
        if not self.smashable():
            return False
        cur_level = self.level
        max_depth = self.max_depth
        if cur_level != max_depth:
            num = math.exp(-0.25 * cur_level)
            self.colour = None
            size = self.size // 2
            lvl = self.level + 1
            pos = self.position
            x = pos[0]
            y = pos[1]
            block1 = Block((x + size, y), size,
                           random.choice(COLOUR_LIST), lvl, max_depth)
            block2 = Block(pos, size,
                           random.choice(COLOUR_LIST), lvl, max_depth)
            block3 = Block((x, y + size), size,
                           random.choice(COLOUR_LIST), lvl, max_depth)
            block4 = Block((x + size, y + size), size,
                           random.choice(COLOUR_LIST), lvl, max_depth)
            self.children = [block1, block2, block3, block4]
            for i in range(4):
                rng = random.random()
                if rng < num:
                    self.children[i].smash()
            return True
        return False

    def swap(self, direction: int) -> bool:
        """Swap the child Blocks of this Block.

        If this Block has no children, do nothing. Otherwise, if <direction> is
        1, swap vertically. If <direction> is 0, swap horizontally.

        Return True iff the swap was performed.

        Precondition: <direction> is either 0 or 1
        """
        if self.children:
            if direction == 0:
                self.children = [self.children[1], self.children[0],
                                 self.children[3], self.children[2]]
            elif direction == 1:
                self.children = [self.children[3], self.children[2],
                                 self.children[1], self.children[0]]
            self._update_children_positions(self.position)
            return True
        return False

    def rotate(self, direction: int) -> bool:
        """Rotate this Block and all its descendants.

        If this Block has no children, do nothing. If <direction> is 1, rotate
        clockwise. If <direction> is 3, rotate counter-clockwise.

        Return True iff the rotate was performed.

        Precondition: <direction> is either 1 or 3.
        """
        if self.children:
            if direction == 1:
                self.children = [self.children[1], self.children[2],
                                 self.children[3], self.children[0]]
            elif direction == 3:
                self.children = [self.children[3], self.children[0],
                                 self.children[1], self.children[2]]
            self.children[0].rotate(direction)
            self.children[1].rotate(direction)
            self.children[2].rotate(direction)
            self.children[3].rotate(direction)
            self._update_children_positions(self.position)
            return True
        return False

    def paint(self, colour: Tuple[int, int, int]) -> bool:
        """Change this Block's colour iff it is a leaf at a level of max_depth
        and its colour is different from <colour>.

        Return True iff this Block's colour was changed.
        """
        if self.level == self.max_depth and self.colour != colour:
            self.colour = colour
            return True
        return False

    def combine(self) -> bool:
        """Turn this Block into c1 leaf based on the majority colour of its
        children.

        The majority colour is the colour with the most child blocks of that
        colour. A tie does not constitute c1 majority (e.g., if there are two
        red children and two blue children, then there is no majority colour).

        If there is no majority colour, do nothing. If this block is not at c1
        level of max_depth - 1, or this block has no children, do nothing.

        Return True iff this Block was turned into c1 leaf node.
        """
        #could use dictionary instead of list for list_count
        level = self.level
        max_depth = self.max_depth
        if level == max_depth - 1 and self.children != []:
            colour = []
            for child in self.children:
                colour.append(child.colour)
            c1 = colour.count(colour[0])
            c2 = colour.count(colour[1])
            c3 = colour.count(colour[2])
            if (c1 == 2 and c2 == 1 and c3 == 2) or \
                    (c1 == 2 and c2 == 1 and c3 == 1) or \
                    c1 == 3 or c1 == 4 or (c1 == 2 and c2 == 2 and c3 == 1):
                self.children = []
                self.colour = colour[0]
            elif (c1 == 1 and c2 == 2 and c3 == 2) or \
                    (c1 == 1 and c2 == 2 and c3 == 1) or c2 == 3:
                self.children = []
                self.colour = colour[1]
            elif c1 == 1 and c2 == 1 and c3 == 2:
                self.children = []
                self.colour = colour[2]
            else:
                return False
            return True
        return False

    def create_copy(self) -> Block:
        """Return a new Block that is a deep copy of this Block.

        Remember that a deep copy has new blocks (not aliases) at every level.
        """
        block = Block(self.position, self.size, self.colour,
                      self.level, self.max_depth)
        for child in self.children:
            block.children.append(child.create_copy())
        return block


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', '__future__', 'math',
            'settings'
        ],
        'max-attributes': 15,
        'max-args': 6
    })

    # This is a board consisting of only one block.
    b1 = Block((0, 0), 750, COLOUR_LIST[0], 0, 1)
    print("=== tiny board ===")
    print(b1)

    # Now let's make a random board.
    b2 = generate_board(3, 750)
    print("\n=== random board ===")
    print(b2)
