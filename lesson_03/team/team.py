"""
Course: CSE 351 
Lesson: L03 team activity
File:   team.py
Author: Hannah Crenshaw

Purpose: Retrieve Star Wars details from a server

Instructions:

- This program requires that the server.py program be started in a terminal window.
- The program will retrieve the names of:
    - characters
    - planets
    - starships
    - vehicles
    - species

- the server will delay the request by 0.5 seconds

TODO
- Create a threaded function to make a call to the server where
  it retrieves data based on a URL.
- The threaded function should only retrieve one URL.
- Create a queue that will be used between the main thread and the threaded functions

- Speed up this program as fast as you can by:
    - creating as many as you can
    - start them all
    - join them all

"""

from datetime import datetime, timedelta
import threading
from common import *

# Include cse 351 common Python files
from cse351 import *
import queue
# global
call_count = 0


def consume_urls(q):
    while True:
        url = q.get()
        if url is None:
            break
        item = get_data_from_server(url)
        print(f'  - {item["name"]}')

def main():
    global call_count
    tasks = queue.Queue()
    # Create queue here? 

    log = Log(show_terminal=True)
    log.start_timer('Starting to retrieve data from the server')

    film6 = get_data_from_server(f'{TOP_API_URL}/films/6')
    call_count += 1
    print_dict(film6)
    # Retrieve people
    great_urls = []
    great_urls.append(film6['characters'])
    great_urls.append(film6['planets'])
    great_urls.append(film6['starships'])
    great_urls.append(film6['vehicles'])
    great_urls.append(film6['species'])

    for urls in great_urls:
        for url in urls:
            tasks.put(url)

    for i in range(50):
        tasks.put(None)
    
    thread_list = []
    for i in range(50):
        thread_list.append(threading.Thread(target=consume_urls, args=(tasks,)))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()



    log.stop_timer('Total Time To complete')
    log.write(f'There were {call_count} calls to the server')

if __name__ == "__main__":
    main()
