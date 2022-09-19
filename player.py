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
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    lst = []
    goals = generate_goals(num_human + num_random + len(smart_players))
    for id_num1 in range(num_human):
        player_h = HumanPlayer(id_num1, goals[id_num1])
        lst.append(player_h)
    for id_num2 in range(num_random):
        player_r = RandomPlayer(id_num2 + num_human, goals[id_num2 + num_human])
        lst.append(player_r)
    smart_players.sort()
    for i in range(len(smart_players)):
        player_s = \
            SmartPlayer(i + num_human + num_random,
                        goals[i + num_human + num_random], smart_players[i])
        lst.append(player_s)
    return lst


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    x = block.position[0]
    y = block.position[1]
    if level == 0 and x <= location[0] < x + block.size \
            and y <= location[1] < y + block.size:
        return block
    elif level > 0 and x <= location[0] < x + block.size \
            and y <= location[1] < y + block.size and (not block.children):
        return block
    else:
        for child in block.children:
            result = _get_block(child, location, level - 1)
            if result is not None:
                return result
    return None


def _list_valid_moves(colour: Tuple[int, int, int], board: Block) -> \
        List[Tuple[str, Optional[int], Block]]:
    """ A helper function for RandomPlayer's make_move,
    which makes a random move on a given block
    """
    blocks = _list_all_blocks(board)
    moves = []
    for block in blocks:
        if len(block.children) != 0:
            moves.append(_create_move(ROTATE_COUNTER_CLOCKWISE, block))
            moves.append(_create_move(ROTATE_CLOCKWISE, block))
            moves.append(_create_move(SWAP_VERTICAL, block))
            moves.append(_create_move(SWAP_HORIZONTAL, block))
        if block.level == block.max_depth and block.colour != colour:
            moves.append(_create_move(PAINT, block))
        if block.level != block.max_depth and len(block.children) == 0:
            moves.append(_create_move(SMASH, block))
        copy = block.create_copy()
        if copy.combine():
            moves.append(_create_move(COMBINE, block))
    return moves


def _list_all_blocks(block: Block) -> List[Block]:
    """ Return a list of all list_blocks in block
    """
    # if len(block.children) == 0:
    #     return [block]
    list_blocks = [block]
    for child in block.children:
        list_blocks.append(child)
        list_blocks.extend(_list_all_blocks(child))
    return list_blocks


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """ A computer player that, as the name implies, chooses moves randomly.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        """ Initialize this RandomPlayer with the given <renderer>, <player_id>
        and <goal>."""
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove
        moves = _list_valid_moves(self.goal.colour, board)
        self._proceed = False
        if moves:
            move = random.choice(moves)
            return move
        else:
            return None


class SmartPlayer(Player):
    """a computer player that chooses moves more intelligently:
    It generates a set of random moves and, for each move, checks what its
    score would be if it were to make that move. Then it picks the one that
    yields the best score.
    """
    # === Private Attributes ===
    # _proceed:
    #   True when the player should make a move, False when the player should
    #   wait.
    # _difficulty:
    #   The number of valid moves in the block
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initialize this SmartPlayer with the given <renderer>, <player_id>,
        <goal> and <difficulty>."""
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def _num_moves(self, copy: Block, n: int) -> List:
        """ Return a list of n number of valid moves with given block copy.
        """
        list_moves = _list_valid_moves(self.goal.colour, copy)
        i = 0
        use_moves = []
        if len(list_moves) != 0:
            while len(use_moves) != n and len(use_moves) != len(list_moves):
                use_moves.append(list_moves[i])
                i += 1
        return use_moves

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        # find random n blocks(put into a list), check the first
        # valid move(put in a list, but if same block cant have same valid move,
        # use the copy to find the score,
        # put the scores in a list. Find the max score i. Use that i
        # to find the 'action' in the list of moves.
        if not self._proceed:
            return None
        self._proceed = False
        copy = board.create_copy()
        blocks_moves = self._num_moves(board, self._difficulty)
        score_lst = []
        max_ = 0
        use_moves = self._num_moves(copy, self._difficulty)
        use_moves_len = len(use_moves)
        for i in range(use_moves_len):
            use_moves = self._num_moves(copy, self._difficulty)
            move = use_moves[i]
            block = use_moves[i][2]
            if move == _create_move(SMASH, block):
                block.smash()
                score_lst.append(self.goal.score(copy))
            if move == _create_move(COMBINE, block):
                block.combine()
                score_lst.append(self.goal.score(copy))
            if move == _create_move(PAINT, block):
                block.paint(self.goal.colour)
                score_lst.append(self.goal.score(copy))
            if move == _create_move(ROTATE_CLOCKWISE, block):
                block.rotate(1)
                score_lst.append(self.goal.score(copy))
            if move == _create_move(ROTATE_COUNTER_CLOCKWISE, block):
                block.rotate(3)
                score_lst.append(self.goal.score(copy))
            if move == _create_move(SWAP_VERTICAL, block):
                block.swap(1)
                score_lst.append(self.goal.score(copy))
            if move == _create_move(SWAP_HORIZONTAL, block):
                block.swap(0)
                score_lst.append(self.goal.score(copy))
            copy = board.create_copy()
        index_best = 0
        if len(score_lst) != 0:
            max_ = max(score_lst)
            index_best = score_lst.index(max_)
        if max_ == 0 and blocks_moves[-1][2] is not None:
            return _create_move(PASS, blocks_moves[-1][2])
        else:
            return blocks_moves[index_best]


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
