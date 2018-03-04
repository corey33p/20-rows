# 20-rows
App to help with 21 consecutive row breaks in Tetris

There is an achievement in Tetris Ultimate on Xbox One with 3 requirements, one of which is to get a 20 Combo. A combo starts when you get  row breaks with consecutive pieces, so a 20 Combo means that 21 consecutive row breaks are required.

The general strategy involves perfectly filling up the left and right sides of the game with pieces leaving a narrow space in the middle where the row breaks will happen. There are 10 columns in standard Tetris, so the 3 colomns on the sides need to be filled leaving 4 columns open in the middle. There are 20 full rows visible in Tetris Ultimate, with the bottom part of row 21 visible. The sides need to be filled to a height of at least 21.

The 20-rows app (the name of which is a slight misnomer) is intended to help with the building of the side walls and the breaking of the rows. The tetris board is interactive, and the pieces in the queue and the blocks on the screen can be manipulated to match any scenario. There are 2 modes, Build and Break, both of which use brute force to try every possible scenario of playing pieces and holding pieces, with a relatively smart function for checking if a board state is good or bad. The tetris engine supports T-spins a la Tetris Ultimate, and the brute force methods also search for T spins. With 1 active piece and 4 in the queue, the process usually takes ~5 minutes to run, and when finished, the good outcomes can be viewed on the game board, and the cmd line will display which first moves resulted in the most good outcomes.

This was developed in Windows on python 3.6, and probably will not run on Linux due to use of the win32gui module to resize the command line window. This can be commented out or adapted.

Required modules: 
PIL - pip install pillow
numpy - pip install numpy
win32gui - pip install pypiwin32
