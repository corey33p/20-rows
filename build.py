from tetris6_engine import TetrisBoard
import copy
import numpy as np
import time
from random import randint

class Build:
    def __init__(self,parent,board=None):
        self.piece_queue=[randint(1,7),randint(1,7),randint(1,7),randint(1,7)]
        self.parent = parent
        if not board: self.board = TetrisBoard(piece_queue=self.piece_queue,
                                                    auto_fill_queue=False)
        else: self.board = board
        self.animate = True
        self.animate_delay = False
        self.animate_delay_value = .04
    def analyze_piece(self,set_blocks,active_blocks):
        def empty_space_check(place,board):
            on_left = place[1] < board.shape[1] // 2
            if on_left:
                height_limit = min([y for y,x in np.argwhere(board[:,:board.shape[1]//2])])
            else:
                height_limit = min([y for y,x in np.argwhere(board[:,board.shape[1]//2:])])
            def adjacent_places(place,height_limit=0):
                middle_columns = (3,4,5,6)
                column = place[1]
                row = place[0]
                adj_places = []
                open_up = False
                open_side = False
                side_opening_set = set()
                if column > 0:
                    if column - 1 not in middle_columns:
                        adj_places.append((row,column-1))
                    else:
                        open_side = True
                        # print("place: " + str(place))
                        side_opening_set.add(place)
                if column < board.shape[1]-1:
                    if column + 1 not in middle_columns:
                        adj_places.append((row,column+1))
                    else:
                        open_side = True
                        # print("place: " + str(place))
                        side_opening_set.add(place)
                if row > 0:
                    if row-1 >= height_limit:
                        adj_places.append((row-1,column))
                    else:
                        # print("OPEN")
                        open_up = True
                if row < board.shape[0]-1:
                    if row+1 > height_limit:
                        adj_places.append((row+1,column))
                    else:
                        # print("OPEN")
                        open_up = True
                return adj_places, open_up, open_side, side_opening_set
            
            new_place_added = True
            open_area = [place]
            open_up = False
            open_side = False
            side_opening_set = set()
            
            while new_place_added:
                starting_len = len(open_area)
                for coords in tuple(open_area):
                    found_adjacent_places = adjacent_places(coords,height_limit=height_limit)
                    open_up = found_adjacent_places[1] or open_up
                    open_side=found_adjacent_places[2] or open_side
                    side_opening_set = side_opening_set|found_adjacent_places[3]
                    for adjacent_place_check in found_adjacent_places[0]:
                        if board[adjacent_place_check] == 0 and adjacent_place_check not in open_area:
                            # print("---\nadjacent_place_check: " + str(adjacent_place_check))
                            # print("found_adjacent_places[0]: " + str(found_adjacent_places[0]))
                            # print("open_area: " + str(open_area)+"\n---")
                            open_area.append(adjacent_place_check)
                if len(open_area) == starting_len: new_place_added = False
            side_opening_size = len(side_opening_set)
            return open_area, open_up, open_side, height_limit, side_opening_size
        
        good_outcome = True
        # false if piece in middle area
        good_outcome = not active_blocks[:,3:7].any()
        where_empty_under_block = []
        
        full_board = np.copy(set_blocks)
        full_board[active_blocks != 0] = active_blocks[active_blocks != 0]
        
        # false if leaves any inaccessible blocks
        if good_outcome:
            where_block = np.argwhere(full_board)
            total_open_area = []
            for location in where_block:
                if location[0] < set_blocks.shape[0] - 1:
                    if (full_board[location[0]+1,location[1]]==0):
                        where_empty_under_block = location[0]+1,location[1]
                        if where_empty_under_block not in total_open_area:
                            # print("where_empty_under_block: " + str(where_empty_under_block))
                            open_area, open_up, open_side, height_limit, side_opening_size = empty_space_check(where_empty_under_block,full_board)
                            total_open_area = total_open_area + open_area
                            # not good if space is inaccessible
                            if not (open_up or open_side): good_outcome = False
                            if (not open_up) and (open_side):
                                # make sure side opening can be filled
                                if not ((len(open_area) % 4 == 0) and (side_opening_size > 1)): good_outcome = False
                            if open_up and (not open_side):
                                for spot in open_area:
                                    if full_board[height_limit:spot[0],spot[1]].any(): good_outcome = False
        return good_outcome
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
    def one_piece_outcomes(self,starting_boards):
        good_outcomes = []
        # bak0 = board key
        # bak1 = piece hold
        # bak2 = rotation
        # bak3 = 
        for board in starting_boards:
            self.board = copy.deepcopy(board)
            board_bak0 = copy.deepcopy(self.board)
            
            # use current piece or switch it
            for i in range(2): 
                board_bak1 = copy.deepcopy(self.board)
                
                # 4 rotations
                for j in range(4): 
                    board_bak2 = copy.deepcopy(self.board)
                    # vertical drops
                    while self.board.move("left"): pass# go all the way left
                    if self.animate:
                        self.parent.update_display()
                        if self.animate_delay: time.sleep(self.animate_delay_value)
                    finished_moving_right = False
                    while not finished_moving_right: # go right and drop
                        board_bak3 = copy.deepcopy(self.board)
                        if not self.board.active_blocks[:,3:7].any():
                            while self.board.move("down",dont_set=True): pass
                            if self.animate:
                                self.parent.update_display()
                                if self.animate_delay: time.sleep(self.animate_delay_value)
                            if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                good_outcomes.append(copy.deepcopy(self.board))
                            board_bak4 = copy.deepcopy(self.board)
                            self.board.rotate()
                            while self.board.move("down",dont_set=True): pass
                            if self.animate:
                                self.parent.update_display()
                                if self.animate_delay: time.sleep(self.animate_delay_value)
                            if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                good_outcomes.append(copy.deepcopy(self.board))
                            self.board = copy.deepcopy(board_bak4)
                            self.board.rotate(ccw="True")
                            while self.board.move("down",dont_set=True): pass
                            if self.animate:
                                self.parent.update_display()
                                if self.animate_delay: time.sleep(self.animate_delay_value)
                            if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                good_outcomes.append(copy.deepcopy(self.board))
                        if self.animate: 
                            self.parent.update_display()
                        self.board = copy.deepcopy(board_bak3)
                        finished_moving_right = not self.board.move("right")
                    self.board = copy.deepcopy(board_bak2)
                    
                    # horizontal placement / drops
                    # self.board = copy.deepcopy(board_bak1)
                    finished_going_down = False
                    while self.board.move("down",dont_set=True):
                        board_bak5 = copy.deepcopy(self.board)
                        set_blocks_rows = set(np.argwhere(self.board.set_blocks)[:,0])
                        active_blocks_rows = set(np.argwhere(self.board.active_blocks)[:,0])
                        if set_blocks_rows.intersection(active_blocks_rows):
                            while self.board.move("left"): 
                                if self.animate: 
                                    self.parent.update_display()
                                    if self.animate_delay: time.sleep(self.animate_delay_value)
                                if not self.board.active_blocks[:,3:7].any():
                                    board_bak6 = copy.deepcopy(self.board)
                                    while self.board.move("down",dont_set=True): pass
                                    if self.animate:
                                        self.parent.update_display()
                                        if self.animate_delay: time.sleep(self.animate_delay_value)
                                    if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                        good_outcomes.append(copy.deepcopy(self.board))
                                    board_bak7 = copy.deepcopy(self.board)
                                    self.board.rotate()
                                    while self.board.move("down",dont_set=True): pass
                                    if self.animate:
                                        self.parent.update_display()
                                        if self.animate_delay: time.sleep(self.animate_delay_value)
                                    if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                        good_outcomes.append(copy.deepcopy(self.board))
                                    self.board = copy.deepcopy(board_bak7)
                                    self.board.rotate(ccw="True")
                                    while self.board.move("down",dont_set=True): pass
                                    if self.animate:
                                        self.parent.update_display()
                                        if self.animate_delay: time.sleep(self.animate_delay_value)
                                    if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                        good_outcomes.append(copy.deepcopy(self.board))
                                    self.board = copy.deepcopy(board_bak6)
                            self.board = copy.deepcopy(board_bak5)
                            while self.board.move("right"):
                                if self.animate:
                                    self.parent.update_display()
                                    if self.animate_delay: time.sleep(self.animate_delay_value)
                                if not self.board.active_blocks[:,3:7].any():
                                    board_bak6 = copy.deepcopy(self.board)
                                    while self.board.move("down",dont_set=True): pass
                                    if self.animate:
                                        self.parent.update_display()
                                        if self.animate_delay: time.sleep(self.animate_delay_value)
                                    if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                        good_outcomes.append(copy.deepcopy(self.board))
                                    board_bak7 = copy.deepcopy(self.board)
                                    self.board.rotate()
                                    while self.board.move("down",dont_set=True): pass
                                    if self.animate:
                                        self.parent.update_display()
                                        if self.animate_delay: time.sleep(self.animate_delay_value)
                                    if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                        good_outcomes.append(copy.deepcopy(self.board))
                                    self.board = copy.deepcopy(board_bak7)
                                    self.board.rotate(ccw="True")
                                    while self.board.move("down",dont_set=True): pass
                                    if self.animate:
                                        self.parent.update_display()
                                        if self.animate_delay: time.sleep(self.animate_delay_value)
                                    if self.analyze_piece(self.board.set_blocks,self.board.active_blocks):
                                        good_outcomes.append(copy.deepcopy(self.board))
                                    self.board = copy.deepcopy(board_bak6)
                        self.board = copy.deepcopy(board_bak5)
                    self.board = copy.deepcopy(board_bak2)
                    self.board.rotate()
                self.board = copy.deepcopy(board_bak1)
                self.board.hold_piece()
                good_outcomes.append(copy.deepcopy(self.board))
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
            board_set = self.one_piece_outcomes(board_set)
            if board_set:
                board_set = self.weed_out_dupes(board_set)
            else:
                print("found no solution")
                return []
            print("len(good_outcomes): " + str(len(board_set)))
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
    def get_favorite(self,board_set):
        best_flatness = 10
        for board in board_set: 
            board.get_flatness_rating()
            if board.flatness < best_flatness:
                self.parent.update_display()
                print("board.flatness: " + str(board.flatness))
                best_flatness = board.flatness
                best_board = copy.deepcopy(board)
        return best_board


# solver = Build([randint(1,7),randint(1,7),randint(1,7),randint(1,7)])
# # a=solver.one_piece_outcomes([solver.board])
# # a=solver.weed_out_dupes(a)
# board_set = solver.go_through_queue()
# # if len(board_set) < 100:
    # # for board in board_set:
        # # board.refresh_screen()
# favorite = solver.get_favorite(board_set)
# favorite.refresh_screen()