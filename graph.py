from Node import *
import json

def queue(a, b, qty):
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

def collector(x0, x1, y0, y1, qty):
    """line segment end points, how many midpoints, hovertext"""
    ptx = queue(x0, x1, qty) # add 2 because the origin will be in the list
    pty = queue(y0, y1, qty)
    ptx.pop(0); ptx.pop()        # pop first and last (the nodes)
    pty.pop(0); pty.pop()        # pop first and last (the nodes)
    return ptx, pty

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
    transaction_edge_list = list()

    initial_y += 2
    for vout in crawling_data[0]['vout']:
        # 기존의 노드가 이미 있다면 X를 증가시키지 않는다.
        address = vout['address']
        spent = vout['spent']
        prev = graph_node_list.get(address)
        if prev != None:
            start_node.addNewNode(address, prev)
            transaction_edge_list.append(crawling_data[0]['transaction'])
            continue

        vout_node = Node(address, spent, initial_x, initial_y)
        start_node.addNewNode(address, vout_node)
        transaction_edge_list.append(crawling_data[0]['transaction'])
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
                transaction_edge_list.append(tr['transaction'])
            # 존재하지 않는다면 노드를 생성하고, 좌표와 연결 리스트에 넣어준다.
            else:
                vout = Node(address, to['spent'], x, prev_y)
                prev_node.addNewNode(address, vout)
                transaction_edge_list.append(tr['transaction'])

                graph_node_list[address] = vout
                x += 30

    # print(len(graph_node_list.get('36tDjCJdDTR9k38G8rmyvCZxeqqxrskXud').get_connected_node()))
    # 모든 노드들에 대해 좌표와 연결 노드를 모두 생성
    G = nx.DiGraph()

    node_name = []
    node_color = []
    node_x = []
    node_y = []

    for address, node in graph_node_list.items():
        # 5개의 주소에서 돈을 보내는 경우 마젠타로 설정
        spent = node.get_node_spent()
        received = node.get_received_node_number()
        send = node.get_send_node_number()
        if spent == 'unspent':
            node_color.append('green')
        elif received >= 5 and send >= 5:
            node_color.append('violet')
        elif received < 3 and send >= 5:
            node_color.append('blue')
        elif received >= 5 and send < 3:
            node_color.append('orange')
        else:
            node_color.append('black')
        
        node_name.append(f'node: {node.__str__()} \t send: {send} \t received: {received}')
        address_node_x, address_node_y = node.get_xy_location()
        # 모든 노드를 Graph에 더한다.
        G.add_node(address, pos=(address_node_x, address_node_y))
        # 노드와 노드간의 연결을 추가
    
    for address, node in graph_node_list.items():
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
        
        middle_x, middle_y = collector(x0, x1, y0, y1, 3)
        edge_middle_x.extend(middle_x)
        edge_middle_y.extend(middle_y)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,   
        line=dict(width=1,color='#BDBDBD'),
        hoverinfo='none',
        mode='lines',
    )

    edege_text_trace = go.Scatter(
        x = edge_middle_x, y = edge_middle_y, 
        mode='markers', 
        showlegend = False,
        hovertemplate = "Transaction %{hovertext}<extra></extra>",
        hovertext = transaction_edge_list, 
        marker = go.scatter.Marker(
            opacity = 0, 
            size=5,
            color='gray')
    )

    fig = go.Figure(data=[edge_trace, node_trace, edege_text_trace],
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
    
    # fig.add_traces(go.Scatter(x=edge_middle_x, y=edge_middle_y,
    #                       hovertext=edege_text_trace['hovertext'],
    #                       mode='markers',
    #                       marker=dict(
    #                           size=0
    #                           )
    #                           )  # Make the clickable area larger
    # )
    fig.show()

if __name__ == '__main__':
    Drawing('fc359e4309594551cfe597e7bb061189795a25130414886903ac7340271e98a1')