from tetris_engine import TetrisBoard
import copy
import numpy as np
import time

class Solver:
    def __init__(self,piece_queue=[4,3,2,1]):
        self.piece_queue = piece_queue
        self.board = TetrisBoard(piece_queue=self.piece_queue)
        self.animate = False
        self.animate_delay = .02
    def analyze_piece(self):
        def empty_space_check(starting_place):
            space_under_block = [starting_place]
            proven_open = False
            def new_space(coords):
                global space_under_block
                global proven_open
                if coords not in space_under_block: space_under_block.append(coords)
                if row < board.shape[0] - 1:
                    if (board[row+1,column]==0) and (piece[row+1,column]==0) and ([row+1,column] not in space_under_block):
                        new_space([row+1,column])
                if column < board.shape[1] -1:
                    if (board[row,column+1]==0) and (piece[row,column+1]==0) and ([row,column+1] not in space_under_block):
                        if (column+1 > 2): proven_open = True
                        else: new_space([row,column+1])
                if column > 0:
                    if (board[row,column-1]==0) and (piece[row,column-1]==0) and ([row,column-1] not in space_under_block):
                        if (column-1 < 7): proven_open = True
                        else: new_space([row,column-1])
            return proven_open, space_under_block
        # def slot_can_be_filled(slot):
            # slot_side = "right"
            # if slot[0][1] < 5: slot_side = "left"
            # for piece in range(1,8): # list of numbers denoting type of piece
                # path = []
                # for rotation_index, _active_board in enumerate(self.piece_rotation_key[piece]):
                    # for i in range(rotation_index): path.append("rotate")
                    # active_board = np.copy(_active_board)
                    # for row in range(board.size[0]):
                                    # while not active_board[active_board.shape[0]-1,:].any(): 
                    # test_move = self.move(active_board,"down")
                    # if not np.logical_and(self.board < 0,test_move > 0).any():
                        # active_board = test_move
                        # path.append("down")
                    
        good_outcome = True
        # false if piece in middle area
        good_outcome = not self.board.active_blocks[:,3:7].any()
        where_empty_under_block = []
        # false if leaves any inaccessible blocks
        if good_outcome:
            where_block = np.argwhere(self.board.active_blocks)
            for location in where_block:
                if location[0] < self.board.rows - 1:
                    if (self.board.set_blocks[location[0]+1,location[1]]==0) and (self.board.active_blocks[location[0]+1,location[1]]==0):
                        where_empty_under_block = location[0]+1,location[1]
                        break
            if not where_empty_under_block:
                where_block = np.argwhere(self.board.set_blocks)
                for location in where_block:
                    if location[0] < self.board.rows - 1:
                        if (self.board.set_blocks[location[0]+1,location[1]]==0) and (self.board.active_blocks[location[0]+1,location[1]]==0):
                            where_empty_under_block = location[0]+1,location[1]
                            break
        if where_empty_under_block:
            good_outcome, where_empty_under_block = empty_space_check(where_empty_under_block)
        return good_outcome
    def weed_out_dupes(self,boards):
        for board in boards: boards[board].make_active_blocks_string()
        new_set = {}
        unique_IDs = []
        new_set[0] = boards[0]
        unique_IDs.append(new_set[0].active_blocks_string)
        for board in boards:
            if boards[board].active_blocks_string not in unique_IDs:
                new_set[len(new_set)] = boards[board]
                unique_IDs.append(boards[board].active_blocks_string)
        return new_set
    def one_piece_outcomes(self,starting_boards):
        good_outcomes = {}
        # bak0 = board key
        # bak1 = piece hold
        # bak2 = rotation
        # bak3 = 
        for board_key in starting_boards:
            self.board = copy.deepcopy(starting_boards[board_key])
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
                            self.board.board_print()
                            time.sleep(self.animate_delay)
                    finished_moving_right = False
                    while not finished_moving_right: # go right and drop
                        self.board_bak3 = copy.deepcopy(self.board)
                        if not self.board.active_blocks[:,3:7].any():
                            while self.board.move("down",dont_set=True): 
                                if self.animate:
                                    self.board.board_print()
                                    time.sleep(self.animate_delay)
                            if self.analyze_piece():
                                good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                            self.board_bak4 = copy.deepcopy(self.board)
                            self.board.rotate()
                            if self.analyze_piece():
                                good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                            self.board = copy.deepcopy(self.board_bak4)
                            self.board.rotate(ccw="True")
                            if self.analyze_piece():
                                good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                        if self.animate: self.board.board_print()
                        self.board = copy.deepcopy(self.board_bak3)
                        finished_moving_right = not self.board.move("right")
                    self.board = copy.deepcopy(self.board_bak2)
                    
                    # horizontal placement / drops
                    self.board = copy.deepcopy(self.board_bak0)
                    finished_going_down = False
                    while self.board.move("down",dont_set=True):
                        self.board_bak5 = copy.deepcopy(self.board)
                        while self.board.move("left"): 
                            if self.animate: 
                                self.board.board_print()
                                time.sleep(self.animate_delay)
                            if not self.board.active_blocks[:,3:7].any():
                                self.board_bak6 = copy.deepcopy(self.board)
                                while self.board.move("down",dont_set=True):
                                    if self.animate:
                                        self.board.board_print()
                                        time.sleep(self.animate_delay)
                                    if self.analyze_piece():
                                        good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                                    self.board_bak7 = copy.deepcopy(self.board)
                                    self.board.rotate()
                                    if self.animate:
                                        self.board.board_print()
                                        time.sleep(self.animate_delay)
                                    if self.analyze_piece():
                                        good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                                    self.board = copy.deepcopy(self.board_bak7)
                                    self.board.rotate(ccw="True")
                                    if self.animate:
                                        self.board.board_print()
                                        time.sleep(self.animate_delay)
                                    if self.analyze_piece():
                                        good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                                self.board = copy.deepcopy(self.board_bak6)
                        self.board = copy.deepcopy(self.board_bak5)
                        while self.board.move("right"): 
                            if self.animate:
                                self.board.board_print()
                                time.sleep(self.animate_delay)
                            if not self.board.active_blocks[:,3:7].any():
                                self.board_bak6 = copy.deepcopy(self.board)
                                while self.board.move("down",dont_set=True):
                                    if self.animate:
                                        self.board.board_print()
                                        time.sleep(self.animate_delay)
                                    if self.analyze_piece():
                                        good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                                    self.board_bak7 = copy.deepcopy(self.board)
                                    self.board.rotate()
                                    if self.animate:
                                        self.board.board_print()
                                        time.sleep(self.animate_delay)
                                    if self.analyze_piece():
                                        good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                                    self.board = copy.deepcopy(self.board_bak7)
                                    self.board.rotate(ccw="True")
                                    if self.animate:
                                        self.board.board_print()
                                        time.sleep(self.animate_delay)
                                    if self.analyze_piece():
                                        good_outcomes[len(good_outcomes)] = copy.deepcopy(self.board)
                                self.board = copy.deepcopy(self.board_bak6)
                        self.board = copy.deepcopy(self.board_bak5)
                    self.board = copy.deepcopy(self.board_bak2)
                    self.board.rotate()
                self.board = copy.deepcopy(self.board_bak1)
                self.board.hold_piece()
        print("len(good_outcomes): " + str(len(good_outcomes)))
        return good_outcomes
                
solver = Solver([7,2,4,6])
a=solver.one_piece_outcomes({0:solver.board})
a=solver.weed_out_dupes(a)
print("len(good_outcomes) after weeding out dupes: " + str(len(a)))
for board in a:
    a[board].board_print()
