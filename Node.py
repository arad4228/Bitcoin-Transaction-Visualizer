import plotly.graph_objects as go
import networkx as nx
from collections import OrderedDict

class Node:
    
    def __init__(self, address, spent, x, y) -> None:
        self.address = address
        self.x = x
        self.y = y
        self.spent = spent
        self.connectedNode = OrderedDict()
        # 해당 노드를 가르키는 노드들의 갯수
        self.directed_node_number = 0

    def __str__(self) -> str:
        return self.address
        
    def addNewNode(self, address, nextNode : 'Node'):
        nextNode.add_directed_node_number()
        self.connectedNode[address] = nextNode

    def get_x_location(self):
        return self.x

    def get_y_location(self):
        return self.y
    
    def get_xy_location(self):
        return self.x, self.y
    
    def add_directed_node_number(self):
        self.directed_node_number += 1

    def get_directed_node_number(self):
        return self.directed_node_number

    def get_connected_node(self):
        return list(self.connectedNode)
    
    def get_node_spent(self):
        return self.spent
