import numpy as np
from random import randint
import os
import tkinter as tk
from tkinter import Canvas,Tk,ttk,Label,Entry,Button
from PIL import Image
from PIL import ImageTk

class TetrisDisplay:
    def __init__(self,master,frame,rows=22,columns=10,queue=4,hold=True):
        self.master = master
        self.board_frame = frame
        self.maximum_board_size=(800,864)
        self.main_font = ("Courier", 16)
        self.piece_queue_length = queue
        self.hold = hold
        self.rows = rows
        self.columns = columns
        self.previous_board_array = np.zeros((rows,columns)) # needed for displaying the board for the first time
        self.unoccupied_blocks = [] # keep track of which blocks to keep open for upcoming piece windows, held pieces, etc
        #
        self.build_board()
        self.the_canvas.pack()
        # mainloop()
    def build_board(self):
        board_size = self.get_board_size(self.maximum_board_size,(self.columns,self.rows))
        self.block_size = board_size[1]//self.rows
        extra_space = ((self.maximum_board_size[0]-board_size[0])-(self.maximum_board_size[0]-board_size[0])%self.block_size,
                       (self.maximum_board_size[1]-board_size[1])-(self.maximum_board_size[1]-board_size[1])%self.block_size)
        self.overall_size = (board_size[0]+extra_space[0],board_size[1]+extra_space[1])
        if extra_space[0] > extra_space[1]: extra_space_is_horizontal = True
        else: extra_space_is_horizontal = False
        
        self.the_canvas = Canvas(self.board_frame)
        self.the_canvas.config(width=self.overall_size[0],height=self.overall_size[1])
        
        # background
        bg_crop_bounds = (2560/2-self.overall_size[0]/2,1600-self.overall_size[1],2560/2+self.overall_size[0]/2,1600)
        self.background_image = Image.open(os.getcwd().replace('\\','/') + "/Source Images/background.jpg").crop(bg_crop_bounds)
        
        # place exterior blocks
        extra_rows = extra_space[1]//self.block_size
        extra_columns = extra_space[0]//self.block_size
        self.total_block_rows_in_display = self.overall_size[1]//self.block_size
        self.total_block_columns_in_display = self.overall_size[0]//self.block_size
        start_point_set = False
        self.columns_left_of_game = extra_columns // 2
        self.columns_right_of_game = extra_columns - self.columns_left_of_game
        
        self.hold_box_update(creation=True)
        self.queue_images_update(creation=True)
        self.score_update(creation=True)
        
        self.load_images()
        
        self.main_board_blocks = []
        for column in range(self.total_block_columns_in_display):
            for row in range(self.total_block_rows_in_display):
                if ((row < (extra_rows // 2)) or (row > ((extra_rows // 2) + self.rows))) or ((column <= (self.columns_left_of_game - 1)) or (column > ((self.columns_right_of_game - 1) + self.columns))):
                    if (row,column) not in self.unoccupied_blocks:
                        box=(column * self.block_size,
                             row * self.block_size,
                             column * self.block_size+self.block_size,
                             row * self.block_size+self.block_size)
                        self.background_image.paste(self.blocks[8], box)
                elif not start_point_set:
                    self.start_pixels = (column * self.block_size,row * self.block_size)
                    self.start_coords = (column,row)
                    start_point_set = True
                    self.main_board_blocks.append((row,column))
                else: self.main_board_blocks.append((row,column))
        
        self.current_frame = ImageTk.PhotoImage(self.background_image)
        self.background_image.save(os.getcwd().replace('\\','/') + "/temp/background_image.png")
        self.working_image = Image.open(os.getcwd().replace('\\','/') + "/temp/background_image.png").crop((self.start_pixels[0],self.start_pixels[1],self.start_pixels[0]+board_size[0],self.start_pixels[1]+board_size[1]))
        self.canvas_image = self.the_canvas.create_image((0,0), anchor='nw', image=self.current_frame)
        
        for row in range(self.rows):
            self.the_canvas.create_line((self.start_pixels[0],
                                         self.start_pixels[1]+(1+row)*self.block_size,
                                         self.start_pixels[0]+board_size[0],
                                         self.start_pixels[1]+(1+row)*self.block_size),fill="#303030")
        for column in range(self.columns):
            self.the_canvas.create_line((self.start_pixels[0]+(1+column)*self.block_size,
                                         self.start_pixels[1],
                                         self.start_pixels[0]+(1+column)*self.block_size,
                                         self.start_pixels[1]+board_size[1]),fill="#303030")
    def load_images(self):
        self.blocks = {}
        self.blocks[0] = (None, 
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Empty Preview.png").resize(self.queue_box_size),Image.ANTIALIAS))
        self.blocks[1] = (ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Blue Block.png").resize((self.block_size,self.block_size)),Image.ANTIALIAS),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Blue Preview.gif").resize(self.queue_box_size),Image.ANTIALIAS),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Blue Preview.gif").resize(self.hold_box_dimension),Image.ANTIALIAS))
        self.blocks[2] = (ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Green Block.png").resize((self.block_size,self.block_size),Image.ANTIALIAS)),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Green Preview.gif").resize(self.queue_box_size),Image.ANTIALIAS),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Green Preview.gif").resize(self.hold_box_dimension),Image.ANTIALIAS))
        self.blocks[3] = (ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Orange Block.png").resize((self.block_size,self.block_size),Image.ANTIALIAS)),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Orange Preview.gif").resize(self.queue_box_size),Image.ANTIALIAS),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Orange Preview.gif").resize(self.hold_box_dimension),Image.ANTIALIAS))
        self.blocks[4] = (ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Purple Block.png").resize((self.block_size,self.block_size),Image.ANTIALIAS)),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Purple Preview.gif").resize(self.queue_box_size),Image.ANTIALIAS),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Purple Preview.gif").resize(self.hold_box_dimension),Image.ANTIALIAS))
        self.blocks[5] = (ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Red Block.png").resize((self.block_size,self.block_size),Image.ANTIALIAS)),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Red Preview.gif").resize(self.queue_box_size),Image.ANTIALIAS),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Red Preview.gif").resize(self.hold_box_dimension),Image.ANTIALIAS))
        self.blocks[6] = (ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Teal Block.png").resize((self.block_size,self.block_size),Image.ANTIALIAS)),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Teal Preview.gif").resize(self.queue_box_size),Image.ANTIALIAS),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Teal Preview.gif").resize(self.hold_box_dimension),Image.ANTIALIAS))
        self.blocks[7] = (ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Yellow Block.png").resize((self.block_size,self.block_size),Image.ANTIALIAS)),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Yellow Preview.gif").resize(self.queue_box_size),Image.ANTIALIAS),
                          ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Yellow Preview.gif").resize(self.hold_box_dimension),Image.ANTIALIAS))
        self.blocks[8] = Image.open(os.getcwd().replace('\\','/') + "/Source Images/Black Block.png").resize((self.block_size,self.block_size),Image.ANTIALIAS)
        self.pause_photoimage = ImageTk.PhotoImage(Image.open(os.getcwd().replace('\\','/') + "/Source Images/Pause Screen.gif"))
    def get_board_size(self, canvas_max_size, board_dimensions):
        if (board_dimensions[0] != canvas_max_size[0]) or (board_dimensions[1] != canvas_max_size[1]):
            if (board_dimensions[0] > canvas_max_size[0]) or (board_dimensions[1] > canvas_max_size[1]):
                if board_dimensions[0]/board_dimensions[1] > canvas_max_size[0]/canvas_max_size[1]:
                    the_resized_size=(int(canvas_max_size[0]),int(canvas_max_size[0]*board_dimensions[1]/board_dimensions[0]))
                else:
                    the_resized_size=(int(canvas_max_size[1]*board_dimensions[0]/board_dimensions[1]),int(canvas_max_size[1]))
            else:
                if board_dimensions[0]/board_dimensions[1] < canvas_max_size[0]/canvas_max_size[1]:
                    the_resized_size=(int(canvas_max_size[1]*board_dimensions[0]/board_dimensions[1]),int(canvas_max_size[1]))
                else:
                    the_resized_size=(int(canvas_max_size[0]),int(canvas_max_size[0]*board_dimensions[1]/board_dimensions[0]))
        else: the_resized_size = board_dimensions
        if board_dimensions[0] < board_dimensions[1]:
            adjusted_width = the_resized_size[0]-the_resized_size[0]%board_dimensions[0]
            return (int(adjusted_width),int(board_dimensions[1]/board_dimensions[0]*adjusted_width))
        else:
            adjusted_height = the_resized_size[1]-the_resized_size[1]%board_dimensions[1]
            return (int(board_dimensions[0]/board_dimensions[1]*adjusted_height),int(adjusted_height))
    def hold_box_update(self,piece = 0,creation = False):
        if creation:
            if self.columns_left_of_game >= 3: 
                self.hold_box_size = (self.columns_left_of_game - 2,self.columns_left_of_game - 2)
                self.hold_box_dimension = (self.block_size * self.hold_box_size[0],self.block_size * self.hold_box_size[0])
                hold_box_starting_point = (1,1) # row, column bcz pertains to grid vis-a-vis numpy
                self.hold_box_starting_point_pixels = (self.block_size,self.block_size) # column, row bcz pertains to pixels
            else: 
                self.hold_box_size = (self.columns_left_of_game,self.columns_left_of_game)
                self.hold_box_dimension = (self.block_size * self.hold_box_size[0],self.block_size * self.hold_box_size[0])
                hold_box_starting_point(1,0) # row, column bcz pertains to grid vis-a-vis numpy
                self.hold_box_starting_point_pixels = (0,self.block_size) # column, row bcz pertains to pixels
            
            for row in range(self.hold_box_size[0]):
                for column in range(self.hold_box_size[1]):
                    self.unoccupied_blocks.append((hold_box_starting_point[0] + row, hold_box_starting_point[1] + column))
        else:
            self.the_canvas.delete("hold")
            if piece in (1,2,3,4,5,6,7):
                self.the_canvas.create_image(self.hold_box_starting_point_pixels, anchor='nw', image=self.blocks[piece][2], tags="hold")
    def queue_images_update(self,new_queue="",creation = False):
        if creation:
            if self.columns_right_of_game >= 3: 
                unit_block_size = self.columns_right_of_game - 2
                box_size_dimension = (unit_block_size) * self.block_size
                self.queue_box_size = (box_size_dimension,box_size_dimension)
                start_column = self.columns_left_of_game+self.columns+1
            else: 
                unit_block_size = self.columns_right_of_game
                box_size_dimension = unit_block_size * self.block_size
                self.queue_box_size = (box_size_dimension,box_size_dimension)
                start_column = self.columns_left_of_game+self.columns
            
            self.preview_box_locations = []
            for i in range(self.piece_queue_length):
                self.preview_box_locations.append([self.block_size * start_column,self.block_size * (1+(unit_block_size+1)*i)])
                for column in range(unit_block_size):
                    for row in range(unit_block_size):
                        self.unoccupied_blocks.append((row + (1+(unit_block_size+1)*i), column + start_column))
        else:
            if isinstance(new_queue,list):
                the_string = ""
                for element in new_queue:
                    the_string += str(element)
                new_queue = the_string
            new_queue=new_queue.replace("line","6")
            new_queue=new_queue.replace("square","7")
            new_queue=new_queue.replace("L","1")
            new_queue=new_queue.replace("l","1")
            new_queue=new_queue.replace("J","2")
            new_queue=new_queue.replace("j","2")
            new_queue=new_queue.replace("S","3")
            new_queue=new_queue.replace("s","3")
            new_queue=new_queue.replace("Z","4")
            new_queue=new_queue.replace("z","4")
            new_queue=new_queue.replace("T","5")
            new_queue=new_queue.replace("t","5")
            new_queue=new_queue.replace(",","")
            self.the_canvas.delete("queue")
            for i in range(len(new_queue)): 
                if new_queue[i] != '0':
                    if (i + 1) <= len(new_queue): 
                        self.the_canvas.create_image(self.preview_box_locations[i], anchor='nw', image=self.blocks[int(new_queue[i])][1], tags="queue")
    def score_update(self,score=0,creation=False):
        if creation:
            if self.columns_right_of_game >= 3: 
                blocks_for_score = self.columns_right_of_game - 2
                box_size_in_pixels = ((blocks_for_score) * self.block_size, self.block_size)
                score_location_on_grid = (self.columns_left_of_game+self.columns+1, self.rows - 2)
                self.score_location_in_pixels = (score_location_on_grid[0] * self.block_size + box_size_in_pixels[0] / 2,
                                            score_location_on_grid[1] * self.block_size + box_size_in_pixels[1] / 2)
            else: 
                blocks_for_score = self.columns_right_of_game
                box_size_in_pixels = ((blocks_for_score) * self.block_size, self.block_size)
                score_location_on_grid = (self.columns_left_of_game+self.columns, self.rows - 2)
                self.score_location_in_pixels = (score_location_on_grid[0] + box_size_in_pixels[0] / 2,
                                            score_location_on_grid[1] + box_size_in_pixels[1] / 2)
            for column in range(blocks_for_score):
                self.unoccupied_blocks.append((self.rows - 2, column + score_location_on_grid[0]))
            
            self.the_canvas.score = self.the_canvas.create_text(self.score_location_in_pixels[0], self.score_location_in_pixels[1],
                                                            fill='white', font=("Courier",int(self.block_size * -.85)),
                                                            text="0")
        else:
            # I shouldn't have to delete and recreate this, but I couldn't get it to display otherwise. Whatever
            self.the_canvas.delete(self.the_canvas.score) 
            self.the_canvas.score = self.the_canvas.create_text(self.score_location_in_pixels[0], self.score_location_in_pixels[1],
                                                            fill='white', font=("Courier",int(self.block_size * -.75)),
                                                            text="0")
            self.the_canvas.itemconfig(self.the_canvas.score, text=str(score))
    def refresh_screen(self,input_array=None):
        if isinstance(input_array,np.ndarray):
            for row in range(input_array.shape[0]):
                for column in range(input_array.shape[1]):
                    if (input_array[row,column] == 0) or (input_array[row,column] != self.previous_board_array[row,column]):
                        self.the_canvas.delete(str(row)+","+str(column))
                    if (input_array[row,column] != 0) and (input_array[row,column] != self.previous_board_array[row,column]):
                        self.the_canvas.create_image((column*self.block_size+self.start_pixels[0],row*self.block_size), anchor='nw', image=self.blocks[int(abs(input_array[row,column]))][0],tags=str(row)+","+str(column))
        self.previous_board_array = np.copy(input_array)
        self.master.update()