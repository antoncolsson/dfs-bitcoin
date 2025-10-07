import os
import pandas as pd
import csv

cwd = os.getcwd()

def analyze_csv_files(parent_folder, sub):
    """
    @brief Calculate the ratio of two-transaction counts to total transactions per depth for each subfolder in the parent directory.
    The function calculates the ratio of two-transaction counts to total transactions per depth for each subfolder in the parent directory.
    It then writes the results to a CSV file in each subfolder directory.

    When analyzing the CSV files, the function reads the 'Depth' and 'TX_Count' columns from each file.
    It then calculates the ratio of two-transaction counts to total transactions per depth for each subfolder in the parent directory.
    This will give an view of the ratio of two-transaction counts to total transactions per depth for each abuse type, for the path taken in the DFS traversal.

    @param parent_folder The parent folder containing the subfolders with CSV files
    @param sub The subfolder name to append to the output CSV file

    """
    for subfolder in os.listdir(parent_folder):
        subfolder_path = os.path.join(parent_folder, subfolder)
        if os.path.isdir(subfolder_path):
            all_depths = pd.DataFrame()
            
            # Process each file in the subfolder
            for file_name in os.listdir(subfolder_path):
                visited_addresses = set()
                if file_name.endswith('.csv') and file_name != 'summed_results.csv':
                    file_path = os.path.join(subfolder_path, file_name)
                    df = pd.read_csv(file_path)
                    df = df.dropna(subset=['TX_Count'])
                    
                    if 'Depth' in df.columns and 'TX_Count' in df.columns:
                        # make sure 'From' is only visited once per transaction
                        df = df[df['From'].apply(lambda x: not (x in visited_addresses or visited_addresses.add(x)))]
                        print(df)
                        # Count occurrences of TX_Count == 2 and total transactions
                        df['TX_Count_2'] = (df['TX_Count'] == 2).astype(int)
                        count_by_depth = df.groupby('Depth').agg({
                            'TX_Count_2': 'sum',
                            'TX_Count': 'size'  # Total count of transactions at each depth
                        }).reset_index()
                        
                        # Combine with all_depths DataFrame
                        all_depths = pd.concat([all_depths, count_by_depth], ignore_index=True)
            
            # Aggregate counts across all files in the subfolder
            if not all_depths.empty:
                all_depths = all_depths.groupby('Depth').sum().reset_index()
                all_depths['Ratio_Percentage_TX_Count_2'] = all_depths['TX_Count_2'] / all_depths['TX_Count'] * 100
                
                grouped = all_depths[['Depth', 'Ratio_Percentage_TX_Count_2']].copy()
                grouped.loc[:, 'Abuse_Type'] = subfolder  # Proper setting of new column without warning
                
                # Output directory and file creation
                output_folder = os.path.join(os.getcwd(), 'data_plot')
                os.makedirs(output_folder, exist_ok=True)
                output_directory = os.path.join(output_folder, sub, 'ratio_percentage_two_tx_count_per_depth')
                os.makedirs(output_directory, exist_ok=True)
                
                output_path_csv = os.path.join(output_directory, f'{subfolder}_ratio_percentage_two_tx_count_per_depth.csv')
                grouped.to_csv(output_path_csv, index=False)

                
# Analyze the CSV files in the '4_5' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '4_5')
analyze_csv_files(parent_folder, '4_5')

# Analyze the CSV files in the '2_10' subfolder
parent_folder = os.path.join(cwd, 'data_dfs', '2_10')
analyze_csv_files(parent_folder, '2_10')
