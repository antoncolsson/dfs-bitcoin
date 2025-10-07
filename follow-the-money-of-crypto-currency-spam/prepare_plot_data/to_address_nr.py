import os
import pandas as pd
import csv
import matplotlib.pyplot as plt
import seaborn as sns
# Set the current working directory to the root of the project
cwd = os.getcwd()

def analyze_csv_files(parent_folder):
    """
    @brief Analyzes CSV files within subfolders of a specified parent folder, excluding 'summed_results.csv'.
    Counts how many unique 'from addresses' have specific 'To_Addresses_Nr' and aggregates this
    information across subfolders. It also checks if necessary columns exist before processing each CSV.
    
    
    @param parent_folder (str): Path to the parent directory that contains subfolders named after abuse types.
    
    @return:
    None: Outputs a file 'To_Addresses_Nr_plotData' with the aggregated data for plotting.
    """
      # Dictionary to hold the data as {abuse_type: {to_address_nr: count_of_addresses}}
    all_data = {}

    # Traverse each subfolder within the parent directory
    for subfolder in os.listdir(parent_folder):
        subfolder_path = os.path.join(parent_folder, subfolder)
        if os.path.isdir(subfolder_path):
            # Dictionary to count unique addresses per To_Addresses_Nr
            to_addresses_count = {}

            # Process each file in the subfolder
            for file_name in os.listdir(subfolder_path):
                if file_name.endswith('.csv') and file_name != 'summed_results.csv':
                    file_path = os.path.join(subfolder_path, file_name)
                    df = pd.read_csv(file_path)

                    # Filter unique from addresses and their To_Addresses_Nr
                    unique_addresses = df.drop_duplicates(subset=['From'])
                    unique_addresses = unique_addresses[['From', 'To_Addresses_Nr']]

                    # Count how many addresses have each To_Addresses_Nr
                    for index, row in unique_addresses.iterrows():
                        to_addr_nr = row['To_Addresses_Nr']
                        if to_addr_nr not in to_addresses_count:
                            to_addresses_count[to_addr_nr] = 0
                        to_addresses_count[to_addr_nr] += 1
                        #if to_addr_nr == 0:
                         #   print(f"Found 0 To_Addresses_Nr in {file_path}")

            # Store results in the all_data dictionary under the current subfolder's name
            all_data[subfolder] = to_addresses_count

    # Output the aggregated data to a file
    output_path_text = os.path.join(cwd, 'data_plot', 'To_Addresses_Nr_plotData.txt')
    output_path_csv = os.path.join(cwd, 'data_plot', 'To_Addresses_Nr_plotData.csv')
    
    with open(output_path_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['To_Addresses_Nr', 'Unique_From_Addresses'])  # Header row
        for abuse_type, counts in all_data.items():
            writer.writerow([abuse_type, ''])  # Write the abuse type as a section header
            for to_addr_nr, addr_count in sorted(counts.items()):
                writer.writerow([to_addr_nr, addr_count])  # Write data rows
             
    with open(output_path_text, 'w') as file:            
        for abuse_type, counts in all_data.items():
            file.write(f"{abuse_type}:\n")
            for to_addr_nr, addr_count in sorted(counts.items()):
                file.write(f"{to_addr_nr} to_address_nr: {addr_count} unique from addresses\n")
            file.write("\n")

parent_folder = os.path.join(cwd, 'data_dfs', '4_5')
analyze_csv_files(parent_folder)
