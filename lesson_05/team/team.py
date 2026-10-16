""" 
Course: CSE 351
Lesson: L05 Team Activity
File:   team.py
Author: <Add name here>
Purpose: Find prime numbers

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)
"""

from datetime import datetime, timedelta
import multiprocessing as mp
import random
from matplotlib.pylab import plt  # load plot library


# Include cse 351 common Python files
from cse351 import *

def is_prime(n):
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def worker(n):
    if is_prime(n):
        return
    return

def main():
    log = Log(show_terminal=True)
    log.start_timer()

    xaxis_cpus = []
    yaxis_times = []

    start_time = time.time()

    start = 10000000000
    range_count = 100000
    numbers_processed = 0
    prime_count = 0

    numbers = list(range(start, start+range_count))

    # results = [pool.apply_async(is_prime, args=(x,)) for x in range(start, start + range_count) ]

    for cpu in range(1, mp.cpu_count() + 1):
        print(f'processing cpu = {cpu}')
        with mp.Pool(cpu) as p:
            results = p.map(worker, numbers)

        end_time = time.time()
        elapsed_time = end_time - start_time

        xaxis_cpus.append(cpu)
        yaxis_times.append(elapsed_time)
        print(f'{cpu} cpus took {elapsed_time} to print')

    

    # create plot of results and also save it to a PNG file
    plt.plot(xaxis_cpus, yaxis_times)
    
    plt.title('Time VS CPUs')
    plt.xlabel('CPU Cores')
    plt.ylabel('Seconds')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
