import os
import pandas as pd
import csv
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import numpy as np

# Set the current working directory to the root of the project
cwd = os.getcwd()

# Dictionary to hold the data as {abuse_type: {to_address_nr: count_of_addresses}}
class DataPlotter_config:
    def __init__(self, file_path, data_format='txt'):
        if data_format == 'csv':
            self.data = self.load_data_from_csv(file_path)
        else:
            self.data = self.load_data(file_path)
    

    def load_data_from_csv(self, csv_file_path):
        """
        Load data from a CSV file into a DataFrame for plotting.
        Checks for correct header and aborts if the header is incorrect.
        """
        data_list = []
        current_abuse_type = None

        with open(csv_file_path, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                # Check if the row is an abuse type header
                if row and row[1] == '':
                    current_abuse_type = row[0]
                elif row and row[0].isdigit():  # Ensure this row contains data
                    data_list.append({
                        'To_Addresses_Nr': int(row[0]),
                        'Unique_From_Addresses': int(row[1]),
                        'Abuse_Type': current_abuse_type
                    })

        # Convert the list of dictionaries to a DataFrame
        return pd.DataFrame(data_list)
    
    
    def load_data(self, file_path):
        """
        @brief Load data from a text file into a DataFrame for plotting.
        """
        # Initialize variables to hold data
        data = {'To_Addresses_Nr': [], 'Unique_From_Addresses': [], 'Abuse_Type': []}
        current_abuse_type = None
        
        # Read data from file
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line.endswith(':'):
                    current_abuse_type = line[:-1]
                elif 'to_address_nr:' in line:
                    parts = line.split()
                    print(parts)
                    to_address_nr = int(parts[0])
                    print(to_address_nr)
                    unique_from_addresses = int(parts[2])
                    print(unique_from_addresses)
                    data['To_Addresses_Nr'].append(to_address_nr)
                    data['Unique_From_Addresses'].append(unique_from_addresses)
                    data['Abuse_Type'].append(current_abuse_type)
        
        return pd.DataFrame(data) # Convert to DataFrame for easier plotting
    
    """
    @brief plot bar chart
    This is a bar chart that shows the number of unique from addresses for each abuse type based on the number of to addresses.
    The bar chart can be displayed on a linear or logarithmic scale.

    @param log_scale (bool): Whether to use a logarithmic scale for the y-axis.
    """
    def plot_bar_chart(self, log_scale=False, tick_frequency=10):
        plt.figure(figsize=(12, 8))
        bar_plot = sns.barplot(x='To_Addresses_Nr', y='Unique_From_Addresses', hue='Abuse_Type', data=self.data)
        
        # Improving the readability of the x-axis, we had a problem with the x-axis labels being too close together
        for ind, label in enumerate(bar_plot.get_xticklabels()):
            if ind % tick_frequency == 0:  # Show only every nth label to avoid clutter
                label.set_visible(True)
            else:
                label.set_visible(False)

        # Optionally set the scale to logarithmic for better visualization
        if log_scale:
            plt.yscale('log')
            plt.ylabel('Unique From Addresses (log scale)', fontsize=12)

        plt.xlabel('To_Addresses_Nr', fontsize=12)
        plt.ylabel('Unique From Addresses', fontsize=12)
        plt.title('Bar Chart of Unique From Addresses by Abuse Type', fontsize=14)
        plt.legend(title='Abuse Type')
        plt.show()
    
    """
    @brief plot box plot
    This is a box plot that shows the distribution of unique from addresses for each abuse type.
    """
    def plot_box_plot(self):
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='Abuse_Type', y='Unique_From_Addresses', data=self.data)
        plt.xlabel('Abuse Type', fontsize=12)
        plt.ylabel('Unique From Addresses', fontsize=12)
        plt.title('Box Plot of Unique From Addresses by Abuse Type', fontsize=14)
        plt.show()
   
    def plot_heatmap(self):
        """
        Plots a heatmap of 'Unique From Addresses' for each 'Abuse Type' against 'To_Addresses_Nr'.
        
        This method uses seaborn's heatmap function to visualize the distribution of 'Unique From Addresses'
        across different 'To_Addresses_Nr', categorized by 'Abuse Type'. The data is presented in a matrix format where
        each cell's color intensity represents the magnitude of 'Unique From Addresses'. Cells with zero values are filled
        to ensure clarity and continuity in the visualization.

        """
        # Creating a pivot table for the heatmap, indexing by 'Abuse_Type' and columns as 'To_Addresses_Nr'.
        # This structures the data suitably for a heatmap where each cell value represents 'Unique_From_Addresses'.
        heatmap_data = self.data.pivot_table(index='Abuse_Type', columns='To_Addresses_Nr', 
                                            values='Unique_From_Addresses', fill_value=0)

        # Setting up the figure size for better visibility.
        plt.figure(figsize=(14, 8))

        # Creating the heatmap with annotations.
        # 'annot=True' displays the data value in each cell, 'fmt="d"' formats these numbers as integers.
        sns.heatmap(heatmap_data, annot=True, fmt="f", cmap="viridis")

        # Labeling the axes and adding a title for context.
        plt.xlabel('To_Addresses_Nr', fontsize=12)
        plt.ylabel('Abuse Type', fontsize=12)
        plt.title('Heatmap of Unique From Addresses by To_Addresses_Nr', fontsize=14)

        # Displaying the plot.
        plt.show()

    
    """
    @brief plot cdf of unique from addresses
    This is a cumulative distribution function (CDF) plot that shows the proportion of unique from addresses
    for each abuse type as the number of to addresses increases.
    """
    def plot_cdf_upto2000(self):
        plt.figure(figsize=(4, 3.3))
        custom_colors = ['#5DADE2', '#FF8C00', '#32A852', '#DC143C']
        for i, (label, df) in enumerate(self.data.groupby('Abuse_Type')):
            # Sorting values for cumulative plot
            df = df.sort_values('To_Addresses_Nr')
            df['To_Addresses_Nr'] = np.clip(df['To_Addresses_Nr'], None, 2000)
            cdf = np.cumsum(df['Unique_From_Addresses'])
            cdf /= cdf.max()  # Normalize to 1
            #cdf = np.clip(cdf,None, 0.75)
            plt.plot(df['To_Addresses_Nr'], cdf, label=label, color=custom_colors[i])
        plt.xlabel('Amount of Addresses Sent To', fontsize=14)
        plt.ylabel('CDF (Normalized Count)', fontsize=14)
        # Set x-axis ticks
        #plt.xticks(np.arange(min(df['To_Addresses_Nr']), max(df['To_Addresses_Nr']), 4))
        #x_tick_positions = [0, 2, 4, 6, 8, 10] 
        x_tick_positions = [0, 500, 1250, 2000]
        plt.xticks(x_tick_positions, fontsize=14)
        # Set y-axis ticks
        y_tick_positions = [0, 0.25, 0.5, 0.75, 1.0]
        plt.yticks(y_tick_positions, fontsize=14)
        plt.tight_layout()
        #plt.title('CDF of Unique From Addresses by Abuse Type', fontsize=14)
        custom_labels = ['Blackmail', 'Darknet', 'Ransomware', 'Tumbler']
        plt.legend(labels=custom_labels, fontsize='10', loc='lower right')
        plt.show()

    def plot_cdf_upto10(self):
        plt.figure(figsize=(4, 3.3))
        custom_colors = ['#5DADE2', '#FF8C00', '#32A852', '#DC143C']
        for i, (label, df) in enumerate(self.data.groupby('Abuse_Type')):
            # Sorting values for cumulative plot
            df = df.sort_values('To_Addresses_Nr')
            df['To_Addresses_Nr'] = np.clip(df['To_Addresses_Nr'], None, 10)
            cdf = np.cumsum(df['Unique_From_Addresses'])
            cdf /= cdf.max()  # Normalize to 1
            #cdf = np.clip(cdf,None, 0.75)
            plt.plot(df['To_Addresses_Nr'], cdf, label=label, color=custom_colors[i])
        plt.xlabel('Amount of Addresses Sent To', fontsize=14)
        plt.ylabel('CDF (Normalized Count)', fontsize=14)
        # Set x-axis ticks
        #plt.xticks(np.arange(min(df['To_Addresses_Nr']), max(df['To_Addresses_Nr']), 4))
        x_tick_positions = [0, 2, 4, 6, 8, 10] 
        plt.xticks(x_tick_positions, fontsize=14)
        # Set y-axis ticks
        y_tick_positions = [0, 0.25, 0.5, 0.75, 1.0]
        plt.yticks(y_tick_positions, fontsize=14)
        plt.tight_layout()
        #plt.title('CDF of Unique From Addresses by Abuse Type', fontsize=14)
        custom_labels = ['Blackmail', 'Darknet', 'Ransomware', 'Tumbler']
        plt.legend(labels=custom_labels, fontsize='10', loc='lower right')
        #plt.text(-2, -0.27, 'a)', fontsize=16, ha='left', va='bottom')
        plt.show()

    def plot_scatter(self):
        plt.figure(figsize=(10, 6))
        scatter_plot = sns.scatterplot(data=self.data, x='To_Addresses_Nr', y='Unique_From_Addresses', hue='Abuse_Type', style='Abuse_Type')

        # Optionally set the scale to logarithmic
        plt.xscale('log')
        plt.yscale('log')

        # Adding labels and title
        plt.xlabel('To_Addresses_Nr (log scale)', fontsize=12)
        plt.ylabel('Unique From Addresses (log scale)', fontsize=12)
        plt.title('Scatter Plot of Unique From Addresses by Abuse Type', fontsize=14)

        # Display the plot
        plt.show()

    def plot_histogram(self, column_name, bins='auto', log_scale=False):
        """
        @brief Plots a histogram for the specified column in the DataFrame.

        
        @param column_name (str): The column in the data DataFrame to plot ('To_Addresses_Nr' or 'Unique_From_Addresses').
        @param bins (int, str): The number of bins to use for the histogram or 'auto' to let numpy decide. Default is 'auto'.
        @param log_scale (bool): Whether to use a logarithmic scale for the y-axis. Default is False.

        This method utilizes matplotlib's histogram plotting capabilities to visualize the distribution of values.
        """
        plt.figure(figsize=(10, 6))
        # Plotting the histogram
        plt.hist(self.data[column_name], bins=bins, color='skyblue', edgecolor='black')

        # Setting logarithmic scale if specified
        if log_scale:
            plt.yscale('log')

        # Adding labels and title
        plt.xlabel(column_name, fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title(f'Histogram of {column_name}', fontsize=14)

        # Display the plot
        plt.show()
    
    def plot_histogram_abuseType(self, bin_edges, log_scale=False): # rename later
        """
        @brief Plots a histogram with separate bars for each abuse type.

        @param bin_edges (list): List of bin edges to use for the histogram bins.
        @param log_scale (bool): Whether to use a logarithmic scale for the y-axis. Default is False.

        """
        plt.figure(figsize=(10, 6))

        # Get the unique abuse types from the data
        abuse_types = self.data['Abuse_Type'].unique()
        
        # Width of each bar should be such that it can fit all abuse types side by side in one bin
        bar_width = (bin_edges[1] - bin_edges[0]) / (len(abuse_types) + 1)
        
        # Create a histogram for each abuse type
        for index, abuse_type in enumerate(abuse_types):
            # Filter data by abuse type
            abuse_data = self.data[self.data['Abuse_Type'] == abuse_type]
            
            # Count the number of unique from addresses within each bin for this abuse type
            counts, _ = np.histogram(abuse_data['To_Addresses_Nr'], bins=bin_edges)
            
            # Calculate the x position for each bar. Each abuse type's bar is shifted slightly to the right.
            bar_positions = bin_edges[:-1] + (index * bar_width)
            
            # Plot bars for this abuse type
            plt.bar(bar_positions, counts, width=bar_width, label=abuse_type, alpha=0.7)
            
        # Set the x-axis labels to show the bin ranges
        bin_labels = [f'{int(left)}-{int(right)-1}' for left, right in zip(bin_edges[:-1], bin_edges[1:])]
        plt.xticks(ticks=bin_edges[:-1] + bar_width * len(abuse_types) / 2, labels=bin_labels, rotation=45)
        
        # Set logarithmic scale if specified
        if log_scale:
            plt.yscale('log')
        
        # Adding labels, title and legend
        plt.xlabel('To_Addresses_Nr Ranges', fontsize=12)
        plt.ylabel('Unique From Addresses Count', fontsize=12)
        plt.title('Grouped Histogram of To_Addresses_Nr by Abuse Type', fontsize=14)
        plt.legend(title='Abuse Type')

        # Display the plot
        plt.show()
    
    def plot_pie_chart(self, threshold=5):
        """
        Plot pie charts for each abuse type from the data, grouping smaller categories into 'Other'.
        """
        grouped_data = self.data.groupby('Abuse_Type')
        for name, group in grouped_data:
            total = group['Unique_From_Addresses'].sum()
            # Apply threshold to determine if a slice is too small
            filtered_data = group[group['Unique_From_Addresses'] / total * 100 >= threshold]
            other_data = group[group['Unique_From_Addresses'] / total * 100 < threshold]
            other_sum = other_data['Unique_From_Addresses'].sum()

            # Create a DataFrame for 'Other' category if necessary
            if other_sum > 0:
                other_df = pd.DataFrame({
                    'To_Addresses_Nr': ['Other'],
                    'Unique_From_Addresses': [other_sum],
                    'Abuse_Type': [name]
                })
                filtered_data = pd.concat([filtered_data, other_df], ignore_index=True)

            sizes = filtered_data['Unique_From_Addresses']
            labels = filtered_data['To_Addresses_Nr'].apply(lambda x: f"{x} to_address_nr")

            fig, ax = plt.subplots(figsize=(10, 6))  # Increase figure size
            wedges, texts, autotexts = ax.pie(sizes, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
            ax.legend(wedges, labels, title="To_Address_Nr", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            ax.set_title(f'Distribution of to_address_nr for {name} Abuse Type')
            plt.show()


# absolute path to the data file
data_file_path = os.path.join(cwd, 'data_plot', 'To_Addresses_Nr_plotData.csv')

config = DataPlotter_config(data_file_path, 'csv')
#config.plot_bar_chart(log_scale=True, tick_frequency=20)
#config.plot_box_plot()
#config.plot_heatmap()
config.plot_cdf_upto10()
config.plot_cdf_upto2000()
#config.plot_scatter()
#config.plot_histogram('To_Addresses_Nr', log_scale=True)
# create a list of bin edges from 0 to 1000 with a step of 100
#bin_edges = list(range(0, 50001, 40000)) # 0-4999, 5000-9999, ..., 45000-49999, 50000-54999
#bin_edges = np.array(bin_edges)
#print(bin_edges)
#config.plot_histogram_abuseType(bin_edges=bin_edges,log_scale=True)
#config.plot_pie_chart(threshold=2) # decrement treshold to see more slices and increase to see less slices 


