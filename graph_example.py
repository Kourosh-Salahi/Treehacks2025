"""
- Take in graph data for locations of soldiers
- Define costs associated with transferring soldiers
- Each soldier should have health score from 0 to 1
- Minimize the cost of relocation such that 
the minimum health score is above a threshold
"""

import json
import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network

graph_data = json.load(open("graph_data.json", "r"))

location_target = (2, 3)
threshold = 0.9

target_soldiers = {p: d for p, d in graph_data.items() if tuple(d["location"]) == location_target}
below_threshold = {p for p, d in target_soldiers.items() if d["health"] < threshold}

healthy_soldiers = {p: d for p, d in graph_data.items() if d["health"] >= threshold and tuple(d["location"]) != location_target}

def distance(loc1, loc2):
    return (loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2

# Greedy algorithm which minimizes the distance that you would have to move healthy troops from other locations to get them to be at location_target
# The output should be a list of tuples (person_a, person_b), where person_a is the person to be replaced, and person_b is the person replacing them. 
total_cost = 0
relocation_plan = []
for soldier in below_threshold:
    if not healthy_soldiers:
        break  # No more healthy soldiers to move
    
    # Find the closest healthy soldier
    closest_replacement = min(healthy_soldiers, key=lambda s: distance(tuple(healthy_soldiers[s]["location"]), location_target))
    total_cost += distance(tuple(healthy_soldiers[closest_replacement]["location"]), location_target)
    
    # Record the move
    relocation_plan.append((soldier, closest_replacement))
    
    # Remove the moved soldier from available replacements
    del healthy_soldiers[closest_replacement]

# Output the final relocation plan
print(relocation_plan)
print(total_cost)

locations = {tuple(d["location"]) for d in graph_data.values()}
donor_locations = {tuple(graph_data[p]["location"]) for _, p in relocation_plan}
# Assign colors based on role
colors = {}
for loc in locations:
    if loc == location_target:
        colors[loc] = "green"  # Target location
    elif loc in donor_locations:
        colors[loc] = "red"    # Donor locations
    else:
        colors[loc] = "blue"   # Other locations

# Plot locations
plt.figure(figsize=(8, 6))
for loc, color in colors.items():
    plt.scatter(loc[0], loc[1], color=color, s=200, edgecolors="black", label=color if color not in plt.gca().get_legend_handles_labels()[1] else "")

# Labels and aesthetics
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.title("Soldier Relocation Visualization")
plt.legend(["Target (Green)", "Donor (Red)", "Neutral (Blue)"])
plt.grid(True)
plt.show()

# Create NetworkX graph
G = nx.Graph()

# Add nodes with colors
for loc in locations:
    G.add_node(loc, color=colors[loc])

# Add edges for relocations
edges = []
edge_labels = {}
for donor, receiver in relocation_plan:
    donor_loc = tuple(graph_data[donor]["location"])
    target_loc = tuple(graph_data[receiver]["location"])

    # Ensure the order of the tuple is consistent: donor -> receiver
    edge_tuple = (donor_loc, target_loc) if donor_loc < target_loc else (target_loc, donor_loc)
    
    G.add_edge(donor_loc, target_loc)
    edges.append((donor_loc, target_loc))
    edge_labels[edge_tuple] = edge_labels.get(edge_tuple, "") + f"{donor} → {receiver} "

# --- Matplotlib Visualization ---
plt.figure(figsize=(8, 6))
pos = {loc: loc for loc in locations}  # Position nodes based on coordinates
node_colors = [colors[n] for n in G.nodes]

nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color="black", node_size=1000, font_size=8, font_weight="bold")
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color="red")

plt.title("Relocation Graph with Transfers")
plt.show()

# --- Pyvis (Interactive Web Visualization) ---
nt = Network('500px', '500px', notebook=True)
for node in G.nodes:
    node_id = str(node)  # Convert the tuple to a string
    nt.add_node(node_id, color=colors[node], title=str(node))  # Add tooltips

# Then, when adding edges to the graph, make sure the correct order is followed:
for edge in G.edges:
    edge_tuple = (edge[0], edge[1]) if edge[0] < edge[1] else (edge[1], edge[0])
    label = edge_labels.get(edge_tuple, "")
    nt.add_edge(str(edge[0]), str(edge[1]), title=label)  # Ensure edge ordering

nt.show("nx.html")