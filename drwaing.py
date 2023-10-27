import plotly.graph_objects as go
import networkx as nx

class Node:
    # Connected Node list
    connectedNode = []

    def __init__(self, address, x, y) -> None:
        self.address = address
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return self.address
        
    def addNewNode(self, nextNode : 'Node'):
        self.connectedNode.append(nextNode)

    def get_x_location(self):
        return self.x

    def get_y_location(self):
        return self.y
    
    def get_xy_location(self):
        return self.x, self.y
    
    def get_connected_node(self):
        return self.connectedNode