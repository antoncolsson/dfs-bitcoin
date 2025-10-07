import os
import csv
import pandas as pd
import convert_JsonToCsv

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
       # print(f"Folder '{folder_name}' created successfully.")
   # else:
        #print(f"Folder '{folder_name}' already exists.")

# Example usage
#folder_name = "my_folder"
#create_folder(folder_name)

#Iterate over all folders in a directory
#Create a new folder with "name" in a new directory if it does not exist
#Run a function on the data in the folder
#Save the result in the new folder
#Repeat for all folders in the directory

def create_all(olddata_path, newdata_path):
    count = 0
    for folder in os.listdir(olddata_path):
        if count >= 3:
            break
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
                        convert_JsonToCsv.convert_JSON_files_from_file_path(json_file, csv_file) #Convert the json file to csv and save it in the new folder
        count = count +  1

olddata_path = r"C:\Users\Anton\kandidat\data"
newdata_path = r"C:\Users\Anton\kandidat\kod\follow-the-money-of-crypto-currency-spam\follow-the-money-of-crypto-currency-spam\data"
create_all(olddata_path, newdata_path)

