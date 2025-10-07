'''
A script to read from a CSV file. This script is used with the DFS algorithm to find the largest receiver of a given address.
functions
- check_address_folder(address) - Check if the address folder exists in the data folder and return the path to the subfolder CSV file if it exists.
- get_nearest_send_transaction(csv_file_path, from_address, from_time=None) - Get the nearest "sent" transaction from the given time of transaction and return its row.
- get_largest_receiver(nearest_send_transaction) - Get the receiver with the largest value received from the given transaction.
'''
import csv
import coinaddrvalidator
import ast
from datetime import datetime, timedelta
import random
import os

# Get the current working directory of the script
cwd = os.getcwd()
# Get the parent directory of the current working directory
parent_dir = os.path.dirname(cwd)

def check_address_folder(address):
    """
    @brief Check if the address folder exists in the data folder and return the path to the subfolder CSV file if it exists.
    @param address: The address to check for in the data folder.
    @return csv_file_path: The path to the subfolder CSV file if it exists, otherwise None.
    """
    data_folder = 'data_csv'  # No leading slash #data or testData
    subfolder_name = address
    subfolder_path = os.path.join("follow-the-money-of-crypto-currency-spam", data_folder, subfolder_name)
    csv_file_path = os.path.join(parent_dir, subfolder_path, address + '.csv')
    if os.path.exists(csv_file_path):  # Check if the subfolder CSV file exists
        return csv_file_path
    else:
        return None

def get_nearest_sent_transaction(csv_file_path, from_address, from_time=None, time_window=None):
    """
    @brief Find the nearest "sent" transaction from the given time of transaction within a specified time span.
    If no time span is given, return the nearest transaction after from_time.
    If from_time is not provided, return the first sent transaction.

    @param csv_file_path: Path to the CSV file containing transactions.
    @param from_address: Address to find transactions from.
    @param from_time: Start time to search for transactions (inclusive).
    @param time_window: Time span in minutes within which to find a transaction after from_time.
    @return: The row of the nearest "sent" transaction or a random one within the time span.
    """
    if csv_file_path is None or from_address is None:
        return None

    from_time_dt = datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S") if from_time else None
    transactions_within_span = []

    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row

        for row in reader:
            if row[1] == from_address:  # Check if the row corresponds to a "sent" transaction from the address
                transaction_time_dt = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")

                if from_time_dt:
                    if time_window:
                        time_span_end = from_time_dt + timedelta(minutes=time_window)
                        if from_time_dt <= transaction_time_dt <= time_span_end:
                            transactions_within_span.append(row)
                    elif transaction_time_dt > from_time_dt:
                        transactions_within_span.append(row)
                else:
                    # If from_time is not provided, just consider all "sent" transactions
                    transactions_within_span.append(row)

    if transactions_within_span:
        if time_window:
            # If a time span is provided, select a random transaction within the span
            return random.choice(transactions_within_span)
        else:
            # If no time span is provided, find the transaction closest to from_time or simply the first one if from_time is not provided
            transactions_within_span.sort(key=lambda x: datetime.strptime(x[4], "%Y-%m-%d %H:%M:%S"))
            return transactions_within_span[0] if from_time_dt else transactions_within_span[-1]  # Return the last transaction if no from_time is provided
    else:
        return None  # Return None if no matching transactions are found

def get_largest_sent_transaction(csv_file_path, from_address, from_time=None, value_received_in_satoshi=None, time_window=None):
    """
    @brief Find the largest "sent" transaction from the given time of transaction within a specified time span.
    If no time span is given, return the largest transaction after from_time.
    If from_time is not provided, return the largest sent transaction.
    Also, return the total sum of the transaction and the number of splits in the transaction, in case they are needed for further analysis.
    
    @param csv_file_path: Path to the CSV file containing transactions.
    @param from_address: Address to find transactions from.
    @param from_time: Start time to search for transactions (inclusive).
    @param value_in_satoshi: Exact value to match in transactions.
    @param time_window: Time span in minutes within which to find the largest transaction after from_time.
    @return: A tuple containing the row of the largest "sent" transaction meeting the criteria, and a tuple of the total sum and the number of splits in the transaction.
    """
    if csv_file_path is None or from_address is None:
        return None

    # Increase the field size limit to handle large values in the CSV file
    csv.field_size_limit(2147483647)

    # Convert the time window to a timedelta object for comparison 
    from_time_dt = datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S") if from_time else None
    # Calculate the end of the time span if both from_time and time_window are provided
    time_span_end = from_time_dt + timedelta(minutes=time_window) if from_time and time_window else None
    transaction_aggregates = {}  # Store total sum of values and split counts for each transaction ID

    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row

        for row in reader:
            transaction_id, transaction_from_address, to_addresses_str, transaction_value, transaction_time_str, number_of_transactions = row
            transaction_value = int(transaction_value)
            transaction_time_dt = datetime.strptime(transaction_time_str, "%Y-%m-%d %H:%M:%S")

            # Check if the row corresponds to a "sent" transaction from the address within the specified time span (if provided)
            if transaction_from_address == from_address and (not from_time_dt or (transaction_time_dt > from_time_dt and (not time_span_end or transaction_time_dt <= time_span_end))):
                if transaction_id not in transaction_aggregates:
                    transaction_aggregates[transaction_id] = {'value': 0, 'splits': 0, 'row': row}

                # Aggregate (total) transaction values by ID and count splits
                transaction_aggregates[transaction_id]['value'] += transaction_value
                transaction_aggregates[transaction_id]['splits'] += 1

    """
    @brief Find the largest transaction by value from the aggregated (i.e. the total sum) transactions. That is, a wallet address that has sent the largest amount of crypto. 
    If no transactions are found, return None.
    """ 
    largest_transaction_id = max(transaction_aggregates, key=lambda tid: transaction_aggregates[tid]['value'], default=None)
    # Get the details of the largest transaction if it exists
    largest_transaction_details = transaction_aggregates[largest_transaction_id] if largest_transaction_id else None

    # Return the transaction row along with the total sum and the number of splits
    return (largest_transaction_details['row'], (largest_transaction_details['value'], largest_transaction_details['splits'])) if largest_transaction_details else (None, (0, 0))

def get_largest_receivers(nearest_send_transaction, top_n=5):
    """
    @brief Get up to 'top_n' receivers with the largest values received from the given transaction.
    
    @param nearest_send_transaction: The transaction to search from.
    @param top_n: The number of top receivers to return. Defaults to 5.
    
    @return:
    A list of tuples, each containing the transaction ID, a receiver address, the value received by that address, and the date.
    Each tuple represents one of the top 'top_n' receivers by value received. If fewer receivers exist, the list will contain fewer tuples.
    """
    if nearest_send_transaction is None or nearest_send_transaction[0] is None:
        return None

    # Extracting the transaction row from the modified structure
    transaction_row, additional_info = nearest_send_transaction
   # nearest_send_transaction = nearest_send_transaction[0]
    total_sum, splits = additional_info  # These could be used for additional context or logic if we want to use the total sum or the number of splits
    
    # Increase the field size limit to handle large values in the CSV file
    csv.field_size_limit(2147483647)

    to_addresses = ast.literal_eval(transaction_row[2])
    receivers = {}
    
    # Aggregate values sent to each address
    for addr_value in to_addresses:
        receiver_address, value = addr_value.split('[')
        value = int(value.rstrip(']'))
        if receiver_address not in receivers:
            receivers[receiver_address] = 0
        receivers[receiver_address] += value

    # Convert dict to list of tuples and sort
    sorted_receivers = sorted(receivers.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # Prepare the return list with transaction ID, address, value, and date for each of the largest receivers
    result = [(transaction_row[0], receiver[0], receiver[1], transaction_row[4], total_sum, splits) for receiver in sorted_receivers]

    return result

"""
def get_largest_sent_transaction(csv_file_path, from_address, from_time=None, value_received_in_satoshi=None, time_window=None):
   
    @brief Find the largest "sent" transaction from the given time of transaction within a specified time span.
    If no time span is given, return the largest transaction after from_time.
    If from_time is not provided, return the largest sent transaction.
    
    @param csv_file_path: Path to the CSV file containing transactions.
    @param from_address: Address to find transactions from.
    @param from_time: Start time to search for transactions (inclusive).
    @param value_in_satoshi: Exact value to match in transactions.
    @param time_window: Time span in minutes within which to find the largest transaction after from_time.
    @return: The row of the largest "sent" transaction meeting the criteria.
    
    if csv_file_path is None or from_address is None:
        return None

    from_time_dt = datetime.strptime(from_time, "%Y-%m-%d %H:%M:%S") if from_time else None
    time_span_end = from_time_dt + timedelta(minutes=time_window) if from_time and time_window else None
    largest_transaction = None
    largest_value = 0

    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row

        for row in reader:
            if row[1] == from_address:  # Check if the row corresponds to a "sent" transaction from the address
                transaction_value = int(row[3])
                transaction_time_dt = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")

                # If a time is provided, find the largest transaction within the time span
                if from_time_dt and transaction_time_dt > from_time_dt and (not time_span_end or transaction_time_dt <= time_span_end):
                    # If a specific value is provided, return the transaction with that value
                    if value_received_in_satoshi and transaction_value == value_received_in_satoshi:
                        return row
                    # If no specific value is provided, find the largest transaction (sent value-wise)
                    elif not value_received_in_satoshi and transaction_value > largest_value:
                        largest_transaction = row
                        largest_value = transaction_value
                # If no time is provided, find the largest transaction based on the value alone
                elif not from_time_dt:
                    # If a specific value is provided, return the transaction with that value
                    if value_received_in_satoshi and transaction_value == value_received_in_satoshi:
                        return row
                    # If no specific value is provided, find the largest transaction (sent value-wise)
                    elif not value_received_in_satoshi and transaction_value > largest_value:
                        largest_transaction = row
                        largest_value = transaction_value

    return largest_transaction

def get_largest_receivers(nearest_send_transaction, top_n=5):
    
    @brief Get up to 'top_n' receivers with the largest values received from the given transaction.
    
    @param nearest_send_transaction: The transaction to search from.
    @param top_n: The number of top receivers to return. Defaults to 5.
    
    @return:
    A list of tuples, each containing the transaction ID, a receiver address, the value received by that address, and the date.
    Each tuple represents one of the top 'top_n' receivers by value received. If fewer receivers exist, the list will contain fewer tuples.
    
    if nearest_send_transaction is None:
        return None
    
    csv.field_size_limit(2147483647)
    to_addresses = ast.literal_eval(nearest_send_transaction[2])
    receivers = []
    
    for addr_value in to_addresses:
        receiver_address, value = addr_value.split('[')
        value = int(value.rstrip(']'))
        receivers.append((receiver_address, value))

    # Sort the receivers by value in descending order and select the top 'top_n'
    largest_receivers = sorted(receivers, key=lambda x: x[1], reverse=True)[:top_n]

    # Prepare the return list with transaction ID, address, value, and date for each of the largest receivers
    result = [(nearest_send_transaction[0], receiver[0], receiver[1], nearest_send_transaction[4]) for receiver in largest_receivers]

    return result

"""