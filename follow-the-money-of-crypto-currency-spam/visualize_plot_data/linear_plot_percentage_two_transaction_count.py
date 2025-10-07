import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.lines as mlines
cwd = os.getcwd()
output_folder_path = os.path.join(cwd, 'follow-the-money-of-crypto-currency-spam', 'visualize_plot_data', 'output_images')
# check if the output folder exists, if not create it
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

def plot_percentage_2tx(*file_paths, sub):
    """
    @brief Plot the average BTC sent in transactions for each depth by abuse type.

    @param file_paths: The paths to the CSV files containing the data to plot.

    """

    # Initialize the plot
    plt.figure(figsize=(4, 3.3))
    sns.set_style("whitegrid")
    custom_palette = ['#5DADE2', '#FF8C00', '#32A852', '#DC143C']
    # Loop over the CSV files to plot each one
    for csv_path in file_paths:
        # Read the CSV file
        data = pd.read_csv(csv_path)
       # data['Depth'] += 1  # Add 1 to the depth to start from 1
        # Extract abuse type from the 'Subfolder' column
        abuse_type = data['Abuse_Type'].iloc[0]
        
        # Plot the data
        g = sns.lineplot(data=data, x='Depth', y='Percentage', marker='o',markersize=5, label=abuse_type)
        
    # Setting the axis labels and plot title
    plt.ylabel('% Two-TX Addresses', fontsize=14)
    plt.xlabel('Depth', fontsize=14)
    #plt.title('Percentage of 2 Transaction Addresses at Each Depth by Abuse Type')
    #plt.gca().invert_yaxis()  # Invert y-axis to show depth 0 at the top
    x_tick_positions = [0, 1, 2, 3, 4, 5] 
    plt.xticks(x_tick_positions, fontsize=14)
    y_tick_positions = [20, 30, 40, 50, 60, 70]
    plt.yticks(y_tick_positions, fontsize=14)
    plt.tight_layout()
    # Show the legend
    custom_labels = ['Blackmail', 'Darknet', 'Ransomware', 'Tumbler']
    #custom_palette_list = [custom_palette[label] for label in custom_labels]
    legend_handles = []
    for color, label in zip(custom_palette, custom_labels):
        line = mlines.Line2D([], [], color=color, marker='o', markersize=5, label=label)
        legend_handles.append(line)
    plt.legend(handles=legend_handles, fontsize='10', loc='lower right')
    sns.set_palette(custom_palette)
    #plt.text(-1.6, 6.5, 'c)', fontsize=16, ha='left', va='bottom') #For 2_10
    #plt.text(-0.8, 6.5, 'c)', fontsize=16, ha='left', va='bottom') #For 4_5
    # Save the plot to a file
    output_filepath = os.path.join(output_folder_path, f'{sub}_percentage_2_tx_addresses_each_depth.pdf') # byt till vilken file extension du vill ha
    g.figure.savefig(output_filepath)
    # Show the plot
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['right'].set_color('black')
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['left'].set_color('black')
    plt.show()

input_folder_path_2_10 = os.path.join(cwd, 'data_plot', '2_10', 'percentage_two_transaction_count_per_depth')
input_folder_path_4_5 = os.path.join(cwd, 'data_plot', '4_5', 'percentage_two_transaction_count_per_depth')

# plot 2_10
path_darknet = os.path.join(input_folder_path_2_10, 'darknet_percentage_two_transaction_count_per_depth.csv')
path_blackmail = os.path.join(input_folder_path_2_10, 'blackmail_percentage_two_transaction_count_per_depth.csv')
path_ransomware = os.path.join(input_folder_path_2_10, 'ransomware_percentage_two_transaction_count_per_depth.csv')
path_tumbler = os.path.join(input_folder_path_2_10, 'tumbler_percentage_two_transaction_count_per_depth.csv')
#plot_percentage_2tx(path_blackmail, path_darknet, path_ransomware, path_tumbler, sub='2_10')

# plot 4_5
path_darknet = os.path.join(input_folder_path_4_5, 'darknet_percentage_two_transaction_count_per_depth.csv')
path_blackmail = os.path.join(input_folder_path_4_5, 'blackmail_percentage_two_transaction_count_per_depth.csv')
path_ransomware = os.path.join(input_folder_path_4_5, 'ransomware_percentage_two_transaction_count_per_depth.csv')
path_tumbler = os.path.join(input_folder_path_4_5, 'tumbler_percentage_two_transaction_count_per_depth.csv')
plot_percentage_2tx(path_blackmail, path_darknet, path_ransomware, path_tumbler, sub='4_5')