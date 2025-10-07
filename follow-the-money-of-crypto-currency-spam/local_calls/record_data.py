import csv
import json
import os
import time
import sys
import datetime
import re

def count_addresses_sent_to(address):
    """
    @brief This function will return the total number of addresses and the number of unique addresses that the address has sent to.

    @param address: The address to count the number of addresses sent to.
    @output: A list containing the total number of addresses[0] and the number of unique addresses[1] that the address has sent to.
    """
    total_address_counter = 0
    seen_addresses = []
    seen_transactions = [] #Some transactions can contain the same sender multiple times so we need to avoid counting the same transaction multiple times
    csv_file_path = "data_csv/" + address + "/" + address + ".csv"  # Set path of csv file
    #print("csv_file_path: ", csv_file_path)
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                tx_count = row[5] #Get the number of transactions in the row (same for all rows)
                if row[1] == address and row[0] not in seen_transactions: #If the address is the sender and the transaction has not been seen before
                    seen_transactions.append(row[0])
                    row_addresses = row[2] #Returns the string of all addresses sent to in one row
                    row_addresses = row_addresses.replace('[', '').replace(']', '') #Clean string to only contain btc addresses
                    if ',' in row_addresses: #If there is a comma, that means there are multiple addresses sent to in thte string
                        row_addresses = row_addresses.split(',')
                        for addr in row_addresses: #Iterate over all the addresses, count and add to the list of seen addresses
                            if addr not in seen_addresses:
                                seen_addresses.append(addr)
                                total_address_counter += 1
                    else: #If there is no comma that means there is only one address sent to in the string
                        if row_addresses not in seen_addresses:
                            seen_addresses.append(row_addresses)
                        
                        total_address_counter += 1
    unique_address_counter = len(seen_addresses)
    return_list = [total_address_counter, unique_address_counter, tx_count]
    #print("Addresses found: ", total_address_counter)
    #print("Unique addresses found: ", unique_address_counter)
    #print("Transactions found: ", tx_count)
    return return_list

address = "3DFsCoPzFPVjzovPb11obVLreACxA7mBS9"
count_addresses_sent_to(address)