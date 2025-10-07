import pandas as pd
import csv
import re

#Returns the to_adress that the given from_adress sends the largest transaction to
def get_biggest_transaction_from_adress(from_adress, csv_file):
   with open (csv_path, 'r') as file:
      data_by_row = []
      reader = csv.reader(file)
      next(reader) #Skip header
      indexCounter = 1
      for row in reader:
          if (row[1] == from_adress): #Match from_adress string with the from_adress in csv file
            savedIndex = indexCounter #To find which row we should look in for the "to_adresses"
            break
          indexCounter = indexCounter + 1
      # Find all numbers enclosed within square brackets in the cell value
      numbers = re.findall(r'\[(\d+)\]', row[2]) #Row[2] is the "To_Adresses[Value_received] field"
      # Extract strings from cell value
      strings = re.findall(r'(\w+)\[\d+\]', row[2])
      # Append each pair of (string, number) to data_by_row
      data_by_row.append(list(zip(strings, map(int, numbers))))
      maxValue = 0 #Saving maxvalue found in each iteratioon.
      savedIndex = 0 #Internal list index.
      indexCounter = 0
      #print(data_by_row[0][0])
      for row in data_by_row:
        #print(row)
        for pair in row: #Iterate over our list
          #print(pair)
          number = pair[1]  # Get the number part of the tuple
          if number > maxValue: #If the new number has a higher value than last maxvalue
            maxValue = number #Store the up until now largest value for a transaction
            savedIndex = indexCounter #Save the index of the highest valued transaction
          indexCounter = indexCounter + 1
      #print(data_by_row)
      return data_by_row[0][savedIndex][0]
      #data_by_row[x][y][z]
      #x is 0 cause only one row in this function
      #y is the index of the internal list containing to_adresses and value_received
      #z is [0] for to_adress and [1] for value_received

#Returns the adress that contains the largest transaction in a given file
def get_biggest_transaction_in_file(from_adress):
    with open (csv_path, 'r') as file:
        data_by_row = []
        reader = csv.reader(file)
        next(reader) #Skip header
        for row in reader:
            cell_value = row[2]  # Get value from specific column
            # Find all numbers enclosed within square brackets in the cell value
            numbers = re.findall(r'\[(\d+)\]', cell_value)
            # Extract strings from cell value
            strings = re.findall(r'(\w+)\[\d+\]', cell_value)
            # Append each pair of (string, number) to data_by_row
            data_by_row.append(list(zip(strings, map(int, numbers))))
        #data_by_row[x][y][z]
        #x gives you the vertical row in the csv file
        #y gives you the to_adress or value_received in order of appearance in csv file, 0, 1, 2 etc
        #z gives you either to_adress with [0] or the value_received with [1]
        rowCount = 0 #To keep track of what row we're on and corresponding adress
        maxValue = 0 #Saving maxvalue found in each iteratioon.
        savedIndex = 0 #Internal list index.
        savedRow = 0 #Row index.
        for row in data_by_row:
          for pair in row:
            number = pair[1]  # Get the number part of the tuple
            if isinstance(number, int):  # Check if it's a single number
             if number > maxValue:
              maxValue = number
              savedIndex = 0 #Must be set to 0 since we're checking a single number and not in a list
              savedRow = rowCount #Save row index
            # print("Number:", number)
            elif isinstance(number, list):  # Check if it's a list of numbers
              numberCount = 0 #Reset to 0 to start counting through the list from start
              for number in number:
                if number > maxValue:
                  maxValue = number
                  savedIndex = numberCount #Save internal list index
                  savedRow = rowCount #Save row index
               # print("Number:", number)
                numberCount = numberCount + 1
          rowCount = rowCount + 1
        return data_by_row[savedRow][savedIndex][0]

# Example usage:
#csv_path = r"C:\Users\Anton\kandidat\kod\follow-the-money-of-crypto-currency-spam\data3.csv"  # Replace 'transactions.csv' with the path to your CSV file
#largest_transaction_address = get_biggest_transaction_from_file(csv_path)
#print("Address with the largest transaction volume:", largest_transaction_address)

csv_path = r"C:\Users\Anton\kandidat\kod\follow-the-money-of-crypto-currency-spam\data3.csv"  # Replace 'transactions.csv' with the path to your CSV file
from_adress = "bc1q36l5czthf7yzzgqyvxnhgy4rcm7wk563lwdccg"
largest_transaction_address = get_biggest_transaction_from_adress(from_adress, csv_path)
print("Address with the largest transaction volume:", largest_transaction_address)