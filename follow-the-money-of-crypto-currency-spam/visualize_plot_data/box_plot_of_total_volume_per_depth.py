import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import os

cwd = os.getcwd()
output_folder_path = os.path.join(cwd, 'follow-the-money-of-crypto-currency-spam', 'visualize_plot_data', 'output_images')
# check if the output folder exists, if not create it
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# Function to create a box plot for each abuse type
def box_plot_of_total_volume_per_depth(*plot_data_file_paths, sub):
    """
    @brief Create a box plot of the total volume sent in BTC for each depth, for each abuse type.

    @param plot_data_file_paths: The paths to the CSV files containing the data to plot.
    @param sub: The subfolder name to append to the output file name.
    """
    # Read each CSV file into a DataFrame and assign an 'Abuse_Type'
    dfs = []
    for file_path in plot_data_file_paths:
        df = pd.read_csv(file_path)
        # Infer the abuse type from the file name
        abuse_type = os.path.basename(file_path).split('_')[0]  # Assumes filename starts with the abuse type
        df['Abuse_Type'] = abuse_type
        dfs.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)

    # Set the style of the visualization
    sns.set_theme(style="whitegrid", palette="pastel")
    
    # Create a FacetGrid with side-by-side boxplots for each 'Abuse_Type'
    g = sns.catplot(x="Depth", y="Volume_Sent_Per_Depth",
                    col="Abuse_Type", col_wrap=2,  # Wrap the plots into 2 columns
                    data=combined_df, kind="box",
                    height=5, aspect=1,  # Control the size and aspect ratio of each plot, higher values increase the size
                    sharey=True, sharex=True, palette=["#32A852"])

    # Customize the plot titles and axis labels 
    for ax in g.axes.flat:
        ax.set_title('')  # Remove the default title
    titles = ["a) blackmail ", "b) darknet", "c) ransomware", "d) tumbler"]
    #for ax, title in zip(g.axes.flat, titles):
        # Set title for each subplot below the plot
    #    ax.text(0.5, -0.000000000001, title, ha='center', va='center', transform=ax.transAxes)
    #for ax in g.axes.flat:
     #   ax.title.set_position([0.5, -200000])
    # Set the y-axis to log scale
    g.set(yscale="log")
    g.set_axis_labels("Depth", "Volume (BTC, log scale)", fontsize = 18)
    g.set_xticklabels(fontsize=14)
    g.set_yticklabels(fontsize=14)
    g.set_xlabels("Depth", fontsize = 18)

    # Move the titles below the plots
    #g.fig.tight_layout()
    #plt.subplots_adjust(bottom=0.2, hspace=0.1, wspace=0, right=0.85)  # Increase the bottom margin to make room for the title, higher values move the title up

    g.fig.tight_layout()
    #plt.subplots_adjust(wspace=0, right=1.5)
    # Adjust the spacing between the plots and the titles
    #plt.subplots_adjust(top=0.9, wspace=0.2, left=0.1) # Increase the top margin to make room for the title, higher values move the title down
    #g.figure.suptitle('Volume Per Depth Across Abuse Types', fontsize=16)
    #ax.text(-1, 1.05, "a) blackmail", ha='center', va='center', transform=ax.transAxes, fontsize=16)
    #ax.text(0.1, 1.05, "b) darknet", ha='center', va='center', transform=ax.transAxes, fontsize=16)
    #ax.text(-1, -0.11, "c) ransomware", ha='center', va='center', transform=ax.transAxes, fontsize=16)
    #ax.text(0.1, -0.11, "d) tumbler", ha='center', va='center', transform=ax.transAxes, fontsize=16)
    # Save the plot to a file
    output_filepath = os.path.join(output_folder_path, f'{sub}_Volume_Sent_Per_Depth_Across_Abuse_Types_BoxPlot.pdf') # byt till vilken file extension du vill ha
    g.savefig(output_filepath)
    #g.set_palette("Blues")
    # Show the plot
    plt.show()

# input folder path
input_folder_path_2_10 = os.path.join(cwd, 'data_plot', '2_10', 'raw_volume_per_depth')
input_folder_path_4_5 = os.path.join(cwd, 'data_plot', '4_5', 'raw_volume_per_depth')

# plot 2_10
#path = os.path.join(input_folder_path_2_10, 'darknet_raw_volume_per_depth.csv')
#path = os.path.join(input_folder_path_2_10, 'blackmail_raw_volume_per_depth.csv')
#path = os.path.join(input_folder_path_2_10, 'ransomware_raw_volume_per_depth.csv') # byt ut filepath till rätt fil
#path = os.path.join(input_folder_path_2_10, 'tumbler_raw_volume_per_depth.csv')# byt ut filepath till rätt fil
#box_plot_of_total_volume_per_depth(path, sub='2_10')  # , path_ransomware, path_tumbler)

# plot 4_5
#path_darknet = os.path.join(input_folder_path_4_5, 'darknet_raw_volume_per_depth.csv')
#path_blackmail = os.path.join(input_folder_path_4_5, 'blackmail_raw_volume_per_depth.csv')
path_ransomware = os.path.join(input_folder_path_4_5, 'ransomware_raw_volume_per_depth.csv')# byt ut filepath till rätt fil
#path_tumbler = os.path.join(input_folder_path_4_5, 'tumbler_raw_volume_per_depth.csv')# byt ut filepath till rätt fil
#box_plot_of_total_volume_per_depth(path_blackmail, path_darknet, path_ransomware, path_tumbler, sub='4_5')  # , path_ransomware, path_tumbler)
box_plot_of_total_volume_per_depth(path_ransomware, sub='4_5')  # , path_ransomware, path_tumbler)


