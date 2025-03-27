import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from main import from_csv


# Set seed for reproducibility
random.seed(42)

# Parse the attendee list
csv_file = 'data/input.txt'
attendees = from_csv(csv_file)
attendee_names = [a.name for a in attendees]
units = sorted(np.unique([a.unit for a in attendees]))
units = [str(u) for u in units]
attendee_offsets = [0 for a in attendees]

unit_offsets = [0 for u in units]
for i, a in enumerate(attendees):
    if a.is_female:
        continue
    iu = units.index(a.unit)
    attendee_offsets[i] = unit_offsets[iu]
    unit_offsets[iu] += .06

unit_offsets = [0 for u in units]
for i, a in enumerate(attendees):
    if not a.is_female:
        continue
    iu = units.index(a.unit)
    attendee_offsets[i] = unit_offsets[iu]
    unit_offsets[iu] += .06

node_labels = {a.name: f"{a.name}/{a.age}" for a in attendees}
node_pos = {a.name: (units.index(a.unit) + attendee_offsets[i], a.age + 6.5*a.is_female) for i, a in enumerate(attendees)}

# Number of nodes and average degree
num_nodes = len(attendees)

# Create an empty graph
G = nx.DiGraph()

# Add nodes
for a in attendees:
    G.add_node(a.name)

# Add weighted edges (edge length proportional to weight)
for node in G.nodes:
    a_idx = attendee_names.index(node)
    a = attendees[a_idx]
    for f in a.friends:
        if f not in attendee_names:
            continue
        fa_idx = attendee_names.index(f)
        fa = attendees[fa_idx]
        age_gap = abs(a.age - fa.age)
        G.add_edge(node, fa.name, weight=age_gap)

# Draw the graph with edge lengths proportional to weights
nx.draw(G, node_pos, with_labels=False, node_size=50, width=1)  # Edge width based on weight (width = weight * multiplier)

# Label the nodes
nx.draw_networkx_labels(G, node_pos, labels=node_labels)

# Add edge labels with weights
# edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in G.edges(data=True)}
# nx.draw_networkx_edge_labels(G, node_pos, edge_labels=edge_labels)

plt.axis("off")  # Turn off axes
plt.show()

