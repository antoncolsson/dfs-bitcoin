import pandas as pd
import os
import requests
import json
import random
import re
import time
from datetime import datetime
import coinaddrvalidator as validateBTC
import sys

test_folder = r"C:\Users\D-RTX3080\Desktop\gitlab\follow-the-money-of-crypto-currency-spam\testData"
BTC_INFO_OUTPUT_DIR = test_folder
ransomware_path = r"C:\Users\D-RTX3080\Desktop\gitlab\follow-the-money-of-crypto-currency-spam\total_missing_addresses_RansomWare.txt"
BTC_ADDR_DIR = ransomware_path

def proxy_is_active(proxy):
    res = None
    try:
        res = requests.get("http://httpbin.org/ip", proxies={"http": f"http://{proxy}"}, timeout=1.8)
        if res.status_code >= 400:
            res = None
        else:
            print("proxy ok", proxy)
    except Exception as e:
        print(e)
    return res is not None


# https://free-proxy-list.net/
def get_active_proxies(refresh=False):
    print("Checking for active proxies:")
    proxies_dir = "proxies.txt" if refresh else "active-proxies.txt"
    with open(proxies_dir, 'r') as f:
        return list(filter(proxy_is_active, f.read().strip().split('\n')))
    
def is_valid_btc_address(addr):
    btc_pattern = r"(bc1|[13])[a-km-zA-HJ-NP-Z1-9]{25,39}"
    return True if re.search(btc_pattern, addr) else False
    
def blockcypher_fetch(addr):
    if not is_valid_btc_address(addr):
        print(f"Invalid BTC address: {addr}")
        return False

    try:
        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{addr}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses

        data = response.json()
        os.makedirs(BTC_INFO_OUTPUT_DIR, exist_ok=True)  # Ensure the output directory exists
        file_path = os.path.join(BTC_INFO_OUTPUT_DIR, f"{addr}.json")
        
        with open(file_path, 'w') as file:
            json.dump(data, file)

        print(f"Data for {addr} saved to {file_path}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for {addr}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error for {addr}: {e}")
        return False

def blockcypher_fetch_all():
   # proxies = get_active_proxies()
    proxies = None
    with open(BTC_ADDR_DIR) as f:
        for i, btc_addr in enumerate(f.readlines()):
            print(f'\n{i}:', btc_addr.strip())
            while True:
                if not proxies:
                    print("All proxies reached the API limit.")
                    return
                proxy = random.choice(proxies)
                print("using proxy", proxy)
                res, status_code = blockcypher_fetch(btc_addr.strip(), proxy=None)
                if status_code == 200:
                    with open(BTC_INFO_OUTPUT_DIR, 'a') as f:
                        json.dump(res, f)
                        f.write('\n')
                elif status_code == 429: # API limit reached
                    print(proxy, "API limit reached")
                    proxies.remove(proxy)
                    continue
                break
"""
def blockchain_fetch(addr):
    assert is_valid_btc_address(addr)
    url = "https://blockchain.info/rawaddr/" + addr
    try:
        return pandas.read_json(url)
    except Exception as e:
        print(e)
        return None        
def blockchain_fetch(addr, save_to_file=False, save_dir='btc_address_data'):
    
    #@brief Fetch Bitcoin address information from the blockchain.info API.
    #@param addr: The Bitcoin address to fetch information for.
    #@param save_to_file: Whether to save the data to a JSON file. Default is False, which returns the DataFrame.
   # @param save_dir: The directory to save the JSON file. Default is 'btc_address_data'.
  #  @return: The DataFrame containing the Bitcoin address information.
    
   # assert is_valid_btc_address(addr)
    url = "https://blockchain.info/rawaddr/" + addr
    try:
        data = pd.read_json(url)
        if save_to_file:
            # Ensure the directory exists
            os.makedirs(save_dir, exist_ok=True)
            # Construct the file path
            file_path = os.path.join(save_dir, f'{addr}.json')
            # Save the DataFrame as a JSON file
            data.to_json(file_path, orient='records', lines=True)
            print(f'Data for address {addr} has been saved to {file_path}')
        return data
    except Exception as e:
        print(e)
        return None
"""

def blockchain_fetch(addr, save_dir='data_json', attempt=0, max_attempts=3, proxies=None):
    if not is_valid_btc_address(addr):
        print(f"Invalid BTC address: {addr}")
        return False

    if attempt >= max_attempts:
        print(f"Max attempts reached for {addr}")
        return False

    if proxies is None:
        #proxies = get_active_proxies()
        proxies = None

   # if not proxies:
    #    print("No active proxies available.")
     #   return False

    #proxy = random.choice(proxies)
    #print(f"Using proxy: {proxy}")

    try:
        #proxies_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
       # response = requests.get(f"https://blockchain.info/rawaddr/{addr}", proxies=proxies_dict, timeout=5)
        # response without proxies
        response = requests.get(f"https://blockchain.info/rawaddr/{addr}", timeout=5)
        response.raise_for_status()

        data = response.json()
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"{addr}.json")
        with open(file_path, 'w') as file:
            json.dump(data, file)
        print(f"Data for {addr} saved to {file_path}")
        return True

    except requests.exceptions.ProxyError as e:
       # print(f"Proxy {proxy} error: {e}")
       # proxies.remove(proxy)  # Remove the failing proxy
        return blockchain_fetch(addr, save_dir, attempt + 1, max_attempts, proxies)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for {addr}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error for {addr}: {e}")
        return False

        
def blockchain_fetch_all():
    with open(BTC_ADDR_DIR) as f:  # Open the file with the list of Bitcoin addresses
        for btc_addr in f.readlines():
            btc_addr = btc_addr.strip()  # Remove any whitespace from the address
            if btc_addr:  # If the address is not empty
                blockchain_fetch(btc_addr)  # Fetch the data for the address

def fetch_single_address(address, output_dir='data_json', offset=0):
    """
    Fetches data for a single Bitcoin address and saves it as a JSON file.

    @param address: Bitcoin address to fetch.
    @param output_dir: Directory to save the JSON file.
    @param offset: Optional offset parameter for the API call.
    """
    url = f"https://blockchain.info/rawaddr/{address}?offset={offset}"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()
    
    # Create a subdirectory named after the address
    address_dir = os.path.join(output_dir, address)
    os.makedirs(address_dir, exist_ok=True)
    
    # Name the file after the address
    filename = f"{address}.json"
    file_path = os.path.join(address_dir, filename)
    
    with open(file_path, 'w') as file:
        json.dump(data, file)
    print(f"Data for {address} saved to {file_path}")

# read from a text file and add each root address to a list
def read_root_addresses(file_path):
    root_addresses = []
    with open(file_path, 'r') as f:
        for line in f:
            if validateBTC.validate('btc',line.strip()):
                root_addresses.append(line.strip())
            else:
                print(f"Invalid BTC address: {line.strip()}")
    return root_addresses

# fetch data for all root addresses in a list
def fetch_root_addresses(root_addresses, output_dir='data_json'):
    for address in root_addresses:
        fetch_single_address(address, output_dir)

#root_addresses = read_root_addresses('root_Darknet_addresses.txt')
#fetch_root_addresses(root_addresses)

#Blockstream API: https://github.com/Blockstream/esplora/blob/master/API.md#transaction-format
#Block stream transaction req: https://blockstream.info/api/address/358XUhiKFgzerNzdJk1WQA8aKz3GPRDzFU/txs
#Block stream address req: https://blockstream.info/api/address/358XUhiKFgzerNzdJk1WQA8aKz3GPRDzFU
#https://blockstream.info/api/address/1KwkiUYFSqY2YGdMCsm4aAhABtEon554TQ/txs/chain/17f9ef08e75e85e0bdf12b7a98ecc630ff3e01b54b3992540f7b4e137dbe9fd3
#Above gets the next 25 transactions after first 25 so format for more than 25 transactions is:
#/api/address/[the address]/txs/chain/[the last txid from the first call]
#Nrofcalls * 25 = number of transactions collected. If nrofcalls is 4, 100 transactions are collected
def blockstream_fetch(addr, save_dir='data_json', attempt=0, max_attempts=3, proxies=None, transactions_to_collect=100, available_transactions=0, counter=0):
    """
    Fetches data for a single Bitcoin address and saves it as multiple JSON files.
    @brief Example call blockstream_fetch(address, transactions_to_collect=25)
    @input: address: Bitcoin address to fetch.
    @input: save_dir: Directory to save the JSON files.
    @param attempt: Current attempt number used for API retries, do not input.
    @param max_attempts: Maximum number of attempts to make with API retries when call fails, do not input.
    @input: proxies: List of active proxies to use for the API calls.
    @input: transactions_to_collect: Total number of transactions to collect for the address in increments of 25, 50, 75...
    @param available_transactions: Total number of transactions available for the address read from the info file, do not input.
    @param counter: Counter for the number of calls made, do not input.
    """

    if attempt >= max_attempts:
        print(f"Max attempts reached for {addr}")
        return False

    if proxies is None:
        #proxies = get_active_proxies()
        proxies = None

   # if not proxies:
    #    print("No active proxies available.")
     #   return False

    #proxy = random.choice(proxies)
    #print(f"Using proxy: {proxy}")

    try:
        #proxies_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
       # response = requests.get(f"https://blockchain.info/rawaddr/{addr}", proxies=proxies_dict, timeout=5)
        # response without proxies
        response = requests.get(f"https://blockstream.info/api/address/{addr}", timeout=10)
        response.raise_for_status()

        if counter == 0: #For first call, get info file, collect total transaction count, save info file then collect transactions
            
            addr_is_valid = validateBTC.validate('btc', addr) #Validate address first call, if not valid, return false
            if not addr_is_valid:
                print(f"Invalid BTC address: {addr}")
                return False
            
            data = response.json()
            save_dir = os.path.join(save_dir, addr) #Name subfolder after the address
            if not os.path.exists(save_dir): #Create subfolder for the address
                os.makedirs(save_dir, exist_ok=True)

            n_tx = data["chain_stats"]["tx_count"] #Gets transactioncount from info file in first call
            file_path = os.path.join(save_dir, f"{addr}_info.json") #
            with open(file_path, 'w') as file:
                json.dump(data, file)
            print(f"Data for {addr} saved to {file_path}")

            addr_txs = addr + "/txs" #Preps next call to get first 25 transaction
            sys.stdout.flush() #Allows terminal to print during runtime, else all is printed at end
            blockstream_fetch(addr_txs, save_dir, attempt, max_attempts, proxies, transactions_to_collect, available_transactions=n_tx, counter = counter + 1) #Recursive call to get all transactions
            return True
        else: #If it is the second call or more, save the data in a file with the counter in name
            addr_split = addr.split('/') #Clean up the address for the file name to reformat between recursive calls
            addr = addr_split[0] #Get first half of the split string

            data = response.json()
            file_path = os.path.join(save_dir, f"{addr}_{counter}.json") #Name file addr_counter.json
            with open(file_path, 'w') as file:
                json.dump(data, file)
            print(f"Data for {addr} saved to {file_path}")
            ##If there are more transactions to collect, get the next 25 transactions
            if transactions_to_collect > counter*25 and available_transactions > counter*25:
                for line in data:
                    if "txid" in line:
                        last_tx = line["txid"] #Iterates over all txs and gets the last txid
                if last_tx is not None:
                    addr_txs = addr + "/txs/chain/" + last_tx #Append last txid to string to get next 25 transactions
                sys.stdout.flush() #Allows terminal to print during runtime, else all is printed at end
                blockstream_fetch(addr_txs, save_dir, attempt, max_attempts, proxies, transactions_to_collect, available_transactions, counter = counter + 1) #Recursive call to get all transactions
                return True
            else:
                return True

    except requests.exceptions.ProxyError as e:
       # print(f"Proxy {proxy} error: {e}")
       # proxies.remove(proxy)  # Remove the failing proxy
        return blockchain_fetch(addr, save_dir, attempt + 1, max_attempts, proxies)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for {addr}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error for {addr}: {e}")
        if attempt < max_attempts:
            return blockchain_fetch(addr, save_dir, attempt + 1, max_attempts, proxies)
        else:
            return False

#ex_address = "13yfvRaqqCH2cTUpDe6wLfHewmcaxVNHrt"
#blockstream_fetch(ex_address, transactions_to_collect=0)
#1KwkiUYFSqY2YGdMCsm4aAhABtEon554TQ has 796 transactions
#https://blockstream.info/api/address/1KwkiUYFSqY2YGdMCsm4aAhABtEon554TQ/txs/chain/17f9ef08e75e85e0bdf12b7a98ecc630ff3e01b54b3992540f7b4e137dbe9fd3
#Above gets the next 25 transactions after first 25 so format for more than 25 transactions is:
#blockstream.info/api/address/[the address]/txs/chain/[the last txid from the first call]
#bc1qpxucqg8flf7mpxwlu882gsxee2kx5hnkl3kw5a
#blockstream_fetch("358XUhiKFgzerNzdJk1WQA8aKz3GPRDzFU", transactions_to_collect=100)