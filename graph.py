from Node import *
import json

def Drawing(filename):
    with open(f'{filename}.json', 'r', encoding='UTF-8') as f:
        crawling_data = json.load(f)
    
    # Make Address Node List
    graph_node_list = OrderedDict()
    initial_x = 1
    initial_y = 1

    # Add start Node (1,1) & start Node Vout Nodes
    start_node = Node("start", 'spent', initial_x, initial_y)
    graph_node_list['start'] = start_node

    initial_y += 2
    for vout in crawling_data[0]['vout']:
        # 기존의 노드가 이미 있다면 X를 증가시키지 않는다.
        address = vout['address']
        spent = vout['spent']
        if graph_node_list.get(address) != None:
            continue

        vout_node = Node(address, spent, initial_x, initial_y)
        start_node.addNewNode(address, vout_node)
        graph_node_list[address] = vout_node
        initial_x += 30
    
    # 나머지 데이터에 대해 노드와 좌표를 생성한다.
    for tr in crawling_data[1:]:
        # find Previous Node Data
        prev_node = graph_node_list.get(tr['address'])
        prev_x, prev_y = prev_node.get_xy_location()
        prev_y += 2

        # 마지막 노드와 이전 노드의 x를 비교해서 가장 높은 x값을 다음 노드 생성의 X값으로 사용한다.
        last_node_address, last_node = graph_node_list.popitem(last=True)
        last_node_x, las_node_y = last_node.get_xy_location()
        graph_node_list[last_node_address] = last_node

        if prev_y == las_node_y: 
            x = max(prev_x, last_node_x) + 30
        else:
            x = prev_x + 30
        
        # 돈을 받은 사용자들에 대해
        for to in tr['vout']:
            address = to['address']
            vout_node_find = graph_node_list.get(address)

            # 이미 해당 주소에 대한 거래가 존재한다면?
            if vout_node_find != None:
                prev_node.addNewNode(address, vout_node_find)
            # 존재하지 않는다면 노드를 생성하고, 좌표와 연결 리스트에 넣어준다.
            else:
                vout = Node(address, to['spent'], x, prev_y)
                prev_node.addNewNode(address, vout)
                graph_node_list[address] = vout
                x += 30

    # 모든 노드들에 대해 좌표와 연결 노드를 모두 생성
    G = nx.DiGraph()

    node_name = []
    node_color = []
    node_x = []
    node_y = []

    for address, node in graph_node_list.items():
        # 5개의 주소에서 돈을 보내는 경우 마젠타로 설정
        if node.get_node_spent() == 'unspent':
            node_color.append('green')
        elif node.get_directed_node_number() >= 5:
            node_color.append('magenta')
        elif node.get_directed_node_number() >= 3:
            node_color.append('coral')
        else:
            node_color.append('black')
        

        address_node_x, address_node_y = node.get_xy_location()
        # 모든 노드를 Graph에 더한다.
        G.add_node(address, pos=(address_node_x, address_node_y))
        # 노드와 노드간의 연결을 추가
        for connected in node.get_connected_node():
            name = connected.__str__()
            G.add_edge(address, name)

    for node in G.nodes():
        node_name.append(node.__str__())
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    # Node의 정보에 대한 데이터로 추정
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        text=node_name,
        mode='markers',
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            reversescale=True,
            color=node_color,
            size=10,
            colorbar=dict(
                thickness=5,
                title='Node Connections',
                titleside='right'
            ),
            line=dict(width=0)))

    # 그래프에서 노드와 Edge에 대한 정보 추출    
    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,   
        line=dict(width=1.5,color='#BDBDBD'),
        hoverinfo='none',
        mode='lines+text',
        text= []
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        autosize=True,
                        title='<br>Bitcoin Transaction Visualizations',
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),               
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    fig.show()

if __name__ == '__main__':
    Drawing('e1aa3eef4368a5ec6b7c3f8c251a141b67bb7b9cfa3ea1f3109b1250fc8374e7')