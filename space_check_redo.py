import numpy as np

a=np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
       [-4, -2, 0, 0, 0, 0, 0, 0, 0, 0],
       [-4, -2,0, 0, 0, 0, 0, 0, 0, 0],
       [-4, -2, 0, 0, 0, 0, 0, 0, 0, 0],
       [-4, -2, 3, 0, 0, 0, 0, -2, 0, 0],
       [-4, -2, 3, 0, 0, 0, 0, -1, -2, -3]])
b=np.array([[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],#10
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],#15
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  6,  6],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  6,  6],
       [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0]])

def board_print(ar, print_now=True):
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

def analyze_piece(set_blocks,active_blocks):
    def empty_space_check(place,board):
        board_print(board)
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
                    print("place: " + str(place))
                    side_opening_set.add(place)
            if column < board.shape[1]-1:
                if column + 1 not in middle_columns:
                    adj_places.append((row,column+1))
                else:
                    open_side = True
                    print("place: " + str(place))
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
                        print("---\nadjacent_place_check: " + str(adjacent_place_check))
                        print("found_adjacent_places[0]: " + str(found_adjacent_places[0]))
                        print("open_area: " + str(open_area)+"\n---")
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
    board_print(full_board)
    
    # false if leaves any inaccessible blocks
    if good_outcome:
        where_block = np.argwhere(full_board)
        total_open_area = []
        for location in where_block:
            # print("location: " + str(location))
            if location[0] < set_blocks.shape[0] - 1:
                if (full_board[location[0]+1,location[1]]==0):
                    where_empty_under_block = location[0]+1,location[1]
                    if where_empty_under_block not in total_open_area:
                        # print("where_empty_under_block: " + str(where_empty_under_block))
                        open_area, open_up, open_side, height_limit, side_opening_size = empty_space_check(where_empty_under_block,full_board)
                        total_open_area = total_open_area + open_area
                        print("side_opening_size: " + str(side_opening_size))
                        # print("open_area: " + str(open_area))
                        print("open_up: " + str(open_up))
                        # not good if space is inaccessible
                        if not (open_up or open_side): good_outcome = False
                        if (not open_up) and (open_side):
                            # make sure side opening can be filled
                            if not ((len(open_area) % 4 == 0) and (side_opening_size > 1)): good_outcome = False
                        if open_up and (not open_side):
                            for spot in open_area:
                                # make sure all spots accessible from top
                                # print("height_limit: " + str(height_limit))
                                # print("full_board[height_limit:spot[0],spot[1]]:\n" + str(full_board[height_limit:spot[0],spot[1]]))
                                if full_board[height_limit:spot[0],spot[1]].any(): good_outcome = False
    print("total_open_area: " + str(total_open_area))
    return good_outcome

answer = analyze_piece(a,b)
print("answer: " + str(answer))
