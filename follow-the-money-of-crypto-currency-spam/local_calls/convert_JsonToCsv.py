import csv
import json
import os
import time
import sys
import datetime

# Get the current working directory of the script
cwd = os.getcwd()
# Get the parent directory of the current working directory
parent_dir = os.path.dirname(cwd)

def convert_JSON_files_from_file_path(json_file_path, csv_file_path):
    """
    @brief Convert a single JSON file in a folder to a single CSV file. This function will append to the CSV file if it already exists.
    note: the function is used if you want to convert on JSON file and append the metadata to one CSV file.

    @param json_file_path: The path to the JSON file to read data from.
    @param csv_file_path: The path to the CSV file to write/append the data to.
    """

     #Create the csv file if it does not exist on csv_file_path
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Transaction_ID', 'From_Address (1:N)', 'To_Addresses[Value_received (satoshi)]', 'Value_Sent (satoshi)', 'Time_Of_Transaction'])

    # if csv file is empty, write the header row  first
    if os.stat(csv_file_path).st_size == 0:
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Transaction_ID', 'From_Address (1:N)', 'To_Addresses[Value_received (satoshi)]', 'Value_Sent (satoshi)', 'Time_Of_Transaction'])

    # Create a set to store the seen transaction IDs, that is, the transaction IDs that have already been written to the CSV file
    seen_transaction_ids = set()
    csv.field_size_limit(2147483647) # to avoid the error: _csv.Error: field larger than field limit (131072) 

    # Read the existing data from the CSV file and store the transaction IDs in the set
    with open(csv_file_path, 'r', newline='', errors='ignore') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            transaction_id = row[0]
            seen_transaction_ids.add(transaction_id)
    
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        
        if(data['txs'] == []):
            print("No transactions found in the JSON file. Exiting...")
            return

    # Open the CSV file for appending
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        
        for transactions in data['txs']:
            tx_hash = transactions['hash']
            # If the transaction ID has been seen before, skip this transaction
            if tx_hash in seen_transaction_ids:
                continue

            # Add the transaction ID to the set of seen transaction IDs
            seen_transaction_ids.add(tx_hash)
            tx_time = time.strftime('%Y-%m-%d %H:%M:%S%z', time.localtime(transactions['time']))

            for from_address in transactions['inputs']:
                prev_out = from_address['prev_out']
                from_addr = prev_out['addr']
                value_sent = prev_out['value']

                # list of to_addresses for each from_address with their associated values
                to_addresses = [f"{to_address['addr']}[{to_address['value']}]" for to_address in transactions['out']] 
                # Write a row for each from_address with all to_addresses
                writer.writerow([tx_hash, from_addr, str(to_addresses), value_sent, tx_time])

"""
import ast

# Convert the string back into a list for our DFS later (maybe)
to_addresses = ast.literal_eval(row['To_Addresses'])

"""
def convert_JSON_files_from_sub_folder(json_folder_path, csv_file_path):
    """
    @brief Convert all JSON files in a folder to a single CSV file. This function will append to the CSV file if it already exists.
    note: the function is used if you have a parent folder with one or several subfolders, with one or multiple json files inside each subfolder.

    @param json_folder_path: The path to the folder containing the subfolders.
    @param csv_file_path: The path to the CSV file to write the data to.
    """
    # if csv file is empty, write the header row  first
    if os.stat(csv_file_path).st_size == 0:
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Transaction_ID', 'From_Address (1:N)', 'To_Addresses[Value_received (satoshi)]', 'Value_Sent (satoshi)', 'Time_Of_Transaction'])

    # Create a set to store the seen transaction IDs, that is, the transaction IDs that have already been written to the CSV file
    seen_transaction_ids = set()
    csv.field_size_limit(2147483647) # to avoid the error: _csv.Error: field larger than field limit (131072) 

    # Read the existing data from the CSV file and store the transaction IDs in the set
    with open(csv_file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            transaction_id = row[0]
            seen_transaction_ids.add(transaction_id)

    # Open the CSV file for appending
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)

        # Iterate over the subfolders in the folder
        for subdir in os.listdir(json_folder_path):
            subdir_path = os.path.join(json_folder_path, subdir)
         
            if os.path.isdir(subdir_path):
                # Iterate over the JSON files in the subfolder
                for filename in os.listdir(subdir_path):
                    
                    if filename.endswith('.json'):
                        file_path = os.path.join(subdir_path, filename)
                        with open(file_path, 'r') as file:
                            data = json.load(file)
                            
                            if(data['txs'] == []):
                                print("No transactions found in the JSON file. Exiting...")
                                continue
                           
                        for transactions in data['txs']:
                            tx_hash = transactions['hash']
                            
                            # If the transaction ID has been seen before, skip this transaction
                            if tx_hash in seen_transaction_ids:
                                continue
              
                            # Add the transaction ID to the set of seen transaction IDs
                            seen_transaction_ids.add(tx_hash)

                            tx_time = time.strftime('%Y-%m-%d %H:%M:%S%z', time.localtime(transactions['time']))

                            for from_address in transactions['inputs']:
                                prev_out = from_address['prev_out']
                                from_addr = prev_out['addr']
                                value_sent = prev_out['value']

                                # list of to_addresses for each from_address with their associated values
                                to_addresses = [f"{to_address['addr']}[{to_address['value']}]" for to_address in transactions['out']] 
                                # Write a row for each from_address with all to_addresses
                                writer.writerow([tx_hash, from_addr, str(to_addresses), value_sent, tx_time])

def blockstream_convert_JSON_files_from_folder(json_folder_path, address):
    """
    @brief Convert all JSON files in a single folder to a single CSV file. This function will append to the CSV file if it already exists.
    note: the function is used on a specific subfolder path that contains the json files directly.

    @param json_folder_path: The path to the folder containing the json files.
    @param address: A string to name the folder and csv file as, use a bitcoin address as the string.
    """  
    data_csv_dir = os.path.join(parent_dir, "follow-the-money-of-crypto-currency-spam", "data_csv", address)

    #csv_file_path = "new_data/" + address #Set path of csv file we want to create
    if not os.path.isdir(data_csv_dir):
        os.makedirs(data_csv_dir)  # Create folder in new data path as it does not exist

    csv_file_path = os.path.join(data_csv_dir, f"{address}.csv") #Set path of csv file we want to create

     #Create the csv file if it does not exist on csv_file_path
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Transaction_ID', 'From_Address (1:N)', 'To_Addresses[Value_received (satoshi)]', 'Value_Sent (satoshi)', 'Time_Of_Transaction', 'TX_Count'])

    # if csv file is empty, write the header row  first
    if os.stat(csv_file_path).st_size == 0:
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Transaction_ID', 'From_Address (1:N)', 'To_Addresses[Value_received (satoshi)]', 'Value_Sent (satoshi)', 'Time_Of_Transaction', 'TX_Count'])

    # Create a set to store the seen transaction IDs, that is, the transaction IDs that have already been written to the CSV file
    seen_transaction_ids = set()
    csv.field_size_limit(2147483647) # to avoid the error: _csv.Error: field larger than field limit (131072) 

    # Read the existing data from the CSV file and store the transaction IDs in the set
    with open(csv_file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            transaction_id = row[0]
            seen_transaction_ids.add(transaction_id)

    # Open the CSV file for appending
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)

        if os.path.isdir(json_folder_path):
            # Iterate over the JSON files in the subfolder
            for filename in os.listdir(json_folder_path): #Info file must be read first to get the transaction count else we cant assign it on all rows
                file_path = os.path.join(json_folder_path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                if filename.endswith('info.json'): #Get transaction count from the info file
                    n_tx = data["chain_stats"]["tx_count"]
            # Iterate over the JSON files in the subfolder
            for filename in os.listdir(json_folder_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(json_folder_path, filename)
                    with open(file_path, 'r') as file:
                        data = json.load(file)

                    if filename.endswith('.json') and "info" not in filename: #Read transaction files
                        for transactions in data:
                            confirmed = transactions['status']['confirmed'] #Boolean, confirmed is true or false
                            if not confirmed: #If unconfirmed transaction, skip
                                continue
                            tx_hash = transactions['txid']
                            # If the transaction ID has been seen before, skip this transaction
                            if tx_hash in seen_transaction_ids:
                                continue
                            # Add the transaction ID to the set of seen transaction IDs
                            seen_transaction_ids.add(tx_hash)
                            block_time = transactions['status']['block_time']
                            dt_object = datetime.datetime.fromtimestamp(block_time)
                            tx_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                            for line in transactions['vin']:
                                from_address = line['prevout']['scriptpubkey_address']
                                from_value_sent = line['prevout']['value']
                                to_addresses = [f"{to_address['scriptpubkey_address']}[{to_address['value']}]" for to_address in transactions['vout'] if to_address.get('scriptpubkey_address') is not None]
                                writer.writerow([tx_hash, from_address, str(to_addresses), from_value_sent, tx_time, n_tx])
                                
def convert_JSON_files_from_folder(json_folder_path, csv_file_path):
    """
    @brief Convert all JSON files in a folder to a single CSV file. This function will append to the CSV file if it already exists.
    note: the function is used if you have a folder with one or multiple json files inside.

    @param json_folder_path: The path to the folder containing the JSON files.
    @param csv_file_path: The path to the CSV file to write the data to.
    """
    # if csv file is empty, write the header row  first
    if os.stat(csv_file_path).st_size == 0:
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Transaction_ID', 'From_Address (1:N)', 'To_Addresses[Value_received (satoshi)]', 'Value_Sent (satoshi)', 'Time_Of_Transaction'])

    # Create a set to store the seen transaction IDs, that is, the transaction IDs that have already been written to the CSV file
    seen_transaction_ids = set()
    csv.field_size_limit(2147483647) # to avoid the error: _csv.Error: field larger than field limit (131072) 

    # Read the existing data from the CSV file and store the transaction IDs in the set
    with open(csv_file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            transaction_id = row[0]
            seen_transaction_ids.add(transaction_id)

    # Open the CSV file for appending
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
          
        # Iterate over the files in the folder
        for filename in os.listdir(json_folder_path):
            
            if filename.endswith('.json'):
                file_path = os.path.join(json_folder_path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    
                    if(data['txs'] == []):
                        print("No transactions found in the JSON file. Exiting...")
                        continue
                    
                for transactions in data['txs']:
                    tx_hash = transactions['hash']
                    
                    # If the transaction ID has been seen before, skip this transaction
                    if tx_hash in seen_transaction_ids:
                        continue
        
                    # Add the transaction ID to the set of seen transaction IDs
                    seen_transaction_ids.add(tx_hash)

                    tx_time = time.strftime('%Y-%m-%d %H:%M:%S%z', time.localtime(transactions['time']))

                    for from_address in transactions['inputs']:
                        prev_out = from_address['prev_out']
                        from_addr = prev_out['addr']
                        value_sent = prev_out['value']

                        # list of to_addresses for each from_address with their associated values
                        to_addresses = [f"{to_address['addr']}[{to_address['value']}]" for to_address in transactions['out']] 
                        # Write a row for each from_address with all to_addresses
                        writer.writerow([tx_hash, from_addr, str(to_addresses), value_sent, tx_time])
"""                   
def convert_all_JSON_to_individual_CSV(olddata_path, newdata_path):
    for folder in os.listdir(olddata_path):
        old_folder_path = os.path.join(olddata_path, folder) #Join the olddata path with the individual folder
        if os.path.isdir(old_folder_path):
            new_folder_path = os.path.join(newdata_path, folder) #Join newdata path with the folder name so it matches with olddatas folder name
            create_folder(new_folder_path) #Create folder in new data path as it does not exist
            csv_file = os.path.join(new_folder_path, f"{os.path.basename(new_folder_path)}.csv") #Set path of csv file we want to create
            #Check if CSV file exists, if not create it, if it does ignore. But this stops us from appending to the file if it already exists
            if not os.path.exists(csv_file):
                for filename in os.listdir(old_folder_path): #Iterate over files in the current old data path folder
                    if filename.endswith('.json'):
                        json_file = os.path.join(old_folder_path, filename) #Get the path of the json file
                        convert_JSON_files_from_file_path(json_file, csv_file) #Convert the json file to csv and save it in the new folder
"""
def convert_all_JSON_to_individual_CSV(olddata_path, newdata_path):
    for folder in os.listdir(olddata_path):
        old_folder_path = os.path.join(olddata_path, folder)  # Join the olddata path with the individual folder
        if os.path.isdir(old_folder_path):
            new_folder_path = os.path.join(newdata_path, folder)  # Join newdata path with the folder name so it matches with olddata's folder name
            
            # Check if the new folder path exists, if not, create the folder
            if not os.path.isdir(new_folder_path):
                os.makedirs(new_folder_path)  # Create folder in new data path as it does not exist
            
            # file path of the csv file we want to create or if it already exists, append to it
            csv_file = os.path.join(new_folder_path, f"{os.path.basename(new_folder_path)}.csv")
            
            # Check if CSV file exists, if not, create it, if it does, ignore.
            # This stops us from appending to the file if it already exists.
            #if not os.path.exists(csv_file):
            for filename in os.listdir(old_folder_path):  # Iterate over files in the current old data path folder
                if filename.endswith('.json'):
                    json_file = os.path.join(old_folder_path, filename)  # Get the path of the json file
                    convert_JSON_files_from_file_path(json_file, csv_file)  # Convert the json file to csv and save it in the new folder

#Example input
#olddata_path = r"C:\Users\Anton\kandidat\data"
#newdata_path = r"C:\Users\Anton\kandidat\kod\follow-the-money-of-crypto-currency-spam\follow-the-money-of-crypto-currency-spam\data"
#json_folder_path = r"C:\Users\Anton\kandidat\kod\follow-the-money-of-crypto-currency-spam\follow-the-money-of-crypto-currency-spam\data_json\3HWz5JjvQ85tF1tLoTudeCXg4cgWeTeTqK"
#csv_path = r"C:\Users\Anton\kandidat\kod\follow-the-money-of-crypto-currency-spam\follow-the-money-of-crypto-currency-spam\test.csv"
#address = "3HWz5JjvQ85tF1tLoTudeCXg4cgWeTeTqK"
#blockstream_convert_JSON_files_from_folder(json_folder_path, address)
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

#blockstream_convert_JSON_files_from_folder(r"C:\Users\D-RTX3080\Desktop\gitlab\follow-the-money-of-crypto-currency-spam\data_json\358XUhiKFgzerNzdJk1WQA8aKz3GPRDzFU",r"C:\Users\D-RTX3080\Desktop\gitlab\follow-the-money-of-crypto-currency-spam\data_csv\358XUhiKFgzerNzdJk1WQA8aKz3GPRDzFU.csv")