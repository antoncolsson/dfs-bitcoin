import csv
import pandas as pd

csv_file = r"C:\Users\D-RTX3080\Desktop\gitlab\follow-the-money-of-crypto-currency-spam\overviews\overview_txs.csv"
#This function is meant to generate "amount" of adresses to be used for our depth first search.
#At the moment it gives ouput in a txt file as the run time is quite substantial for lager amounts.
#It returns unique adresses.
def generate_dataset(csv_file, abuse_type, amount, output_file):
  with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        address_set = set()
        addresses_added = set()
        for row in reader:
            abuse_number = int(row[6])
            address = row[3]
            if (abuse_number == abuse_type and address not in addresses_added):
                address_set.add((address, row[2])) #Add adress1, value
                addresses_added.add(address) #Seperate set so we can have unique addresses and check it in the if statement
        sorted_set = sorted(address_set, key=lambda x: x[1], reverse=True) #Sorts the adress_set by value in descending order
        top_adresses =[]
        for i in range (amount):
            top_adresses.append(sorted_set[i][0]) #Adds ONLY adresses to the output, not the associated value
        #print(top_adresses)

        with open(output_file, 'w') as output:
            for address in top_adresses:
                output.write(address+'\n')
        print(f"Top addresses exported to %s" % output_file)

generate_dataset(csv_file, 1, 10, "root_RansomWare_addresses.txt")
generate_dataset(csv_file, 2, 10, "root_Darknet_addresses.txt")
generate_dataset(csv_file, 3, 10, "root_Tumbler_addresses.txt")
generate_dataset(csv_file, 4, 10, "root_Blackmail_addresses.txt")

#1 Ransomware
#2 Darknet market
#3 Bitcoin tumbler
#4 Blackmail scam
#5 Sextortion
#99 Other (e.g. fake charity, social engineering)