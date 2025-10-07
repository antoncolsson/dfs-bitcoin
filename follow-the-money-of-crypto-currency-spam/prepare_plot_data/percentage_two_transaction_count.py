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
            dfs_list = []

            # Process each file in the subfolder
            for file_name in os.listdir(subfolder_path):
                if file_name.endswith('.csv') and file_name != 'summed_results.csv':
                    file_path = os.path.join(subfolder_path, file_name)
                    df = pd.read_csv(file_path)
                    df['From'] = df['From'].drop_duplicates() #Drop duplicate From addresses since their TX_Count appear multiple times
                    df = df.dropna(subset=['From']) #Remove rows with NaN values in 'From'
                    # Ensure necessary columns are present
                    if 'TX_Count' in df.columns:
                        # Count occurrences of each depth
                        depth_counts = df['Depth'].value_counts().reset_index()
                        depth_counts.columns = ['Depth', 'Depth_Count']
                        # Count occurrences of TX_Count being 2 at each depth
                        tx_count_2_counts = df[df['TX_Count'] == 2]['Depth'].value_counts().reset_index()
                        tx_count_2_counts.columns = ['Depth', '2_TX_Count']
                        # Concatenate depth_counts and tx_count_2_counts into a single DataFrame
                        merged_counts = pd.merge(depth_counts, tx_count_2_counts, on='Depth', how='left')
                        dfs_list.append(merged_counts)
            # Combine all the DataFrames in dfs_list into a single DataFrame
            all_depths = pd.concat(dfs_list, ignore_index=True)

            # Group the merged DataFrame by the same occurring depths
            grouped = all_depths.groupby('Depth').sum().reset_index()
            #print(grouped)
            grouped['Percentage'] = round(grouped['2_TX_Count'] / grouped['Depth_Count'] * 100, 2)

            # Fill NaN values with 0
            grouped['Percentage'] = grouped['Percentage'].fillna(0)

            # Drop any NaN values
            grouped = grouped.dropna()
            if not all_depths.empty:
                grouped = grouped[['Depth', 'Percentage']]
                grouped['Abuse_Type'] = subfolder  # Add subfolder name to the results
                grouped = grouped[['Abuse_Type', 'Depth', 'Percentage']]  # Reorder columns
                output_folder = os.path.join(cwd, 'data_plot')
                os.makedirs(output_folder, exist_ok=True)
                output_directory = os.path.join(output_folder, sub, 'percentage_two_transaction_count_per_depth')
                os.makedirs(output_directory, exist_ok=True)
                #Output the aggregated data to a CSV file in the subfolder directory
                output_path_csv = os.path.join(output_directory, f'{subfolder}_percentage_two_transaction_count_per_depth.csv')
                grouped.to_csv(output_path_csv, index=False)

# Analyze the CSV files in the '4_5' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '2_10')
analyze_csv_files(parent_folder, '2_10')

# Analyze the CSV files in the '2_10' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '4_5')
analyze_csv_files(parent_folder, '4_5')
