import csv
import read_from_CSV
import convert_JsonToCsv as convert
import coinaddrvalidator as validator
import fetch as make_API_call
import os
import time
import pandas as pd
import statistics
#import record_data as recorder

# Get the current working directory of the script
cwd = os.getcwd()

# Get the parent directory of the current working directory
parent_dir = os.path.dirname(cwd)

# Set the directory to save the CSV files

# Constants for time spans
TIME_SPAN_DAY = 1440
TIME_SPAN_WEEK = TIME_SPAN_DAY * 7
TIME_SPAN_MONTH = TIME_SPAN_DAY * 30
TIME_SPAN_YEAR = TIME_SPAN_DAY * 365

# This class will hold the configuration options for the DFS function
class DFSConfig:
    """
    @brief Configuration options for the DFS function to specify the search type, time window, abuse type, etc.

    How it works:   The class will hold the configuration options for the DFS function.
                    The configuration options include the top_receivers_count, search_type, time_window, abuse_type, csv_file_path, start_address, previous_date, level, and Make_API_call.

    @param top_receivers_count: The number of top receivers to consider. Defaults to 5.
    @param search_type: The search type to use for the DFS function. Defaults to 'largest'.
    @param time_window: The time window to consider for the search. Defaults to None.
    @param abuse_type: The abuse type to consider for the search. Defaults to None.
    @param csv_file_path: The path to the CSV file for the address. Defaults to None.
    @param start_address: The address to start the search from. Defaults to None.
    @param previous_date: A holder for the previous date that can be used in the search to log the date of certain transactions. Defaults to None.
    @param level: The depth of the search (i.e. how many levels to traverse). Defaults to None.
    @param Make_API_call: A flag to indicate whether to make an API call to fetch the transactions for the address. Defaults to False.
    """
    def __init__(self, top_receivers_count=5, search_type='largest', time_window=None, abuse_type=None, csv_file_path=None, start_address=None, previous_date=None, level = None, Make_API_call=False):
        self.top_receivers_count = top_receivers_count
        self.search_type = search_type
        self.time_window = time_window
        self.abuse_type = abuse_type
        self.csv_file_path = csv_file_path
        self.start_address = start_address
        self.previous_date = previous_date
        self.level = level
        self.Make_API_call = Make_API_call
         
def get_transaction_based_on_search_type(csv_file_path, parent_address, current_date, config, value_received_in_satoshi=None):
    """
    @brief Get the transaction based on the search type specified in the configuration options for the DFS function.

    How it works:   The function will check the search type specified in the configuration options.
                    If the search type is 'nearest', it will get the nearest transaction based on the time window specified in the configuration options.
                    If the search type is 'largest', it will get the largest transaction based on the value received in satoshi and the time window specified in the configuration options.

    @param csv_file_path: The path to the CSV file for the address.
    @param parent_address: The address to start the search from.
    @param current_date: The date to start the search from.
    @param config: The configuration options for the DFS function.
    @param value_received_in_satoshi: The value received in satoshi. Defaults to None.

    @return: The selected transaction based on the search type specified in the configuration options.
    """
    if config.search_type == 'nearest':
        return read_from_CSV.get_nearest_sent_transaction(csv_file_path, parent_address, current_date, config.time_window)
    elif config.search_type == 'largest':
        return read_from_CSV.get_largest_sent_transaction(csv_file_path, parent_address, current_date, value_received_in_satoshi, config.time_window)
    else:
        raise ValueError("Invalid search_type. Choose either 'nearest' or 'largest'.")
    
def handle_missing_address(parent_address, level, current_date, depth, state, config):
    """
    @brief Handle the case where the address is missing or a dead-end in the dataset by updating the state of the DFS.

    How it works:   The function will check if the address is valid. If the address is not valid, it will update the state of the DFS to 'invalid'.
                    If the API call has not been made before for this address, it will make the API call to fetch the transactions for the address.
                    If the API call has been made before for this address, it will recheck for the CSV file path in case the dataset has been updated.

    @param parent_address: The address to start the search from (i.e. the missing or dead-end address).
    @param level: The depth of the search (i.e. how many levels to traverse).
    @param current_date: The date to start the search from.
    @param depth: The current depth of the search.
    @param state: Dictionary to hold the state of the DFS.
    @param config: The configuration options for the DFS function.

    @return: The CSV file path for the address if it is found, otherwise None.
    """
    addr_is_valid = validator.validate('btc', parent_address)
    if not addr_is_valid.valid:
        #print(f"Address {parent_address} is not valid")
        state['address_markers'][parent_address] = 'invalid'
        #return

    # Check if the API call has been made before for this address and make the API call if not
    if parent_address not in state['api_calls_made']:
        #print(f"Making API call for address: {parent_address}")
        state['api_calls_made'].add(parent_address) # Mark that an API call has been made for this address
        if config.Make_API_call == True:
            make_API_call.blockstream_fetch(parent_address, transactions_to_collect=1000)
            data_json_dir = os.path.join(cwd, "data_json", parent_address)
            data_csv_dir = os.path.join(parent_dir, "data_csv", parent_address + ".csv")
            convert.blockstream_convert_JSON_files_from_folder(data_json_dir, parent_address)
    
    # After making an API call, recheck for the CSV file path in case the dataset has been updated
    csv_file_path = read_from_CSV.check_address_folder(parent_address)
    if csv_file_path is None:
        state['address_markers'][parent_address] = 'missing or dead-end'
    else:
        return dfs(parent_address, level, current_date, depth, state, config)
        # **************************   Here we can update address_markers as needed (i.e. 'missing or dead-end' or 'invalid' and so on) and save it to a file if we want to   
    # Update address_markers as needed (i.e. 'missing or dead-end' or 'invalid' and so on)

def process_selected_transaction(selected_transaction, parent_address, level, current_date, depth, state, config):
    """
    @brief Process the selected transaction and update the state of the DFS based on the selected transaction.

    How it works:   The function will check if the selected transaction is None. If it is None, it will update the state of the DFS to 'no_transaction' which means that no transaction was found for the address.
                    If the level is 0, it will update the state of the DFS to 'max_depth_reached' which means that the maximum depth has been reached.
                    If the selected transaction is not None and the level is not 0, it will process the selected transaction and update the state of the DFS.
                    The function will then recursively call itself with the next address as the parent_address until the specified level of depth is reached.
    
    @param selected_transaction: The selected transaction to process.
    @param parent_address: The address to start the search from.
    @param level: The depth of the search (i.e. how many levels to traverse).
    @param current_date: The date to start the search from (i.e. the date of the parent transaction).
    @param depth: The current depth of the search.
    @param state: Dictionary to hold the state of the DFS.
    @param config: The configuration options for the DFS function.
    
    @return: None
    """
    
    if selected_transaction is None:
        #print(f"{' ' * depth}No From_address found in the CSV file at depth {depth} for {parent_address}")
        state['address_markers'][parent_address] = 'no_transaction'
        return
    elif level == 0:
        state['address_markers'][parent_address] = 'max_depth_reached' # the to-address will be the max depth reached
        write_to_csv(None, depth, parent_address, None, None, None, None, config.previous_date, state)
        return
    else:
        largest_receivers = read_from_CSV.get_largest_receivers(selected_transaction, top_n=config.top_receivers_count)
        if not largest_receivers:
            #print(f"{' ' * depth}Leaf node: No next addresses found at depth {depth} for {parent_address}")
            state['address_markers'][parent_address] = 'leaf_node'
            write_to_csv(None, depth, parent_address, None, None, None, None, None, state)
            return
        else:
            for receiver in largest_receivers:
                next_address, value_received, transaction_date, total_value_sent_by_parent, number_of_splits = receiver[1], receiver[2], receiver[3], receiver[4], receiver[5]
                if next_address in state['visited']:
                    if level >= 1: # only register flow-backs if we are not at max depth
                        state['address_markers'][parent_address] = 'flow_back'
                        #print(f"{' ' * depth}Depth {depth}: Flow-back detected to address {next_address}")
                        Tx_ID = selected_transaction[0][0]
                        write_to_csv(Tx_ID, depth, parent_address, None, None, None, None, None, state)
                else:
                    state['visited'].append(next_address)
                    #print(f"{' ' * depth}Depth {depth}: Parent address: {parent_address} | Next address: {next_address} | Value received: {value_received} | Transaction date: {transaction_date}")
                    Tx_ID = selected_transaction[0][0]
                    write_to_csv(Tx_ID, depth, parent_address, next_address, total_value_sent_by_parent, value_received, number_of_splits, transaction_date, state)
                    config.previous_date = transaction_date # Save the previous date to be used in the last write_to_csv for max depth, otherwise it will give the date for "max depth + 1"
  
                    dfs(next_address, level - 1, transaction_date, depth + 1, state, config)

def dfs(parent_address, level, current_date, depth=0, state=None, config=None):
    """
    @brief Perform a Depth-First Search (DFS) on the Bitcoin transaction graph starting from the given address.
    The search is performed up to the specified level of depth.

    How it works:   The function will start at the parent_address and search for the nearest or largest transaction based on the search_type specified in the config.
                    It will then process the selected transaction and update the state of the DFS.
                    If the level is not reached, the function will recursively call itself with the next address as the parent_address.
                    The function will continue until the specified level of depth is reached.

    @param parent_address: The address to start the search from.
    @param level: The depth of the search (i.e. how many levels to traverse).
    @param current_date: The date to start the search from (i.e. the date of the parent transaction).
    @param depth: The current depth of the search. Defaults to 0.
    @param state: Dictionary to hold the state of the DFS. Defaults to None. The state will be updated as the DFS progresses.
    @param config: The configuration options for the DFS function. Defaults to None. The configuration options will be used to specify the search type, time window, etc.

    @return: The state of the DFS after the search has been completed.
    """
    if config is None:
        config = DFSConfig() # Default configuration options : top_receivers_count=5, search_type='nearest', time_window=None, abuse_type=None, csv_file_path=None, start_address=None
    
    # Initialize the state and configuration options if not provided as arguments
    if state is None:
        state = {'visited': [parent_address], 'address_markers': {}, 'api_calls_made': set()}
        config.start_address = parent_address
        config.level = level
        prepare_folders()

    if level == -1:
        #print(f"{' ' * depth}Reached max depth at address {parent_address}")
        return state['address_markers']

    csv_file_path = read_from_CSV.check_address_folder(parent_address)
    if csv_file_path is None:
        csv_file_path = handle_missing_address(parent_address, level, current_date, depth, state, config)
    # Check if the address is valid and proceed with the updated dataset     
    else:
        selected_transaction = get_transaction_based_on_search_type(csv_file_path, parent_address, current_date, config) # default : value_received_in_satoshi=None. It means it will not be used in get_largest_sent_transaction
        process_selected_transaction(selected_transaction, parent_address, level, current_date, depth, state, config)

    return state['address_markers']

#################################### ****************************** Write new dataset to file and write analytic to file  ****************************** ####################################

def write_to_csv(Tx_ID, depth, from_address, to_address, total_value_sent, value_received, number_of_splits, time_of_transaction, state):
    csv_file_path = config.csv_file_path  # Ensure config.csv_file_path is defined in your configuration
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    # Determine if we need to write the header
    write_header = not os.path.exists(csv_file_path) or os.stat(csv_file_path).st_size == 0

    # Open the file in append mode to prevent overwriting
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)

        # Write the header if needed
        if write_header:
            writer.writerow(['Depth', 'From', 'To', 'Total_Value_Sent', 'value_received', 'Number_Of_Splits', 'Time_Of_Transaction', 'TX_Count', 'To_Addresses_Nr', 'Unique_To_Addresses_Nr', 'State_Comment', 'Tx_ID'])

        recorded_list = count_addresses_sent_to(from_address)
        total_address_counter = recorded_list[0]
        unique_address_counter = recorded_list[1]
        tx_count = recorded_list[2]
        # Write the data row
        """" #Commented out because we only write state_comments on the from address, not the to address
        if state['address_markers'].get(from_address) is None:
            if state['address_markers'].get(to_address) == 'max_depth_reached':
                state_comment = 'max_depth_reached'
            elif state['address_markers'].get(to_address) == 'flow_back':
                state_comment = 'flow_back'
            else:
                state_comment = None
            writer.writerow([depth, from_address, to_address, total_value_sent, value_received, number_of_splits, time_of_transaction, tx_count, total_address_counter, unique_address_counter, state_comment])
        else:
        """
        state_comment = state['address_markers'].get(from_address)
        if state_comment == "flow_back" and to_address in state['visited']:
            state_comment = '' #Prevents multiple flow_backs to be written to csv for a single from_address. Now only writes to the row with empty "to_address"
        writer.writerow([depth, from_address, to_address, total_value_sent, value_received, number_of_splits, time_of_transaction, tx_count, total_address_counter, unique_address_counter, state_comment, Tx_ID])

def count_addresses_sent_to(address):
    """
    @brief This function will return the total number of addresses and the number of unique addresses that the address has sent to.

    @param address: The address to count the number of addresses sent to.
    @output: A list containing the total number of addresses[0] and the number of unique addresses[1] that the address has sent to.
    """
    return_list = []
    unique_address_counter = 0
    row_addresses = ""
    total_address_counter = 0
    tx_count = 0
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

def prepare_folders():
    width = config.top_receivers_count
    level = config.level
    folder_name = os.path.join(cwd, "data_dfs", str(width) + "_" + str(level), config.abuse_type) # absolute path from cwd
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    config.csv_file_path = os.path.join(folder_name, config.start_address + ".csv") # absolute path from cwd
    if os.path.exists(config.csv_file_path): #Remove the file if it already exists so we dont append more info to it, we rewrite the entire file instead
        os.remove(config.csv_file_path)

def sum_results(width, level, abuse_type):
    # Construct the folder path
    abuse_type_folder = os.path.join(cwd, "data_dfs", f"{width}_{level}", abuse_type)
    # Write the results to a CSV file
    summed_results_path = os.path.join(abuse_type_folder, "summed_results.csv")
    # if csv file already exists, remove it
    if os.path.exists(summed_results_path):
        os.remove(summed_results_path)
    
    total = 0
  #  for k in range(1, level + 1):
  #      print(f"level: {k} total: {total} + {width ** (k - 1)}") # number of nodes at each level, i.e. if all addresses are unique we will have this many nodes
  #      total += width ** (k - 1)

    # Initialize variables
    stats = {
        "total_value_sent": 0,
        "value_received": 0,
        "number_of_splits": 0,
        "tx_count": 0,
        "to_addresses_nr": 0,
        "unique_to_addresses_nr": 0,
        "edges_followed": 0,
        "max_nodes_visited": 0, #(((width**level) - 1) // (width - 1)) 
        #"followed_transactions": 0,
        "two_tx_count": 0,  # Onion peel wallets
        "deadend_count": 0,  # No outgoing transaction wallet
        "flow_back": 0,
        "splits_per_tx": 0,
        "actual_nodes_visited": 0,
        "max_depth_count": 0,
        "sending_addresses": 0
    }

    calculated_stats = {
        "splits_per_edge": 0,
        "percentage_2_tx": 0,
        "percentage_deadend": 0,
        "percentage_flow_back": 0,
        "percentage_maxdepth": 0,
        "value_sent_per_edge": 0,
        "value_received_per_edge": 0,
        "to_addresses_per_node": 0,
        "average_tx_per_node": 0,
        "median_tx_per_node": 0
    }
    
    # Process each CSV file in the directory
    for file_name in os.listdir(abuse_type_folder):
        if file_name.endswith(".csv"):
            csv_file_path = os.path.join(abuse_type_folder, file_name)
            with open(csv_file_path, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)  # Skip header row
                from_addr = []
                median_tx_count_list = []
                categorized_addr = []
                total += (((width**(level+1)) - 1) // (width - 1)) #-1 #-1 at end gives us max number of graph edges or nodes moved to from start node. without -1 we get max number of nodes in the graph
                for row in reader:
                    if row[1] not in from_addr: #Only count each from addr once since they can appear several times and their columns have the same values which would otherwise be counted multiple times
                        #The values in this if statement appear several times and are based on the from address, so we only want to count them once per from address
                        from_addr.append(row[1])
                        stats["tx_count"] += int(row[7]) if row[7].isdigit() else 0
                        stats["to_addresses_nr"] += int(row[8]) if row[8].isdigit() else 0
                        stats["unique_to_addresses_nr"] += int(row[9]) if row[9].isdigit() else 0
                        median_tx_count_list.append(int(row[7])) if row[7].isdigit() else 0
                        if row[5].isdigit():
                            stats["number_of_splits"] += int(row[5]) # if num = 1 then it is a single transaction, if num > 1 then it is a split transaction (multiple outputs)
                        if row[3].isdigit():
                            stats["total_value_sent"] += int(row[3]) if row[10] != 'flow_back' else 0 # if flow_back then we dont add the value to 'total_value_sent'
                        if row[7] == '2':
                            stats["two_tx_count"] += 1
                        stats["sending_addresses"] += 1
                    if row[10] == 'leaf_node':
                        stats["deadend_count"] += 1
                    if row[10] == 'flow_back':
                        stats["flow_back"] += 1
                    if row [10] == 'max_depth_reached':
                        stats["max_depth_count"] += 1
                    if row[4].isdigit():
                        stats["value_received"] += int(row[4]) if row[10] != 'flow_back' else 0 # if flow_back then we dont add the value to 'value_received
                        #stats["number_of_splits"] += int(row[5]) # if num = 1 then it is a single transaction, if num > 1 then it is a split transaction (multiple outputs)
                        #stats["followed_transactions"] += 1 # ************************** problemet här är att vi inte loggar tx_id, så det kan finnas case där vi följer samma tx flera gånger *************************** dvs en loop som inte är back-flow
                    if row[2] != "": #Dont count the last nodes visited without a to_address
                        stats["edges_followed"] += 1 # Detta är "edges" i en trägraf, dvs antalet noder som besökts från startnoden (startnod ej medräknat)
                stats["actual_nodes_visited"] += len(from_addr)
            stats["max_nodes_visited"] = total # for each file we add the total number of nodes at each level
    #print("total value sent: ", stats["total_value_sent"])
    stats["unique_to_addresses_nr"] = stats["to_addresses_nr"] - stats["unique_to_addresses_nr"] #Gets us the number of addresses that have been sent to more than once
    calculated_stats["splits_per_edge"] = stats["number_of_splits"] / stats["sending_addresses"] #Edges being the transactions we followed, each transaction having a number of splits
    calculated_stats["percentage_2_tx"] = round((stats["two_tx_count"] / stats["actual_nodes_visited"]),2) #Nodes being the wallet we visited
    calculated_stats["percentage_deadend"] = round((stats["deadend_count"] / stats["actual_nodes_visited"]),2)
    calculated_stats["percentage_flow_back"] = round((stats["flow_back"] / stats["actual_nodes_visited"]),2)
    calculated_stats["percentage_maxdepth"] = round((stats["max_depth_count"] / stats["actual_nodes_visited"]),2)
    calculated_stats["value_sent_per_edge"] = round(stats["total_value_sent"] / stats["sending_addresses"], 2)
    calculated_stats["value_received_per_edge"] = round(stats["value_received"] / stats["edges_followed"], 2)
    calculated_stats["to_addresses_per_node"] = round(stats["to_addresses_nr"] / stats["actual_nodes_visited"], 2)
    calculated_stats["average_tx_per_node"] = round(stats["tx_count"] / stats["actual_nodes_visited"], 2)
    calculated_stats["median_tx_per_node"] = statistics.median(median_tx_count_list)

    with open(summed_results_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Raw Stats'])
        writer.writerow(['Maximum Node Visits', 'Actual Node Visits', 'Edges Followed', 'Total_Value_Sent', 'Value_Received', 'Splits',
                        'TX_Count', 'To_Addr_Count', 'Re_Used_Addrs', '2_TX_Count', 'Deadend_Count', 'Flow_Back_Count'])
        writer.writerow([
            stats["max_nodes_visited"], stats["actual_nodes_visited"], stats["edges_followed"],
            stats["total_value_sent"], stats["value_received"], stats["number_of_splits"],
            stats["tx_count"], stats["to_addresses_nr"], stats["unique_to_addresses_nr"],
            stats["two_tx_count"], stats["deadend_count"], stats["flow_back"]
        ])
        writer.writerow([]) #Skip row for formatting
        writer.writerow(['Calculated Stats'])
        writer.writerow(['Average Value Received per Edge', 'Average Value Sent per Edge', 'Average Splits per Edge', '% of 2 TX Addresses', '% of Deadend Addresses', 
                         '% of Flow Back Addresses', 'Average To Addresses Amount per Node', 'Average TX Amount per Node', 'Median TX Amount per Node', '% of Max Depth Addresses'])
        writer.writerow([
            calculated_stats["value_received_per_edge"], calculated_stats["value_sent_per_edge"],
            calculated_stats["splits_per_edge"], calculated_stats["percentage_2_tx"],
            calculated_stats["percentage_deadend"], calculated_stats["percentage_flow_back"], 
            calculated_stats["to_addresses_per_node"], calculated_stats["average_tx_per_node"], calculated_stats["median_tx_per_node"], calculated_stats["percentage_maxdepth"]
        ])

#################################### ****************************** Testing ****************************** ####################################

# set the configuration options for the DFS function: note set the config.Make_API_call to True if you want to make API calls
sum_results(2, 10, "darknet")
sum_results(2, 10, "blackmail")
sum_results(4, 5, "darknet")
sum_results(4, 5, "blackmail")
sum_results(2, 10, "tumbler")
sum_results(2, 10, "ransomware")
sum_results(4, 5, "tumbler")
sum_results(4, 5, "ransomware")
"""
with open('root_Darknet_addresses.txt') as f:
    # Initialize the configuration options for the DFS function
    config = DFSConfig(top_receivers_count=2, search_type='largest', time_window=TIME_SPAN_YEAR, abuse_type="darknet", Make_API_call=False) # top_receivers_count=10, search_type='largest', time_window=5 * TIME_SPAN_YEAR 
    # Run the DFS function for each address in the file
   # print("Running DFS for Darknet addresses")
    for line in f:
        # helper: dfs(parent_address, level, current_date, depth, state, config)
        address_markers = dfs(line.strip(), 20, None, 0, None, config)
        #if(address_markers is not None):
            #print(f"\n                Marked addresses for DFS-run with root-node \n                {address_markers}")
        #print("Done with DFS for Darknet addresses")
       # print("\n\n")

    sum_results(config.top_receivers_count, 10, config.abuse_type)
"""
"""
with open('root_Darknet_addresses.txt') as f:
    config = DFSConfig(top_receivers_count=4, search_type='largest', time_window=TIME_SPAN_YEAR, abuse_type="darknet") # top_receivers_count=10, search_type='largest', time_window=5 * TIME_SPAN_YEAR 
    # Run the DFS function for each address in the file
    for line in f:
        # helper: dfs(parent_address, level, current_date, depth, state, config)
        address_markers = dfs(line.strip(), 5, None, 0, None, config)
       # if(address_markers is not None):
       #     print(f"\n                Marked addresses for DFS-run with root-node \n                {address_markers}")
        print("\n\n")

   # sum_results(config.top_receivers_count, 5, config.abuse_type)
"""
"""
with open('root_Blackmail_addresses.txt') as f:
    # Initialize the configuration options for the DFS function
    config = DFSConfig(top_receivers_count=2, search_type='largest', time_window=TIME_SPAN_YEAR, abuse_type="blackmail", Make_API_call=False) # top_receivers_count=10, search_type='largest', time_window=5 * TIME_SPAN_YEAR 
    #print("Running DFS for Blackmail addresses")
    for line in f:
        # helper: dfs(parent_address, level, current_date, depth, state, config)
        address_markers = dfs(line.strip(), 20, None, 0, None, config)
       # if(address_markers is not None):
       #     print(f"\n                Marked addresses for DFS-run with root-node \n                {address_markers}")
        #print("Done with DFS for Blackmail addresses")
       # print("\n\n")
    
    sum_results(2, 20, "blackmail")
"""
"""
with open('root_Blackmail_addresses.txt') as f:    
    config = DFSConfig(top_receivers_count=4, search_type='largest', time_window=TIME_SPAN_YEAR, abuse_type="blackmail") # top_receivers_count=10, search_type='largest', time_window=5 * TIME_SPAN_YEAR 
    # Run the DFS function for each address in the file
    for line in f:
        # helper: dfs(parent_address, level, current_date, depth, state, config)
        address_markers = dfs(line.strip(), 5, None, 0, None, config)
        #if(address_markers is not None):
         #   print(f"\n                Marked addresses for DFS-run with root-node \n                {address_markers}")
        print("\n\n")
    
    #sum_results(config.top_receivers_count, 5, config.abuse_type)

"""
#sum_results(2, 20, "blackmail")
#sum_results(2, 20, "darknet")