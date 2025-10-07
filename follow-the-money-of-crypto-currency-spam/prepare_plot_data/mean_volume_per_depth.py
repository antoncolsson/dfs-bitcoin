import os
import pandas as pd
import csv

# Constants
SATOSHI_PER_BTC = 100000000
cwd = os.getcwd()
data_csv_folder_path = os.path.join(cwd, 'data_csv')

def analyze_csv_files(parent_folder, sub):
    """
    @brief Analyze the CSV files in the specified parent folder and subfolders.
    The function calculates the total mean value sent in BTC, over an entire transaction, for each depth and
    writes the results to a CSV file in each subfolder directory.

    When analyzing the CSV files, the function reads the 'Depth', 'From', and 'Tx_ID' columns from each file.
    It then searches for the corresponding 'From' and 'Tx_ID' in the 'data_csv' folder ('data_csv' is the raw data folder for the transactions) to calculate the total mean value sent in BTC.
    This will give an view of the total mean value sent in BTC for each depth, for each abuse type, for the path taken in the DFS traversal.
    
    @param parent_folder The parent folder containing the subfolders with CSV files
    @param sub The subfolder name to append to the output CSV file

    @Note How to use: analyze_csv_files(parent_folder, sub). e.g. analyze_csv_files('data_dfs/4_5', '4_5')

    """
    results = []
    
    # Traverse each subfolder within the parent directory
    for subfolder in os.listdir(parent_folder):
        subfolder_path = os.path.join(parent_folder, subfolder)
        if os.path.isdir(subfolder_path):
            # Initialize a list to collect data from all files in the subfolder
            depth_values = []
         
           # print(subfolder)
            # Process each file in the subfolder
            for file_name in os.listdir(subfolder_path):
                # Reset the set for each file
                processed_tx_ids = set()
                if file_name.endswith('.csv') and file_name != 'summed_results.csv':
                    file_path = os.path.join(subfolder_path, file_name)
                    df = pd.read_csv(file_path)
                    df = df.dropna(subset=['Total_Value_Sent']) # Drop rows with NaN values in 'Total_Value_Sent'
                    df = df.dropna(subset=['Tx_ID']) # Drop rows with NaN values in 'Tx_ID'
                    # Check necessary columns are present
                    if 'Depth' in df.columns and 'From' in df.columns and 'Tx_ID' in df.columns:
                        # Filter rows with unique Tx_ID within the file
                        df = df[df['Tx_ID'].apply(lambda x: not (x in processed_tx_ids or processed_tx_ids.add(x)))]
                        for _, row in df.iterrows():
                            # Path to the corresponding '1A' file based on 'From' column
                            data_csv_file_path = os.path.join(data_csv_folder_path, row['From'], row['From'] + '.csv')
                            if os.path.exists(data_csv_file_path):
                                df_sender_address = pd.read_csv(data_csv_file_path)

                                # Filter rows where Transaction_ID matches Tx_ID
                                df_matched = df_sender_address[df_sender_address['Transaction_ID'] == row['Tx_ID']]

                                # Calculate sum of 'Value_Sent (satoshi)' for matched transactions
                                if not df_matched.empty:
                                    total_value_sent_satoshi = df_matched['Value_Sent (satoshi)'].dropna().sum()
                                    total_value_sent_btc = total_value_sent_satoshi / SATOSHI_PER_BTC
                                    depth_values.append({'Depth': row['Depth'], 'Total_Mean_Value_Sent_BTC': total_value_sent_btc})
            
            # Convert list to DataFrame
            if depth_values:
                df_depth_values = pd.DataFrame(depth_values)

                # Group by 'Depth' and calculate the mean value sent in BTC
                df_grouped = df_depth_values.groupby('Depth')['Total_Mean_Value_Sent_BTC'].mean().reset_index()
                df_grouped['Abuse_Type'] = subfolder
                df_grouped = df_grouped[['Abuse_Type', 'Depth', 'Total_Mean_Value_Sent_BTC']]  # Reorder columns
                results.append(df_grouped)
   
        # Combine all results into a single DataFrame
        if results:
            
            output_folder = os.path.join(cwd, 'data_plot')
            final_results = pd.concat(results, ignore_index=True)
            output_directory = os.path.join(output_folder, sub, 'total_mean_value_sent_per_depth')
            os.makedirs(output_directory, exist_ok=True)
            output_path = os.path.join(output_directory, f'{subfolder}_total_mean_value_sent_per_depth.csv')
            final_results.to_csv(output_path, index=False)
            results = [] # Reset results for next subfolder

# Analyze the CSV files in the '4_5' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '4_5')
analyze_csv_files(parent_folder, '4_5')

# Analyze the CSV files in the '2_10' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '2_10')
analyze_csv_files(parent_folder, '2_10')

