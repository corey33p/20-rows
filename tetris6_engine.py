import numpy as np
from random import randint
import tkinter as tk
from tkinter import mainloop, Tk
import statistics as stats

class TetrisBoard:
    def __init__(self,
                 rows=22,
                 columns=10,
                 min_queue_length=4,
                 piece_queue=[],
                 auto_fill_queue=True):
        self.rows = rows
        self.columns = columns
        self.set_blocks = np.zeros((rows,columns),np.int32)
        self.active_blocks = np.zeros((rows,columns),np.int32)
        self.active_blocks_window = np.zeros((4),np.int32)
        self.current_piece_number = 0
        self.rotation_count = 0
        self.rows_cleared = 0
        self.pieces_made = 0
        self.game_lost = False
        self.flow_tracking = False
        self.save_history = True
        self.history = []
        self.history_depth = 5
        self.moves_with_piece = 0
        self.row_clear_scores=(10,25,60,150)
        self.score = 0
        for i in range(self.history_depth):
            self.history.append(np.zeros((self.rows,self.columns),np.int32))
        self.next_piece_template_maker()
        self.piece_queue = piece_queue
        self.min_queue_length = min_queue_length
        self.auto_fill_queue = auto_fill_queue
        if self.auto_fill_queue:
            while len(self.piece_queue) < self.min_queue_length: self.piece_queue.append(randint(1,7))
        self.auto_get_next_piece = True
        self.held_piece = 0
        self.hold_lock = False
        # get first piece
        try: next_piece = self.piece_queue.pop(0)
        except: 
            print("got random piece")
            next_piece = randint(1,7)
        self.get_next_piece(next_piece)
    def hold_piece(self):
        if not self.active_blocks.any() or self.hold_lock or not self.piece_queue: return
        where = np.argwhere(self.active_blocks)[0]
        previously_held_piece = False
        if self.held_piece: 
            switch_with = self.held_piece
            previously_held_piece = True
        self.held_piece = self.active_blocks[where[0],where[1]]
        self.active_blocks[...] = 0
        if previously_held_piece: 
            self.get_next_piece(switch_with)
        else: 
            try: next_piece = self.piece_queue.pop(0)
            except: 
                print("got random piece")
                next_piece = randint(1,7)
            self.get_next_piece(next_piece)
        self.hold_lock = True
    def get_flatness_rating(self):
        # computes stdev of column height for columns 0,1,2,7,8,9
        column_heights = []
        excluded = (3,4,5,6)
        for column in range(self.columns):
            if column not in excluded:
                if self.active_blocks[:,column].any(): a = np.argwhere(self.active_blocks[:,column]).min()
                else: a = self.rows
                if self.set_blocks[:,column].any(): b = np.argwhere(self.set_blocks[:,column]).min()
                else: b = self.rows
                column_heights.append(float(min(a,b)))
        if column_heights: self.flatness = stats.pstdev(column_heights)
        else: self.flatness = "NA"
        return
    def edit_queue(self,new_queue,active_piece=0,hold=-1):
        new_queue = list(new_queue)
        for i, piece in enumerate(new_queue):
            if piece not in (0,1,2,3,4,5,6,7):
                new_queue[i] = randint(1,7)
        self.queue = new_queue
        if active_piece in (1,2,3,4,5,6,7):
            self.active_blocks[...] = 0
            self.get_next_piece(active_piece)
        if hold in (0,1,2,3,4,5,6,7): self.held_piece = hold
    def board_snapshot(self):
        answer = np.copy(self.set_blocks)
        answer[self.active_blocks != 0] = self.active_blocks[self.active_blocks != 0]
        return answer
    def board_to_string(self):
        self.blocks_string = ""
        for row in range(self.rows):
            for column in range(self.columns):
                if self.active_blocks[row,column] != 0:
                    self.blocks_string += str(self.active_blocks[row,column])
                elif self.set_blocks[row,column] != 0:
                    self.blocks_string += str(abs(self.active_blocks[row,column]))
                else:
                    self.blocks_string += "0"
    def string_to_board(self,the_string):
        return np.asarray(the_string).reshape(self.rows,self.columns).astype(np.int32)
    def next_piece_template_maker(self):
        if self.flow_tracking: print("---> template maker")
        self.next_piece_template = np.zeros((8,self.rows,self.columns),dtype=np.int32)
        self.starting_window = np.zeros((8,4),dtype=np.int32)
        for i in range(1,8): # 7 pieces
            if i == 1: # L piece
                self.next_piece_template[i,1,self.next_piece_template.shape[0]//2-1:self.next_piece_template.shape[0]//2+2]=1
                self.next_piece_template[i,0,self.next_piece_template.shape[0]//2+1]=1
                self.starting_window[1,0] = 0
                self.starting_window[1,1] = 3
                self.starting_window[1,2] = self.next_piece_template.shape[0]//2-1
                self.starting_window[1,3] = self.next_piece_template.shape[0]//2+2
            elif i == 2: # J piece
                self.next_piece_template[i,1,self.next_piece_template.shape[0]//2-1:self.next_piece_template.shape[0]//2+2]=2
                self.next_piece_template[i,0,self.next_piece_template.shape[0]//2-1]=2
                self.starting_window[2,0] = 0
                self.starting_window[2,1] = 3
                self.starting_window[2,2] = self.next_piece_template.shape[0]//2-1
                self.starting_window[2,3] = self.next_piece_template.shape[0]//2+2
            elif i == 3: # S piece
                self.next_piece_template[i,0,self.next_piece_template.shape[0]//2:self.next_piece_template.shape[0]//2+2]=3
                self.next_piece_template[i,1,self.next_piece_template.shape[0]//2-1:self.next_piece_template.shape[0]//2+1]=3
                self.starting_window[3,0] = 0
                self.starting_window[3,1] = 3
                self.starting_window[3,2] = self.next_piece_template.shape[0]//2-1
                self.starting_window[3,3] = self.next_piece_template.shape[0]//2+2
            elif i == 4: # Z piece
                self.next_piece_template[i,0,self.next_piece_template.shape[0]//2-1:self.next_piece_template.shape[0]//2+1]=4
                self.next_piece_template[i,1,self.next_piece_template.shape[0]//2:self.next_piece_template.shape[0]//2+2]=4
                self.starting_window[4,0] = 0
                self.starting_window[4,1] = 3
                self.starting_window[4,2] = self.next_piece_template.shape[0]//2-1
                self.starting_window[4,3] = self.next_piece_template.shape[0]//2+2
            elif i == 5: # T piece
                self.next_piece_template[i,0,self.next_piece_template.shape[0]//2]=5
                self.next_piece_template[i,1,self.next_piece_template.shape[0]//2-1:self.next_piece_template.shape[0]//2+2]=5
                self.starting_window[5,0] = 0
                self.starting_window[5,1] = 3
                self.starting_window[5,2] = self.next_piece_template.shape[0]//2-1
                self.starting_window[5,3] = self.next_piece_template.shape[0]//2+2
            elif i == 6: # line piece
                self.next_piece_template[i,1,self.next_piece_template.shape[0]//2-1:self.next_piece_template.shape[0]//2+3]=6
                self.starting_window[6,0] = 0
                self.starting_window[6,1] = 4
                self.starting_window[6,2] = self.next_piece_template.shape[0]//2-1
                self.starting_window[6,3] = self.next_piece_template.shape[0]//2+3
            elif i == 7: # square piece
                self.next_piece_template[i,0,self.next_piece_template.shape[0]//2:self.next_piece_template.shape[0]//2+2]=7
                self.next_piece_template[i,1,self.next_piece_template.shape[0]//2:self.next_piece_template.shape[0]//2+2]=7
                self.starting_window[7,0] = 0
                self.starting_window[7,1] = 2
                self.starting_window[7,2] = self.next_piece_template.shape[0]//2
                self.starting_window[7,3] = self.next_piece_template.shape[0]//2+2
        self.rotate_template = {}
        for i in range(1,8): # 7 pieces
            window = (self.starting_window[i,0],
                    self.starting_window[i,1],
                    self.starting_window[i,2],
                    self.starting_window[i,3])
            self.rotate_template[i]=np.zeros((4,window[1]-window[0],window[3]-window[2]),dtype=np.int32)
            #
            self.rotate_template[i][0,...] = np.copy(self.next_piece_template[i,window[0]:window[1],window[2]:window[3]])
            self.rotate_template[i][1,...] = np.rot90(self.rotate_template[i][0,...],k=3)
            self.rotate_template[i][2,...] = np.rot90(self.rotate_template[i][1,...],k=3)
            self.rotate_template[i][3,...] = np.rot90(self.rotate_template[i][2,...],k=3)
    def get_next_piece(self, piece_type=randint(1,7)):
        if self.flow_tracking: print("---> get next piece, piece = " + str(piece_type))
        # 1 - J piece
        # 2 - L piece
        # 3 - S piece
        # 4 - Z piece
        # 5 - T piece
        # 6 - line piece
        # 7 - square piece
        
        # The intention is that whenever get_next_piece is called, there will be a 
        # piece popped from the queue immediately before that. So here the queue is 
        # refilled, and the piece that was popped before, passed in as piece_type,
        # is now added to the game.
        self.current_piece = piece_type
        if self.auto_fill_queue:
            while len(self.piece_queue) < self.min_queue_length: self.piece_queue.append(randint(1,7))
        self.hold_lock = False
        
        # if piece cannot be inserted, return False
        if np.logical_and(self.set_blocks,self.next_piece_template[piece_type]).any(): 
            return False
        
        # insert the piece
        self.active_blocks = np.copy(self.next_piece_template[piece_type])
        self.active_blocks_window = np.copy(self.starting_window[piece_type,:])
        self.current_piece_number = piece_type
        self.rotation_count = 0
        
        self.moves_with_piece = 0
        
        return True
    def move(self,direction="down",step=1,dont_set=False,dont_break=False):
        if self.flow_tracking: print("---> move, direction = " + str(direction) + ", step = " + str(step))
        if not self.active_blocks.any(): return False
        test_move = np.copy(self.active_blocks)
        move_successful = True
        if step == 0: return move_successful
        if direction == "down":
            if self.active_blocks[self.rows-1,:].any(): 
                move_successful = False
            else:
                empty_rows = np.zeros((step,self.active_blocks.shape[1]),np.int32)
                test_move = np.concatenate((empty_rows,self.active_blocks[:self.active_blocks.shape[0]-step,:]),0)
                if np.logical_and(test_move,self.set_blocks).any(): move_successful = False
                else:
                    self.active_blocks = test_move
                    self.active_blocks_window[0:2]+=1
            if not dont_set and not move_successful:
                self.active_blocks = self.active_blocks * -1
                self.set_blocks[self.active_blocks != 0] = self.active_blocks[self.active_blocks != 0]
                self.active_blocks[...] = 0
                if not dont_break: self.break_rows()
                try: next_piece = self.piece_queue.pop(0)
                except: 
                    next_piece = randint(1,7)
                # if not self.auto_fill_queue and not self.piece_queue: self.game_lost = True
                if self.auto_get_next_piece: 
                    if not self.get_next_piece(next_piece): self.game_lost = True
        elif direction == "left":
            if self.active_blocks[:,0].any(): move_successful = False
            else:
                empty_columns = np.zeros((self.active_blocks.shape[0],step),np.int32)
                test_move = np.concatenate((self.active_blocks[:,step:],empty_columns),1)
                if np.logical_and(test_move,self.set_blocks).any(): move_successful = False
                else:
                    # self.active_blocks[...] = 0
                    self.active_blocks = test_move
                    self.active_blocks_window[2:4]-=1
        elif direction == "up": # why? you never know
            if self.active_blocks[0,:].any(): move_successful = False
            else:
                empty_rows = np.zeros((step,self.active_blocks.shape[1]),np.int32)
                test_move = np.concatenate((self.active_blocks[step:,:],empty_rows),0)
                if np.logical_and(test_move,self.set_blocks).any(): move_successful = False
                else:
                    # self.active_blocks[...] = 0
                    self.active_blocks = test_move
                    self.active_blocks_window[0:2]-=1
        elif direction == "right":
            if self.active_blocks[:,self.columns-1].any(): move_successful = False
            else:
                empty_columns = np.zeros((self.active_blocks.shape[0],step),np.int32)
                test_move = np.concatenate((empty_columns,self.active_blocks[:,:self.active_blocks.shape[1]-step]),1)
                if np.logical_and(test_move,self.set_blocks).any(): move_successful = False
                else:
                    # self.active_blocks[...] = 0
                    self.active_blocks = test_move
                    self.active_blocks_window[2:4]+=1
        if self.save_history:
            self.history.pop(0)
            full_board = self.board_snapshot()
            self.history.append(full_board)
        if move_successful: self.moves_with_piece += 1
        return move_successful
    def break_rows(self):
        if self.flow_tracking: print("---> break rows")
        cleared_rows_this_time = 0
        # all blocks become "True" which computes as 1
        simplified_board = self.board_snapshot()
        simplified_board = simplified_board != False
        
        # get row sums
        sums = simplified_board.sum(1).reshape(self.rows)
        
        # make false where not full row
        sums = (sums == self.columns)
        
        rows_cleared = 0
        if sums.any():
            empty_row = np.zeros((1,self.columns),np.int32)
            for row in range(sums.shape[0]):
                if sums[row]:
                    empty_row = np.zeros((1,self.columns),np.int32)
                    self.set_blocks[:row+1,:] = np.concatenate((empty_row,self.set_blocks[:row,:]),0)
                    self.rows_cleared += 1
                    cleared_rows_this_time += 1
            self.score += self.row_clear_scores[cleared_rows_this_time - 1]
        
        return cleared_rows_this_time
    def rotate(self, ccw=False):
        if self.flow_tracking: print("---> rotate, ccw = " + str(ccw))
        if not self.active_blocks.any(): return
        
        active_blocks_backup = np.copy(self.active_blocks)
        
        adjust = [0,0]
        while (self.active_blocks_window[0] < 0):
            self.active_blocks_window[0:2] += 1
            adjust[0] += 1
        while (self.active_blocks_window[2] < 0):
            self.active_blocks_window[2:4] += 1
            adjust[1] += 1
        while (self.active_blocks_window[1] > self.rows):
            self.active_blocks_window[0:2] -= 1
            adjust[0] -= 1
        while (self.active_blocks_window[3] > self.columns):
            self.active_blocks_window[2:4] -= 1
            adjust[1] -= 1
        if ccw:
            self.rotation_count -= 1
        else:
            self.rotation_count += 1
        self.active_blocks[...]=0
        self.active_blocks[self.active_blocks_window[0]:self.active_blocks_window[1],self.active_blocks_window[2]:self.active_blocks_window[3]] = np.copy(self.rotate_template[self.current_piece_number][self.rotation_count % 4,...])
        while (adjust[1] > 0) and self.move("left"):
            adjust[1] -= 1
            self.active_blocks_window[0:2] -= 1
        while (adjust[1] < 0) and self.move("right"):
            adjust[1] += 1
            self.active_blocks_window[0:2] += 1
        while (adjust[0] > 0) and self.move("up"):
            adjust[0] -= 1
            self.active_blocks_window[2:4] -= 1
        while (adjust[0] < 0) and self.move("down",dont_set = True):
            adjust[0] += 1
            self.active_blocks_window[2:4] += 1
        
        # if the new piece does not intersect with any existing pieces, set it in
        successfully_rotated = not np.logical_and(self.active_blocks,self.set_blocks).any()
        if successfully_rotated: 
            self.moves_with_piece += 1
            if self.save_history:
                self.history.pop(0)
                full_board = self.board_snapshot()
                self.history.append(full_board)
            return True
    
        # try moving left
        self.move("left",1)
        self.active_blocks_window[0:2] -= 1
        successfully_rotated = not np.logical_and(self.active_blocks,self.set_blocks).any()
        if successfully_rotated: 
            self.moves_with_piece += 1
            if self.save_history:
                self.history.pop(0)
                full_board = self.board_snapshot()
                self.history.append(full_board)
            return True
        
        # try moving right
        self.move("right",2)
        self.active_blocks_window[0:2] += 2
        successfully_rotated = not np.logical_and(self.active_blocks,self.set_blocks).any()
        if successfully_rotated and (self.active_blocks > 0).sum() % 4 == 0: 
            self.moves_with_piece += 1
            if self.save_history:
                self.history.pop(0)
                full_board = self.board_snapshot()
                self.history.append(full_board)
            return True
        else: 
            self.active_blocks = active_blocks_backup
            if ccw:
                self.rotation_count += 1
            else:
                self.rotation_count -= 1
    def board_print(self, ar=None, print_now=True):
        if self.flow_tracking: print("---> board print")
        if ar is None:
            ar = self.board_snapshot()
        line_list = []
        for i in range(ar.shape[0]+2): line_list.append("")
        for row in range(ar.shape[0]):
            if row == 0: line_list[0] += '  ____________________'
            line_list[row+1] += " |"
            for column in range(ar.shape[1]):
                if ar[row,column] < 0:
                    line_list[row+1] +=  "██"
                elif ar[row,column] > 0:
                    line_list[row+1] +=  "▒▒"
                else: line_list[row+1] +=  "__"
            line_list[row+1] += "| "
        if print_now:
            for line in line_list: print(line)
        else: return line_list