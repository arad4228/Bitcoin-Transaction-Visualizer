import plotly.graph_objects as go
import networkx as nx
from collections import OrderedDict
from collections import deque 

class Node:
    
    def __init__(self, address, spent, x, y) -> None:
        self.address = address
        self.x = x
        self.y = y
        self.spent = spent
        self.connectedNode = OrderedDict()
        # 내가 돈을 받은 주소의 수
        self.received_node_number = 0
        # 내가 돈을 보낸 주소의 수
        self.send_node_number = 0

    def __str__(self) -> str:
        return self.address
        
    def add_new_node(self, address, nextNode : 'Node'):
        if address == self.address:
            return
        # 상대방의 노드이 받은 수와 자신의 돈을 보낸 수를 증가
        check = self.connectedNode.get(address)
        nextNode.add_received_node_number()
        if check == None:
            self.add_send_node_number()
            self.connectedNode[address] = nextNode

    def get_x_location(self):
        return self.x

    def get_y_location(self):
        return self.y
    
    def get_xy_location(self):
        return self.x, self.y
    
    def add_received_node_number(self):
        self.received_node_number = self.received_node_number + 1
    
    def add_send_node_number(self):
        self.send_node_number = self.send_node_number + 1

    def get_received_node_number(self):
        return self.received_node_number

    def get_send_node_number(self):
        return self.send_node_number

    def get_connected_node(self):
        return list(self.connectedNode)
    
    def get_node_spent(self):
        return self.spent
