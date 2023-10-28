import plotly.graph_objects as go
import networkx as nx
from collections import OrderedDict

class Node:
    
    def __init__(self, address, x, y) -> None:
        self.address = address
        self.x = x
        self.y = y
        self.connectedNode = OrderedDict()

    def __str__(self) -> str:
        return self.address
        
    def addNewNode(self, address, nextNode : 'Node'):
        self.connectedNode[address] = nextNode

    def get_x_location(self):
        return self.x

    def get_y_location(self):
        return self.y
    
    def get_xy_location(self):
        return self.x, self.y
    
    def get_connected_node(self):
        return list(self.connectedNode)