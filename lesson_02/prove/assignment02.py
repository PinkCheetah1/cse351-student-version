"""
Course    : CSE 351
Assignment: 02
Student   : Hannah Crenshaw

Instructions:
    - review instructions in the course
"""

# Don't import any other packages for this assignment
import os
import random
import threading
from money import *
from cse351 import *

# ---------------------------------------------------------------------------
def main(): 

    print('\nATM Processing Program:')
    print('=======================\n')

    create_data_files_if_needed()

    # Load ATM data files
    data_files = get_filenames('data_files')
    # print(data_files)
    
    log = Log(show_terminal=True) #Creates log file? 
    log.start_timer() #Tracking time

    bank = Bank()

    # NOTES
    # Need Lock? 

    # TODO - Add an ATM_Reader for each data file
    for file_path in data_files:
        atm_list = []
        new_atm = ATM_Reader(file_path, bank)
        atm_list.append(new_atm)

    for atm in atm_list:
        atm.start()

    test_balances(bank) # Automated Tests

    log.stop_timer('Total time') #Tracking time


# ===========================================================================
class ATM_Reader(threading.Thread):
    # TODO - implement this class here
    # Make threaded
    # RECEIVE file path
    # Add variables to process file data
    # call bank Withdraw, Deposit 
    # Run method
    def __init__(self, file_path, bank):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.bank = bank
        self.acc_id = ''
        self.amount = ''
        self.trans_type = ''

    def run(self):
        # open file
        with open(self.file_path, 'r') as file: 
            next(file, None)
            # One line at a time, pars data
            for line in file: 
                clean_line = line.strip()
                line_data = clean_line.split(',')
                self.acc_id = line_data[0]
                self.trans_type = line_data[1]
                self.amount = line_data[2]

                # Call bank with our data
                if self.trans_type == 'w':
                    self.bank.withdraw(acc_id=self.acc_id, amount=self.amount)
                elif self.trans_type == 'd':
                    self.bank.withraw(self.acc_id, self.amount)

                return


# ===========================================================================
class Account():
    # TODO - implement this class here
    # Method Deposit(amount)
    # Method Withdraw(amount)
    # Method GetBal() : Money
    ...


# ===========================================================================
class Bank():

    # TODO - implement this class here
    # Receive account info? 
    # Have account dictionary variable
    # Deposit Method (acc.id, amount)
    # Withdraw Method (acc.id, amount)
    # Get balance method (acc)
    def __init__(self):
        ...
    def withdraw(acc_id, amount):
        ...
    def deposit(acc_id, amount):
        ...


# ---------------------------------------------------------------------------

def get_filenames(folder):
    """ Don't Change """
    filenames = []
    for filename in os.listdir(folder):
        if filename.endswith(".dat"):
            filenames.append(os.path.join(folder, filename))
    return filenames

# ---------------------------------------------------------------------------
def create_data_files_if_needed():
    """ Don't Change """
    ATMS = 10
    ACCOUNTS = 20
    TRANSACTIONS = 250000

    sub_dir = 'data_files'
    if os.path.exists(sub_dir):
        return

    print('Creating Data Files: (Only runs once)')
    os.makedirs(sub_dir)

    random.seed(102030)
    mean = 100.00
    std_dev = 50.00

    for atm in range(1, ATMS + 1):
        filename = f'{sub_dir}/atm-{atm:02d}.dat'
        print(f'- {filename}')
        with open(filename, 'w') as f:
            f.write(f'# Atm transactions from machine {atm:02d}\n')
            f.write('# format: account number, type, amount\n')

            # create random transactions
            for i in range(TRANSACTIONS):
                account = random.randint(1, ACCOUNTS)
                trans_type = 'd' if random.randint(0, 1) == 0 else 'w'
                amount = f'{(random.gauss(mean, std_dev)):0.2f}'
                f.write(f'{account},{trans_type},{amount}\n')

    print()

# ---------------------------------------------------------------------------
def test_balances(bank):
    """ Don't Change """

    # Verify balances for each account
    correct_results = (
        (1, '59362.93'),
        (2, '11988.60'),
        (3, '35982.34'),
        (4, '-22474.29'),
        (5, '11998.99'),
        (6, '-42110.72'),
        (7, '-3038.78'),
        (8, '18118.83'),
        (9, '35529.50'),
        (10, '2722.01'),
        (11, '11194.88'),
        (12, '-37512.97'),
        (13, '-21252.47'),
        (14, '41287.06'),
        (15, '7766.52'),
        (16, '-26820.11'),
        (17, '15792.78'),
        (18, '-12626.83'),
        (19, '-59303.54'),
        (20, '-47460.38'),
    )

    wrong = False
    for account_number, balance in correct_results:
        bal = bank.get_balance(account_number)
        print(f'{account_number:02d}: balance = {bal}')
        if Money(balance) != bal:
            wrong = True
            print(f'Wrong Balance: account = {account_number}, expected = {balance}, actual = {bal}')

    if not wrong:
        print('\nAll account balances are correct')



if __name__ == "__main__":
    main()

