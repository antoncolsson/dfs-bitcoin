import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

cwd = os.getcwd()
output_folder_path = os.path.join(cwd, 'follow-the-money-of-crypto-currency-spam', 'visualize_plot_data', 'output_images')
# check if the output folder exists, if not create it
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)


def plot_average_btc_received(*file_paths, sub):
    """
    @brief Plot the average BTC received in transactions for each depth by abuse type.

    @param file_paths: The paths to the CSV files containing the data to plot.
    
    """
    # Initialize the plot
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    # Loop over the CSV files to plot each one
    for csv_path in file_paths:
        # Read the CSV file
        data = pd.read_csv(csv_path)
        data['Depth'] += 1  # Add 1 to the depth to start from 1
        # Extract abuse type from the 'Subfolder' column
        abuse_type = data['Abuse_Type'].iloc[0]
        
        # Plot the data
        g = sns.lineplot(data=data, x='Depth', y='Mean_Value_Received_BTC', marker='o', label=abuse_type)
        
    # Setting the axis labels and plot title
    plt.ylabel('Average Received (BTC)')
    plt.xlabel('Depth')
    plt.title('Average BTC Received at Each Depth by Abuse Type')
    #plt.gca().invert_yaxis()  # Invert y-axis to show depth 0 at the top
    
    # Show the legend
    plt.legend(title='Abuse Type')
    
    # Save the plot to a file
    output_filepath = os.path.join(output_folder_path, f'{sub}_Mean_Received_Per_Depth_LinearPlot.pdf') # byt till vilken file extension du vill ha
    g.figure.savefig(output_filepath)

    # Show the plot
    plt.show()

input_folder_path_2_10 = os.path.join(cwd, 'data_plot', '2_10', 'mean_value_received_per_depth')
input_folder_path_4_5 = os.path.join(cwd, 'data_plot', '4_5', 'mean_value_received_per_depth')

# plot 2_10
path_darknet = os.path.join(input_folder_path_2_10, 'darknet_mean_value_received_per_depth.csv')
path_blackmail = os.path.join(input_folder_path_2_10, 'blackmail_mean_value_received_per_depth.csv')
path_ransomware = os.path.join(input_folder_path_2_10, 'ransomware_mean_value_received_per_depth.csv')
path_tumbler = os.path.join(input_folder_path_2_10, 'tumbler_mean_value_received_per_depth.csv')
plot_average_btc_received(path_blackmail, path_darknet, path_ransomware, path_tumbler, sub='2_10')

# plot 4_5
path_darknet = os.path.join(input_folder_path_4_5, 'darknet_mean_value_received_per_depth.csv')
path_blackmail = os.path.join(input_folder_path_4_5, 'blackmail_mean_value_received_per_depth.csv')
path_ransomware = os.path.join(input_folder_path_4_5, 'ransomware_mean_value_received_per_depth.csv')
path_tumbler = os.path.join(input_folder_path_4_5, 'tumbler_mean_value_received_per_depth.csv')
plot_average_btc_received(path_blackmail, path_darknet, path_ransomware, path_tumbler, sub='4_5')