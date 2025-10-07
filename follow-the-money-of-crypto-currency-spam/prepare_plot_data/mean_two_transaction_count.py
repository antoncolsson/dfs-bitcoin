import os
import pandas as pd
import csv

cwd = os.getcwd()

def analyze_csv_files(parent_folder, sub):
    """
    @ Calculate the mean number of two-transaction counts per depth for each subfolder in the parent directory.
    The function calculates the mean number of two-transaction counts per depth for each subfolder in the parent directory.
    It then writes the results to a CSV file in each subfolder directory.

    When analyzing the CSV files, the function reads the 'Depth', 'TX_Count', and 'Tx_ID' columns from each file.
    It then calculates the mean number of two-transaction counts per depth for each subfolder in the parent directory.
    This will give an view of the mean number of two-transaction counts per depth for each abuse type, for the path taken in the DFS traversal.

    @param parent_folder The parent folder containing the subfolders with CSV files
    @param sub The subfolder name to append to the output CSV file

    @Note How to use: analyze_csv_files(parent_folder, sub). e.g. analyze_csv_files('data_dfs/4_5', '4_5')

    """

    # Traverse each subfolder within the parent directory
    for subfolder in os.listdir(parent_folder):
        subfolder_path = os.path.join(parent_folder, subfolder)
        if os.path.isdir(subfolder_path):
            # Initialize a DataFrame to collect data from all files in the subfolder
            all_depths = pd.DataFrame()
            
            # Process each file in the subfolder
            for file_name in os.listdir(subfolder_path):
                if file_name.endswith('.csv') and file_name != 'summed_results.csv':
                    
                    # Reset the set for each file
                    processed_tx_ids = set()
                    file_path = os.path.join(subfolder_path, file_name)
                    df = pd.read_csv(file_path)
                    df = df.dropna(subset=['TX_Count']) # Drop rows with NaN values in 'TX_Count'
                    #df = df.dropna(subset=['Tx_ID']) # Drop rows with NaN values in 'Tx_ID'
                    # Ensure necessary columns are present
                    if 'Depth' in df.columns and 'TX_Count' in df.columns and 'Tx_ID' in df.columns:
                        # Filter rows with unique Tx_ID within the file
                        df = df[df['Tx_ID'].apply(lambda x: not (x in processed_tx_ids or processed_tx_ids.add(x)))]
                        
                        # Initialize a column for count where TX_Count == 2
                        df['Two_Transaction_Count'] = (df['TX_Count'] == 2).astype(int)
                        # Aggregate counts by depth within each file
                        count_by_depth = df.groupby('Depth')['Two_Transaction_Count'].sum().reset_index()
                        #print(file_name) # Print the file name being processed ***************** check till Anton
                        #print("count_by_depth: ", count_by_depth) # Print the aggregated data for each file ***************** check till Anton
                        # Combine with all_depths DataFrame to accumulate counts across files
                        all_depths = pd.concat([all_depths, count_by_depth], ignore_index=True)
                        #print("all_depths: ", all_depths) # Print the accumulated data across all files ***************** check till Anton
            # Aggregate counts across all files in the subfolder
            if not all_depths.empty:
                #all_depths = all_depths.groupby('Depth')['Two_Transaction_Count']
                #print(all_depths) # Print the aggregated data for each subfolder ***************** check till Anton
                #grouped = all_depths.groupby('Depth')['Two_Transaction_Count'].mean().reset_index()
                #grouped = all_depths.groupby('Depth')['Two_Transaction_Count']
                #print("grouped: ", grouped) # Print the aggregated data for each subfolder ***************** check till Anton
                grouped = count_by_depth.div(all_depths["Two_Transaction_Count"])
                print("grouped: ", grouped) # Print the aggregated data for each subfolder ***************** check till Anton
                grouped['Abuse_Type'] = subfolder  # Add subfolder name to the results
                grouped = grouped[['Abuse_Type', 'Depth', 'Two_Transaction_Count']]  # Reorder columns
                output_folder = os.path.join(cwd, 'data_plot')
                os.makedirs(output_folder, exist_ok=True)
                output_directory = os.path.join(output_folder, sub, 'mean_two_transaction_count_per_depth')
                os.makedirs(output_directory, exist_ok=True)
                # Output the aggregated data to a CSV file in the subfolder directory
                output_path_csv = os.path.join(output_directory, f'{subfolder}_mean_two_transaction_count_per_depth.csv')
                grouped.to_csv(output_path_csv, index=False)
                

# Analyze the CSV files in the '4_5' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '4_5')
analyze_csv_files(parent_folder, '4_5')

# Analyze the CSV files in the '2_10' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '2_10')
analyze_csv_files(parent_folder, '2_10')
