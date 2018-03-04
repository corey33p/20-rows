import tkinter as tk
from tkinter import Canvas,Tk,ttk,Label,Entry,Button,mainloop,Text,Frame,LEFT,Checkbutton,IntVar
from tetris6_display import TetrisDisplay
from build import Build
from brea import Break
import multiprocessing
import threading
import win32gui
import time
import numpy as np
from random import randint

class Main:
    def __init__(self):
        self.master = Tk()
        self.master.wm_title("20 Combo Challenge")
        self.master.minsize(width=100,height=100)
        self.master.maxsize(width=1600,height=950)
        self.master.geometry('1048x863+860+80')
        main_font = ("Courier", 22, "bold")
        self.set_piece_marker = False
        self.on_builder = True
        board_frame = ttk.Frame(self.master)
        board_frame.grid(row=0,column=1,rowspan=20)
        self.display = TetrisDisplay(self.master, board_frame)
        self.handler = Build(self)
        self.make_canvas_interactive()
        self.board_set_index = 0
        self.board_set = [self.handler.board]
        self.update_display()
        self.history_position = self.handler.board.history_depth - 1
        #
        self.hold_entry = Entry(self.master,justify=LEFT,width=6)
        self.hold_entry.config(font=main_font)
        self.hold_entry.grid(row=2,column=0)
        #
        def add_blocks():
            self.last_block_altered = None
            if self.remove_blocks_check.get() == 1:
                self.remove_blocks_check.set(0)
                self.add_blocks_check.set(1)
        self.add_blocks_check = IntVar()
        self.add_blocks_check.set(0)
        self.add_blocks_button = Checkbutton(self.master, 
                                             text="Add", 
                                             variable=self.add_blocks_check, 
                                             command=add_blocks)
        self.add_blocks_button.config(font=main_font)
        self.add_blocks_button.grid(row=3, column=0, sticky='w')
        #
        def remove_blocks():
            self.last_block_altered = None
            if self.add_blocks_check.get() == 1:
                self.add_blocks_check.set(0)
                self.remove_blocks_check.set(1)
        self.remove_blocks_check = IntVar()
        self.remove_blocks_check.set(0)
        self.remove_blocks_button = Checkbutton(self.master, 
                                                text="Rem", 
                                                variable=self.remove_blocks_check,
                                                command=remove_blocks)
        self.remove_blocks_button.config(font=main_font)
        self.remove_blocks_button.grid(row=4, column=0, sticky='w')
        #
        def clear_blocks():
            self.handler.board.set_blocks[...] = 0
            self.update_display()
        self.clear_blocks_button = Button(self.master,text="Clear\nBoard",command=clear_blocks)
        self.clear_blocks_button.config(font=main_font)
        self.clear_blocks_button.grid(row=10,column=0)
        ########
        self.active_piece_entry = Entry(self.master,justify=LEFT,width=6)
        self.active_piece_entry.config(font=main_font)
        self.active_piece_entry.grid(row=0,column=2)
        #
        ttk.Separator(self.master, orient="horizontal").grid(row=1, column=2, sticky="ew")
        #
        self.queue1_entry = Entry(self.master,justify=LEFT,width=6)
        self.queue1_entry.config(font=main_font)
        self.queue1_entry.grid(row=2,column=2)
        #
        self.queue2_entry = Entry(self.master,justify=LEFT,width=6)
        self.queue2_entry.config(font=main_font)
        self.queue2_entry.grid(row=3,column=2)
        #
        self.queue3_entry = Entry(self.master,justify=LEFT,width=6)
        self.queue3_entry.config(font=main_font)
        self.queue3_entry.grid(row=4,column=2)
        #
        self.queue4_entry = Entry(self.master,justify=LEFT,width=6)
        self.queue4_entry.config(font=main_font)
        self.queue4_entry.grid(row=5,column=2)
        #
        self.update_button = Button(self.master,text="Update",command=self.update_pieces)
        self.update_button.config(font=main_font)
        self.update_button.grid(row=6,column=2)
        #
        def build_thread():
            build_thread = multiprocessing.Process(target=self.build_it())
            build_thread.daemon = True
            build_thread.start()
        self.build_button = Button(self.master,text="Build",command=build_thread)
        self.build_button.config(font=main_font)
        self.build_button.grid(row=7,column=2)
        #
        def break_thread():
            break_thread = multiprocessing.Process(target=self.break_it())
            break_thread.daemon = True
            break_thread.start()
        self.break_button = Button(self.master,text="Break",command=break_thread)
        self.break_button.config(font=main_font)
        self.break_button.grid(row=8,column=2)
        #
        def clear_piece():
            self.handler.board.active_blocks[...] = 0
            self.update_display()
        self.clear_piece_button = Button(self.master,text="Clear\nPiece",command=clear_piece)
        self.clear_piece_button.config(font=main_font)
        self.clear_piece_button.grid(row=9,column=2)
        #
        def make_columns():
            random_fill = np.random.randint(1,7,self.handler.board.set_blocks.shape)
            self.handler.board.set_blocks[2:,:3]=random_fill[2:,:3]
            self.handler.board.set_blocks[2:,7:]=random_fill[2:,7:]
            self.update_display()
        self.make_columns_button = Button(self.master,text="Make\nColumns",command=make_columns)
        self.make_columns_button.config(font=main_font)
        self.make_columns_button.grid(row=10,column=2)
        #
        self.index_entry = Entry(self.master,justify=LEFT,width=6)
        self.index_entry.config(font=main_font,justify="center")
        self.index_entry.grid(row=11,column=2)
        self.index_entry.insert("end","0/0")
        self.index_entry.config(state="disabled")
        #
        history_buttons_frame = ttk.Frame(self.master)
        history_buttons_frame.grid(row=12,column=2)
        def history_back():
            if self.board_set_index > 0:
                self.board_set_index -= 1
                self.handler.board = self.board_set[self.board_set_index]
                self.update_index_entry()
                self.update_display()
        def history_forward():
            if self.board_set_index < len(self.board_set)-1:
                self.board_set_index += 1
                self.handler.board = self.board_set[self.board_set_index]
                self.update_index_entry()
                self.update_display()
        self.previous_button = Button(history_buttons_frame,text="<--",command=history_back)
        self.previous_button.config(font=main_font)
        self.previous_button.pack(side="left")
        self.next_button = Button(history_buttons_frame,text="-->",command=history_forward)
        self.next_button.config(font=main_font)
        self.next_button.pack(side="right")
        #
        self.resize_CLI_window()
        mainloop()
    def make_canvas_interactive(self):
        self.last_block_altered = None
        def callback(event):
            if self.add_blocks_check.get() or self.remove_blocks_check.get():
                block_location = (int(event.y / self.display.block_size),int(event.x / self.display.block_size))
                if block_location in self.display.main_board_blocks:
                    board_location = list(block_location)
                    board_location[1] = board_location[1] - self.display.columns_left_of_game
                    if self.add_blocks_check.get() and board_location != self.last_block_altered:
                        if self.handler.board.active_blocks[board_location[0],board_location[1]] == 0:
                            self.handler.board.set_blocks[board_location[0],board_location[1]]=randint(-7,-1)
                            self.update_display()
                            self.last_block_altered = board_location
                    if self.remove_blocks_check.get() and board_location != self.last_block_altered:
                        self.handler.board.set_blocks[board_location[0],board_location[1]]=0
                        self.update_display()
                        self.last_block_altered = board_location
        self.display.the_canvas.bind("<Button-1>", callback)
        self.display.the_canvas.bind("<B1-Motion>", callback)
    def update_display(self):
        self.display.hold_box_update(self.handler.board.held_piece)
        self.display.queue_images_update(self.handler.board.piece_queue)
        self.display.refresh_screen(self.handler.board.board_snapshot())
    def state_change(self,state):
        self.hold_entry.config(state=state)
        self.active_piece_entry.config(state=state)
        self.queue1_entry.config(state=state)
        self.queue2_entry.config(state=state)
        self.queue3_entry.config(state=state)
        self.queue4_entry.config(state=state)
        self.build_button.config(state=state)
        self.break_button.config(state=state)
        self.clear_piece_button.config(state=state)
        self.previous_button.config(state=state)
        self.next_button.config(state=state)
        self.add_blocks_button.config(state=state)
        self.remove_blocks_button.config(state=state)
        self.clear_blocks_button.config(state=state)
        self.update_button.config(state=state)
        self.make_columns_button.config(state=state)
        if state == "disabled":
            if self.add_blocks_check.get() == 1:
                self.add_blocks_check.set(0)
            if self.remove_blocks_check.get() == 1:
                self.remove_blocks_check.set(0)
    def update_index_entry(self):
        self.index_entry.config(state="normal")
        self.index_entry.delete(0,"end")
        self.index_entry.insert("end",str(self.board_set_index+1) + "/" + str(len(self.board_set)))
        self.index_entry.config(state="disabled")
    def update_pieces(self):
        if self.set_piece_marker:
            self.handler.board.active_blocks = self.handler.board.active_blocks * -1
            self.handler.board.set_blocks[self.handler.board.active_blocks != 0] = self.handler.board.active_blocks[self.handler.board.active_blocks != 0]
            self.handler.board.active_blocks[...] = 0
            self.set_piece_marker = False
        # 1 - J piece
        # 2 - L piece
        # 3 - S piece
        # 4 - Z piece
        # 5 - T piece
        # 6 - line piece
        # 7 - square piece
        acceptable_entries=(1,2,3,4,5,6,7)
        hold = self.hold_entry.get()
        q1 = self.queue1_entry.get()
        q2 = self.queue2_entry.get()
        q3 = self.queue3_entry.get()
        q4 = self.queue4_entry.get()
        active_piece = self.active_piece_entry.get()
        
        entry_list = [active_piece,hold,q1,q2,q3,q4]
        the_string = ''
        for i in range(len(entry_list)):
            if entry_list[i] not in acceptable_entries:
                if entry_list[i] == 'l' or entry_list[i] == 'L' or entry_list[i] == '1':
                    the_string += '1'
                    entry_list[i] = 1
                elif entry_list[i] == 'j' or entry_list[i] == 'J' or entry_list[i] == '2':
                    the_string += '2'
                    entry_list[i] = 2
                elif entry_list[i] == 's' or entry_list[i] == 'S' or entry_list[i] == '3':
                    the_string += '3'
                    entry_list[i] = 3
                elif entry_list[i] == 'z' or entry_list[i] == 'Z' or entry_list[i] == '4':
                    the_string += '4'
                    entry_list[i] = 4
                elif entry_list[i] == 't' or entry_list[i] == 'T' or entry_list[i] == '5':
                    the_string += '5'
                    entry_list[i] = 5
                elif entry_list[i] == 'line' or entry_list[i] == 'LINE' or entry_list[i] == '6':
                    the_string += '6'
                    entry_list[i] = 6
                elif entry_list[i] == 'square' or entry_list[i] == 'SQUARE' or entry_list[i] == '7':
                    the_string += '7'
                    entry_list[i] = 7
                else: 
                    the_string += '0'
                    entry_list[i] = 0
        self.handler.board.held_piece = int(the_string[1])
        self.display.hold_box_update(piece = entry_list[1])
        self.handler.board.piece_queue = entry_list[2:]
        while 0 in self.handler.board.piece_queue:
            self.handler.board.piece_queue.pop(self.handler.board.piece_queue.index(0))
        self.display.queue_images_update(new_queue=the_string[2:])
        
        active_piece = entry_list[0]
        if active_piece in acceptable_entries:
            self.handler.board.active_blocks[...] = 0
            self.handler.board.piece_queue = [active_piece] + self.handler.board.piece_queue
            next_piece = self.handler.board.piece_queue.pop(0)
            self.handler.board.set_blocks
            if self.handler.board.auto_get_next_piece: 
                if not self.handler.board.get_next_piece(next_piece): self.handler.board.game_lost = True
        self.update_display()
        print("Board updated\n")
    def resize_CLI_window(self):
        def get_windows():
            def check(hwnd, param):
                title = win32gui.GetWindowText(hwnd)
                # print("title: " + str(title))
                if 'python  -u' in title:
                    param.append(hwnd)
            winds = []
            win32gui.EnumWindows(check, winds)
            return winds
        for window in get_windows():
            win32gui.MoveWindow(window,0,0,868,1020,True)
    def build_it(self):
        if not self.on_builder:
            self.handler = Build(self.handler.board)
            self.on_builder = True
        self.state_change("disabled")
        self.board_set = self.handler.go_through_queue()
        # favorite = self.handler.get_favorite(self.board_set)
        self.board_set_index = 0
        self.handler.board = self.board_set[0]
        self.update_index_entry()
        self.update_display()
        self.set_piece_marker = True
        self.state_change("normal")
        self.master.deiconify()
        self.master.focus_force()
    def break_it(self):
        if self.on_builder:
            self.handler = Break(self,self.handler.board)
            self.on_builder = False
        self.state_change("disabled")
        self.board_set = self.handler.go_through_queue()
        self.board_set_index = 0
        self.handler.board = self.board_set[0]
        self.update_index_entry()
        self.update_display()
        self.set_piece_marker = True
        self.state_change("normal")
        self.master.deiconify()
        self.master.focus_force()
if __name__ == '__main__':
    main_object = Main()
