import os
import pandas as pd
import csv

# Constants
SATOSHI_PER_BTC = 100000000
cwd = os.getcwd()

def analyze_csv_files(parent_folder, sub):
    """
    @ Analyze the CSV files in the specified parent folder and subfolders.
    The function calculates the mean value sent in BTC for each depth and
    writes the results to a CSV file in each subfolder directory.

    When analyzing the CSV files, the function reads the 'Depth' and 'Total_Value_Sent' columns from each file.
    It then calculates the mean value sent in BTC for each depth and writes the results to a CSV file in each subfolder directory.
    This will give an view of the mean value sent in BTC for each depth, for each abuse type, for the path taken in the DFS traversal.

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
                    #print(f"Initial data size: {len(df)}, Columns: {df.columns.tolist()}")
                    df = df.dropna(subset=['Total_Value_Sent']) # Drop rows with NaN values in 'Total_Value_Sent'
                    df = df.dropna(subset=['Tx_ID']) # Drop rows with NaN values in 'Tx_ID'
                   # print(f"Data size after removing NaN: {len(df)}")
                    # Ensure necessary columns are present
                    if 'Depth' in df.columns and 'Total_Value_Sent' in df.columns and 'Tx_ID' in df.columns:
                        # Filter rows with unique Tx_ID within the file
                        df = df[df['Tx_ID'].apply(lambda x: not (x in processed_tx_ids or processed_tx_ids.add(x)))]
                        #print(df)
                        # Convert 'Total_Value_Sent' to BTC
                        df['Mean_Value_Sent_BTC'] = df['Total_Value_Sent'] / SATOSHI_PER_BTC
                        df = df[['Depth', 'Mean_Value_Sent_BTC']]
                        all_depths = pd.concat([all_depths, df], ignore_index=True)
            
            # Group by 'Depth' and calculate the mean value received in BTC
            if not all_depths.empty:
                #print(f"Data for {subfolder}: {all_depths}")
                grouped = all_depths.groupby('Depth').mean().reset_index()
                #print(f"Grouped data for {subfolder}: {grouped}")
                grouped['Abuse_Type'] = subfolder  # Add subfolder name to the results
                grouped = grouped[['Abuse_Type', 'Depth', 'Mean_Value_Sent_BTC']]  # Reorder columns
                output_folder = os.path.join(cwd, 'data_plot')
                os.makedirs(output_folder, exist_ok=True)
                output_directory = os.path.join(output_folder, sub, 'mean_value_sent_per_depth')
                os.makedirs(output_directory, exist_ok=True)
                # Output the aggregated data to a CSV file in the subfolder directory
                output_path_csv = os.path.join(output_directory, f'{subfolder}_mean_value_sent_per_depth.csv')
                grouped.to_csv(output_path_csv, index=False)

# Analyze the CSV files in the '4_5' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '4_5')
analyze_csv_files(parent_folder, '4_5')

# Analyze the CSV files in the '2_10' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '2_10')
analyze_csv_files(parent_folder, '2_10')
