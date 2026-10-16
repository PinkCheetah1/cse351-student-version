"""
Course    : CSE 351
Assignment: 04
Student   : Hannah Crenshaw

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *

from cse351 import *

THREADS = 200               # TODO - set for your program
WORKERS = 10                 # TODO - set for your program
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(fetch_q, write_q, fetch_empty, fetch_full, write_empty, write_full):
    # TODO - fill out this thread function (and arguments)
    while True:
        fetch_full.acquire() # -1 to full spots
        queue_request = fetch_q.get()
        fetch_empty.release() # +1 to empty spots

        if queue_request is None:
            return

        city, rec_num = queue_request
        # Fetch from server yay
        city_data = get_data_from_server(f"{TOP_API_URL}/record/{city}/{rec_num}")
        
        name = city_data['city']
        date = city_data['date']
        temp = city_data['temp']
        # Put in new queue!
        write_empty.acquire()
        write_q.put((name, date, temp))
        write_full.release()
    return
    ...


# ---------------------------------------------------------------------------
# TODO - Create Worker threaded class
class Worker(threading.Thread):
    def __init__(self, write_q, write_empty, write_full, noaa):
        threading.Thread.__init__(self)
        self.write_q = write_q
        self.write_empty = write_empty
        self.write_full = write_full
        self.noaa = noaa

    def run(self):
        while True:
            # Pull from queue
            self.write_full.acquire()
            city_data = self.write_q.get()
            self.write_empty.release()

            # If is none, return
            if city_data is None:
                return

            # Parse data and write to NOAA
            name = city_data[0]
            date = city_data[1]
            temp = city_data[2]

            self.noaa.write(name, date, temp)

        return


# ---------------------------------------------------------------------------
# TODO - Complete this class
class NOAA:

    def __init__(self):

        # dictionary stores city : [(date, temp), ...]
        self.city_records = {}
        for city in CITIES:
            self.city_records[city] = []
        self.lock = threading.Lock()
        

    def write(self, name, date, temp):
        with self.lock:
            self.city_records[name].append((date, temp))

    def get_temp_details(self, city):
        temps = []
        for date, temp in self.city_records[city]:
            temps.append(temp)
        return sum(temps) / len(temps)


# ---------------------------------------------------------------------------
class Queue351():
    """ This is the queue object to use for this class. Do not modify!! """

    def __init__(self):
        self.__items = []
   
    def put(self, item):
        assert len(self.__items) <= 10
        self.__items.append(item)

    def get(self):
        return self.__items.pop(0)

    def get_size(self):
        """ Return the size of the queue like queue.Queue does -> Approx size """
        extra = 1 if random.randint(1, 50) == 1 else 0
        if extra > 0:
            extra *= -1 if random.randint(1, 2) == 1 else 1
        return len(self.__items) + extra


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]['records']:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    # TODO - Create any queues, semaphores, locks or barriers you need
    fetch_q = Queue351()
    write_q = Queue351()


    # Fetching Semaphors
    fetch_empty = threading.Semaphore(10)
    fetch_full = threading.Semaphore(0)

    # Writing Semaphors
    write_empty = threading.Semaphore(10)
    write_full = threading.Semaphore(0)

    # Create threads first so they start pulling from queue immediately
    fetch_threads = []
    for i in range(THREADS):
        new_thread = threading.Thread(target=retrieve_weather_data, args=(fetch_q, write_q, fetch_empty, fetch_full, write_empty, write_full))
        fetch_threads.append(new_thread)
        new_thread.start()

    # Create workers
    workers = []
    for i in range(WORKERS):
        new_worker = Worker(write_q, write_empty, write_full, noaa)
        workers.append(new_worker)
        new_worker.start()        

    # Start loading the queue
    for city in CITIES:
        print(f"queueing {city}")
        for i in range(RECORDS_TO_RETRIEVE):
            fetch_empty.acquire() # -1 to empty spots
            fetch_q.put((city, i))
            fetch_full.release() # +1 to full spots



    # After loading queue, put fetch sentinels 
    for i in range(THREADS):
        fetch_empty.acquire() # -1 to empty spots
        fetch_q.put(None)
        fetch_full.release()

    # join threads
    for thread in fetch_threads:
        thread.join()

    # after threads join, put worker sentinels
    for i in range(WORKERS):
        write_empty.acquire()
        write_q.put(None)
        write_full.release()

    # join workers
    for worker in workers:
        worker.join()

    



    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()

