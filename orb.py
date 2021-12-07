from dataclasses import dataclass
from types import FunctionType
from pprint import pprint
import operator
import random


# Convert orb map into graph
# Use BFS to find shortest path from start (22) to end (30)

# Node has either a value or a function, never both
# Value nodes are connected to function nodes only
# Function nodes are connected to value nodes only
@dataclass(eq=False, frozen=True)
class Node:
	value: int = None
	op: FunctionType = None

node1 = Node(value=22)
node2 = Node(op=operator.sub)
node3 = Node(value=9)
node4 = Node(op=operator.mul)
node5 = Node(op=operator.add)
node6 = Node(value=4)
node7 = Node(op=operator.sub)
node8 = Node(value=18)
node9 = Node(value=4)
node10 = Node(op=operator.mul)
node11 = Node(value=11)
node12 = Node(op=operator.mul)
node13 = Node(op=operator.mul)
node14 = Node(value=8)
node15 = Node(op=operator.sub)
node16 = Node(value=1)

nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9, node10, node11, node12, node13, node14, node15, node16]


#Path is just a list of nodes
#22 - 4 + 22
test_path = [node1, node2, node6, node5, node1]

orb_map = {
	node1: [node2, node5],
	#node2: [node1, node3, node6],
	node2: [node3, node6],
	node3: [node2, node4, node7],
	node4: [node3, node8],
	#node5: [node1, node6, node9],
	node5: [node6, node9],
	node6: [node2, node5, node7, node10],
	node7: [node3, node6, node8, node11],
	node8: [node4, node7, node12],
	node9: [node5, node10, node13],
	node10: [node6, node9, node11, node14],
	node11: [node7, node10, node12, node15],
	node12: [node8, node11, node16],
	node13: [node9, node14],
	node14: [node10, node13, node15],
	node15: [node11, node14, node16],
	node16: [node12, node15]
}

def get_path_value(path):
	value = path[0].value
	for op_node, value_node in zip(path[1::2], path[2::2]):
		value = op_node.op(value, value_node.value)
	return value

def expand_path(path):
	expansions = []
	last_node = path[-1]
	expansion_ops = orb_map[last_node]
	for op_node in expansion_ops:
		expansion_values = orb_map[op_node]
		expansions.extend([path + [op_node] + [value_node] for value_node in expansion_values])
	return expansions

# print(get_path_value(test_path))
# pprint(expand_path([node1]))
# pprint(list(map(get_path_value, expand_path([node1]))))

def find_path_to_30():
	paths = [[node1]]
	while True:
		print(len(paths))
		new_paths = [new_path for old_path in paths for new_path in expand_path(old_path)]
		for path in new_paths:
			if path[-1] == node16:
				if get_path_value(path) == 30:
					return path
				new_paths.remove(path)
		paths = new_paths

# print(find_path_to_30())
# 22 + 22 + 4 - 18 * 1
#      44 + 4 - 18 * 1
#          48 - 18 * 1
#               30 * 1
#                   30
#
#
# north
# south
# north (Return to start)
# east
# east
# north
# north
# But returning to start room makes orb evaporate; disable connections back to node 1

# print(find_path_to_30())
# 22 + 4 - 18 - 4 * 8 - 1 - 1
# 
# north
# east
# east
# east
# west
# west
# north
# north
# east
# east (Reach end)
# west
# east
# But reaching end room makes orb evaporate; prune paths that reach node 16 without total of 30

print(find_path_to_30())
# 22 + 4 - 11 * 4 - 18 - 11 - 1
#
# north
# east
# east
# north
# west 
# south
# east
# east
# west
# north
# north
# east
# But the hourglass is still running; maybe look for a longer path
# Never mind, this is the right answer