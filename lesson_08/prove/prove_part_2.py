"""
Course: CSE 351 
Assignment: 08 Prove Part 2
File:   prove_part_2.py
Author: Hannah Crenshaw

Purpose: Part 2 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

I think we'd have to use classes. Because I wouldn't want to make a new class for each 
recursive function call, I would make a new threaded class for each thread. Right now, the threads
do not return any value because threads aren't designed to return or preserve a value after being
called. I would create a new class for each thread to preserve the movement data. After the
end has been found, the class that found the end would return to its starting point in recursion
where it branched off and alert that class of which path was the right one. In other words, it
would work similar to part 1 by using classes to preserve and return the data. 

Why would it work?

Classes can preserve data even after the thread has been closed. This allows us to retreive 
the solution information and piece together the maze solution at the end, adding each move to
a list as they retrace their steps. 

"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


# TODO: Add any function(s) you need, if any, here.


def solve_find_end(maze):
    """ Finds the end position using threads. Nothing is returned. """
    # When one of the threads finds the end position, stop all of them.
    global stop
    stop = False

    global thread_count
    thread_count = 0

    # Lock for thread count
    count_lock = threading.Lock()

    def move_from_space(maze, x, y, color, count_lock):
        global stop
        global thread_count
        # List of threads, for joining
        threads = []
        # Lock for maze, when drawing
        maze_lock = threading.Lock()
        
        # End thread if the maze has been solved
        if stop:
            return
        
        # Color space with thread color if not already colored.
        if maze.can_move_here(x, y):
            maze.move(x, y, color)
        else:
            return

        if maze.at_end(x, y):
            stop = True
            return

        possible_moves = maze.get_possible_moves(x, y)

        # Make sure there are moves available
        if len(possible_moves) != 0:
            # Save first move, remove from list. 
            first_x, first_y = possible_moves.pop(0)

            # Only create more threads if there are more moves available
            if len(possible_moves) != 0:
                for next_x, next_y in possible_moves:
                    with count_lock:
                        thread_count += 1
                    new_thread = threading.Thread(target=move_from_space, args=(maze, next_x, next_y, get_color(), count_lock))
                    new_thread.start()
                    threads.append(new_thread)

            # After starting new threads, if any, continue recursively with same color
            move_from_space(maze, first_x, first_y, color, count_lock)

        # Once all is said and done, join threads and return.
        for thread in threads:
            thread.join()
        return 
    
    # Get starting x, y
    x, y = maze.get_start_pos()
    # Start moving from that point. 
    move_from_space(maze, x, y, COLOR, count_lock)
    return # Return to main when done



def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()