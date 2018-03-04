from tetris6_engine import TetrisBoard
import copy
import numpy as np
import time
from random import randint

class Break:
    def __init__(self, parent, board=None):
        self.parent = parent
        self.piece_queue = []
        if not board: self.board = TetrisBoard(piece_queue=self.piece_queue)
        else: self.board = board
        self.animate = True
        self.animate_delay = False
        self.animate_delay_value = .03
    def weed_out_dupes(self,boards):
        for board in boards: board.board_to_string()
        new_set = []
        unique_IDs = []
        new_set.append(boards[0])
        unique_IDs.append(new_set[0].blocks_string)
        for board in boards:
            if board.blocks_string not in unique_IDs:
                new_set.append(board)
                unique_IDs.append(board.blocks_string)
        return new_set
    def check_result(self,first_piece=False):
        debug = False
        if debug: self.board.board_print()
        if debug: print("first_piece: " + str(first_piece))
        if self.board.active_blocks[:,0:3].any(): 
            if debug: input("False")
            return False
        if self.board.active_blocks[:,7:].any(): 
            if debug: input("False0")
            return False
        if not self.board.move("down",dont_set=True,dont_break=True):
            if not first_piece:
                if self.board.break_rows() == 1: 
                    if debug: input("True1")
                    return True
                else: 
                    if debug: input("False1")
                    return False
            else:
                if self.board.break_rows() == 0: 
                    if debug: input("True2")
                    return True
                else: 
                    if debug: input("False2")
                    return False
    def one_piece_outcomes(self,starting_boards,first_piece=False):
        good_outcomes = []
        # bak0 = board key
        # bak1 = piece hold
        # bak2 = rotation
        # bak3 = 
        for board in starting_boards:
            # if first_piece: self.board.first_move = None
            # elif self.board.first_move == None: 
                # print("self.board.first_move: " + str(self.board.first_move))
                # self.board.first_move = np.copy(self.board.set_blocks)
                # print("self.board.first_move: " + str(self.board.first_move))
            self.board = copy.deepcopy(board)
            self.board_bak0 = copy.deepcopy(self.board)
            
            # use current piece or switch it
            for i in range(2): 
                self.board_bak1 = copy.deepcopy(self.board)
                
                # 4 rotations
                for i in range(4): 
                    self.board_bak2 = copy.deepcopy(self.board)
                    # vertical drops
                    while self.board.move("left"): # go all the way left
                        if self.animate:
                            self.parent.update_display()
                            if self.animate_delay: time.sleep(self.animate_delay_value)
                    finished_moving_right = False
                    while not finished_moving_right: # go right and drop
                        self.board_bak3 = copy.deepcopy(self.board)
                        if not self.board.active_blocks[:,:3].any() or not self.board.active_blocks[:,7:].any():
                            #
                            while self.board.move("down",dont_break=True,dont_set=True): 
                                if self.animate:
                                    self.parent.update_display()
                                    if self.animate_delay: time.sleep(self.animate_delay_value)
                            if self.check_result(first_piece=first_piece):
                                good_outcomes.append(copy.deepcopy(self.board))
                            #
                            self.board_bak4 = copy.deepcopy(self.board)
                            self.board = copy.deepcopy(self.board_bak4)
                            self.board_bak4 = copy.deepcopy(self.board)
                            self.board.rotate()
                            if self.animate:
                                self.parent.update_display()
                                if self.animate_delay: time.sleep(self.animate_delay_value)
                            if self.check_result(first_piece=first_piece):
                                good_outcomes.append(copy.deepcopy(self.board))
                            #
                            self.board = copy.deepcopy(self.board_bak4)
                            self.board.rotate(ccw="True")
                            if self.animate:
                                self.parent.update_display()
                                if self.animate_delay: time.sleep(self.animate_delay_value)
                            if self.check_result(first_piece=first_piece):
                                good_outcomes.append(copy.deepcopy(self.board))
                            #
                        if self.animate: self.parent.update_display()
                        self.board = copy.deepcopy(self.board_bak3)
                        finished_moving_right = not self.board.move("right")
                    self.board = copy.deepcopy(self.board_bak2)
                    self.board.rotate()
                self.board = copy.deepcopy(self.board_bak1)
                self.board.hold_piece()
            # try: self.board.board_print(self.board.first_move)
            # except: print("No first move")
        return good_outcomes
    def go_through_queue(self):
        if self.board.active_blocks.any():
            where_active_block = np.argwhere(self.board.active_blocks)[0]
            piece_type = self.board.active_blocks[where_active_block[0],where_active_block[1]]
            self.board.piece_queue = [piece_type] + self.board.piece_queue
            self.board.active_blocks[...] = 0
        next_piece = self.board.piece_queue.pop(0)
        self.board.get_next_piece(next_piece)
        board_set = [self.board]
        for i in range(len(self.board.piece_queue)):
            for board in board_set: board.move("down")
            if i == 1: # save the first move
                for board in board_set:
                    board.first_move = np.copy(board.set_blocks)
                    board.first_move[board.active_blocks < 0] = board.active_blocks[board.active_blocks < 0]
                    board.first_move[board.first_move < 0] = board.first_move[board.first_move < 0] * -1
            if i == 0: board_set = self.one_piece_outcomes(board_set,first_piece = True)
            else:  board_set = self.one_piece_outcomes(board_set,first_piece = False)
            if board_set:
                board_set = self.weed_out_dupes(board_set)
            else:
                print("found no solution")
                return []
            print("len(board_set): " + str(len(board_set)))
        first_move_boards_list = []
        first_move_boards_counted = []
        for board in board_set:
            first_move_boards_list.append(tuple(map(tuple, board.first_move)))
        for board in first_move_boards_list:
            if board not in [b for a,b in first_move_boards_counted]:
                first_move_boards_counted.append((first_move_boards_list.count(board),board))
        first_move_boards_counted.sort(key=lambda x: int(x[0]), reverse=True)
        for board in first_move_boards_counted:
            print(str(board[0]) + " occurrences of ")
            self.board.board_print(np.asarray(board[1]))
        return board_set

