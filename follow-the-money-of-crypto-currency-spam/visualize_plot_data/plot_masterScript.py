import subprocess
import logging
import os

cwd = os.getcwd()

# Paths to the folders containing the plot data and scripts
plot_data_folder_path = os.path.join(cwd, 'plot_data')
plot_script_folder_path = os.path.join(cwd, 'visualize_plot_data')

# Paths to the scripts to run
box_plot_script_path = os.path.join(plot_script_folder_path, 'box_plot_of_total_volume_per_depth.py')
dfs_graph_script_path = os.path.join(plot_script_folder_path, 'DFS_Graph_Visualization_Script.py')
linear_plot_mean_received_path = os.path.join(plot_script_folder_path, 'linear_plot_mean_received_per_depth.py')
linear_plot_mean_sent_path = os.path.join(plot_script_folder_path, 'linear_plot_mean_sent_per_depth.py')
linear_plot_mean_volume_path = os.path.join(plot_script_folder_path, 'linear_plot_mean_volume_per_depth.py')
plot_to_address_nr_path = os.path.join(plot_script_folder_path, 'plot_to_address_nr.py')

path_darknet_2_10 = os.path.join(plot_data_folder_path, '2_10', 'mean_value_received_per_depth', 'darknet_mean_value_received_per_depth.csv')
path_blackmail_2_10 = os.path.join(plot_data_folder_path, '2_10', 'mean_value_received_per_depth', 'blackmail_mean_value_received_per_depth.csv')
path_ransomware_2_10 = os.path.join(plot_data_folder_path, '2_10', 'mean_value_received_per_depth', 'ransomware_mean_value_received_per_depth.csv')
path_tumbler_2_10 = os.path.join(plot_data_folder_path, '2_10', 'mean_value_received_per_depth', 'tumbler_mean_value_received_per_depth.csv')

path_darknet_4_5 = os.path.join(plot_data_folder_path, '4_5', 'mean_value_received_per_depth', 'darknet_mean_value_received_per_depth.csv')
path_blackmail_4_5 = os.path.join(plot_data_folder_path, '4_5', 'mean_value_received_per_depth', 'blackmail_mean_value_received_per_depth.csv')
path_ransomware_4_5 = os.path.join(plot_data_folder_path, '4_5', 'mean_value_received_per_depth', 'ransomware_mean_value_received_per_depth.csv')
path_tumbler_4_5 = os.path.join(plot_data_folder_path, '4_5', 'mean_value_received_per_depth', 'tumbler_mean_value_received_per_depth.csv')


# Setup basic configuration for logging
logging.basicConfig(filename='script_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_path, *args):
    """Execute a script using subprocess and handle output, passing additional arguments."""
    try:
        # Prepare the command with script path and arguments
        command = ['python', script_path] + list(args)
        # Execute the script and capture output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Output of {script_path}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        # Log and print the error
        error_message = f"An error occurred while running {script_path}: {e}\nError Output: {e.stderr}"
        logging.error(error_message)
        print(error_message)

def main():
    # List of scripts with their paths and optional arguments
    scripts = [
        (box_plot_script_path, 'arg1', 'arg2')
        #(dfs_graph_script_path),
        #(linear_plot_mean_received_path, 'arg1', 'arg2', 'arg3'),
        #(linear_plot_mean_sent_path, 'arg1', 'arg2', 'arg3'),
        #(linear_plot_mean_volume_path, 'arg1', 'arg2', 'arg3')
        #(plot_to_address_nr_path)
    ]
    
    # Execute each script with arguments
    for script_info in scripts:
        script_path, *script_args = script_info
        run_script(script_path, *script_args)

if __name__ == '__main__':
    main()
