import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import random
import math

cwd = os.getcwd()
path_to_folder = os.path.join(cwd, 'data_dfs')

# Load data
data = pd.read_csv(os.path.join(path_to_folder, '2_10', 'darknet', '31murN3u4dvWjVLEdSQRnhnPeuorxAxcer.csv'))

# Mapping from addresses to IDs
unique_addresses = pd.concat([data['From'], data['To']])#.unique()
address_to_id = {address: idx for idx, address in enumerate(unique_addresses)}

# Create directed graph
G_id = nx.DiGraph()
prev_from_id = None
prev_to_id = None
stop_flag = False
random_ID = random.randint(11, 100)
# Modify the graph construction logic
for idx, row in data.iterrows():
    from_id = address_to_id[row['From']]
    to_id = address_to_id[row['To']]
 
    if pd.isna(row['State_Comment']) == False:
        stop_flag = True
      #  if row['State_Comment'] != 'max_depth_reached':
        G_id.add_edge(from_id, from_id, State_Comment=str(row['State_Comment']))
       # else:
         #   None
    #print(str(row['To']))
    # Only add edges if there is no stopping comment and it's not the last depth
    #if pd.isna(row['State_Comment']) and pd.isna(row['To']):
        #print(row['To'] == "")
       # G_id.add_edge(from_id, to_id, State_Comment=str(row['State_Comment']))


# Modify the positions to separate nodes horizontally based on depth
max_depth = data['Depth'].max()
x_spacing = 3  # Increase this factor to spread nodes further apart

pos_depth = {}
for idx, row in data.iterrows():
    from_id = address_to_id[row['From']]
    to_id = address_to_id[row['To']]
    depth_factor_from = (row['Depth'] / max_depth) * x_spacing
    depth_factor_to = ((row['Depth'] + 1) / max_depth) * x_spacing
    pos_depth[from_id] = (depth_factor_from, -row['Depth'])
    pos_depth[to_id] = (depth_factor_to, -(row['Depth'] + 1))

for k, (x, y) in pos_depth.items():
    pos_depth[k] = (x + k * 20, y)  # Offset x position slightly for each node

# Positions using depth, adjusting for clarity
#pos_depth = {address_to_id[row['From']]: (0, -row['Depth']) for idx, row in data.iterrows()}
#pos_depth.update({address_to_id[row['To']]: (0.5, -row['Depth']-1) for idx, row in data.iterrows()})
#for k, (x, y) in pos_depth.items():
 #   pos_depth[k] = (x + k * 0.1, y)

# Define colors and shapes based on node comments
node_comments = {}
for idx, row in data.iterrows():
    from_id = address_to_id[row['From']]
    to_id = address_to_id[row['To']]
    node_comments[from_id] = row['State_Comment'] if pd.notna(row['State_Comment']) else ""
    node_comments[to_id] = row['State_Comment'] if pd.notna(row['State_Comment']) else ""

node_colors = []
node_shapes = []
comment_color_shape = {
    'leaf_node': ('red', 'o'),
    'max_depth': ('gray', 'o'),
    'flow_back': ('green', '^')
}
default_color = 'blue'
default_shape = 'o'

for node in G_id.nodes():
    node_comment = node_comments.get(node, "")
    matched = False
    for comment, (color, shape) in comment_color_shape.items():
        if comment in str(node_comment):
            node_colors.append(color)
            node_shapes.append(shape)
            matched = True
            break
    if not matched:
        node_colors.append(default_color)
        node_shapes.append(default_shape)

# Drawing the graph
plt.figure(figsize=(15, 10))
unique_shapes = set(node_shapes)
for shape in unique_shapes:
    nx.draw_networkx_nodes(G_id, pos_depth, nodelist=[node for node, node_shape in zip(G_id.nodes(), node_shapes) if node_shape == shape],
                           node_color=[node_colors[i] for i, node_shape in enumerate(node_shapes) if node_shape == shape],
                           node_shape=shape, node_size=500)

nx.draw_networkx_edges(G_id, pos_depth, edge_color='k', style='solid', width=1)

# Create a dictionary mapping node ID to its depth
node_depth_labels = {node_id: f"{row['Depth']}" for _, row in data.iterrows()
                     for node_id in (address_to_id[row['From']], address_to_id[row['To']])}

# Draw labels using the node_depth_labels dictionary
nx.draw_networkx_labels(G_id, pos_depth, labels=node_depth_labels, font_size=12, font_color='white')

nx.draw_networkx_edge_labels(G_id, pos_depth, edge_labels={(u, v): f"{d['State_Comment']}" for u, v, d in G_id.edges(data=True)}, # here the edge comment is added
                             font_color='red')
"""
for shape in unique_shapes:
    nx.draw_networkx_nodes(G_id, pos_depth, nodelist=[node for node, node_shape in zip(G_id.nodes(), node_shapes) if node_shape == shape],
                           node_color=[node_colors[i] for i, node_shape in enumerate(node_shapes) if node_shape == shape],
                           node_shape=shape, node_size=500)
nx.draw_networkx_edges(G_id, pos_depth, edge_color='k', style='solid', width=1)
nx.draw_networkx_labels(G_id, pos_depth, font_size=12, font_color='white')
nx.draw_networkx_edge_labels(G_id, pos_depth, edge_labels={(u, v): f"{d['State_Comment']}" for u, v, d in G_id.edges(data=True)},
                             font_color='red')
"""
# Add legend
red_patch = plt.Line2D([], [], color='red', marker='o', markersize=10, label='Leaf node or Max Depth')
green_patch = plt.Line2D([], [], color='red', marker='^', markersize=10, label='Flow back (loop detected)')
gray_patch = plt.Line2D([], [], color='blue', marker='o', markersize=10, label='Regular node')
plt.legend(handles=[red_patch, green_patch, gray_patch])
plt.title('DFS Graph of a traversal of the Darknet dataset with 4 in width and 5 in depth')
plt.show()
