from Node import *
import json

class Transaction_Graph:

    def __init__(self, filename) -> None:
        self.filename = filename
        self.graph_node_list = OrderedDict()
        self.graph_edge_text_list = list()
        self.vin_x = 1
        self.vin_y = 1
        self.vout_x = 1
        self.vout_y = 11

    def queue(self, a, b, qty):
        """either x0 and x1 or y0 and y1, qty of points to create"""
        q = deque()
        q.append((0, qty - 1)) # indexing starts at 0
        pts = [0] * qty
        pts[0] = a; pts[-1] = b # x0 is the first value, x1 is the last
        while len(q) != 0:
            left, right = q.popleft()       # remove working segment from queue
            center = (left + right + 1)//2  # creates index values for pts
            pts[center] = (pts[left] + pts[right])/2
            if right - left > 2:            # stop when qty met
                q.append((left, center))
                q.append((center, right))
        return pts

    def collector(self, x0, x1, y0, y1, qty):
        """line segment end points, how many midpoints, hovertext"""
        ptx = self.queue(x0, x1, qty) # add 2 because the origin will be in the list
        pty = self.queue(y0, y1, qty)
        ptx.pop(0); ptx.pop()        # pop first and last (the nodes)
        pty.pop(0); pty.pop()        # pop first and last (the nodes)
        return ptx, pty

    def make_graph_data(self):
        # get Json Data
        with open(f'{self.filename}.json', 'r', encoding='UTF-8') as f:
            crawling_data = json.load(f)
        
        # Node 
        for datas in crawling_data[:100]:
            # 전체 노드 생성
            for vin in datas['vin']:
                address = vin['address']
                if self.graph_node_list.get(address) == None:
                    spent = vin['spent']
                    self.graph_node_list[address] =  Node(address, spent, self.vin_x, self.vin_y)
                    self.vin_x += 10

            # vout에 대한 노드 생성
            for vout in datas['vout']:
                address = vout['address']
                spent = vout['spent']
                if self.graph_node_list.get(address) == None:
                    self.graph_node_list[address] = Node(address, spent, self.vout_x, self.vout_y)
                self.vout_x += 10

            # vin과 vout을 연결
            for vin in datas['vin']:
                address = vin['address']
                vin_node = self.graph_node_list.get(address)
                for vout in datas['vout']:
                    vout_address = vout['address']
                    vout_node = self.graph_node_list.get(vout_address)
                    vin_node.add_new_node(vout_address, vout_node)
                    self.graph_edge_text_list.append(datas['transaction'])
            self.vin_x = self.vout_x + 100
            self.vout_x = 1
            self.vin_y = self.vout_y
            self.vout_y += 10
            
    def Drawing(self):
        # 모든 노드들에 대해 좌표와 연결 노드를 모두 생성
        G = nx.DiGraph()

        node_name = []
        node_color = []
        node_x = []
        node_y = []

        for address, node in self.graph_node_list.items():
            # 5개의 주소에서 돈을 보내는 경우 마젠타로 설정
            spent = node.get_node_spent()
            received = node.get_received_node_number()
            send = node.get_send_node_number()
            if spent == 'unspent':
                node_color.append('green')
            elif received >= 10 and send >= 10:
                node_color.append('violet')
            elif received < 5 and send >= 10:
                node_color.append('blue')
            elif send >= 10:
                node_color.append('red')
            elif received >= 10 and send < 5:
                node_color.append('orange')
            elif received >= 10:
                node_color.append('yellow')
            else:
                node_color.append('black')
            
            node_name.append(f'node: {node.__str__()} \t send: {send} \t received: {received}')
            address_node_x, address_node_y = node.get_xy_location()
            # 모든 노드를 Graph에 더한다.
            G.add_node(address, pos=(address_node_x, address_node_y))
            # 노드와 노드간의 연결을 추가
        
        for address, node in self.graph_node_list.items():
            for connected in node.get_connected_node():
                name = connected.__str__()
                G.add_edge(address, name)

        for node in G.nodes():
            x, y = G.nodes[node]['pos']
            node_x.append(x)
            node_y.append(y)

        # Node의 정보에 대한 데이터로 추정
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            text=node_name,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=False,
                colorscale='YlGnBu',
                reversescale=True,
                color=node_color,
                size=10,
                line=dict(width=0)
            )
        )

        # 그래프에서 노드와 Edge에 대한 정보 추출    
        edge_x = []
        edge_y = []
        edge_middle_x = []
        edge_middle_y = []

        for edge in G.edges():
            x0, y0 = G.nodes[edge[0]]['pos']
            x1, y1 = G.nodes[edge[1]]['pos']
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)
            
            middle_x, middle_y = self.collector(x0, x1, y0, y1, 3)
            edge_middle_x.extend(middle_x)
            edge_middle_y.extend(middle_y)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,   
            line=dict(width=1,color='#BDBDBD'),
            hoverinfo='none',
            mode='lines',
        )

        # edege_text_trace = go.Scatter(
        #     x = edge_middle_x, y = edge_middle_y, 
        #     mode='markers', 
        #     showlegend = False,
        #     hovertemplate = "Transaction %{hovertext}<extra></extra>",
        #     hovertext = self.graph_edge_text_list, 
        #     marker = go.scatter.Marker(
        #         opacity = 0, 
        #         size=5,
        #         color='gray')
        # )

        fig = go.Figure(data=[edge_trace, node_trace], # edege_text_trace],
                        layout=go.Layout(
                            autosize=True,
                            title='<br>Bitcoin Transaction Visualizations',
                            titlefont=dict(size=16),
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            # width=7680, height= 4320, 
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        
        fig.show()

if __name__ == '__main__':
    tg = Transaction_Graph('Web_bf05f899c90589cdd3c42a44d032e28933fa819a1c5c19e44d37b2be592afb6b')
    tg.make_graph_data()
    tg.Drawing()
